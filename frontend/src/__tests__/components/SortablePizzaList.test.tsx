import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import SortablePizzaList from '@/app/admin/SortablePizzaList'
import * as actions from '@/app/admin/actions'
import type { PizzaOut } from '@/lib/types'

const { refreshMock, pushMock } = vi.hoisted(() => ({ refreshMock: vi.fn(), pushMock: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}))

vi.mock('@/app/admin/actions', () => ({
  reorderPizzasAction: vi.fn(),
  toggleAvailabilityAction: vi.fn(),
  deletePizzaAction: vi.fn(),
}))

const reorderPizzasAction = vi.mocked(actions.reorderPizzasAction)

function pizza(id: string, name: string): PizzaOut {
  return {
    id,
    name,
    description: '',
    ingredients: ['x'],
    allergens: [],
    price: { amount: '8.00', currency: 'EUR' },
    available: true,
  }
}

const menu = [pizza('a', 'Margherita'), pizza('b', 'Diavola'), pizza('c', 'Capricciosa')]

// jsdom lays nothing out; give each row a stacked 60px box so dnd-kit's
// keyboard sensor can find the row below the one being moved.
beforeAll(() => {
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (
    this: HTMLElement,
  ) {
    const row = this.closest('[data-pizza-id]')
    const index = row ? Array.from(row.parentElement!.children).indexOf(row) : 0
    const top = index * 60
    return {
      x: 0, y: top, top, left: 0, right: 600, bottom: top + 60, width: 600, height: 60,
      toJSON: () => ({}),
    } as DOMRect
  })
})

beforeEach(() => {
  vi.clearAllMocks()
})

function rowNames(): string[] {
  return screen
    .getAllByRole('listitem')
    .map((li) => within(li).getByRole('button', { name: /^Riordina / }).getAttribute('aria-label')!)
    .map((label) => label.replace('Riordina ', ''))
}

// dnd-kit's KeyboardSensor attaches its document listener in a setTimeout,
// so each key press waits a tick for the previous one to take effect.
const tick = () => new Promise((resolve) => setTimeout(resolve, 0))

async function press(target: Element, code: string, key: string) {
  await act(async () => {
    fireEvent.keyDown(target, { code, key })
    await tick()
  })
}

async function moveDownOnce(name: string) {
  const handle = screen.getByRole('button', { name: `Riordina ${name}` })
  handle.focus()
  await press(handle, 'Space', ' ')
  await press(handle, 'ArrowDown', 'ArrowDown')
  await press(handle, 'Space', ' ')
}

describe('SortablePizzaList', () => {
  it('renders the pizzas in Menu Order, each with a drag handle', () => {
    render(<SortablePizzaList pizzas={menu} />)
    expect(rowNames()).toEqual(['Margherita', 'Diavola', 'Capricciosa'])
  })

  it('moves a pizza with the keyboard and saves the new order', async () => {
    reorderPizzasAction.mockResolvedValue({ ok: true, data: undefined })
    render(<SortablePizzaList pizzas={menu} />)

    await moveDownOnce('Margherita')

    await waitFor(() => expect(reorderPizzasAction).toHaveBeenCalledWith(['b', 'a', 'c']))
    expect(rowNames()).toEqual(['Diavola', 'Margherita', 'Capricciosa'])
    await waitFor(() => expect(refreshMock).toHaveBeenCalled())
  })

  it('puts the pizzas back and explains when the Menu changed meanwhile', async () => {
    reorderPizzasAction.mockResolvedValue({ ok: false, error: { kind: 'conflict' } })
    render(<SortablePizzaList pizzas={menu} />)

    await moveDownOnce('Margherita')

    expect(await screen.findByRole('alert')).toHaveTextContent(/cambiato nel frattempo/i)
    expect(rowNames()).toEqual(['Margherita', 'Diavola', 'Capricciosa'])
    await waitFor(() => expect(refreshMock).toHaveBeenCalled())
  })

  it('puts the pizzas back and explains when the backend is unreachable', async () => {
    reorderPizzasAction.mockResolvedValue({ ok: false, error: { kind: 'unavailable' } })
    render(<SortablePizzaList pizzas={menu} />)

    await moveDownOnce('Margherita')

    expect(await screen.findByRole('alert')).toHaveTextContent(/non è raggiungibile/i)
    expect(rowNames()).toEqual(['Margherita', 'Diavola', 'Capricciosa'])
  })

  it('goes to login when the session has expired', async () => {
    reorderPizzasAction.mockResolvedValue({ ok: false, error: { kind: 'unauthorized' } })
    render(<SortablePizzaList pizzas={menu} />)

    await moveDownOnce('Margherita')

    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/admin/login'))
  })
})
