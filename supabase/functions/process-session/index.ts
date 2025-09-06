import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ProcessSessionRequest {
  session_id: string
}

interface ProcessSessionResponse {
  session_id: string
  status: string
  message: string
  total_domains: number
  processed_domains: number
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // Get user from JWT
    const {
      data: { user },
      error: userError,
    } = await supabaseClient.auth.getUser()

    if (userError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Parse request body
    const { session_id }: ProcessSessionRequest = await req.json()

    if (!session_id) {
      return new Response(
        JSON.stringify({ error: 'Missing required field: session_id' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get session details
    const { data: session, error: sessionError } = await supabaseClient
      .from('analysis_sessions')
      .select('*')
      .eq('id', session_id)
      .eq('user_id', user.id)
      .single()

    if (sessionError || !session) {
      return new Response(
        JSON.stringify({ error: 'Session not found' }),
        { 
          status: 404, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Check if session is already processing or completed
    if (session.status === 'processing') {
      return new Response(
        JSON.stringify({ error: 'Session is already being processed' }),
        { 
          status: 409, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    if (session.status === 'completed') {
      return new Response(
        JSON.stringify({ error: 'Session is already completed' }),
        { 
          status: 409, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get user profile to check credits
    const { data: profile, error: profileError } = await supabaseClient
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (profileError || !profile) {
      return new Response(
        JSON.stringify({ error: 'Profile not found' }),
        { 
          status: 404, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Check credits for non-admin users
    const isAdmin = profile.role === 'admin'
    const remainingDomains = session.total_domains - session.processed_domains

    if (!isAdmin && profile.credits < remainingDomains) {
      return new Response(
        JSON.stringify({ 
          error: 'Insufficient credits',
          required: remainingDomains,
          available: profile.credits
        }),
        { 
          status: 402, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Update session status to processing
    const { error: updateError } = await supabaseClient
      .from('analysis_sessions')
      .update({
        status: 'processing',
        started_at: new Date().toISOString()
      })
      .eq('id', session_id)

    if (updateError) {
      return new Response(
        JSON.stringify({ error: 'Failed to update session status' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get pending domains for this session
    const { data: pendingDomains, error: domainsError } = await supabaseClient
      .from('session_domains')
      .select('*')
      .eq('session_id', session_id)
      .eq('status', 'pending')
      .limit(10) // Process in batches

    if (domainsError) {
      return new Response(
        JSON.stringify({ error: 'Failed to get pending domains' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    if (!pendingDomains || pendingDomains.length === 0) {
      // No more domains to process, mark session as completed
      await supabaseClient
        .from('analysis_sessions')
        .update({
          status: 'completed',
          completed_at: new Date().toISOString()
        })
        .eq('id', session_id)

      return new Response(
        JSON.stringify({
          session_id,
          status: 'completed',
          message: 'All domains have been processed',
          total_domains: session.total_domains,
          processed_domains: session.total_domains
        }),
        { 
          status: 200, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Process domains asynchronously
    const processDomains = async () => {
      let processedCount = 0
      let successfulCount = 0
      let failedCount = 0
      let creditsUsed = 0

      for (const domain of pendingDomains) {
        try {
          // Update domain status to processing
          await supabaseClient
            .from('session_domains')
            .update({ status: 'processing' })
            .eq('id', domain.id)

          // Call Python analysis service
          const analysisResponse = await fetch(`${Deno.env.get('PYTHON_SERVICE_URL')}/analyze`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${Deno.env.get('PYTHON_SERVICE_TOKEN')}`
            },
            body: JSON.stringify({
              domain: domain.domain,
              url: domain.url,
              profile_type: session.profile_type
            })
          })

          if (analysisResponse.ok) {
            const analysisResult = await analysisResponse.json()

            // Create analysis record
            const { data: analysis, error: analysisError } = await supabaseClient
              .from('analyses')
              .insert({
                user_id: user.id,
                domain: domain.domain,
                url: domain.url,
                profile_type: session.profile_type,
                status: 'completed',
                result_classification: analysisResult.classification,
                result_confidence: analysisResult.confidence,
                result_comment: analysisResult.comment,
                processing_time_seconds: analysisResult.processing_time,
                credits_used: 1,
                raw_data: analysisResult
              })
              .select()
              .single()

            if (!analysisError && analysis) {
              // Update domain with analysis reference
              await supabaseClient
                .from('session_domains')
                .update({ 
                  status: 'completed',
                  analysis_id: analysis.id
                })
                .eq('id', domain.id)

              successfulCount++
            } else {
              throw new Error('Failed to save analysis')
            }
          } else {
            throw new Error(`Analysis failed: ${analysisResponse.status}`)
          }

          processedCount++
          creditsUsed++

          // Deduct credits for non-admin users
          if (!isAdmin) {
            await supabaseClient
              .from('profiles')
              .update({
                credits: profile.credits - creditsUsed
              })
              .eq('id', user.id)

            // Record credit transaction
            await supabaseClient
              .from('credit_transactions')
              .insert({
                user_id: user.id,
                amount: -1,
                transaction_type: 'usage',
                description: `Batch analysis of ${domain.domain}`,
                analysis_id: analysis?.id
              })
          }

        } catch (error) {
          console.error(`Error processing domain ${domain.domain}:`, error)

          // Update domain status to failed
          await supabaseClient
            .from('session_domains')
            .update({ 
              status: 'failed'
            })
            .eq('id', domain.id)

          failedCount++
          processedCount++
        }
      }

      // Update session statistics
      await supabaseClient
        .from('analysis_sessions')
        .update({
          processed_domains: session.processed_domains + processedCount,
          successful_analyses: session.successful_analyses + successfulCount,
          failed_analyses: session.failed_analyses + failedCount,
          credits_used: session.credits_used + creditsUsed
        })
        .eq('id', session_id)

      // Check if session is complete
      const { data: updatedSession } = await supabaseClient
        .from('analysis_sessions')
        .select('*')
        .eq('id', session_id)
        .single()

      if (updatedSession && updatedSession.processed_domains >= updatedSession.total_domains) {
        await supabaseClient
          .from('analysis_sessions')
          .update({
            status: 'completed',
            completed_at: new Date().toISOString()
          })
          .eq('id', session_id)
      }
    }

    // Start processing in background
    processDomains().catch(console.error)

    const response: ProcessSessionResponse = {
      session_id,
      status: 'processing',
      message: `Started processing ${pendingDomains.length} domains`,
      total_domains: session.total_domains,
      processed_domains: session.processed_domains
    }

    return new Response(
      JSON.stringify(response),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Internal server error', details: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})
