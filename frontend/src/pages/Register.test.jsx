import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import Register from './Register'
import { useAuth } from '../context/AuthContext'
import { NotificationProvider } from '../context/NotificationContext'
import { register as registerRequest } from '../services/authService'

vi.mock('../context/AuthContext')
vi.mock('../services/authService')

const navigateMock = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigateMock }
})

function renderRegister() {
  return render(
    <NotificationProvider>
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    </NotificationProvider>,
  )
}

async function fillCommonFields(user, { dateOfBirth }) {
  await user.type(screen.getByLabelText(/full name/i), 'Jane Silva')
  await user.type(screen.getByLabelText(/date of birth/i), dateOfBirth)
  await user.type(screen.getByLabelText(/^email$/i), 'jane@example.com')
  await user.type(screen.getByLabelText(/^username$/i), 'janesilva')
  await user.type(screen.getByLabelText(/^password$/i), 'supersecret')
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.useFakeTimers({ shouldAdvanceTime: true })
  vi.setSystemTime(new Date('2026-01-01T00:00:00'))
  useAuth.mockReturnValue({ login: vi.fn() })
})

afterEach(() => {
  vi.useRealTimers()
})

it('rejects submission client-side when the user is under 15', async () => {
  const user = userEvent.setup({ delay: null })
  renderRegister()

  // born 2015-01-02 -> 10 years old as of the frozen "today"
  await fillCommonFields(user, { dateOfBirth: '2015-01-02' })
  await user.click(screen.getByRole('button', { name: /create account/i }))

  expect(screen.getByText('You must be at least 15 years old to register.')).toBeInTheDocument()
  expect(registerRequest).not.toHaveBeenCalled()
  expect(navigateMock).not.toHaveBeenCalled()
})

it('registers, logs in, and navigates home when old enough', async () => {
  const user = userEvent.setup({ delay: null })
  const loginFn = vi.fn()
  useAuth.mockReturnValue({ login: loginFn })
  registerRequest.mockResolvedValue({
    access_token: 'a',
    refresh_token: 'r',
    user: { username: 'janesilva' },
  })

  renderRegister()
  await fillCommonFields(user, { dateOfBirth: '2000-01-01' })
  await user.click(screen.getByRole('button', { name: /create account/i }))

  await waitFor(() => expect(loginFn).toHaveBeenCalled())
  expect(navigateMock).toHaveBeenCalledWith('/')

  const payload = registerRequest.mock.calls[0][0]
  expect(payload.full_name).toBe('Jane Silva')
  expect(payload).not.toHaveProperty('phone_number')
})

it('includes phone_number in the payload when provided', async () => {
  const user = userEvent.setup({ delay: null })
  registerRequest.mockResolvedValue({ access_token: 'a', refresh_token: 'r', user: {} })

  renderRegister()
  await fillCommonFields(user, { dateOfBirth: '2000-01-01' })
  await user.type(screen.getByLabelText(/phone number/i), '0771234567')
  await user.click(screen.getByRole('button', { name: /create account/i }))

  await waitFor(() => expect(registerRequest).toHaveBeenCalled())
  expect(registerRequest.mock.calls[0][0].phone_number).toBe('0771234567')
})

it('shows a server-side error and does not navigate on failure', async () => {
  const user = userEvent.setup({ delay: null })
  registerRequest.mockRejectedValue({
    response: { data: { message: 'email: Already registered.' } },
  })

  renderRegister()
  await fillCommonFields(user, { dateOfBirth: '2000-01-01' })
  await user.click(screen.getByRole('button', { name: /create account/i }))

  await waitFor(() => expect(screen.getByText('email: Already registered.')).toBeInTheDocument())
  expect(navigateMock).not.toHaveBeenCalled()
})
