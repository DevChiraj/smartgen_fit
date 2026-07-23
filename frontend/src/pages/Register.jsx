import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotifications } from '../context/NotificationContext'
import { register as registerRequest } from '../services/authService'
import { calculateAge } from '../utils/age'
import { formatApiError } from '../utils/formatApiError'

const MIN_REGISTRATION_AGE = 15

const initialForm = {
  full_name: '',
  date_of_birth: '',
  gender: 'female',
  email: '',
  username: '',
  password: '',
  phone_number: '',
}

export default function Register() {
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()
  const { showToast } = useNotifications()
  const navigate = useNavigate()

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (calculateAge(form.date_of_birth) < MIN_REGISTRATION_AGE) {
      setError(`You must be at least ${MIN_REGISTRATION_AGE} years old to register.`)
      return
    }

    setIsSubmitting(true)
    try {
      const payload = { ...form }
      if (!payload.phone_number) delete payload.phone_number

      const data = await registerRequest(payload)
      login(data)
      showToast('Account created — welcome to SmartGen Fit!', 'success')
      navigate('/')
    } catch (err) {
      setError(formatApiError(err, 'Registration failed. Please check your details.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto py-4" style={{ maxWidth: 480 }}>
      <div className="card p-4 p-md-5 shadow-lg">
        <h1 className="h3 fw-bold mb-1">Create an account</h1>
        <p className="text-secondary mb-4">Get your body type analyzed and matched to a plan.</p>
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label" htmlFor="full_name">
              Full name
            </label>
            <input
              id="full_name"
              name="full_name"
              className="form-control"
              value={form.full_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="date_of_birth">
              Date of birth
            </label>
            <input
              id="date_of_birth"
              name="date_of_birth"
              type="date"
              className="form-control"
              value={form.date_of_birth}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="gender">
              Gender
            </label>
            <select
              id="gender"
              name="gender"
              className="form-select"
              value={form.gender}
              onChange={handleChange}
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-control"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              name="username"
              className="form-control"
              value={form.username}
              onChange={handleChange}
              required
              minLength={3}
              maxLength={50}
              pattern="[a-zA-Z0-9_]+"
              title="Letters, numbers, and underscores only"
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-control"
              value={form.password}
              onChange={handleChange}
              required
              minLength={8}
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="phone_number">
              Phone number (optional)
            </label>
            <input
              id="phone_number"
              name="phone_number"
              className="form-control"
              value={form.phone_number}
              onChange={handleChange}
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary rounded-pill w-100 mt-2"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating account...' : 'Create account'}
          </button>
        </form>
        <p className="mt-4 mb-0 text-secondary">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
