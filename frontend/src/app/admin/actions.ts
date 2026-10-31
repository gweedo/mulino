'use server'

import { revalidateTag, updateTag } from 'next/cache'
import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { createRateLimiter } from '@/lib/rate-limit'
import { authHeader, createSupabaseServerClient } from '@/lib/supabase/server'

const BACKEND = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'

/** Shape that PizzaForm always submits. */
export interface PizzaFormValues {
  name: string
  description: string
  ingredients: string[]
  allergens: string[]
  price_amount: string
  price_currency: string
  available?: boolean
}

// Same budget the backend's slowapi limit used to enforce: 5 attempts/min/IP.
// Supabase's own limit counts per IP too, and every call comes from this server.
const loginLimiter = createRateLimiter({ limit: 5, windowMs: 60_000 })

function invalidatePizzas() {
  updateTag('pizzas')
  revalidateTag('pizzas', 'seconds')
}

export async function createPizzaAction(data: PizzaFormValues) {
  const res = await fetch(`${BACKEND}/api/pizzas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `${res.status}`)
  }
  invalidatePizzas()
  redirect('/admin')
}

export async function updatePizzaAction(id: string, data: PizzaFormValues) {
  const res = await fetch(`${BACKEND}/api/pizzas/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `${res.status}`)
  }
  invalidatePizzas()
  redirect('/admin')
}

export async function toggleAvailabilityAction(id: string, available: boolean) {
  const res = await fetch(`${BACKEND}/api/pizzas/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify({ available }),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  invalidatePizzas()
}

export async function deletePizzaAction(id: string) {
  const res = await fetch(`${BACKEND}/api/pizzas/${id}`, {
    method: 'DELETE',
    headers: await authHeader(),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  invalidatePizzas()
}

export async function loginAction(email: string, password: string) {
  const forwardedFor = (await headers()).get('x-forwarded-for') ?? ''
  const ip = forwardedFor.split(',')[0].trim() || 'unknown'
  if (!loginLimiter.allow(ip)) throw new Error('429')

  const supabase = await createSupabaseServerClient()
  const { error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) {
    if (error.code === 'invalid_credentials') throw new Error('401')
    throw new Error(`${error.status ?? 500}`)
  }
  // No redirect() here — redirect() throws a special pseudo-error that gets
  // swallowed by the try-catch in LoginForm's useTransition. The client
  // navigates to /admin after this action resolves successfully.
}

export async function logoutAction() {
  const supabase = await createSupabaseServerClient()
  // 'local' ends only this browser's session; a Menu Manager's other devices stay signed in.
  await supabase.auth.signOut({ scope: 'local' })
  redirect('/admin/login')
}
