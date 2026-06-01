/**
 * Typed HTTP client for browser-side (admin) API calls.
 * Uses relative URLs so Next.js rewrites /api/* → BACKEND_INTERNAL_URL/api/*.
 */
import type { MeResponse, PizzaIn, PizzaOut, PizzaUpdate } from './types'

const BASE = '/api'

/** Thrown by every failed request so callers can branch on the HTTP status. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    statusText: string,
  ) {
    super(`${status} ${statusText}`)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) throw new ApiError(res.status, res.statusText)
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

// ── Auth ──────────────────────────────────────────────────────────────────
export const login = (email: string, password: string) =>
  request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

export const logout = () =>
  request<void>('/auth/logout', { method: 'POST' })

export const me = () =>
  request<MeResponse>('/auth/me')

// ── Pizzas (public) ───────────────────────────────────────────────────────
export const listPizzas = () =>
  request<PizzaOut[]>('/pizzas')

// ── Pizzas (admin) ────────────────────────────────────────────────────────
export const listAllPizzas = () =>
  request<PizzaOut[]>('/admin/pizzas')

export const createPizza = (data: PizzaIn) =>
  request<PizzaOut>('/pizzas', { method: 'POST', body: JSON.stringify(data) })

export const updatePizza = (id: string, data: PizzaUpdate) =>
  request<void>(`/pizzas/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deletePizza = (id: string) =>
  request<void>(`/pizzas/${id}`, { method: 'DELETE' })
