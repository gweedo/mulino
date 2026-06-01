import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Gate checks only for the *presence* of the session cookie;
// the backend still verifies it on every request.
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // The login page itself must stay reachable, or the redirect would loop.
  if (pathname === '/admin/login') {
    return NextResponse.next()
  }

  if (!request.cookies.has('session')) {
    const url = request.nextUrl.clone()
    url.pathname = '/admin/login'
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/admin', '/admin/:path*'],
}
