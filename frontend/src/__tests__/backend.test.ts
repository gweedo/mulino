import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { revalidateTag, updateTag } from 'next/cache'
import { BACKEND, handlers, mockPizza } from './msw/handlers'
import {
  createPizza,
  deletePizza,
  getAdminPizza,
  listAdminPizzas,
  listMenu,
  rearrangeMenu,
  updatePizza,
} from '@/lib/backend'

const { authHeaderMock } = vi.hoisted(() => ({ authHeaderMock: vi.fn() }))

vi.mock('@/lib/supabase/server', () => ({ authHeader: authHeaderMock }))
vi.mock('next/cache', () => ({ revalidateTag: vi.fn(), updateTag: vi.fn() }))

const server = setupServer(...handlers)

/** Records every request FastAPI would have received. */
const seen: Request[] = []

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
beforeEach(() => {
  vi.clearAllMocks()
  seen.length = 0
  authHeaderMock.mockResolvedValue({ Authorization: 'Bearer tok-123' })
  server.events.on('request:start', ({ request }) => {
    seen.push(request.clone())
  })
})
afterEach(() => {
  server.resetHandlers()
  server.events.removeAllListeners()
})
afterAll(() => server.close())

const pizzaIn = {
  name: 'Diavola',
  description: 'Piccante.',
  ingredients: ['pomodoro', 'salame piccante'],
  allergens: ['gluten'],
  price_amount: '11.00',
  price_currency: 'EUR',
}

function expectInvalidated() {
  expect(updateTag).toHaveBeenCalledWith('pizzas')
  expect(revalidateTag).toHaveBeenCalledWith('pizzas', expect.anything())
}

function expectNotInvalidated() {
  expect(updateTag).not.toHaveBeenCalled()
  expect(revalidateTag).not.toHaveBeenCalled()
}

describe('listMenu (public)', () => {
  it('returns the available pizzas', async () => {
    expect(await listMenu()).toEqual({ ok: true, data: [mockPizza] })
  })

  it('sends no Authorization header', async () => {
    await listMenu()
    expect(seen[0].headers.get('Authorization')).toBeNull()
    expect(authHeaderMock).not.toHaveBeenCalled()
  })

  it('is unavailable when FastAPI cannot be reached', async () => {
    server.use(http.get(`${BACKEND}/api/pizzas`, () => HttpResponse.error()))
    expect(await listMenu()).toEqual({ ok: false, error: { kind: 'unavailable' } })
  })
})

describe('admin reads', () => {
  it('listAdminPizzas forwards the Supabase token as a Bearer header', async () => {
    expect(await listAdminPizzas()).toEqual({ ok: true, data: [mockPizza] })
    expect(seen[0].headers.get('Authorization')).toBe('Bearer tok-123')
  })

  it('getAdminPizza fetches one pizza by id', async () => {
    expect(await getAdminPizza(mockPizza.id)).toEqual({ ok: true, data: mockPizza })
    expect(new URL(seen[0].url).pathname).toBe(`/api/admin/pizzas/${mockPizza.id}`)
  })

  it('getAdminPizza reports a missing pizza as not_found', async () => {
    const result = await getAdminPizza('nope')
    expect(result).toEqual({ ok: false, error: { kind: 'not_found', detail: 'Pizza not found' } })
  })
})

describe('status → error kind', () => {
  it.each([
    [401, 'unauthorized'],
    [403, 'forbidden'],
    [404, 'not_found'],
    [409, 'conflict'],
    [422, 'validation'],
    [400, 'validation'],
    [500, 'unavailable'],
    [503, 'unavailable'],
  ] as const)('%i → %s', async (status, kind) => {
    server.use(
      http.get(`${BACKEND}/api/admin/pizzas`, () =>
        HttpResponse.json({ detail: 'nope' }, { status }),
      ),
    )
    const result = await listAdminPizzas()
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.kind).toBe(kind)
  })

  it('keeps a string detail from FastAPI for logs, never required', async () => {
    server.use(
      http.post(`${BACKEND}/api/admin/pizzas`, () =>
        HttpResponse.json({ detail: 'A pizza with this name already exists' }, { status: 409 }),
      ),
    )
    expect(await createPizza(pizzaIn)).toEqual({
      ok: false,
      error: { kind: 'conflict', detail: 'A pizza with this name already exists' },
    })
  })

  it('drops a non-string detail (FastAPI request validation lists)', async () => {
    server.use(
      http.post(`${BACKEND}/api/admin/pizzas`, () =>
        HttpResponse.json({ detail: [{ loc: ['body', 'name'], msg: 'x' }] }, { status: 422 }),
      ),
    )
    expect(await createPizza(pizzaIn)).toEqual({ ok: false, error: { kind: 'validation' } })
  })

  it('maps a network failure to unavailable', async () => {
    server.use(http.get(`${BACKEND}/api/admin/pizzas`, () => HttpResponse.error()))
    expect(await listAdminPizzas()).toEqual({ ok: false, error: { kind: 'unavailable' } })
  })
})

describe('mutations', () => {
  it('createPizza posts the pizza and invalidates the menu', async () => {
    const result = await createPizza(pizzaIn)

    expect(result.ok).toBe(true)
    if (result.ok) expect(result.data.name).toBe('Diavola')
    expect(seen[0].method).toBe('POST')
    expect(new URL(seen[0].url).pathname).toBe('/api/admin/pizzas')
    expect(seen[0].headers.get('Authorization')).toBe('Bearer tok-123')
    expect(await seen[0].json()).toEqual(pizzaIn)
    expectInvalidated()
  })

  it('updatePizza sends only the patch', async () => {
    expect(await updatePizza('abc-123', { available: false })).toEqual({ ok: true, data: undefined })
    expect(seen[0].method).toBe('PUT')
    expect(new URL(seen[0].url).pathname).toBe('/api/admin/pizzas/abc-123')
    expect(await seen[0].json()).toEqual({ available: false })
    expectInvalidated()
  })

  it('deletePizza deletes by id', async () => {
    expect(await deletePizza('abc-123')).toEqual({ ok: true, data: undefined })
    expect(seen[0].method).toBe('DELETE')
    expect(new URL(seen[0].url).pathname).toBe('/api/admin/pizzas/abc-123')
    expectInvalidated()
  })

  it('rearrangeMenu sends the whole Menu Order', async () => {
    expect(await rearrangeMenu(['c', 'a', 'b'])).toEqual({ ok: true, data: undefined })
    expect(seen[0].method).toBe('PUT')
    expect(new URL(seen[0].url).pathname).toBe('/api/admin/pizzas/order')
    expect(await seen[0].json()).toEqual({ pizza_ids: ['c', 'a', 'b'] })
    expectInvalidated()
  })

  it('does not invalidate when FastAPI rejects the change', async () => {
    server.use(
      http.put(`${BACKEND}/api/admin/pizzas/order`, () =>
        HttpResponse.json({ detail: 'stale' }, { status: 409 }),
      ),
    )
    const result = await rearrangeMenu(['a'])
    expect(result).toEqual({ ok: false, error: { kind: 'conflict', detail: 'stale' } })
    expectNotInvalidated()
  })

  it('sends no Authorization header when there is no session', async () => {
    authHeaderMock.mockResolvedValue({})
    server.use(
      http.delete(`${BACKEND}/api/admin/pizzas/:id`, () =>
        HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 }),
      ),
    )
    const result = await deletePizza('abc-123')
    expect(seen[0].headers.get('Authorization')).toBeNull()
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.kind).toBe('unauthorized')
  })
})
