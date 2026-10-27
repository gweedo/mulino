import { loginAction, logoutAction, createPizzaAction } from '@/app/admin/actions'

const { auth, headerStore, redirectMock } = vi.hoisted(() => ({
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
    await loginAction('owner@example.com', 'secret')
    expect(auth.signInWithPassword).toHaveBeenCalledWith({
      email: 'owner@example.com',
      password: 'secret',
    })
  })

  it('throws "401" on invalid credentials', async () => {
    auth.signInWithPassword.mockResolvedValueOnce({
      data: {},
      error: { status: 400, code: 'invalid_credentials', message: 'Invalid login credentials' },
    })
    await expect(loginAction('owner@example.com', 'wrong')).rejects.toThrow('401')
  })

  it('throws "429" after 5 attempts per minute from one IP, without calling Supabase', async () => {
    auth.signInWithPassword.mockResolvedValue({
      data: {},
      error: { status: 400, code: 'invalid_credentials', message: '' },
    })
    for (let i = 0; i < 5; i++) {
      await expect(loginAction('owner@example.com', 'wrong')).rejects.toThrow('401')
    }
    await expect(loginAction('owner@example.com', 'wrong')).rejects.toThrow('429')
    expect(auth.signInWithPassword).toHaveBeenCalledTimes(5)
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

describe('admin mutations', () => {
  it('forward the Supabase access token as a Bearer header', async () => {
    auth.getSession.mockResolvedValueOnce({
      data: { session: { access_token: 'tok-123' } },
      error: null,
    })
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 201 }))

    await createPizzaAction({
      name: 'Diavola',
      description: 'd',
      ingredients: ['x'],
      allergens: [],
      price_amount: '9.00',
      price_currency: 'EUR',
    })

    const [, init] = fetchMock.mock.calls[0]
    expect((init?.headers as Record<string, string>).Authorization).toBe('Bearer tok-123')
    expect((init?.headers as Record<string, string>).Cookie).toBeUndefined()
    fetchMock.mockRestore()
  })
})
