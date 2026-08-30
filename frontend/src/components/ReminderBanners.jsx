import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import PropTypes from 'prop-types'
import { Dumbbell, Droplets } from 'lucide-react'
import { getWorkoutLogHistory } from '../services/workoutLogService'
import {
  HYDRATION_REMINDER_NEXT_AT_KEY,
  WORKOUT_REMINDER_DISMISSED_DATE_KEY,
} from '../utils/storageKeys'

const HYDRATION_INTERVAL_MS = 60 * 60 * 1000
const EXIT_ANIMATION_MS = 320

const BANNER_ICON = {
  workout: Dumbbell,
  hydration: Droplets,
}

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

function ReminderBanner({ banner, onDismiss }) {
  const [isExiting, setIsExiting] = useState(false)
  const Icon = BANNER_ICON[banner.id]

  const handleDismiss = () => {
    setIsExiting(true)
    setTimeout(() => onDismiss(banner.id), EXIT_ANIMATION_MS)
  }

  return (
    <div className={`reminder-banner-item ${isExiting ? 'is-exiting' : ''}`}>
      <div className="reminder-banner">
        <Icon className="reminder-banner-icon" size={20} strokeWidth={1.75} aria-hidden="true" />
        <div className="reminder-banner-message small">{banner.message}</div>
        <div className="reminder-banner-actions">
          {banner.actionTo && (
            <Link to={banner.actionTo} className="btn btn-sm btn-primary rounded-pill">
              {banner.actionLabel}
            </Link>
          )}
          <button
            type="button"
            className="reminder-banner-close"
            aria-label="Dismiss reminder"
            onClick={handleDismiss}
          >
            &times;
          </button>
        </div>
      </div>
    </div>
  )
}

ReminderBanner.propTypes = {
  banner: PropTypes.shape({
    id: PropTypes.string.isRequired,
    message: PropTypes.string.isRequired,
    actionLabel: PropTypes.string,
    actionTo: PropTypes.string,
  }).isRequired,
  onDismiss: PropTypes.func.isRequired,
}

export default function ReminderBanners() {
  const [banners, setBanners] = useState([])
  const location = useLocation()

  useEffect(() => {
    let cancelled = false
    let hydrationTimer

    const showHydrationReminder = () => {
      if (cancelled) return
      localStorage.setItem(HYDRATION_REMINDER_NEXT_AT_KEY, String(Date.now() + HYDRATION_INTERVAL_MS))
      setBanners((prev) =>
        prev.some((b) => b.id === 'hydration')
          ? prev
          : [
              ...prev,
              {
                id: 'hydration',
                message:
                  'Remember to drink water — staying hydrated helps you get the most out of your day.',
              },
            ],
      )
      hydrationTimer = setTimeout(showHydrationReminder, HYDRATION_INTERVAL_MS)
    }

    const scheduleHydrationReminder = () => {
      const storedNext = Number(localStorage.getItem(HYDRATION_REMINDER_NEXT_AT_KEY) || 0)
      const now = Date.now()
      if (!storedNext || now >= storedNext) {
        showHydrationReminder()
      } else {
        hydrationTimer = setTimeout(showHydrationReminder, storedNext - now)
      }
    }

    const checkWorkoutReminder = async () => {
      if (localStorage.getItem(WORKOUT_REMINDER_DISMISSED_DATE_KEY) === todayIsoDate()) return
      try {
        const data = await getWorkoutLogHistory()
        if (cancelled) return
        const loggedToday = (data.history || []).some((log) => log.log_date === todayIsoDate())
        if (!loggedToday) {
          setBanners((prev) =>
            prev.some((b) => b.id === 'workout')
              ? prev
              : [
                  {
                    id: 'workout',
                    message:
                      "You haven't logged a workout today — even a short session counts.",
                    actionLabel: 'Log a workout',
                    actionTo: '/workout-tracker',
                  },
                  ...prev,
                ],
          )
        }
      } catch {
        // A reminder is a nice-to-have, not worth surfacing an error for.
      }
    }

    if (!location.pathname.startsWith('/workout-tracker')) {
      checkWorkoutReminder()
    }
    scheduleHydrationReminder()

    return () => {
      cancelled = true
      clearTimeout(hydrationTimer)
    }
  }, [location.pathname])

  const dismiss = (id) => {
    if (id === 'workout') {
      localStorage.setItem(WORKOUT_REMINDER_DISMISSED_DATE_KEY, todayIsoDate())
    }
    setBanners((prev) => prev.filter((b) => b.id !== id))
  }

  if (banners.length === 0) return null

  return (
    <div className="reminder-banner-stack">
      {banners.map((banner) => (
        <ReminderBanner key={banner.id} banner={banner} onDismiss={dismiss} />
      ))}
    </div>
  )
}
