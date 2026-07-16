import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import HealthStatusCard from '../components/HealthStatusCard'
import { useAuth } from '../context/AuthContext'
import { getApiHealth, getDbHealth } from '../services/healthService'

export default function LandingPage() {
  const [apiStatus, setApiStatus] = useState('checking')
  const [dbStatus, setDbStatus] = useState('checking')
  const { isAuthenticated, isLoading, user, logout } = useAuth()

  useEffect(() => {
    getApiHealth()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('error'))

    getDbHealth()
      .then((data) => setDbStatus(data.status))
      .catch(() => setDbStatus('error'))
  }, [])

  return (
    <div>
      <h1>SmartGen Fit</h1>
      <p>AI-powered personalized nutrition and fitness recommendations.</p>
      <HealthStatusCard label="Backend API" status={apiStatus} />
      <HealthStatusCard label="Database connection" status={dbStatus} />

      {!isLoading && (
        <div className="mt-3">
          {isAuthenticated ? (
            <>
              <p>
                Welcome back, <strong>{user?.username}</strong>.
              </p>
              <button type="button" className="btn btn-outline-secondary" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <p>
              <Link to="/login">Log in</Link> or <Link to="/register">create an account</Link>.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
