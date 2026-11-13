'use server'

import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import * as backend from '@/lib/backend'
import { createRateLimiter } from '@/lib/rate-limit'
import type { Result } from '@/lib/result'
import { createSupabaseServerClient } from '@/lib/supabase/server'
import type { PizzaIn, PizzaOut, PizzaUpdate } from '@/lib/types'

// Expected failures are return values, never thrown: Next.js may strip thrown
// messages in production, and the components branch on `error.kind`.

export async function createPizzaAction(input: PizzaIn): Promise<Result<PizzaOut>> {
  return backend.createPizza(input)
}

export async function updatePizzaAction(id: string, patch: PizzaUpdate): Promise<Result<void>> {
  return backend.updatePizza(id, patch)
}

export async function toggleAvailabilityAction(
  id: string,
  available: boolean,
): Promise<Result<void>> {
  return backend.updatePizza(id, { available })
}

export async function deletePizzaAction(id: string): Promise<Result<void>> {
  return backend.deletePizza(id)
}

/** Saves the whole Menu Order; `conflict` means the Menu changed meanwhile. */
export async function reorderPizzasAction(pizzaIds: string[]): Promise<Result<void>> {
  return backend.rearrangeMenu(pizzaIds)
}

// ── Login / logout ───────────────────────────────────────────────────────────

export type LoginResult =
  | { ok: true }
  | { ok: false; error: { kind: 'invalid_credentials' | 'rate_limited' | 'unavailable' } }

// Same budget the backend's slowapi limit used to enforce: 5 attempts/min/IP.
// Supabase's own limit counts per IP too, and every call comes from this server.
const loginLimiter = createRateLimiter({ limit: 5, windowMs: 60_000 })

export async function loginAction(email: string, password: string): Promise<LoginResult> {
  const forwardedFor = (await headers()).get('x-forwarded-for') ?? ''
  const ip = forwardedFor.split(',')[0].trim() || 'unknown'
  if (!loginLimiter.allow(ip)) return { ok: false, error: { kind: 'rate_limited' } }

  const supabase = await createSupabaseServerClient()
  const { error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) {
    const kind = error.code === 'invalid_credentials' ? 'invalid_credentials' : 'unavailable'
    return { ok: false, error: { kind } }
  }
  // The client navigates to /admin on { ok: true }.
  return { ok: true }
}

export async function logoutAction() {
  const supabase = await createSupabaseServerClient()
  // 'local' ends only this browser's session; a Menu Manager's other devices stay signed in.
  await supabase.auth.signOut({ scope: 'local' })
  redirect('/admin/login')
}
