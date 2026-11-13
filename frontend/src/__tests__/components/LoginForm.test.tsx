import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as actions from '@/app/admin/actions'
import LoginForm from '@/components/LoginForm'

const { pushMock, refreshMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  refreshMock: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}))

vi.mock('@/app/admin/actions', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/app/admin/actions')>()
  return { ...actual, loginAction: vi.fn() }
})

const loginAction = vi.mocked(actions.loginAction)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('LoginForm', () => {
  it('submits valid credentials via loginAction', async () => {
    const user = userEvent.setup()
    loginAction.mockResolvedValueOnce({ ok: true })

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    await waitFor(() => {
      expect(loginAction).toHaveBeenCalledWith('owner@example.com', 'secret123')
    })
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/admin'))
  })

  it('shows an inline error on invalid credentials without leaking which field was wrong', async () => {
    const user = userEvent.setup()
    loginAction.mockResolvedValueOnce({ ok: false, error: { kind: 'invalid_credentials' } })

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'wrongpass')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/email o password non corretti/i)
  })

  it('shows a generic error when login is unavailable', async () => {
    const user = userEvent.setup()
    loginAction.mockResolvedValueOnce({ ok: false, error: { kind: 'unavailable' } })

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/riprova/i)
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('asks to wait when rate limited', async () => {
    const user = userEvent.setup()
    loginAction.mockResolvedValueOnce({ ok: false, error: { kind: 'rate_limited' } })

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/troppi tentativi/i)
  })

  it('blocks submission and shows validation messages when fields are empty', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    expect(screen.getByText(/inserisci un'email valida/i)).toBeInTheDocument()
    expect(screen.getByText(/inserisci la password/i)).toBeInTheDocument()
    expect(loginAction).not.toHaveBeenCalled()
  })

  it('rejects a malformed email before calling the action', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'not-an-email')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    expect(screen.getByText(/inserisci un'email valida/i)).toBeInTheDocument()
    expect(loginAction).not.toHaveBeenCalled()
  })

  it('disables the submit control while the action is in flight', async () => {
    const user = userEvent.setup()
    let resolve: () => void = () => {}
    loginAction.mockImplementationOnce(
      () => new Promise((r) => { resolve = () => r({ ok: true }) }),
    )

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    const button = screen.getByRole('button')
    await waitFor(() => expect(button).toBeDisabled())
    expect(button).toHaveTextContent(/accesso in corso/i)

    resolve()
  })
})
