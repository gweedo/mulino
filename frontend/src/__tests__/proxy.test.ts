import { NextRequest } from 'next/server'
import { proxy } from '@/proxy'

const { getClaims } = vi.hoisted(() => ({ getClaims: vi.fn() }))

vi.mock('@supabase/ssr', () => ({
  createServerClient: () => ({ auth: { getClaims } }),
}))

beforeEach(() => {
  vi.clearAllMocks()
  process.env.SUPABASE_URL = 'https://test-project.supabase.co'
  process.env.SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_test'
})

const req = (path: string) => new NextRequest(new URL(path, 'http://localhost:3000'))

describe('proxy', () => {
  it('redirects to login when there is no verified session', async () => {
    getClaims.mockResolvedValueOnce({ data: null, error: null })
    const res = await proxy(req('/admin'))
    expect(res.status).toBe(307)
    expect(res.headers.get('location')).toBe('http://localhost:3000/admin/login')
  })

  it('lets a verified session through', async () => {
    getClaims.mockResolvedValueOnce({ data: { claims: { sub: 'u1' } }, error: null })
    const res = await proxy(req('/admin/pizzas/new'))
    expect(res.headers.get('location')).toBeNull()
  })

  it('never redirects the login page itself', async () => {
    getClaims.mockResolvedValueOnce({ data: null, error: null })
    const res = await proxy(req('/admin/login'))
    expect(res.headers.get('location')).toBeNull()
  })
})
