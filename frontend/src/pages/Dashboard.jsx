import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { API_ORIGIN } from '../services/apiClient'
import { calculateBmi } from '../services/bmiService'
import { getLatestRecommendation } from '../services/recommendationService'

const CATEGORY_VARIANT = {
  Underweight: 'info',
  'Normal weight': 'success',
  Overweight: 'warning',
  Obese: 'danger',
}

export default function Dashboard() {
  const { user } = useAuth()
  const [bmiResult, setBmiResult] = useState(null)
  const [bmiError, setBmiError] = useState('')
  const [recommendation, setRecommendation] = useState(null)
  const [isLoadingRecommendation, setIsLoadingRecommendation] = useState(true)

  useEffect(() => {
    if (!user?.height_cm || !user?.weight_kg) return
    calculateBmi({ height_cm: user.height_cm, weight_kg: user.weight_kg })
      .then(setBmiResult)
      .catch(() => setBmiError('Could not calculate your BMI.'))
  }, [user?.height_cm, user?.weight_kg])

  useEffect(() => {
    getLatestRecommendation()
      .then((data) => setRecommendation(data.recommendation))
      .finally(() => setIsLoadingRecommendation(false))
  }, [])

  if (!user) {
    return null
  }

  const variant = bmiResult
    ? CATEGORY_VARIANT[bmiResult.category?.category_name] || 'secondary'
    : null
  const gaugePercent = bmiResult
    ? Math.min(
        100,
        Math.max(
          0,
          ((Number(bmiResult.bmi) - Number(bmiResult.category.min_bmi)) /
            (Number(bmiResult.category.max_bmi) - Number(bmiResult.category.min_bmi))) *
            100,
        ),
      )
    : 0

  return (
    <div>
      <h1>Welcome back, {user.full_name}</h1>

      <div className="row g-4 mt-1">
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body d-flex align-items-center gap-3">
              {user.profile_picture_url ? (
                <img
                  src={`${API_ORIGIN}${user.profile_picture_url}`}
                  alt="Profile"
                  width={64}
                  height={64}
                  style={{ objectFit: 'cover', borderRadius: '50%' }}
                />
              ) : (
                <div
                  className="bg-secondary-subtle d-flex align-items-center justify-content-center small"
                  style={{ width: 64, height: 64, borderRadius: '50%' }}
                >
                  No photo
                </div>
              )}
              <div>
                <h2 className="h5 mb-1">{user.full_name}</h2>
                <p className="text-muted mb-0 small">
                  {user.username} &middot; {user.age} years old &middot; {user.gender}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h2 className="h5">Your BMI</h2>
              {!user.height_cm || !user.weight_kg ? (
                <p className="text-muted mb-0">
                  Add your height and weight in <Link to="/profile">your profile</Link> to see
                  your BMI here.
                </p>
              ) : bmiError ? (
                <p className="text-danger mb-0">{bmiError}</p>
              ) : bmiResult ? (
                <>
                  <div className="d-flex align-items-baseline gap-2 mb-2">
                    <span className="display-6 fw-bold">{bmiResult.bmi}</span>
                    <span className={`badge text-bg-${variant}`}>
                      {bmiResult.category?.category_name}
                    </span>
                  </div>
                  <div className="progress" style={{ height: 8 }}>
                    <div
                      className={`progress-bar bg-${variant}`}
                      style={{ width: `${gaugePercent}%` }}
                    />
                  </div>
                  <p className="text-muted small mt-2 mb-0">
                    {bmiResult.category?.category_name} range: {bmiResult.category?.min_bmi}
                    &ndash;{bmiResult.category?.max_bmi}
                  </p>
                </>
              ) : (
                <p className="text-muted mb-0">Calculating...</p>
              )}
            </div>
          </div>
        </div>

        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h2 className="h5">Body type &amp; latest plan</h2>
              {isLoadingRecommendation ? (
                <p className="text-muted mb-0">Loading...</p>
              ) : recommendation ? (
                <div className="row g-3">
                  <div className="col-md-4">
                    <strong>Body type:</strong> {recommendation.body_type?.name}
                  </div>
                  <div className="col-md-4">
                    <strong>Meal plan:</strong> {recommendation.meal_plan?.plan_code} (
                    {recommendation.meal_plan?.calories} kcal)
                  </div>
                  <div className="col-md-4">
                    <strong>Workout plan:</strong> {recommendation.workout_plan?.plan_code} (
                    {recommendation.workout_plan?.duration_minutes} min,{' '}
                    {recommendation.workout_plan?.calories_burned} kcal burned)
                  </div>
                </div>
              ) : (
                <p className="text-muted mb-0">
                  You haven&apos;t been analyzed yet. Photo-based body type classification and
                  personalized meal/workout plans are coming in a future update.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="col-12">
          <h2 className="h5 mt-2">Quick actions</h2>
          <div className="row g-3">
            <div className="col-sm-6 col-lg-3">
              <Link to="/profile" className="btn btn-outline-primary w-100 h-100">
                Edit profile
              </Link>
            </div>
            <div className="col-sm-6 col-lg-3">
              <Link to="/bmi-calculator" className="btn btn-outline-primary w-100 h-100">
                Recalculate BMI
              </Link>
            </div>
            <div className="col-sm-6 col-lg-3">
              <Link to="/analyze" className="btn btn-outline-primary w-100 h-100">
                Analyze body photo
              </Link>
            </div>
            <div className="col-sm-6 col-lg-3">
              <button type="button" className="btn btn-outline-secondary w-100 h-100" disabled>
                Meal &amp; workout plans (coming soon)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
