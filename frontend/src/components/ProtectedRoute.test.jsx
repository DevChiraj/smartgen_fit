import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext')

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div>Protected content</div>
            </ProtectedRoute>
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
  useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true })
  const { container } = renderAt('/dashboard')
  expect(container).toBeEmptyDOMElement()
})

it('redirects to /login when not authenticated', () => {
  useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false })
  renderAt('/dashboard')
  expect(screen.getByText('Login page')).toBeInTheDocument()
})

it('renders the protected content when authenticated', () => {
  useAuth.mockReturnValue({ isAuthenticated: true, isLoading: false })
  renderAt('/dashboard')
  expect(screen.getByText('Protected content')).toBeInTheDocument()
})
