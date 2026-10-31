import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createServerClient } from '@supabase/ssr'
import { authCookieOptions, supabaseEnv } from '@/lib/supabase/config'

// Refreshes the Supabase session and redirects visitors without a verified one.
// This is a convenience, not the security boundary: FastAPI verifies the token
// on every admin request (ADR 0001).
export async function proxy(request: NextRequest) {
  // The login page itself must stay reachable, or the redirect would loop.
  if (request.nextUrl.pathname === '/admin/login') {
    return NextResponse.next()
  }

  const { url, key } = supabaseEnv()
  let response = NextResponse.next({ request })

  const supabase = createServerClient(url, key, {
    cookieOptions: authCookieOptions(request.nextUrl.protocol === 'https:'),
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll: (toSet, cacheHeaders) => {
        toSet.forEach(({ name, value }) => request.cookies.set(name, value))
        response = NextResponse.next({ request })
        toSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
        Object.entries(cacheHeaders ?? {}).forEach(([k, v]) => response.headers.set(k, v))
      },
    },
  })

  // getClaims() verifies the JWT (and refreshes it if needed); getSession() would not.
  const { data } = await supabase.auth.getClaims()
  if (!data?.claims) {
    const loginUrl = request.nextUrl.clone()
    loginUrl.pathname = '/admin/login'
    return NextResponse.redirect(loginUrl)
  }

  return response
}

export const config = {
  matcher: ['/admin', '/admin/:path*'],
}
