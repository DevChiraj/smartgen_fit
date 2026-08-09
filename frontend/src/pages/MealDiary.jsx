import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useNotifications } from '../context/NotificationContext'
import { getFoods } from '../services/foodService'
import { getMealLogHistory, logMeal } from '../services/mealLogService'
import { formatApiError } from '../utils/formatApiError'

const MEAL_TYPE_OPTIONS = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'morning_snack', label: 'Morning snack' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'evening_snack', label: 'Evening snack' },
  { value: 'dinner', label: 'Dinner' },
]

const MEAL_TYPE_LABEL = Object.fromEntries(MEAL_TYPE_OPTIONS.map((o) => [o.value, o.label]))

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

const initialForm = {
  food_id: '',
  meal_type: 'breakfast',
  quantity_servings: '1',
  log_date: todayIsoDate(),
  notes: '',
}

export default function MealDiary() {
  const { showToast } = useNotifications()
  const [foods, setFoods] = useState([])
  const [history, setHistory] = useState([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState(initialForm)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    getFoods()
      .then((data) => setFoods(data.foods || []))
      .catch(() => setFoods([]))
  }, [])

  useEffect(() => {
    getMealLogHistory()
      .then((data) => setHistory(data.history || []))
      .catch((err) => setError(formatApiError(err, 'Could not load your meal history.')))
      .finally(() => setIsLoadingHistory(false))
  }, [])

  const selectedFood = useMemo(
    () => foods.find((food) => String(food.food_id) === String(form.food_id)),
    [foods, form.food_id],
  )

  const estimatedCalories =
    selectedFood && form.quantity_servings
      ? Math.round(selectedFood.calories * Number(form.quantity_servings))
      : null

  const todaySummary = useMemo(() => {
    const today = todayIsoDate()
    const todaysLogs = history.filter((log) => log.log_date === today)
    const totalCalories = todaysLogs.reduce((sum, log) => sum + log.calories, 0)
    const totalProtein = todaysLogs.reduce((sum, log) => sum + Number(log.protein_g), 0)
    const loggedMealTypes = new Set(todaysLogs.map((log) => log.meal_type))
    return { count: todaysLogs.length, totalCalories, totalProtein, loggedMealTypes }
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
        food_id: Number(form.food_id),
        meal_type: form.meal_type,
        quantity_servings: Number(form.quantity_servings),
        log_date: form.log_date || undefined,
        notes: form.notes || undefined,
      }
      const data = await logMeal(payload)
      setHistory((prev) => [data.log, ...prev])
      setForm({ ...initialForm, log_date: todayIsoDate() })
      showToast('Meal logged!', 'success')
    } catch (err) {
      setError(formatApiError(err, 'Could not log this meal.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div>
      <h1>Meal Diary</h1>
      <p className="text-muted">
        Log what you actually eat, picked from the real{' '}
        <Link to="/healthy-foods">nutrition database</Link> &mdash; not a suggestion, your real
        history.
      </p>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-4 mt-1">
        <div className="col-md-5">
          <div className="card h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">Log a meal</h2>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label" htmlFor="food_id">
                    Food
                  </label>
                  <select
                    id="food_id"
                    name="food_id"
                    className="form-select"
                    value={form.food_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="" disabled>
                      Select a food...
                    </option>
                    {foods.map((food) => (
                      <option key={food.food_id} value={food.food_id}>
                        {food.food_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="meal_type">
                    Meal
                  </label>
                  <select
                    id="meal_type"
                    name="meal_type"
                    className="form-select"
                    value={form.meal_type}
                    onChange={handleChange}
                    required
                  >
                    {MEAL_TYPE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
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
                  <label className="form-label" htmlFor="quantity_servings">
                    Servings
                  </label>
                  <input
                    id="quantity_servings"
                    name="quantity_servings"
                    type="number"
                    className="form-control"
                    min={0.1}
                    max={20}
                    step={0.1}
                    value={form.quantity_servings}
                    onChange={handleChange}
                    required
                  />
                  {estimatedCalories !== null && (
                    <div className="form-text">Estimated: {estimatedCalories} kcal</div>
                  )}
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
                  {isSubmitting ? 'Logging...' : 'Log meal'}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-md-7">
          <div className="card mb-4">
            <div className="card-body">
              <h2 className="h5 mb-3">Today</h2>
              <div className="row g-3 text-center">
                <div className="col-4">
                  <div className="display-6 fw-bold">{todaySummary.count}</div>
                  <div className="text-muted small">Meals logged</div>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold">{todaySummary.totalCalories}</div>
                  <div className="text-muted small">Kcal consumed</div>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold">{todaySummary.totalProtein.toFixed(1)}</div>
                  <div className="text-muted small">Protein (g)</div>
                </div>
              </div>
              <div className="d-flex flex-wrap gap-2 mt-3">
                {MEAL_TYPE_OPTIONS.map((option) => (
                  <span
                    key={option.value}
                    className={`badge rounded-pill ${
                      todaySummary.loggedMealTypes.has(option.value)
                        ? 'text-bg-success'
                        : 'text-bg-light border'
                    }`}
                  >
                    {option.label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h2 className="h5 mb-3">History</h2>
              {isLoadingHistory ? (
                <p className="text-muted mb-0">Loading...</p>
              ) : history.length === 0 ? (
                <p className="text-muted mb-0">
                  No meals logged yet &mdash; log your first one to start building your history.
                </p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Meal</th>
                        <th>Food</th>
                        <th className="text-end">Servings</th>
                        <th className="text-end">Calories</th>
                        <th className="text-end">Protein</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((log) => (
                        <tr key={log.log_id}>
                          <td>{log.log_date}</td>
                          <td>{MEAL_TYPE_LABEL[log.meal_type] || log.meal_type}</td>
                          <td>{log.food?.food_name}</td>
                          <td className="text-end">{log.quantity_servings}</td>
                          <td className="text-end">{log.calories}</td>
                          <td className="text-end">{log.protein_g}g</td>
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
