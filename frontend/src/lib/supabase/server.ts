/**
 * Supabase client for Server Actions and Server Components. One per request.
 */
import { createServerClient } from '@supabase/ssr'
import { cookies, headers } from 'next/headers'
import { authCookieOptions, supabaseEnv } from './config'

export async function createSupabaseServerClient() {
  const store = await cookies()
  const https = (await headers()).get('x-forwarded-proto') === 'https'
  const { url, key } = supabaseEnv()

  return createServerClient(url, key, {
    cookieOptions: authCookieOptions(https),
    cookies: {
      getAll: () => store.getAll(),
      setAll: (toSet) => {
        try {
          toSet.forEach(({ name, value, options }) => store.set(name, value, options))
        } catch {
          // Server Components can't set cookies; proxy.ts keeps the session fresh.
        }
      },
    },
  })
}

/**
 * Authorization header carrying the Supabase access token to FastAPI, which
 * verifies it. The token is only forwarded, never trusted here.
 */
export async function authHeader(): Promise<Record<string, string>> {
  const supabase = await createSupabaseServerClient()
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}
