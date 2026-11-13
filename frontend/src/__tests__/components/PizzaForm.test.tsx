import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PizzaForm, { type PizzaFormValues } from '@/components/PizzaForm'
import type { Result } from '@/lib/result'
import type { PizzaOut } from '@/lib/types'

const { pushMock, refreshMock } = vi.hoisted(() => ({ pushMock: vi.fn(), refreshMock: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}))

beforeEach(() => {
  vi.clearAllMocks()
})

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

describe('PizzaForm submit', () => {
  async function save(action: (data: PizzaFormValues) => Promise<Result<unknown>>) {
    const user = userEvent.setup()
    render(<PizzaForm initial={pizza} action={action} />)
    await user.click(screen.getByRole('button', { name: /salva/i }))
  }

  it('sends the edited pizza and goes back to the Menu when saved', async () => {
    const action = vi.fn<(data: PizzaFormValues) => Promise<Result<unknown>>>().mockResolvedValue({ ok: true, data: undefined })
    await save(action)

    await waitFor(() =>
      expect(action).toHaveBeenCalledWith({
        name: 'Margherita',
        description: 'Classica e senza tempo.',
        ingredients: ['farina', 'pomodoro', 'mozzarella'],
        allergens: ['gluten', 'milk'],
        price_amount: '8.00',
        price_currency: 'EUR',
        available: true,
      }),
    )
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/admin'))
  })

  it('explains a duplicate name in Italian and stays on the form', async () => {
    const action = vi.fn<(data: PizzaFormValues) => Promise<Result<unknown>>>().mockResolvedValue({
      ok: false,
      error: { kind: 'conflict', detail: 'A pizza with this name already exists' },
    })
    await save(action)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Esiste già una pizza con questo nome.')
    expect(alert).not.toHaveTextContent(/already exists/)
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('goes to login when the session has expired', async () => {
    const action = vi.fn<(data: PizzaFormValues) => Promise<Result<unknown>>>().mockResolvedValue({ ok: false, error: { kind: 'unauthorized' } })
    await save(action)

    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/admin/login'))
  })
})
