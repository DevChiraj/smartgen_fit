import { useEffect, useState } from 'react'
import { getFoods } from '../../services/foodService'
import { createFood, deleteFood, updateFood } from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

const EMPTY_FORM = {
  food_name: '',
  category: '',
  serving_size: '',
  calories: '',
  protein_g: '',
  carbs_g: '',
  fat_g: '',
  fiber_g: '',
  vitamins: '',
  minerals: '',
}

function toPayload(form) {
  return {
    food_name: form.food_name,
    category: form.category,
    serving_size: form.serving_size || null,
    calories: Number(form.calories),
    protein_g: Number(form.protein_g),
    carbs_g: Number(form.carbs_g),
    fat_g: Number(form.fat_g),
    fiber_g: form.fiber_g === '' ? null : Number(form.fiber_g),
    vitamins: form.vitamins || null,
    minerals: form.minerals || null,
  }
}

export default function AdminFoods() {
  const [foods, setFoods] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)

  const fetchFoods = () => {
    return getFoods()
      .then((data) => setFoods(data.foods))
      .catch((err) => setError(formatApiError(err, 'Could not load foods.')))
  }

  useEffect(() => {
    fetchFoods().finally(() => setIsLoading(false))
  }, [])

  const openCreateForm = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEditForm = (food) => {
    setEditingId(food.food_id)
    setForm({
      food_name: food.food_name,
      category: food.category,
      serving_size: food.serving_size || '',
      calories: food.calories,
      protein_g: food.protein_g,
      carbs_g: food.carbs_g,
      fat_g: food.fat_g,
      fiber_g: food.fiber_g ?? '',
      vitamins: food.vitamins || '',
      minerals: food.minerals || '',
    })
    setShowForm(true)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      if (editingId) {
        await updateFood(editingId, toPayload(form))
      } else {
        await createFood(toPayload(form))
      }
      setShowForm(false)
      await fetchFoods()
    } catch (err) {
      setError(formatApiError(err, 'Could not save food.'))
    }
  }

  const handleDelete = async (food) => {
    if (!window.confirm(`Delete "${food.food_name}"?`)) return
    setError('')
    try {
      await deleteFood(food.food_id)
      await fetchFoods()
    } catch (err) {
      setError(formatApiError(err, 'Could not delete food.'))
    }
  }

  if (isLoading) return <p className="text-muted">Loading...</p>

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}

      <button type="button" className="btn btn-primary mb-3" onClick={openCreateForm}>
        Add food
      </button>

      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Serving</th>
              <th className="text-end">Calories</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {foods.map((food) => (
              <tr key={food.food_id}>
                <td>{food.food_name}</td>
                <td>{food.category}</td>
                <td>{food.serving_size}</td>
                <td className="text-end">{food.calories}</td>
                <td>
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm me-2"
                    onClick={() => openEditForm(food)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => handleDelete(food)}
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
                <h2 className="modal-title h5">{editingId ? 'Edit food' : 'Add food'}</h2>
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
                    <label className="form-label" htmlFor="food_name">
                      Name
                    </label>
                    <input
                      id="food_name"
                      name="food_name"
                      className="form-control"
                      required
                      value={form.food_name}
                      onChange={(e) => setForm({ ...form, food_name: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_category">
                      Category
                    </label>
                    <input
                      id="food_category"
                      name="category"
                      className="form-control"
                      required
                      value={form.category}
                      onChange={(e) => setForm({ ...form, category: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_serving_size">
                      Serving size
                    </label>
                    <input
                      id="food_serving_size"
                      name="serving_size"
                      className="form-control"
                      placeholder="e.g. 100g"
                      value={form.serving_size}
                      onChange={(e) => setForm({ ...form, serving_size: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_calories">
                      Calories
                    </label>
                    <input
                      id="food_calories"
                      name="calories"
                      type="number"
                      min="0"
                      className="form-control"
                      required
                      value={form.calories}
                      onChange={(e) => setForm({ ...form, calories: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_fiber_g">
                      Fiber (g)
                    </label>
                    <input
                      id="food_fiber_g"
                      name="fiber_g"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      value={form.fiber_g}
                      onChange={(e) => setForm({ ...form, fiber_g: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_protein_g">
                      Protein (g)
                    </label>
                    <input
                      id="food_protein_g"
                      name="protein_g"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      required
                      value={form.protein_g}
                      onChange={(e) => setForm({ ...form, protein_g: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_carbs_g">
                      Carbs (g)
                    </label>
                    <input
                      id="food_carbs_g"
                      name="carbs_g"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      required
                      value={form.carbs_g}
                      onChange={(e) => setForm({ ...form, carbs_g: e.target.value })}
                    />
                  </div>
                  <div className="col-4">
                    <label className="form-label" htmlFor="food_fat_g">
                      Fat (g)
                    </label>
                    <input
                      id="food_fat_g"
                      name="fat_g"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      required
                      value={form.fat_g}
                      onChange={(e) => setForm({ ...form, fat_g: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="food_vitamins">
                      Vitamins
                    </label>
                    <input
                      id="food_vitamins"
                      name="vitamins"
                      className="form-control"
                      value={form.vitamins}
                      onChange={(e) => setForm({ ...form, vitamins: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="food_minerals">
                      Minerals
                    </label>
                    <input
                      id="food_minerals"
                      name="minerals"
                      className="form-control"
                      value={form.minerals}
                      onChange={(e) => setForm({ ...form, minerals: e.target.value })}
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
