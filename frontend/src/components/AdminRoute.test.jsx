import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import AdminRoute from './AdminRoute'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext')

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/dashboard" element={<div>Dashboard page</div>} />
        <Route
          path="/admin/users"
          element={
            <AdminRoute>
              <div>Admin content</div>
            </AdminRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
})

it('renders nothing while auth state is loading', () => {
  useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true, user: null })
  const { container } = renderAt('/admin/users')
  expect(container).toBeEmptyDOMElement()
})

it('redirects to /login when not authenticated', () => {
  useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false, user: null })
  renderAt('/admin/users')
  expect(screen.getByText('Login page')).toBeInTheDocument()
})

it('redirects to /dashboard when authenticated but not an admin', () => {
  useAuth.mockReturnValue({
    isAuthenticated: true,
    isLoading: false,
    user: { role: 'user' },
  })
  renderAt('/admin/users')
  expect(screen.getByText('Dashboard page')).toBeInTheDocument()
})

it('renders the admin content when the user has the admin role', () => {
  useAuth.mockReturnValue({
    isAuthenticated: true,
    isLoading: false,
    user: { role: 'admin' },
  })
  renderAt('/admin/users')
  expect(screen.getByText('Admin content')).toBeInTheDocument()
})
