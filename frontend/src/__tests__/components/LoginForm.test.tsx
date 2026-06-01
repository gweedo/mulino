import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ApiError } from '@/lib/api'
import * as api from '@/lib/api'
import LoginForm from '@/components/LoginForm'

const { pushMock, refreshMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  refreshMock: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}))

vi.mock('@/lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/api')>()
  return { ...actual, login: vi.fn() }
})

const login = vi.mocked(api.login)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('LoginForm', () => {
  it('submits valid credentials and navigates to /admin', async () => {
    const user = userEvent.setup()
    login.mockResolvedValueOnce(undefined)

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith('owner@example.com', 'secret123')
    })
    expect(pushMock).toHaveBeenCalledWith('/admin')
  })

  it('shows an inline error on 401 without leaking which field was wrong', async () => {
    const user = userEvent.setup()
    login.mockRejectedValueOnce(new ApiError(401, 'Unauthorized'))

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'wrongpass')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/email o password non corretti/i)
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('shows a generic error on non-401 failures', async () => {
    const user = userEvent.setup()
    login.mockRejectedValueOnce(new ApiError(500, 'Internal Server Error'))

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'owner@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/riprova/i)
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('blocks submission and shows validation messages when fields are empty', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    expect(screen.getByText(/inserisci un'email valida/i)).toBeInTheDocument()
    expect(screen.getByText(/inserisci la password/i)).toBeInTheDocument()
    expect(login).not.toHaveBeenCalled()
  })

  it('rejects a malformed email before calling the API', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)
    await user.type(screen.getByLabelText(/email/i), 'not-an-email')
    await user.type(screen.getByLabelText(/password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /accedi/i }))

    expect(screen.getByText(/inserisci un'email valida/i)).toBeInTheDocument()
    expect(login).not.toHaveBeenCalled()
  })

  it('disables the submit control while the request is in flight', async () => {
    const user = userEvent.setup()
    let resolve: () => void = () => {}
    login.mockImplementationOnce(() => new Promise<void>((r) => { resolve = r }))

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
