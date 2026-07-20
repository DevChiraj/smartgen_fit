import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import Login from './Login'
import { useAuth } from '../context/AuthContext'
import { login as loginRequest } from '../services/authService'

vi.mock('../context/AuthContext')
vi.mock('../services/authService')

const navigateMock = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigateMock }
})

beforeEach(() => {
  vi.resetAllMocks()
})

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>,
  )
}

it('logs in, updates auth state, and navigates home on success', async () => {
  const user = userEvent.setup()
  const loginFn = vi.fn()
  useAuth.mockReturnValue({ login: loginFn })
  loginRequest.mockResolvedValue({ access_token: 'a', refresh_token: 'r', user: { username: 'jane' } })

  renderLogin()
  await user.type(screen.getByLabelText(/username or email/i), 'jane')
  await user.type(screen.getByLabelText(/password/i), 'supersecret')
  await user.click(screen.getByRole('button', { name: /log in/i }))

  await waitFor(() => expect(loginFn).toHaveBeenCalledWith({
    access_token: 'a',
    refresh_token: 'r',
    user: { username: 'jane' },
  }))
  expect(navigateMock).toHaveBeenCalledWith('/')
})

it('shows an error and does not navigate when login fails', async () => {
  const user = userEvent.setup()
  const loginFn = vi.fn()
  useAuth.mockReturnValue({ login: loginFn })
  loginRequest.mockRejectedValue({
    response: { data: { message: 'Invalid username/email or password.' } },
  })

  renderLogin()
  await user.type(screen.getByLabelText(/username or email/i), 'jane')
  await user.type(screen.getByLabelText(/password/i), 'wrong')
  await user.click(screen.getByRole('button', { name: /log in/i }))

  await waitFor(() =>
    expect(screen.getByText('Invalid username/email or password.')).toBeInTheDocument(),
  )
  expect(loginFn).not.toHaveBeenCalled()
  expect(navigateMock).not.toHaveBeenCalled()
})
