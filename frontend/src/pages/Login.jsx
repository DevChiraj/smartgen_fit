import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotifications } from '../context/NotificationContext'
import { login as loginRequest } from '../services/authService'
import { formatApiError } from '../utils/formatApiError'

export default function Login() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()
  const { showToast } = useNotifications()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const data = await loginRequest({ identifier, password })
      login(data)
      showToast(`Welcome back, ${data.user.full_name}!`, 'success')
      navigate('/')
    } catch (err) {
      setError(formatApiError(err, 'Login failed. Please check your credentials.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto py-4" style={{ maxWidth: 420 }}>
      <div className="card p-4 p-md-5 shadow-lg">
        <h1 className="h3 fw-bold mb-1">Welcome back</h1>
        <p className="text-secondary mb-4">Log in to see your matched plan.</p>
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label" htmlFor="identifier">
              Username or email
            </label>
            <input
              id="identifier"
              className="form-control"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary rounded-pill w-100 mt-2"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Logging in...' : 'Log in'}
          </button>
        </form>
        <p className="mt-4 mb-0 text-secondary">
          Don&apos;t have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  )
}
