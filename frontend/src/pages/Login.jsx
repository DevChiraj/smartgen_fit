import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { login as loginRequest } from '../services/authService'
import { formatApiError } from '../utils/formatApiError'

export default function Login() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const data = await loginRequest({ identifier, password })
      login(data)
      navigate('/')
    } catch (err) {
      setError(formatApiError(err, 'Login failed. Please check your credentials.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 420 }}>
      <h1>Log in</h1>
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
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in...' : 'Log in'}
        </button>
      </form>
      <p className="mt-3">
        Don&apos;t have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  )
}
