import { render, screen } from '@testing-library/react'
import PizzaList from '@/components/PizzaList'
import type { PizzaItem } from '@/lib/types'

const basePizza: PizzaItem = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Margherita',
  description: 'Classica e senza tempo.',
  ingredients: ['farina', 'pomodoro', 'mozzarella', 'basilico'],
  allergens: ['gluten', 'milk'],
  price: { amount: '9.50', currency: 'EUR' },
  available: true,
}

const secondPizza: PizzaItem = {
  id: '22222222-2222-2222-2222-222222222222',
  name: 'Diavola',
  description: 'Per chi ama il piccante.',
  ingredients: ['farina', 'pomodoro', 'salame piccante', 'mozzarella'],
  allergens: ['gluten', 'milk'],
  price: { amount: '11.00', currency: 'EUR' },
  available: true,
}

describe('PizzaList', () => {
  it('renders the menu heading', () => {
    render(<PizzaList pizzas={[basePizza]} />)
    expect(screen.getByRole('heading', { name: /menu/i })).toBeInTheDocument()
  })

  it('shows empty state message when no pizzas are passed', () => {
    render(<PizzaList pizzas={[]} />)
    expect(screen.getByText(/nessuna pizza disponibile/i)).toBeInTheDocument()
  })

  it('renders all pizza names when populated', () => {
    render(<PizzaList pizzas={[basePizza, secondPizza]} />)
    expect(screen.getByText('Margherita')).toBeInTheDocument()
    expect(screen.getByText('Diavola')).toBeInTheDocument()
  })

  it('renders allergen badges in Italian', () => {
    render(<PizzaList pizzas={[basePizza]} />)
    expect(screen.getByText('Glutine')).toBeInTheDocument()
    expect(screen.getByText('Latte')).toBeInTheDocument()
  })

  it('renders formatted price', () => {
    render(<PizzaList pizzas={[basePizza]} />)
    expect(screen.getByText(/9[,.]50/)).toBeInTheDocument()
  })

  it('renders description text', () => {
    render(<PizzaList pizzas={[basePizza]} />)
    expect(screen.getByText('Classica e senza tempo.')).toBeInTheDocument()
  })
})
