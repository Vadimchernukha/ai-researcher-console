import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CreatePromptRequest {
  name: string
  profile_type: string
  prompt_type: 'extraction' | 'classification'
  content: string
  variables?: Record<string, any>
  is_default?: boolean
}

interface UpdatePromptRequest {
  id: string
  content?: string
  variables?: Record<string, any>
  is_active?: boolean
  is_default?: boolean
}

interface PromptResponse {
  id: string
  name: string
  profile_type: string
  prompt_type: string
  version: number
  content: string
  variables: Record<string, any>
  is_active: boolean
  is_default: boolean
  performance_score?: number
  usage_count: number
  success_rate?: number
  avg_processing_time?: number
  created_at: string
  updated_at: string
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

    // Check if user is admin
    const { data: profile, error: profileError } = await supabaseClient
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single()

    if (profileError || !profile || profile.role !== 'admin') {
      return new Response(
        JSON.stringify({ error: 'Admin access required' }),
        { 
          status: 403, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const url = new URL(req.url)
    const method = req.method
    const path = url.pathname.split('/').pop()

    switch (method) {
      case 'GET':
        return await handleGetPrompts(supabaseClient, url)
      
      case 'POST':
        if (path === 'create') {
          return await handleCreatePrompt(supabaseClient, req, user.id)
        } else if (path === 'update') {
          return await handleUpdatePrompt(supabaseClient, req, user.id)
        } else if (path === 'activate') {
          return await handleActivatePrompt(supabaseClient, req, user.id)
        } else if (path === 'deactivate') {
          return await handleDeactivatePrompt(supabaseClient, req, user.id)
        } else if (path === 'set-default') {
          return await handleSetDefaultPrompt(supabaseClient, req, user.id)
        }
        break
      
      case 'DELETE':
        return await handleDeletePrompt(supabaseClient, req, user.id)
    }

    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { 
        status: 405, 
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

async function handleGetPrompts(supabaseClient: any, url: URL) {
  const profileType = url.searchParams.get('profile_type')
  const promptType = url.searchParams.get('prompt_type')
  const activeOnly = url.searchParams.get('active_only') === 'true'

  let query = supabaseClient
    .from('prompts')
    .select('*')
    .order('updated_at', { ascending: false })

  if (profileType) {
    query = query.eq('profile_type', profileType)
  }
  
  if (promptType) {
    query = query.eq('prompt_type', promptType)
  }
  
  if (activeOnly) {
    query = query.eq('is_active', true)
  }

  const { data, error } = await query

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to fetch prompts' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompts: data }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleCreatePrompt(supabaseClient: any, req: Request, userId: string) {
  const body: CreatePromptRequest = await req.json()

  if (!body.name || !body.profile_type || !body.prompt_type || !body.content) {
    return new Response(
      JSON.stringify({ error: 'Missing required fields' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  // If setting as default, deactivate other defaults for this profile/type
  if (body.is_default) {
    await supabaseClient
      .from('prompts')
      .update({ is_default: false })
      .eq('profile_type', body.profile_type)
      .eq('prompt_type', body.prompt_type)
  }

  const { data, error } = await supabaseClient
    .from('prompts')
    .insert({
      name: body.name,
      profile_type: body.profile_type,
      prompt_type: body.prompt_type,
      content: body.content,
      variables: body.variables || {},
      is_default: body.is_default || false,
      created_by: userId
    })
    .select()
    .single()

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to create prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompt: data }),
    { 
      status: 201, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleUpdatePrompt(supabaseClient: any, req: Request, userId: string) {
  const body: UpdatePromptRequest = await req.json()

  if (!body.id) {
    return new Response(
      JSON.stringify({ error: 'Missing prompt ID' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  // If setting as default, deactivate other defaults
  if (body.is_default) {
    const { data: currentPrompt } = await supabaseClient
      .from('prompts')
      .select('profile_type, prompt_type')
      .eq('id', body.id)
      .single()

    if (currentPrompt) {
      await supabaseClient
        .from('prompts')
        .update({ is_default: false })
        .eq('profile_type', currentPrompt.profile_type)
        .eq('prompt_type', currentPrompt.prompt_type)
        .neq('id', body.id)
    }
  }

  const updateData: any = {}
  if (body.content !== undefined) updateData.content = body.content
  if (body.variables !== undefined) updateData.variables = body.variables
  if (body.is_active !== undefined) updateData.is_active = body.is_active
  if (body.is_default !== undefined) updateData.is_default = body.is_default

  const { data, error } = await supabaseClient
    .from('prompts')
    .update(updateData)
    .eq('id', body.id)
    .select()
    .single()

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to update prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompt: data }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleActivatePrompt(supabaseClient: any, req: Request, userId: string) {
  const { id } = await req.json()

  if (!id) {
    return new Response(
      JSON.stringify({ error: 'Missing prompt ID' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  const { data, error } = await supabaseClient
    .from('prompts')
    .update({ is_active: true })
    .eq('id', id)
    .select()
    .single()

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to activate prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompt: data }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleDeactivatePrompt(supabaseClient: any, req: Request, userId: string) {
  const { id } = await req.json()

  if (!id) {
    return new Response(
      JSON.stringify({ error: 'Missing prompt ID' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  const { data, error } = await supabaseClient
    .from('prompts')
    .update({ is_active: false })
    .eq('id', id)
    .select()
    .single()

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to deactivate prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompt: data }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleSetDefaultPrompt(supabaseClient: any, req: Request, userId: string) {
  const { id } = await req.json()

  if (!id) {
    return new Response(
      JSON.stringify({ error: 'Missing prompt ID' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  // Get current prompt details
  const { data: currentPrompt } = await supabaseClient
    .from('prompts')
    .select('profile_type, prompt_type')
    .eq('id', id)
    .single()

  if (!currentPrompt) {
    return new Response(
      JSON.stringify({ error: 'Prompt not found' }),
      { 
        status: 404, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  // Deactivate other defaults for this profile/type
  await supabaseClient
    .from('prompts')
    .update({ is_default: false })
    .eq('profile_type', currentPrompt.profile_type)
    .eq('prompt_type', currentPrompt.prompt_type)
    .neq('id', id)

  // Set this prompt as default
  const { data, error } = await supabaseClient
    .from('prompts')
    .update({ is_default: true, is_active: true })
    .eq('id', id)
    .select()
    .single()

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to set default prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ prompt: data }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}

async function handleDeletePrompt(supabaseClient: any, req: Request, userId: string) {
  const url = new URL(req.url)
  const id = url.searchParams.get('id')

  if (!id) {
    return new Response(
      JSON.stringify({ error: 'Missing prompt ID' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  const { error } = await supabaseClient
    .from('prompts')
    .delete()
    .eq('id', id)

  if (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to delete prompt' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  return new Response(
    JSON.stringify({ message: 'Prompt deleted successfully' }),
    { 
      status: 200, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    }
  )
}
