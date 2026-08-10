import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import AdminUsers from './AdminUsers'
import { useAuth } from '../../context/AuthContext'
import { createUser, deleteUser, getUsers, updateUser } from '../../services/adminService'

vi.mock('../../context/AuthContext')
vi.mock('../../services/adminService')

const EXISTING_USER = {
  user_id: 2,
  username: 'plainuser',
  full_name: 'Plain User',
  email: 'plain@example.com',
  age: 25,
  role: 'user',
}

beforeEach(() => {
  vi.resetAllMocks()
  useAuth.mockReturnValue({ user: { user_id: 1, username: 'admin1' } })
  getUsers.mockResolvedValue({ users: [EXISTING_USER] })
})

it('lists existing users', async () => {
  render(<AdminUsers />)

  expect(await screen.findByText('plainuser')).toBeInTheDocument()
})

it('opens the Add user modal and creates a new user', async () => {
  const user = userEvent.setup()
  createUser.mockResolvedValue({ user: { user_id: 3, username: 'newuser' } })
  render(<AdminUsers />)
  await screen.findByText('plainuser')

  await user.click(screen.getByRole('button', { name: /add user/i }))
  expect(screen.getByRole('heading', { name: /add user/i })).toBeInTheDocument()

  await user.type(screen.getByLabelText(/full name/i), 'New User')
  await user.type(screen.getByLabelText(/date of birth/i), '2000-01-01')
  await user.type(screen.getByLabelText(/^email$/i), 'newuser@example.com')
  await user.type(screen.getByLabelText(/^username$/i), 'newuser')
  await user.type(screen.getByLabelText(/^password$/i), 'supersecret')

  await user.click(screen.getByRole('button', { name: /create user/i }))

  await waitFor(() =>
    expect(createUser).toHaveBeenCalledWith(
      expect.objectContaining({
        full_name: 'New User',
        date_of_birth: '2000-01-01',
        email: 'newuser@example.com',
        username: 'newuser',
        password: 'supersecret',
      }),
    ),
  )
  expect(getUsers).toHaveBeenCalledTimes(2)
})

it('shows an error and keeps the modal open when creation fails', async () => {
  const user = userEvent.setup()
  createUser.mockRejectedValue({ response: { data: { message: 'Email is already registered.' } } })
  render(<AdminUsers />)
  await screen.findByText('plainuser')

  await user.click(screen.getByRole('button', { name: /add user/i }))
  await user.type(screen.getByLabelText(/full name/i), 'New User')
  await user.type(screen.getByLabelText(/date of birth/i), '2000-01-01')
  await user.type(screen.getByLabelText(/^email$/i), 'plain@example.com')
  await user.type(screen.getByLabelText(/^username$/i), 'newuser')
  await user.type(screen.getByLabelText(/^password$/i), 'supersecret')
  await user.click(screen.getByRole('button', { name: /create user/i }))

  expect(await screen.findByText('Email is already registered.')).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: /add user/i })).toBeInTheDocument()
})

it('changes a user role', async () => {
  const user = userEvent.setup()
  updateUser.mockResolvedValue({ user: { ...EXISTING_USER, role: 'admin' } })
  render(<AdminUsers />)
  await screen.findByText('plainuser')

  await user.selectOptions(screen.getByDisplayValue('user'), 'admin')

  await waitFor(() => expect(updateUser).toHaveBeenCalledWith(2, { role: 'admin' }))
})

it('deletes a user after confirmation', async () => {
  const user = userEvent.setup()
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  deleteUser.mockResolvedValue()
  render(<AdminUsers />)
  await screen.findByText('plainuser')

  await user.click(screen.getByRole('button', { name: /delete/i }))

  await waitFor(() => expect(deleteUser).toHaveBeenCalledWith(2))
})
