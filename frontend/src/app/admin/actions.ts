'use server'

import { revalidateTag, updateTag } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

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

async function sessionHeader(): Promise<HeadersInit> {
  const store = await cookies()
  const session = store.get('session')
  return session ? { Cookie: `session=${session.value}` } : {}
}

function invalidatePizzas() {
  updateTag('pizzas')
  revalidateTag('pizzas', 'seconds')
}

export async function createPizzaAction(data: PizzaFormValues) {
  const res = await fetch(`${BACKEND}/api/pizzas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await sessionHeader()) },
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
    headers: { 'Content-Type': 'application/json', ...(await sessionHeader()) },
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
    headers: { 'Content-Type': 'application/json', ...(await sessionHeader()) },
    body: JSON.stringify({ available }),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  invalidatePizzas()
}

export async function deletePizzaAction(id: string) {
  const res = await fetch(`${BACKEND}/api/pizzas/${id}`, {
    method: 'DELETE',
    headers: await sessionHeader(),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  invalidatePizzas()
}

export async function logoutAction() {
  await fetch(`${BACKEND}/api/auth/logout`, {
    method: 'POST',
    headers: await sessionHeader(),
  })
  const store = await cookies()
  store.delete('session')
  redirect('/admin/login')
}
