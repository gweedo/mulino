/**
 * Shared Supabase settings for the server client and proxy.ts.
 * Server-only env vars: no Supabase client ever runs in the browser (ADR 0001).
 */
import type { CookieOptionsWithName } from '@supabase/ssr'

export function supabaseEnv(): { url: string; key: string } {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_PUBLISHABLE_KEY
  if (!url || !key) {
    throw new Error('SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set')
  }
  return { url, key }
}

// @supabase/ssr defaults to httpOnly: false so a browser client can read the
// tokens. We never create one, so keep the session cookies out of JS reach.
export function authCookieOptions(https: boolean): CookieOptionsWithName {
  return { httpOnly: true, sameSite: 'lax', secure: https, path: '/' }
}
