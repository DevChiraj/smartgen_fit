import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { calculateBmi } from '../services/bmiService'
import { formatApiError } from '../utils/formatApiError'

const CATEGORY_VARIANT = {
  Underweight: 'info',
  'Normal weight': 'success',
  Overweight: 'warning',
  Obese: 'danger',
}

export default function BMICalculator() {
  const { user } = useAuth()
  const [heightCm, setHeightCm] = useState(user?.height_cm || '')
  const [weightKg, setWeightKg] = useState(user?.weight_kg || '')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setResult(null)
    setIsSubmitting(true)
    try {
      const data = await calculateBmi({ height_cm: heightCm, weight_kg: weightKg })
      setResult(data)
    } catch (err) {
      setError(formatApiError(err, 'Could not calculate your BMI.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const variant = result ? CATEGORY_VARIANT[result.category?.category_name] || 'secondary' : null

  return (
    <div style={{ maxWidth: 420 }}>
      <h1>BMI Calculator</h1>
      <p className="text-muted">
        A quick, stateless way to check your Body Mass Index. This calculator doesn&apos;t save
        anything to your account.
      </p>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label" htmlFor="height_cm">
            Height (cm)
          </label>
          <input
            id="height_cm"
            type="number"
            step="0.1"
            className="form-control"
            value={heightCm}
            onChange={(event) => setHeightCm(event.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="weight_kg">
            Weight (kg)
          </label>
          <input
            id="weight_kg"
            type="number"
            step="0.1"
            className="form-control"
            value={weightKg}
            onChange={(event) => setWeightKg(event.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Calculating...' : 'Calculate BMI'}
        </button>
      </form>

      {result && (
        <div className="mt-4 p-3 border rounded text-center">
          <div className="display-6 fw-bold">{result.bmi}</div>
          <span className={`badge text-bg-${variant}`}>{result.category?.category_name}</span>
        </div>
      )}
    </div>
  )
}
