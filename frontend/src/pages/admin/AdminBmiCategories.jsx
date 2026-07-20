import { useEffect, useState } from 'react'
import {
  createBmiCategory,
  deleteBmiCategory,
  getBmiCategories,
  updateBmiCategory,
} from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

const EMPTY_FORM = { category_name: '', min_bmi: '', max_bmi: '' }

export default function AdminBmiCategories() {
  const [categories, setCategories] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [showForm, setShowForm] = useState(false)

  const fetchCategories = () => {
    return getBmiCategories()
      .then((data) => setCategories(data.bmi_categories))
      .catch((err) => setError(formatApiError(err, 'Could not load BMI categories.')))
  }

  useEffect(() => {
    fetchCategories().finally(() => setIsLoading(false))
  }, [])

  const openCreateForm = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEditForm = (category) => {
    setEditingId(category.bmi_category_id)
    setForm({
      category_name: category.category_name,
      min_bmi: category.min_bmi,
      max_bmi: category.max_bmi,
    })
    setShowForm(true)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    const payload = {
      category_name: form.category_name,
      min_bmi: Number(form.min_bmi),
      max_bmi: Number(form.max_bmi),
    }
    try {
      if (editingId) {
        await updateBmiCategory(editingId, payload)
      } else {
        await createBmiCategory(payload)
      }
      setShowForm(false)
      await fetchCategories()
    } catch (err) {
      setError(formatApiError(err, 'Could not save BMI category.'))
    }
  }

  const handleDelete = async (category) => {
    if (!window.confirm(`Delete "${category.category_name}"?`)) return
    setError('')
    try {
      await deleteBmiCategory(category.bmi_category_id)
      await fetchCategories()
    } catch (err) {
      setError(formatApiError(err, 'Could not delete BMI category.'))
    }
  }

  if (isLoading) return <p className="text-muted">Loading...</p>

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}

      <button type="button" className="btn btn-primary mb-3" onClick={openCreateForm}>
        Add BMI category
      </button>

      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>Category</th>
              <th>Min BMI</th>
              <th>Max BMI</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => (
              <tr key={category.bmi_category_id}>
                <td>{category.category_name}</td>
                <td>{category.min_bmi}</td>
                <td>{category.max_bmi}</td>
                <td>
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm me-2"
                    onClick={() => openEditForm(category)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => handleDelete(category)}
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
                <h2 className="modal-title h5">
                  {editingId ? 'Edit BMI category' : 'Add BMI category'}
                </h2>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowForm(false)}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                <div className="mb-2">
                  <label className="form-label" htmlFor="bmi_category_name">
                    Category name
                  </label>
                  <input
                    id="bmi_category_name"
                    name="category_name"
                    className="form-control"
                    required
                    value={form.category_name}
                    onChange={(e) => setForm({ ...form, category_name: e.target.value })}
                  />
                </div>
                <div className="row g-2">
                  <div className="col-6">
                    <label className="form-label" htmlFor="bmi_min">
                      Min BMI
                    </label>
                    <input
                      id="bmi_min"
                      name="min_bmi"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      required
                      value={form.min_bmi}
                      onChange={(e) => setForm({ ...form, min_bmi: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="bmi_max">
                      Max BMI
                    </label>
                    <input
                      id="bmi_max"
                      name="max_bmi"
                      type="number"
                      min="0"
                      step="0.1"
                      className="form-control"
                      required
                      value={form.max_bmi}
                      onChange={(e) => setForm({ ...form, max_bmi: e.target.value })}
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
