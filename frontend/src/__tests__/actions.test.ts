import {
  loginAction,
  logoutAction,
  createPizzaAction,
  updatePizzaAction,
  toggleAvailabilityAction,
  deletePizzaAction,
  reorderPizzasAction,
} from '@/app/admin/actions'

const { auth, headerStore, redirectMock, backend } = vi.hoisted(() => ({
  backend: {
    createPizza: vi.fn(),
    updatePizza: vi.fn(),
    deletePizza: vi.fn(),
    rearrangeMenu: vi.fn(),
  },
  auth: {
    signInWithPassword: vi.fn(),
    signOut: vi.fn(),
    getSession: vi.fn(),
  },
  headerStore: new Map<string, string>(),
  redirectMock: vi.fn(),
}))

vi.mock('@supabase/ssr', () => ({ createServerClient: () => ({ auth }) }))
vi.mock('next/headers', () => ({
  headers: async () => ({ get: (k: string) => headerStore.get(k) ?? null }),
  cookies: async () => ({ getAll: () => [], set: vi.fn() }),
}))
vi.mock('next/cache', () => ({ revalidateTag: vi.fn(), updateTag: vi.fn() }))
vi.mock('next/navigation', () => ({ redirect: redirectMock }))
vi.mock('@/lib/backend', () => backend)

const pizzaIn = {
  name: 'Diavola',
  description: 'd',
  ingredients: ['x'],
  allergens: [],
  price_amount: '9.00',
  price_currency: 'EUR',
}

let ipCounter = 0
beforeEach(() => {
  vi.clearAllMocks()
  process.env.SUPABASE_URL = 'https://test-project.supabase.co'
  process.env.SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_test'
  // A fresh client IP per test keeps the module-level rate limiter isolated.
  headerStore.set('x-forwarded-for', `10.0.0.${++ipCounter}, 172.16.0.1`)
})

describe('loginAction', () => {
  it('signs in with Supabase', async () => {
    auth.signInWithPassword.mockResolvedValueOnce({ data: {}, error: null })
    expect(await loginAction('owner@example.com', 'secret')).toEqual({ ok: true })
    expect(auth.signInWithPassword).toHaveBeenCalledWith({
      email: 'owner@example.com',
      password: 'secret',
    })
  })

  it('returns invalid_credentials on wrong email or password', async () => {
    auth.signInWithPassword.mockResolvedValueOnce({
      data: {},
      error: { status: 400, code: 'invalid_credentials', message: 'Invalid login credentials' },
    })
    expect(await loginAction('owner@example.com', 'wrong')).toEqual({
      ok: false,
      error: { kind: 'invalid_credentials' },
    })
  })

  it('returns rate_limited after 5 attempts per minute from one IP, without calling Supabase', async () => {
    auth.signInWithPassword.mockResolvedValue({
      data: {},
      error: { status: 400, code: 'invalid_credentials', message: '' },
    })
    for (let i = 0; i < 5; i++) {
      expect((await loginAction('owner@example.com', 'wrong')).ok).toBe(false)
    }
    expect(await loginAction('owner@example.com', 'wrong')).toEqual({
      ok: false,
      error: { kind: 'rate_limited' },
    })
    expect(auth.signInWithPassword).toHaveBeenCalledTimes(5)
  })

  it('returns unavailable when Supabase fails for another reason', async () => {
    auth.signInWithPassword.mockResolvedValueOnce({
      data: {},
      error: { status: 500, code: 'unexpected_failure', message: '' },
    })
    expect(await loginAction('owner@example.com', 'secret')).toEqual({
      ok: false,
      error: { kind: 'unavailable' },
    })
  })
})

describe('logoutAction', () => {
  it('signs out this session only and redirects to login', async () => {
    auth.signOut.mockResolvedValueOnce({ error: null })
    await logoutAction()
    expect(auth.signOut).toHaveBeenCalledWith({ scope: 'local' })
    expect(redirectMock).toHaveBeenCalledWith('/admin/login')
  })
})

describe('admin actions', () => {
  it('pass the typed result from the backend module through unchanged', async () => {
    const conflict = { ok: false as const, error: { kind: 'conflict' as const } }
    backend.rearrangeMenu.mockResolvedValueOnce(conflict)
    expect(await reorderPizzasAction(['c', 'a', 'b'])).toBe(conflict)
    expect(backend.rearrangeMenu).toHaveBeenCalledWith(['c', 'a', 'b'])
  })

  it('create forwards the pizza without redirecting', async () => {
    const created = { ok: true as const, data: { id: 'new' } }
    backend.createPizza.mockResolvedValueOnce(created)
    expect(await createPizzaAction(pizzaIn)).toBe(created)
    expect(backend.createPizza).toHaveBeenCalledWith(pizzaIn)
    expect(redirectMock).not.toHaveBeenCalled()
  })

  it('update forwards the patch without redirecting', async () => {
    backend.updatePizza.mockResolvedValueOnce({ ok: true, data: undefined })
    await updatePizzaAction('p1', { name: 'Nuova' })
    expect(backend.updatePizza).toHaveBeenCalledWith('p1', { name: 'Nuova' })
    expect(redirectMock).not.toHaveBeenCalled()
  })

  it('toggle sends only availability', async () => {
    backend.updatePizza.mockResolvedValueOnce({ ok: true, data: undefined })
    await toggleAvailabilityAction('p1', false)
    expect(backend.updatePizza).toHaveBeenCalledWith('p1', { available: false })
  })

  it('delete forwards the id', async () => {
    backend.deletePizza.mockResolvedValueOnce({ ok: true, data: undefined })
    await deletePizzaAction('p1')
    expect(backend.deletePizza).toHaveBeenCalledWith('p1')
  })
})
