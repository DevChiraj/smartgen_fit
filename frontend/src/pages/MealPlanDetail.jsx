import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getLatestRecommendation } from '../services/recommendationService'
import { getSuggestedWorkoutDays } from '../utils/weeklySchedule'

const BODY_TYPE_VARIANT = {
  Thin: 'info',
  Normal: 'success',
  Overweight: 'warning',
}

export default function MealPlanDetail() {
  const [recommendation, setRecommendation] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getLatestRecommendation()
      .then((data) => setRecommendation(data.recommendation))
      .finally(() => setIsLoading(false))
  }, [])

  if (isLoading) {
    return <p className="text-muted">Loading...</p>
  }

  if (!recommendation) {
    return (
      <div>
        <h1>My Meal &amp; Workout Plan</h1>
        <p className="text-muted mb-0">
          <Link to="/analyze">Analyze a body photo</Link> to get a personalized meal and workout
          plan matched to you.
        </p>
      </div>
    )
  }

  const { meal_record: meal, workout_record: workout } = recommendation

  return (
    <div>
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <h1 className="mb-0">My Meal &amp; Workout Plan</h1>
        <span
          className={`badge fs-6 text-bg-${
            BODY_TYPE_VARIANT[recommendation.body_type?.name] || 'secondary'
          }`}
        >
          {recommendation.body_type?.name} &middot; BMI {recommendation.bmi_value}
        </span>
      </div>
      <p className="text-muted">
        Matched from a real dataset of similar people (age, gender, and predicted body type) using
        a K-Nearest-Neighbors model &mdash; not generated. Looking for ingredient nutrition facts?
        Check <Link to="/healthy-foods">Healthy Foods</Link>.
      </p>

      <div className="row g-4 mt-1">
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h2 className="h5">Meal plan</h2>
              <p className="mb-3">
                <span className="badge text-bg-light border fs-6">
                  {meal?.daily_calories} kcal / day
                </span>
              </p>
              <dl className="row mb-0">
                <dt className="col-4">Breakfast</dt>
                <dd className="col-8">{meal?.breakfast}</dd>
                <dt className="col-4">Morning snack</dt>
                <dd className="col-8">{meal?.morning_snack}</dd>
                <dt className="col-4">Lunch</dt>
                <dd className="col-8">{meal?.lunch}</dd>
                <dt className="col-4">Evening snack</dt>
                <dd className="col-8">{meal?.evening_snack}</dd>
                <dt className="col-4">Dinner</dt>
                <dd className="col-8">{meal?.dinner}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h2 className="h5">Workout plan</h2>
              <p className="mb-3 d-flex flex-wrap gap-2">
                <span className="badge text-bg-light border fs-6">{workout?.workout_type}</span>
                <span className="badge text-bg-light border fs-6">
                  {workout?.intensity} intensity
                </span>
                <span className="badge text-bg-light border fs-6">
                  {workout?.calories_burned} kcal burned
                </span>
              </p>
              <dl className="row mb-3">
                <dt className="col-4">Category</dt>
                <dd className="col-8">{workout?.workout_category}</dd>
                <dt className="col-4">Duration</dt>
                <dd className="col-8">
                  {workout?.duration_min} min ({workout?.warmup_min} min warm-up,{' '}
                  {workout?.cooldown_min} min cool-down)
                </dd>
                <dt className="col-4">Location</dt>
                <dd className="col-8">{workout?.indoor_outdoor}</dd>
                <dt className="col-4">Target muscle</dt>
                <dd className="col-8">{workout?.target_muscle}</dd>
                <dt className="col-4">Equipment</dt>
                <dd className="col-8">{workout?.equipment || 'None'}</dd>
                <dt className="col-4">Goal</dt>
                <dd className="col-8">{workout?.goal}</dd>
              </dl>

              <h3 className="h6 text-uppercase text-muted">
                Suggested weekly schedule ({workout?.days_per_week} days/week)
              </h3>
              <div className="d-flex gap-2 mb-2">
                {getSuggestedWorkoutDays(workout?.days_per_week).map(({ day, isWorkoutDay }) => (
                  <span
                    key={day}
                    className={`badge rounded-pill ${
                      isWorkoutDay ? 'text-bg-primary' : 'text-bg-light border'
                    }`}
                    style={{ width: 48 }}
                  >
                    {day}
                  </span>
                ))}
              </div>
              <p className="text-muted small mb-0">
                A suggested spread based on your {workout?.days_per_week}-day/week frequency, not a
                specific day-by-day exercise plan. Browse <Link to="/workouts">Workouts</Link> for
                exercises to fill each session.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
