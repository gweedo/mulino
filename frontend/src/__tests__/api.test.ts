import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { handlers, mockPizza } from './msw/handlers'
import {
  listPizzas,
  listAllPizzas,
  createPizza,
  updatePizza,
  deletePizza,
  ApiError,
} from '@/lib/api'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('auth errors', () => {
  it('admin calls throw ApiError with the status when unauthenticated', async () => {
    server.use(
      http.get('/api/admin/pizzas', () =>
        HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 }),
      ),
    )
    const err = await listAllPizzas().catch((e) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(401)
  })
})

describe('public pizzas', () => {
  it('listPizzas returns available pizzas', async () => {
    const pizzas = await listPizzas()
    expect(pizzas).toHaveLength(1)
    expect(pizzas[0].name).toBe('Margherita')
  })
})

describe('admin pizzas', () => {
  it('listAllPizzas returns all pizzas', async () => {
    const pizzas = await listAllPizzas()
    expect(pizzas).toHaveLength(1)
  })

  it('createPizza posts to /api/pizzas and returns the created pizza', async () => {
    const created = await createPizza({
      name: 'Diavola',
      description: 'Salame piccante e fior di latte.',
      ingredients: ['farina 00', 'salame piccante', 'fior di latte'],
      allergens: ['gluten', 'milk'],
      price_amount: '11.00',
      price_currency: 'EUR',
    })
    expect(created.name).toBe('Diavola')
    expect(created.id).toBe('new-456')
  })

  it('updatePizza puts to /api/pizzas/:id and resolves on 204', async () => {
    await expect(updatePizza(mockPizza.id, { available: false })).resolves.toBeUndefined()
  })

  it('deletePizza resolves on 204', async () => {
    await expect(deletePizza(mockPizza.id)).resolves.toBeUndefined()
  })

  it('createPizza throws ApiError on 422', async () => {
    server.use(
      http.post('/api/pizzas', () =>
        HttpResponse.json({ detail: 'Validation error' }, { status: 422 }),
      ),
    )
    const err = await createPizza({
      name: '',
      description: '',
      ingredients: [],
      allergens: [],
      price_amount: '0',
      price_currency: 'EUR',
    }).catch((e) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(422)
  })
})
