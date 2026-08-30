import { useEffect, useState } from 'react'
import { getExercises } from '../../services/exerciseService'
import { createExercise, deleteExercise, updateExercise } from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

const EMPTY_FORM = {
  exercise_name: '',
  target_muscle: '',
  difficulty: 'Beginner',
  equipment: '',
  sets: '',
  reps: '',
  calories_per_30min: '',
  benefit: '',
}

function toPayload(form) {
  return {
    exercise_name: form.exercise_name,
    target_muscle: form.target_muscle,
    difficulty: form.difficulty,
    equipment: form.equipment || null,
    sets: Number(form.sets),
    reps: Number(form.reps),
    calories_per_30min: Number(form.calories_per_30min),
    benefit: form.benefit,
  }
}

export default function AdminExercises() {
  const [exercises, setExercises] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)

  const fetchExercises = () => {
    return getExercises()
      .then((data) => setExercises(data.exercises))
      .catch((err) => setError(formatApiError(err, 'Could not load exercises.')))
  }

  useEffect(() => {
    fetchExercises().finally(() => setIsLoading(false))
  }, [])

  const openCreateForm = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEditForm = (exercise) => {
    setEditingId(exercise.exercise_id)
    setForm({
      exercise_name: exercise.exercise_name,
      target_muscle: exercise.target_muscle,
      difficulty: exercise.difficulty,
      equipment: exercise.equipment || '',
      sets: exercise.sets,
      reps: exercise.reps,
      calories_per_30min: exercise.calories_per_30min,
      benefit: exercise.benefit,
    })
    setShowForm(true)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      if (editingId) {
        await updateExercise(editingId, toPayload(form))
      } else {
        await createExercise(toPayload(form))
      }
      setShowForm(false)
      await fetchExercises()
    } catch (err) {
      setError(formatApiError(err, 'Could not save exercise.'))
    }
  }

  const handleDelete = async (exercise) => {
    if (!window.confirm(`Delete "${exercise.exercise_name}"?`)) return
    setError('')
    try {
      await deleteExercise(exercise.exercise_id)
      await fetchExercises()
    } catch (err) {
      setError(formatApiError(err, 'Could not delete exercise.'))
    }
  }

  if (isLoading) return <p className="text-muted">Loading...</p>

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}

      <button type="button" className="btn btn-primary mb-3" onClick={openCreateForm}>
        Add exercise
      </button>

      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Target muscle</th>
              <th>Difficulty</th>
              <th>Sets x Reps</th>
              <th className="text-end">Calories / 30 min</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {exercises.map((exercise) => (
              <tr key={exercise.exercise_id}>
                <td>{exercise.exercise_name}</td>
                <td>{exercise.target_muscle}</td>
                <td>{exercise.difficulty}</td>
                <td>
                  {exercise.sets} x {exercise.reps}
                </td>
                <td className="text-end">{exercise.calories_per_30min}</td>
                <td>
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm me-2"
                    onClick={() => openEditForm(exercise)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => handleDelete(exercise)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div
          className="modal d-block"
          tabIndex={-1}
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowForm(false)}
        >
          <div
            className="modal-dialog modal-dialog-centered"
            onClick={(event) => event.stopPropagation()}
          >
            <form className="modal-content" onSubmit={handleSubmit}>
              <div className="modal-header">
                <h2 className="modal-title h5">{editingId ? 'Edit exercise' : 'Add exercise'}</h2>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowForm(false)}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                <div className="row g-2">
                  <div className="col-8">
                    <label className="form-label" htmlFor="exercise_name">
                      Name
                    </label>
                    <input
                      id="exercise_name"
                      name="exercise_name"
                      className="form-control"
                      required
                      value={form.exercise_name}
                      onChange={(e) => setForm({ ...form, exercise_name: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="exercise_difficulty">
                      Difficulty
                    </label>
                    <select
                      id="exercise_difficulty"
                      name="difficulty"
                      className="form-select"
                      value={form.difficulty}
                      onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                    >
                      <option>Beginner</option>
                      <option>Intermediate</option>
                      <option>Advanced</option>
                    </select>
                  </div>
                  <div className="col-8">
                    <label className="form-label" htmlFor="exercise_target_muscle">
                      Target muscle
                    </label>
                    <input
                      id="exercise_target_muscle"
                      name="target_muscle"
                      className="form-control"
                      required
                      value={form.target_muscle}
                      onChange={(e) => setForm({ ...form, target_muscle: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="exercise_equipment">
                      Equipment
                    </label>
                    <input
                      id="exercise_equipment"
                      name="equipment"
                      className="form-control"
                      placeholder="None"
                      value={form.equipment}
                      onChange={(e) => setForm({ ...form, equipment: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="exercise_sets">
                      Sets
                    </label>
                    <input
                      id="exercise_sets"
                      name="sets"
                      type="number"
                      min="1"
                      className="form-control"
                      required
                      value={form.sets}
                      onChange={(e) => setForm({ ...form, sets: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="exercise_reps">
                      Reps
                    </label>
                    <input
                      id="exercise_reps"
                      name="reps"
                      type="number"
                      min="1"
                      className="form-control"
                      required
                      value={form.reps}
                      onChange={(e) => setForm({ ...form, reps: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="exercise_calories">
                      Calories / 30 min
                    </label>
                    <input
                      id="exercise_calories"
                      name="calories_per_30min"
                      type="number"
                      min="0"
                      className="form-control"
                      required
                      value={form.calories_per_30min}
                      onChange={(e) => setForm({ ...form, calories_per_30min: e.target.value })}
                    />
                  </div>
                  <div className="col-12">
                    <label className="form-label" htmlFor="exercise_benefit">
                      Benefit
                    </label>
                    <input
                      id="exercise_benefit"
                      name="benefit"
                      className="form-control"
                      required
                      value={form.benefit}
                      onChange={(e) => setForm({ ...form, benefit: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
