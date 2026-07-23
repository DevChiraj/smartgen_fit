import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { API_ORIGIN } from '../services/apiClient'
import { calculateBmi } from '../services/bmiService'
import { getLatestRecommendation } from '../services/recommendationService'
import { getAnalysisHistory } from '../services/imageAnalysisService'
import AnalysisHistoryChart from '../components/AnalysisHistoryChart'

const CATEGORY_VARIANT = {
  Underweight: 'info',
  'Normal weight': 'success',
  Overweight: 'warning',
  Obese: 'danger',
}

const BODY_TYPE_VARIANT = {
  Thin: 'info',
  Normal: 'success',
  Overweight: 'warning',
}

export default function Dashboard() {
  const { user } = useAuth()
  const [bmiResult, setBmiResult] = useState(null)
  const [bmiError, setBmiError] = useState('')
  const [recommendation, setRecommendation] = useState(null)
  const [isLoadingRecommendation, setIsLoadingRecommendation] = useState(true)
  const [analysisHistory, setAnalysisHistory] = useState([])

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

  useEffect(() => {
    getAnalysisHistory()
      .then((data) => setAnalysisHistory(data.history || []))
      .catch(() => setAnalysisHistory([]))
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
        <div className="col-md-6 animate-in" style={{ '--animate-delay': '0ms' }}>
          <div className="card card-interactive h-100">
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

        <div className="col-md-6 animate-in" style={{ '--animate-delay': '80ms' }}>
          <div className="card card-interactive h-100">
            <div className="card-body">
              <h2 className="h5">Your BMI</h2>
              {!user.height_cm || !user.weight_kg ? (
                <p className="text-muted mb-0">
                  Add your height and weight in <Link to="/profile">your profile</Link> to see your
                  BMI here.
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

        <div className="col-12 animate-in" style={{ '--animate-delay': '160ms' }}>
          <div className="card">
            <div className="card-body">
              <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
                <h2 className="h5 mb-0">Your personalized plan</h2>
                {recommendation && (
                  <div className="d-flex align-items-center gap-2">
                    <span
                      className={`badge text-bg-${
                        BODY_TYPE_VARIANT[recommendation.body_type?.name] || 'secondary'
                      }`}
                    >
                      {recommendation.body_type?.name} &middot; BMI {recommendation.bmi_value}
                    </span>
                    <Link to="/meal-plan" className="small">
                      View full plan
                    </Link>
                  </div>
                )}
              </div>

              {isLoadingRecommendation ? (
                <p className="text-muted mb-0">Loading...</p>
              ) : recommendation ? (
                <div className="row g-4">
                  <div className="col-md-6">
                    <h3 className="h6 text-uppercase text-muted">Meal plan</h3>
                    <p className="mb-2">
                      <span className="badge text-bg-light border">
                        {recommendation.meal_record?.daily_calories} kcal / day
                      </span>
                    </p>
                    <dl className="row mb-0 small">
                      <dt className="col-5">Breakfast</dt>
                      <dd className="col-7">{recommendation.meal_record?.breakfast}</dd>
                      <dt className="col-5">Morning snack</dt>
                      <dd className="col-7">{recommendation.meal_record?.morning_snack}</dd>
                      <dt className="col-5">Lunch</dt>
                      <dd className="col-7">{recommendation.meal_record?.lunch}</dd>
                      <dt className="col-5">Evening snack</dt>
                      <dd className="col-7">{recommendation.meal_record?.evening_snack}</dd>
                      <dt className="col-5">Dinner</dt>
                      <dd className="col-7">{recommendation.meal_record?.dinner}</dd>
                    </dl>
                  </div>

                  <div className="col-md-6">
                    <h3 className="h6 text-uppercase text-muted">Workout plan</h3>
                    <p className="mb-2 d-flex flex-wrap gap-2">
                      <span className="badge text-bg-light border">
                        {recommendation.workout_record?.workout_type}
                      </span>
                      <span className="badge text-bg-light border">
                        {recommendation.workout_record?.intensity} intensity
                      </span>
                      <span className="badge text-bg-light border">
                        {recommendation.workout_record?.calories_burned} kcal burned
                      </span>
                    </p>
                    <dl className="row mb-0 small">
                      <dt className="col-5">Category</dt>
                      <dd className="col-7">{recommendation.workout_record?.workout_category}</dd>
                      <dt className="col-5">Duration</dt>
                      <dd className="col-7">
                        {recommendation.workout_record?.duration_min} min (
                        {recommendation.workout_record?.warmup_min} min warm-up,{' '}
                        {recommendation.workout_record?.cooldown_min} min cool-down)
                      </dd>
                      <dt className="col-5">Schedule</dt>
                      <dd className="col-7">
                        {recommendation.workout_record?.days_per_week} days/week &middot;{' '}
                        {recommendation.workout_record?.indoor_outdoor}
                      </dd>
                      <dt className="col-5">Target muscle</dt>
                      <dd className="col-7">{recommendation.workout_record?.target_muscle}</dd>
                      <dt className="col-5">Equipment</dt>
                      <dd className="col-7">
                        {recommendation.workout_record?.equipment || 'None'}
                      </dd>
                      <dt className="col-5">Goal</dt>
                      <dd className="col-7">{recommendation.workout_record?.goal}</dd>
                    </dl>
                  </div>
                </div>
              ) : (
                <p className="text-muted mb-0">
                  <Link to="/analyze">Analyze a body photo</Link> to get a personalized meal and
                  workout plan matched to you.
                </p>
              )}
            </div>
          </div>
        </div>

        {analysisHistory.length > 0 && (
          <div className="col-12 animate-in" style={{ '--animate-delay': '240ms' }}>
            <div className="card">
              <div className="card-body">
                <h2 className="h5 mb-1">Body type analysis history</h2>
                <p className="text-muted small mb-3">
                  Confidence score of your last {Math.min(analysisHistory.length, 10)} photo
                  analyses.
                </p>
                <AnalysisHistoryChart history={analysisHistory} />
              </div>
            </div>
          </div>
        )}

        <div className="col-12 animate-in" style={{ '--animate-delay': '320ms' }}>
          <h2 className="h5 mt-2">Quick actions</h2>
          <div className="row g-3">
            <div className="col-sm-6 col-lg-4">
              <Link to="/profile" className="btn btn-outline-primary w-100 h-100">
                Edit profile
              </Link>
            </div>
            <div className="col-sm-6 col-lg-4">
              <Link to="/bmi-calculator" className="btn btn-outline-primary w-100 h-100">
                Recalculate BMI
              </Link>
            </div>
            <div className="col-sm-6 col-lg-4">
              <Link to="/analyze" className="btn btn-outline-primary w-100 h-100">
                Analyze body photo
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
