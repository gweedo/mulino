/**
 * The one module that talks to FastAPI. Server-only: FastAPI is reached from the
 * Next.js server, never from the browser (ADR 0004).
 *
 * Every function returns a Result instead of throwing. Admin calls forward the
 * Supabase access token; FastAPI verifies it. Successful mutations invalidate the
 * cached public Menu, so callers can't forget to.
 */
import 'server-only'
import { revalidateTag, updateTag } from 'next/cache'
import { authHeader } from '@/lib/supabase/server'
import type { BackendErrorKind, Result } from '@/lib/result'
import type { PizzaIn, PizzaOut, PizzaUpdate } from '@/lib/types'

const PIZZAS_TAG = 'pizzas'

function baseUrl(): string {
  return process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'
}

function kindFor(status: number): BackendErrorKind {
  if (status === 401) return 'unauthorized'
  if (status === 403) return 'forbidden'
  if (status === 404) return 'not_found'
  if (status === 409) return 'conflict'
  if (status === 400 || status === 422) return 'validation'
  return 'unavailable'
}

async function detailOf(res: Response): Promise<string | undefined> {
  try {
    const body: unknown = await res.json()
    const detail = (body as { detail?: unknown } | null)?.detail
    return typeof detail === 'string' ? detail : undefined
  } catch {
    return undefined
  }
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  admin: boolean
  next?: { tags: string[]; revalidate: number }
}

async function request<T>(path: string, opts: RequestOptions): Promise<Result<T>> {
  const headers: Record<string, string> = opts.admin ? await authHeader() : {}
  if (opts.body !== undefined) headers['Content-Type'] = 'application/json'

  let res: Response
  try {
    res = await fetch(`${baseUrl()}${path}`, {
      method: opts.method ?? 'GET',
      headers,
      body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
      ...(opts.next ? { next: opts.next } : { cache: 'no-store' }),
    })
  } catch {
    return { ok: false, error: { kind: 'unavailable' } }
  }

  if (!res.ok) {
    const detail = await detailOf(res)
    return {
      ok: false,
      error: detail === undefined ? { kind: kindFor(res.status) } : { kind: kindFor(res.status), detail },
    }
  }
  if (res.status === 204) return { ok: true, data: undefined as T }
  try {
    return { ok: true, data: (await res.json()) as T }
  } catch {
    return { ok: false, error: { kind: 'unavailable' } }
  }
}

/** Mutations: on success, expire the cached public Menu (read-your-own-writes). */
async function mutate<T>(path: string, opts: Omit<RequestOptions, 'admin'>): Promise<Result<T>> {
  const result = await request<T>(path, { ...opts, admin: true })
  if (result.ok) {
    updateTag(PIZZAS_TAG)
    revalidateTag(PIZZAS_TAG, 'seconds')
  }
  return result
}

// ── Public ───────────────────────────────────────────────────────────────────

/** The Available pizzas in Menu Order, cached for the homepage (ISR, 60s). */
export function listMenu(): Promise<Result<PizzaOut[]>> {
  return request('/api/pizzas', { admin: false, next: { tags: [PIZZAS_TAG], revalidate: 60 } })
}

// ── Admin ────────────────────────────────────────────────────────────────────

/** Every pizza, Available or not, in Menu Order. */
export function listAdminPizzas(): Promise<Result<PizzaOut[]>> {
  return request('/api/admin/pizzas', { admin: true })
}

export function getAdminPizza(id: string): Promise<Result<PizzaOut>> {
  return request(`/api/admin/pizzas/${encodeURIComponent(id)}`, { admin: true })
}

export function createPizza(input: PizzaIn): Promise<Result<PizzaOut>> {
  return mutate('/api/admin/pizzas', { method: 'POST', body: input })
}

/** Changes only the fields present in `patch`, including `available`. */
export function updatePizza(id: string, patch: PizzaUpdate): Promise<Result<void>> {
  return mutate(`/api/admin/pizzas/${encodeURIComponent(id)}`, { method: 'PUT', body: patch })
}

export function deletePizza(id: string): Promise<Result<void>> {
  return mutate(`/api/admin/pizzas/${encodeURIComponent(id)}`, { method: 'DELETE' })
}

/** Saves the whole Menu Order; `conflict` means the Menu changed since it was loaded. */
export function rearrangeMenu(pizzaIds: string[]): Promise<Result<void>> {
  return mutate('/api/admin/pizzas/order', { method: 'PUT', body: { pizza_ids: pizzaIds } })
}
