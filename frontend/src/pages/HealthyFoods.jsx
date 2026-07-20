import { useEffect, useState } from 'react'
import { getFoodCategories, getFoods } from '../services/foodService'
import { formatApiError } from '../utils/formatApiError'
import heroBg from '../assets/healthy-foods-hero-bg.png'

export default function HealthyFoods() {
  const [foods, setFoods] = useState([])
  const [categories, setCategories] = useState([])
  const [category, setCategory] = useState('')
  const [search, setSearch] = useState('')
  const [selectedFood, setSelectedFood] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getFoodCategories()
      .then((data) => setCategories(data.categories))
      .catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsLoading(true)
      setError('')
      getFoods({ category: category || undefined, q: search || undefined })
        .then((data) => setFoods(data.foods))
        .catch((err) => setError(formatApiError(err, 'Could not load foods.')))
        .finally(() => setIsLoading(false))
    }, 300)
    return () => clearTimeout(timeout)
  }, [category, search])

  return (
    <div>
      <div
        className="p-4 p-md-5 rounded-4 hero-section mb-4"
        style={{
          backgroundImage: `linear-gradient(rgba(10, 10, 12, 0.82), rgba(10, 10, 12, 0.93)), url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <h1>Healthy Foods</h1>
        <p className="text-muted mb-0">
          Nutrition facts for common Sri Lankan foods &mdash; search or filter by category, and
          click a food for its full breakdown.
        </p>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-md-4">
          <input
            type="search"
            className="form-control"
            placeholder="Search foods..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="col-sm-6 col-md-4">
          <select
            className="form-select"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {isLoading ? (
        <p className="text-muted">Loading...</p>
      ) : foods.length === 0 ? (
        <p className="text-muted">No foods match your search.</p>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>Food</th>
                <th>Category</th>
                <th>Serving</th>
                <th className="text-end">Calories</th>
                <th className="text-end">Protein (g)</th>
                <th className="text-end">Carbs (g)</th>
                <th className="text-end">Fat (g)</th>
              </tr>
            </thead>
            <tbody>
              {foods.map((food) => (
                <tr
                  key={food.food_id}
                  role="button"
                  onClick={() => setSelectedFood(food)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>{food.food_name}</td>
                  <td>
                    <span className="badge text-bg-light border">{food.category}</span>
                  </td>
                  <td>{food.serving_size}</td>
                  <td className="text-end">{food.calories}</td>
                  <td className="text-end">{food.protein_g}</td>
                  <td className="text-end">{food.carbs_g}</td>
                  <td className="text-end">{food.fat_g}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedFood && (
        <div
          className="modal d-block"
          tabIndex={-1}
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedFood(null)}
        >
          <div className="modal-dialog modal-dialog-centered" onClick={(e) => e.stopPropagation()}>
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title h5">{selectedFood.food_name}</h2>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedFood(null)}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                <p className="text-muted mb-3">
                  {selectedFood.category} &middot; per {selectedFood.serving_size}
                </p>
                <dl className="row mb-0">
                  <dt className="col-6">Calories</dt>
                  <dd className="col-6">{selectedFood.calories} kcal</dd>
                  <dt className="col-6">Protein</dt>
                  <dd className="col-6">{selectedFood.protein_g} g</dd>
                  <dt className="col-6">Carbohydrates</dt>
                  <dd className="col-6">{selectedFood.carbs_g} g</dd>
                  <dt className="col-6">Fat</dt>
                  <dd className="col-6">{selectedFood.fat_g} g</dd>
                  {selectedFood.fiber_g != null && (
                    <>
                      <dt className="col-6">Fiber</dt>
                      <dd className="col-6">{selectedFood.fiber_g} g</dd>
                    </>
                  )}
                  {selectedFood.vitamins && (
                    <>
                      <dt className="col-6">Vitamins</dt>
                      <dd className="col-6">{selectedFood.vitamins}</dd>
                    </>
                  )}
                  {selectedFood.minerals && (
                    <>
                      <dt className="col-6">Minerals</dt>
                      <dd className="col-6">{selectedFood.minerals}</dd>
                    </>
                  )}
                </dl>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
