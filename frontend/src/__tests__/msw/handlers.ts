import { http, HttpResponse } from 'msw'
import type { PizzaOut, MeResponse } from '@/lib/types'

export const mockPizza: PizzaOut = {
  id: 'abc-123',
  name: 'Margherita',
  description: 'Pomodoro San Marzano, fior di latte, basilico.',
  ingredients: ['farina 00', 'pomodoro', 'fior di latte', 'basilico'],
  allergens: ['gluten', 'milk'],
  price: { amount: '9.50', currency: 'EUR' },
  available: true,
}

export const mockOwner: MeResponse = {
  id: 'owner-1',
  email: 'owner@example.com',
}

export const handlers = [
  // Auth
  http.post('/api/auth/login', () =>
    HttpResponse.json({ detail: 'OK' }, { status: 200 }),
  ),

  http.post('/api/auth/logout', () => new HttpResponse(null, { status: 204 })),

  http.get('/api/auth/me', () => HttpResponse.json(mockOwner)),

  // Public pizzas
  http.get('/api/pizzas', () => HttpResponse.json([mockPizza])),

  // Admin pizza create (POST /api/pizzas, auth required)
  http.post('/api/pizzas', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const created: PizzaOut = {
      id: 'new-456',
      name: body.name as string,
      description: body.description as string,
      ingredients: body.ingredients as string[],
      allergens: body.allergens as string[],
      price: { amount: body.price_amount as string, currency: 'EUR' },
      available: true,
    }
    return HttpResponse.json(created, { status: 201 })
  }),

  // Admin pizza update (PUT /api/pizzas/:id → 204 no content)
  http.put('/api/pizzas/:id', () => new HttpResponse(null, { status: 204 })),

  // Admin pizza delete (DELETE /api/pizzas/:id → 204 no content)
  http.delete('/api/pizzas/:id', () => new HttpResponse(null, { status: 204 })),

  // Admin list (GET /api/admin/pizzas)
  http.get('/api/admin/pizzas', () => HttpResponse.json([mockPizza])),
]
