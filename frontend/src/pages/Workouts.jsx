import { useEffect, useState } from 'react'
import { getExerciseDifficulties, getExercises } from '../services/exerciseService'
import { formatApiError } from '../utils/formatApiError'
import FloatingIcons from '../components/FloatingIcons'
import ExerciseDemoGif from '../components/ExerciseDemoGif'

const DIFFICULTY_VARIANT = {
  Beginner: 'success',
  Intermediate: 'warning',
  Advanced: 'danger',
}

export default function Workouts() {
  const [exercises, setExercises] = useState([])
  const [difficulties, setDifficulties] = useState([])
  const [difficulty, setDifficulty] = useState('')
  const [search, setSearch] = useState('')
  const [selectedExercise, setSelectedExercise] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getExerciseDifficulties()
      .then((data) => setDifficulties(data.difficulties))
      .catch(() => setDifficulties([]))
  }, [])

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsLoading(true)
      setError('')
      getExercises({ difficulty: difficulty || undefined, q: search || undefined })
        .then((data) => setExercises(data.exercises))
        .catch((err) => setError(formatApiError(err, 'Could not load exercises.')))
        .finally(() => setIsLoading(false))
    }, 300)
    return () => clearTimeout(timeout)
  }, [difficulty, search])

  return (
    <div>
      <div className="position-relative pb-2">
        <FloatingIcons />
        <h1>Workouts</h1>
        <p className="text-muted">
          A library of exercises with sets, reps, calories burned, and target muscles &mdash; search
          or filter by difficulty, and click an exercise for its full detail.
        </p>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-4">
          <input
            type="search"
            className="form-control"
            placeholder="Search exercises..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="col-sm-6 col-md-4">
          <select
            className="form-select"
            value={difficulty}
            onChange={(event) => setDifficulty(event.target.value)}
          >
            <option value="">All difficulty levels</option>
            {difficulties.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {isLoading ? (
        <p className="text-muted">Loading...</p>
      ) : exercises.length === 0 ? (
        <p className="text-muted">No exercises match your search.</p>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>Exercise</th>
                <th>Target muscle</th>
                <th>Difficulty</th>
                <th>Sets x Reps</th>
                <th className="text-end">Calories / 30 min</th>
              </tr>
            </thead>
            <tbody>
              {exercises.map((exercise) => (
                <tr
                  key={exercise.exercise_id}
                  role="button"
                  onClick={() => setSelectedExercise(exercise)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>{exercise.exercise_name}</td>
                  <td>{exercise.target_muscle}</td>
                  <td>
                    <span
                      className={`badge text-bg-${DIFFICULTY_VARIANT[exercise.difficulty] || 'secondary'}`}
                    >
                      {exercise.difficulty}
                    </span>
                  </td>
                  <td>
                    {exercise.sets} x {exercise.reps}
                  </td>
                  <td className="text-end">{exercise.calories_per_30min}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedExercise && (
        <div
          className="modal d-block"
          tabIndex={-1}
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedExercise(null)}
        >
          <div className="modal-dialog modal-dialog-centered" onClick={(e) => e.stopPropagation()}>
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title h5">{selectedExercise.exercise_name}</h2>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedExercise(null)}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                <ExerciseDemoGif
                  exerciseId={selectedExercise.exercise_id}
                  alt={`How to perform ${selectedExercise.exercise_name}`}
                  className="mb-3"
                />
                <p className="mb-3">
                  <span
                    className={`badge text-bg-${DIFFICULTY_VARIANT[selectedExercise.difficulty] || 'secondary'}`}
                  >
                    {selectedExercise.difficulty}
                  </span>
                </p>
                <p className="text-muted">{selectedExercise.benefit}</p>
                <dl className="row mb-0">
                  <dt className="col-6">Target muscle</dt>
                  <dd className="col-6">{selectedExercise.target_muscle}</dd>
                  <dt className="col-6">Sets x Reps</dt>
                  <dd className="col-6">
                    {selectedExercise.sets} x {selectedExercise.reps}
                  </dd>
                  <dt className="col-6">Calories (per 30 min)</dt>
                  <dd className="col-6">{selectedExercise.calories_per_30min}</dd>
                  <dt className="col-6">Equipment</dt>
                  <dd className="col-6">{selectedExercise.equipment || 'None (bodyweight)'}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
