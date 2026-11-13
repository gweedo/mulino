import { render, screen } from '@testing-library/react'
import PizzaForm from '@/components/PizzaForm'
import type { PizzaOut } from '@/lib/types'

const pizza: PizzaOut = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Margherita',
  description: 'Classica e senza tempo.',
  ingredients: ['farina', 'pomodoro', 'mozzarella'],
  allergens: ['gluten', 'milk'],
  price: { amount: '8.00', currency: 'EUR' },
  available: true,
}

function priceInput(): HTMLInputElement {
  return screen.getByRole('spinbutton') as HTMLInputElement
}

describe('PizzaForm price field', () => {
  it('steps up by half a euro from a whole price', () => {
    render(<PizzaForm initial={pizza} action={vi.fn()} />)
    const input = priceInput()

    input.stepUp()

    expect(input.value).toBe('8.5')
  })

  it('steps down by half a euro from a whole price', () => {
    render(<PizzaForm initial={pizza} action={vi.fn()} />)
    const input = priceInput()

    input.stepDown()

    expect(input.value).toBe('7.5')
  })
})
