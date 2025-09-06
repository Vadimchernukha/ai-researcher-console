import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CreateSessionRequest {
  name: string
  profile_type: string
  domains: string[]
}

interface CreateSessionResponse {
  session_id: string
  total_domains: number
  estimated_credits: number
  message: string
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

    // Parse request body
    const { name, profile_type, domains }: CreateSessionRequest = await req.json()

    if (!name || !profile_type || !domains || !Array.isArray(domains) || domains.length === 0) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: name, profile_type, domains' }),
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

    // Check domain limit
    const maxDomainsPerSession = 1000
    if (domains.length > maxDomainsPerSession) {
      return new Response(
        JSON.stringify({ error: `Too many domains. Maximum ${maxDomainsPerSession} per session.` }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Check credits for non-admin users
    const isAdmin = profile.role === 'admin'
    const estimatedCredits = domains.length

    if (!isAdmin && profile.credits < estimatedCredits) {
      return new Response(
        JSON.stringify({ 
          error: 'Insufficient credits',
          required: estimatedCredits,
          available: profile.credits
        }),
        { 
          status: 402, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Create analysis session
    const { data: session, error: sessionError } = await supabaseClient
      .from('analysis_sessions')
      .insert({
        user_id: user.id,
        name,
        profile_type,
        total_domains: domains.length,
        status: 'pending'
      })
      .select()
      .single()

    if (sessionError || !session) {
      return new Response(
        JSON.stringify({ error: 'Failed to create session' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Create session domains
    const sessionDomains = domains.map(domain => ({
      session_id: session.id,
      domain: domain.replace(/^https?:\/\//, '').split('/')[0], // Extract domain only
      url: domain.startsWith('http') ? domain : `https://${domain}`
    }))

    const { error: domainsError } = await supabaseClient
      .from('session_domains')
      .insert(sessionDomains)

    if (domainsError) {
      // Clean up session if domains insertion failed
      await supabaseClient
        .from('analysis_sessions')
        .delete()
        .eq('id', session.id)

      return new Response(
        JSON.stringify({ error: 'Failed to create session domains' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const response: CreateSessionResponse = {
      session_id: session.id,
      total_domains: domains.length,
      estimated_credits: estimatedCredits,
      message: isAdmin 
        ? 'Session created successfully (admin - unlimited credits)'
        : `Session created successfully. ${estimatedCredits} credits will be used.`
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
