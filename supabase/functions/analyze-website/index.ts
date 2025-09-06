import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface AnalysisRequest {
  domain: string
  url: string
  profile_type: string
}

interface AnalysisResult {
  id: string
  domain: string
  classification: string
  confidence: number
  comment: string
  processing_time: number
  credits_used: number
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

    // Get user profile
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

    // Check if user is admin (unlimited credits)
    const isAdmin = profile.role === 'admin'
    
    // Check credits for non-admin users
    if (!isAdmin && profile.credits < 1) {
      return new Response(
        JSON.stringify({ error: 'Insufficient credits' }),
        { 
          status: 402, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Parse request body
    const { domain, url, profile_type }: AnalysisRequest = await req.json()

    if (!domain || !url || !profile_type) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: domain, url, profile_type' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate profile type
    const validProfiles = [
      'software', 'iso', 'telemedicine', 'pharma', 'edtech', 'marketing',
      'fintech', 'healthtech', 'elearning', 'software_products',
      'salesforce_partner', 'hubspot_partner', 'aws', 'shopify',
      'ai_companies', 'mobile_app', 'recruiting', 'banking', 'platforms'
    ]

    if (!validProfiles.includes(profile_type)) {
      return new Response(
        JSON.stringify({ error: 'Invalid profile_type' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Create analysis record
    const { data: analysis, error: analysisError } = await supabaseClient
      .from('analyses')
      .insert({
        user_id: user.id,
        domain,
        url,
        profile_type,
        status: 'processing'
      })
      .select()
      .single()

    if (analysisError || !analysis) {
      return new Response(
        JSON.stringify({ error: 'Failed to create analysis record' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Perform analysis (this would call your Python analysis service)
    const startTime = Date.now()
    
    try {
      // Call Python analysis service
      const analysisResponse = await fetch(`${Deno.env.get('PYTHON_SERVICE_URL')}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Deno.env.get('PYTHON_SERVICE_TOKEN')}`
        },
        body: JSON.stringify({
          domain,
          url,
          profile_type
        })
      })

      if (!analysisResponse.ok) {
        throw new Error(`Analysis service error: ${analysisResponse.status}`)
      }

      const analysisResult = await analysisResponse.json()
      const processingTime = (Date.now() - startTime) / 1000

      // Update analysis record with results
      const { error: updateError } = await supabaseClient
        .from('analyses')
        .update({
          status: 'completed',
          result_classification: analysisResult.classification,
          result_confidence: analysisResult.confidence,
          result_comment: analysisResult.comment,
          processing_time_seconds: processingTime,
          credits_used: 1,
          raw_data: analysisResult,
          completed_at: new Date().toISOString()
        })
        .eq('id', analysis.id)

      if (updateError) {
        console.error('Failed to update analysis:', updateError)
      }

      // Deduct credits for non-admin users
      if (!isAdmin) {
        // Update user credits
        const { error: creditError } = await supabaseClient
          .from('profiles')
          .update({
            credits: profile.credits - 1
          })
          .eq('id', user.id)

        if (creditError) {
          console.error('Failed to update credits:', creditError)
        }

        // Record credit transaction
        await supabaseClient
          .from('credit_transactions')
          .insert({
            user_id: user.id,
            amount: -1,
            transaction_type: 'usage',
            description: `Analysis of ${domain}`,
            analysis_id: analysis.id
          })
      }

      const result: AnalysisResult = {
        id: analysis.id,
        domain,
        classification: analysisResult.classification,
        confidence: analysisResult.confidence,
        comment: analysisResult.comment,
        processing_time: processingTime,
        credits_used: 1
      }

      return new Response(
        JSON.stringify(result),
        { 
          status: 200, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )

    } catch (error) {
      // Update analysis record with error
      await supabaseClient
        .from('analyses')
        .update({
          status: 'failed',
          error_message: error.message,
          completed_at: new Date().toISOString()
        })
        .eq('id', analysis.id)

      return new Response(
        JSON.stringify({ error: 'Analysis failed', details: error.message }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

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
