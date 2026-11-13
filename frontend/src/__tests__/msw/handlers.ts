import { http, HttpResponse } from 'msw'
import type { PizzaOut } from '@/lib/types'

/** Where src/lib/backend.ts sends requests when BACKEND_INTERNAL_URL is unset. */
export const BACKEND = 'http://localhost:8000'

export const mockPizza: PizzaOut = {
  id: 'abc-123',
  name: 'Margherita',
  description: 'Pomodoro San Marzano, fior di latte, basilico.',
  ingredients: ['farina 00', 'pomodoro', 'fior di latte', 'basilico'],
  allergens: ['gluten', 'milk'],
  price: { amount: '9.50', currency: 'EUR' },
  available: true,
}

/** Happy-path FastAPI routes; tests override them with `server.use(...)` for failures. */
export const handlers = [
  http.get(`${BACKEND}/api/pizzas`, () => HttpResponse.json([mockPizza])),

  http.get(`${BACKEND}/api/admin/pizzas`, () => HttpResponse.json([mockPizza])),

  http.get(`${BACKEND}/api/admin/pizzas/:id`, ({ params }) =>
    params.id === mockPizza.id
      ? HttpResponse.json(mockPizza)
      : HttpResponse.json({ detail: 'Pizza not found' }, { status: 404 }),
  ),

  http.post(`${BACKEND}/api/admin/pizzas`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const created: PizzaOut = {
      id: 'new-456',
      name: body.name as string,
      description: body.description as string,
      ingredients: body.ingredients as string[],
      allergens: body.allergens as string[],
      price: { amount: String(body.price_amount), currency: body.price_currency as string },
      available: true,
    }
    return HttpResponse.json(created, { status: 201 })
  }),

  http.put(`${BACKEND}/api/admin/pizzas/order`, () => new HttpResponse(null, { status: 204 })),

  http.put(`${BACKEND}/api/admin/pizzas/:id`, () => new HttpResponse(null, { status: 204 })),

  http.delete(`${BACKEND}/api/admin/pizzas/:id`, () => new HttpResponse(null, { status: 204 })),
]
