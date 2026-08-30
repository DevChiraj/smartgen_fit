import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useNotifications } from '../context/NotificationContext'
import { getExercises } from '../services/exerciseService'
import { getWorkoutLogHistory, logWorkout } from '../services/workoutLogService'
import { formatApiError } from '../utils/formatApiError'
import ExerciseDemoGif from '../components/ExerciseDemoGif'

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

const initialForm = {
  exercise_id: '',
  duration_minutes: '',
  calories_burned: '',
  log_date: todayIsoDate(),
  notes: '',
}

export default function WorkoutTracker() {
  const { showToast } = useNotifications()
  const [exercises, setExercises] = useState([])
  const [history, setHistory] = useState([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState(initialForm)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    getExercises()
      .then((data) => setExercises(data.exercises || []))
      .catch(() => setExercises([]))
  }, [])

  useEffect(() => {
    getWorkoutLogHistory()
      .then((data) => setHistory(data.history || []))
      .catch((err) => setError(formatApiError(err, 'Could not load your workout history.')))
      .finally(() => setIsLoadingHistory(false))
  }, [])

  const selectedExercise = useMemo(
    () => exercises.find((exercise) => String(exercise.exercise_id) === String(form.exercise_id)),
    [exercises, form.exercise_id],
  )

  const estimatedCalories =
    selectedExercise && form.duration_minutes
      ? Math.round((selectedExercise.calories_per_30min * Number(form.duration_minutes)) / 30)
      : null

  const summary = useMemo(() => {
    const totalCalories = history.reduce((sum, log) => sum + log.calories_burned, 0)
    const totalMinutes = history.reduce((sum, log) => sum + log.duration_minutes, 0)
    const lastLogDate = history[0]?.log_date || null
    return { count: history.length, totalCalories, totalMinutes, lastLogDate }
  }, [history])

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const payload = {
        exercise_id: Number(form.exercise_id),
        duration_minutes: Number(form.duration_minutes),
        log_date: form.log_date || undefined,
        calories_burned: form.calories_burned ? Number(form.calories_burned) : undefined,
        notes: form.notes || undefined,
      }
      const data = await logWorkout(payload)
      setHistory((prev) => [data.log, ...prev])
      setForm({ ...initialForm, log_date: todayIsoDate() })
      showToast('Workout logged!', 'success')
    } catch (err) {
      setError(formatApiError(err, 'Could not log this workout.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div>
      <h1>Workout Tracker</h1>
      <p className="text-muted">
        Log the workouts you actually complete, picked from the real{' '}
        <Link to="/workouts">exercise library</Link> &mdash; not a suggestion, your real history.
      </p>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-4 mt-1">
        <div className="col-md-5">
          <div className="card h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">Log a completed workout</h2>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label" htmlFor="exercise_id">
                    Exercise
                  </label>
                  <select
                    id="exercise_id"
                    name="exercise_id"
                    className="form-select"
                    value={form.exercise_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="" disabled>
                      Select an exercise...
                    </option>
                    {exercises.map((exercise) => (
                      <option key={exercise.exercise_id} value={exercise.exercise_id}>
                        {exercise.exercise_name}
                      </option>
                    ))}
                  </select>
                </div>
                {selectedExercise && (
                  <ExerciseDemoGif
                    exerciseId={selectedExercise.exercise_id}
                    alt={`How to perform ${selectedExercise.exercise_name}`}
                    className="mb-3"
                  />
                )}
                <div className="mb-3">
                  <label className="form-label" htmlFor="log_date">
                    Date
                  </label>
                  <input
                    id="log_date"
                    name="log_date"
                    type="date"
                    className="form-control"
                    value={form.log_date}
                    onChange={handleChange}
                    max={todayIsoDate()}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="duration_minutes">
                    Duration (minutes)
                  </label>
                  <input
                    id="duration_minutes"
                    name="duration_minutes"
                    type="number"
                    className="form-control"
                    min={1}
                    max={600}
                    value={form.duration_minutes}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="calories_burned">
                    Calories burned (optional)
                  </label>
                  <input
                    id="calories_burned"
                    name="calories_burned"
                    type="number"
                    className="form-control"
                    min={0}
                    max={5000}
                    placeholder={
                      estimatedCalories ? `Auto-estimate: ${estimatedCalories} kcal` : 'Auto-estimated'
                    }
                    value={form.calories_burned}
                    onChange={handleChange}
                  />
                  <div className="form-text">
                    Leave blank to estimate from the exercise&apos;s reference rate and your
                    duration.
                  </div>
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="notes">
                    Notes (optional)
                  </label>
                  <input
                    id="notes"
                    name="notes"
                    type="text"
                    className="form-control"
                    maxLength={255}
                    value={form.notes}
                    onChange={handleChange}
                  />
                </div>
                <button type="submit" className="btn btn-primary w-100" disabled={isSubmitting}>
                  {isSubmitting ? 'Logging...' : 'Log workout'}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-md-7">
          <div className="card mb-4">
            <div className="card-body">
              <h2 className="h5 mb-3">Your progress</h2>
              <div className="row g-3 text-center">
                <div className="col-4">
                  <div className="display-6 fw-bold">{summary.count}</div>
                  <div className="text-muted small">Workouts logged</div>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold">{summary.totalCalories}</div>
                  <div className="text-muted small">Total kcal burned</div>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold">{summary.totalMinutes}</div>
                  <div className="text-muted small">Total minutes</div>
                </div>
              </div>
              {summary.lastLogDate && (
                <p className="text-muted small mt-3 mb-0">Last workout: {summary.lastLogDate}</p>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h2 className="h5 mb-3">History</h2>
              {isLoadingHistory ? (
                <p className="text-muted mb-0">Loading...</p>
              ) : history.length === 0 ? (
                <p className="text-muted mb-0">
                  No workouts logged yet &mdash; log your first one to start building your history.
                </p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Exercise</th>
                        <th className="text-end">Duration</th>
                        <th className="text-end">Calories</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((log) => (
                        <tr key={log.log_id}>
                          <td>{log.log_date}</td>
                          <td>{log.exercise?.exercise_name}</td>
                          <td className="text-end">{log.duration_minutes} min</td>
                          <td className="text-end">{log.calories_burned}</td>
                          <td className="text-muted small">{log.notes || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
