import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAnalysisHistory } from '../services/imageAnalysisService'
import { getSmartNotifications } from '../services/notificationService'

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [history, setHistory] = useState([])
  const [alerts, setAlerts] = useState([])
  const [hasLoaded, setHasLoaded] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    Promise.allSettled([getAnalysisHistory(), getSmartNotifications()]).then(
      ([historyResult, alertsResult]) => {
        setHistory(historyResult.status === 'fulfilled' ? historyResult.value.history || [] : [])
        setAlerts(
          alertsResult.status === 'fulfilled' ? alertsResult.value.notifications || [] : [],
        )
        setHasLoaded(true)
      },
    )
  }, [])

  useEffect(() => {
    if (!isOpen) return undefined
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  const recent = history.slice(0, 5)
  const badgeCount = alerts.length + recent.length

  return (
    <div className="notification-bell" ref={containerRef}>
      <button
        type="button"
        className="notification-bell-btn"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Notifications"
        aria-expanded={isOpen}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {badgeCount > 0 && <span className="notification-bell-badge">{badgeCount}</span>}
      </button>

      {isOpen && (
        <div className="notification-dropdown glass-card">
          {!hasLoaded ? (
            <p className="text-muted small px-3 py-2 mb-0">Loading...</p>
          ) : (
            <>
              {alerts.length > 0 && (
                <>
                  <div className="notification-dropdown-header">Alerts</div>
                  <ul className="notification-dropdown-list">
                    {alerts.map((alert, index) => (
                      <li key={index}>
                        <span className="notification-dot" />
                        <div className="small">
                          {alert.severity === 'warning' && <strong className="me-1">&#9888;</strong>}
                          {alert.message}
                        </div>
                      </li>
                    ))}
                  </ul>
                </>
              )}
              <div className="notification-dropdown-header">Recent activity</div>
              {recent.length === 0 ? (
                <p className="text-muted small px-3 py-2 mb-0">
                  No activity yet — <Link to="/analyze">analyze a photo</Link> to get started.
                </p>
              ) : (
                <ul className="notification-dropdown-list">
                  {recent.map((item) => (
                    <li key={item.analysis_id}>
                      <span className="notification-dot" />
                      <div>
                        <div className="small">
                          Body type analyzed: <strong>{item.predicted_body_type?.name}</strong> (
                          {(Number(item.confidence_score) * 100).toFixed(0)}%)
                        </div>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                          {new Date(item.created_at).toLocaleString()}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
