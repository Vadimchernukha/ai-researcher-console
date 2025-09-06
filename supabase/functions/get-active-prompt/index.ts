import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface GetActivePromptRequest {
  profile_type: string
  prompt_type: 'extraction' | 'classification'
}

interface ActivePromptResponse {
  id: string
  name: string
  content: string
  variables: Record<string, any>
  version: number
  profile_type: string
  prompt_type: string
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
    const { profile_type, prompt_type }: GetActivePromptRequest = await req.json()

    if (!profile_type || !prompt_type) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: profile_type, prompt_type' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate prompt_type
    if (!['extraction', 'classification'].includes(prompt_type)) {
      return new Response(
        JSON.stringify({ error: 'Invalid prompt_type. Must be "extraction" or "classification"' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get active prompt using the database function
    const { data, error } = await supabaseClient
      .rpc('get_active_prompt', {
        p_profile_type: profile_type,
        p_prompt_type: prompt_type
      })

    if (error) {
      console.error('Database error:', error)
      return new Response(
        JSON.stringify({ error: 'Failed to fetch active prompt' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    if (!data || data.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No active prompt found for this profile and type' }),
        { 
          status: 404, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const prompt = data[0]

    const response: ActivePromptResponse = {
      id: prompt.id,
      name: prompt.name,
      content: prompt.content,
      variables: prompt.variables || {},
      version: prompt.version,
      profile_type: profile_type,
      prompt_type: prompt_type
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
