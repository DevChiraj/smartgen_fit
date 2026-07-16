import { useEffect, useState } from 'react'
import HealthStatusCard from '../components/HealthStatusCard'
import { getApiHealth, getDbHealth } from '../services/healthService'

export default function LandingPage() {
  const [apiStatus, setApiStatus] = useState('checking')
  const [dbStatus, setDbStatus] = useState('checking')

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
    </div>
  )
}
