import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PizzaRow from '@/app/admin/PizzaRow'
import * as actions from '@/app/admin/actions'
import type { PizzaOut } from '@/lib/types'

const { refreshMock, pushMock } = vi.hoisted(() => ({ refreshMock: vi.fn(), pushMock: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}))

vi.mock('@/app/admin/actions', () => ({
  toggleAvailabilityAction: vi.fn(),
  deletePizzaAction: vi.fn(),
}))

const deletePizzaAction = vi.mocked(actions.deletePizzaAction)
const toggleAvailabilityAction = vi.mocked(actions.toggleAvailabilityAction)

async function confirmDelete(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: 'Elimina' }))
  const dialog = screen.getByRole('dialog')
  await user.click(
    Array.from(dialog.querySelectorAll('button')).find((b) => b.textContent === 'Elimina')!,
  )
}

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
      deletePizzaAction.mockResolvedValue({ ok: true, data: undefined })
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Elimina' }))
      const dialog = screen.getByRole('dialog')
      await user.click(
        Array.from(dialog.querySelectorAll('button')).find((b) => b.textContent === 'Elimina')!,
      )

      await waitFor(() => expect(deletePizzaAction).toHaveBeenCalledWith(pizza.id))
      await waitFor(() => expect(refreshMock).toHaveBeenCalled())
    })

    it('keeps the dialog open and explains when deletion fails', async () => {
      const user = userEvent.setup()
      deletePizzaAction.mockResolvedValue({ ok: false, error: { kind: 'unavailable' } })
      render(<PizzaRow pizza={pizza} />)

      await confirmDelete(user)

      expect(await screen.findByRole('alert')).toHaveTextContent(/non è raggiungibile/i)
      expect(screen.getByRole('dialog')).toBeVisible()
    })

    it('goes to login when the session has expired', async () => {
      const user = userEvent.setup()
      deletePizzaAction.mockResolvedValue({ ok: false, error: { kind: 'unauthorized' } })
      render(<PizzaRow pizza={pizza} />)

      await confirmDelete(user)

      await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/admin/login'))
    })
  })

  describe('availability toggle', () => {
    it('saves the opposite availability and refreshes', async () => {
      const user = userEvent.setup()
      toggleAvailabilityAction.mockResolvedValue({ ok: true, data: undefined })
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Disattiva pizza' }))

      await waitFor(() => expect(toggleAvailabilityAction).toHaveBeenCalledWith(pizza.id, false))
      await waitFor(() => expect(refreshMock).toHaveBeenCalled())
    })

    it('explains when the change could not be saved', async () => {
      const user = userEvent.setup()
      toggleAvailabilityAction.mockResolvedValue({ ok: false, error: { kind: 'unavailable' } })
      render(<PizzaRow pizza={pizza} />)

      await user.click(screen.getByRole('button', { name: 'Disattiva pizza' }))

      expect(await screen.findByRole('alert')).toHaveTextContent(/non è raggiungibile/i)
    })
  })
})
