import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { title: 'Body Type Analysis', description: 'Image-based classification powered by a trained CNN.' },
  { title: 'Sri Lankan Meal Plans', description: 'Nutrition guidance built around local, familiar foods.' },
  { title: 'Workout Plans', description: 'Routines matched to your body type, BMI, and age group.' },
  { title: 'BMI Tracking', description: 'Calculate and track your BMI category over time.' },
]

export default function LandingPage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      <section className="text-center py-5">
        <h1 className="display-5 fw-bold">AI-Powered Personalized Nutrition &amp; Fitness</h1>
        <p className="lead text-muted col-lg-8 mx-auto">
          SmartGen Fit analyzes a photo to classify your body type, then matches you with a Sri
          Lankan meal plan and workout routine — chosen from a curated database, never invented
          by AI.
        </p>
        <div className="d-flex justify-content-center gap-2 mt-4">
          {isAuthenticated ? (
            <Link to="/profile" className="btn btn-primary btn-lg">
              Go to your profile
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary btn-lg">
                Get started
              </Link>
              <Link to="/login" className="btn btn-outline-primary btn-lg">
                Log in
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="py-5">
        <h2 className="text-center mb-4">What you get</h2>
        <div className="row g-4">
          {FEATURES.map((feature) => (
            <div className="col-md-3 col-sm-6" key={feature.title}>
              <div className="card h-100 text-center">
                <div className="card-body">
                  <h3 className="h6">{feature.title}</h3>
                  <p className="card-text text-muted small">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="py-5 bg-light rounded-3 px-3">
        <div className="col-lg-8 mx-auto text-center">
          <h2>Our AI boundary</h2>
          <p className="text-muted mb-0">
            Our AI model performs one task only: classifying your body type from a photo. It
            never generates meal plans, workouts, calories, or health advice — every
            recommendation comes from a predefined, rule-based lookup that administrators
            manage directly. <Link to="/about">Learn more</Link>.
          </p>
        </div>
      </section>
    </div>
  )
}
