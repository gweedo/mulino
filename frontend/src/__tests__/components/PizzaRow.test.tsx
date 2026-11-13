import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PizzaRow from '@/app/admin/PizzaRow'
import * as actions from '@/app/admin/actions'
import type { PizzaOut } from '@/lib/types'

const { refreshMock } = vi.hoisted(() => ({ refreshMock: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), refresh: refreshMock }),
}))

vi.mock('@/app/admin/actions', () => ({
  toggleAvailabilityAction: vi.fn(),
  deletePizzaAction: vi.fn(),
}))

const deletePizzaAction = vi.mocked(actions.deletePizzaAction)

// jsdom has no modal <dialog> support; browsers provide the real behaviour.
beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) {
    this.setAttribute('open', '')
  }
  HTMLDialogElement.prototype.close = function (this: HTMLDialogElement) {
    this.removeAttribute('open')
    this.dispatchEvent(new Event('close'))
  }
})

beforeEach(() => {
  vi.clearAllMocks()
})

const pizza: PizzaOut = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Diavola',
  description: 'Per chi ama il piccante.',
  ingredients: ['farina', 'pomodoro', 'salame piccante', 'mozzarella'],
  allergens: ['gluten', 'milk'],
  price: { amount: '11.00', currency: 'EUR' },
  available: true,
}

describe('PizzaRow', () => {
  it('shows the description', () => {
    render(<PizzaRow pizza={pizza} />)
    expect(screen.getByText('Per chi ama il piccante.')).toBeInTheDocument()
  })

  it('shows the ingredients', () => {
    render(<PizzaRow pizza={pizza} />)
    expect(
      screen.getByText('farina, pomodoro, salame piccante, mozzarella', { exact: false }),
    ).toBeInTheDocument()
  })

  describe('delete confirmation', () => {
    it('opens a dialog naming the pizza instead of deleting right away', async () => {
      const user = userEvent.setup()
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Elimina' }))

      const dialog = screen.getByRole('dialog', { name: /Diavola/ })
      expect(dialog).toBeVisible()
      expect(deletePizzaAction).not.toHaveBeenCalled()
    })

    it('closes without deleting when cancelled', async () => {
      const user = userEvent.setup()
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Elimina' }))
      await user.click(screen.getByRole('button', { name: 'Annulla' }))

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      expect(deletePizzaAction).not.toHaveBeenCalled()
    })

    it('deletes the pizza when confirmed in the dialog', async () => {
      const user = userEvent.setup()
      deletePizzaAction.mockResolvedValue(undefined)
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Elimina' }))
      const dialog = screen.getByRole('dialog')
      await user.click(
        Array.from(dialog.querySelectorAll('button')).find((b) => b.textContent === 'Elimina')!,
      )

      await waitFor(() => expect(deletePizzaAction).toHaveBeenCalledWith(pizza.id))
      await waitFor(() => expect(refreshMock).toHaveBeenCalled())
    })
  })
})
