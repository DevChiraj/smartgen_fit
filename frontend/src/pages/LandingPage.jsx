import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  {
    title: 'Body Type Analysis',
    description: 'Image-based classification powered by a trained CNN.',
    icon: (
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
      </svg>
    ),
  },
  {
    title: 'Sri Lankan Meal Plans',
    description: 'Nutrition guidance built around local, familiar foods.',
    icon: (
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M18 8a6 6 0 0 1-12 0" />
        <path d="M4 8h16l-1.5 12a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2L4 8Z" />
      </svg>
    ),
  },
  {
    title: 'Workout Plans',
    description: 'Routines matched to your body type, BMI, and age group.',
    icon: (
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M6.5 6.5 17.5 17.5" />
        <path d="m17 5 2 2M5 17l2 2M4 10l6-6M20 14l-6 6" />
      </svg>
    ),
  },
  {
    title: 'BMI Tracking',
    description: 'Calculate and track your BMI category over time.',
    icon: (
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M3 3v18h18" />
        <path d="M7 15l4-4 3 3 5-6" />
      </svg>
    ),
  },
]

const PIPELINE = [
  { label: 'Upload a body photo', done: true },
  { label: 'AI classifies your body type', done: true },
  { label: 'Matched to a real meal + workout plan', done: false },
]

export default function LandingPage() {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      <section className="py-5">
        <div className="row align-items-center g-5">
          <div className="col-lg-7">
            <span className="hero-badge mb-4">
              <span className="dot" />
              AI-Powered Body Analysis
            </span>
            <h1 className="hero-display mb-4">
              Know your body.
              <br />
              <span className="text-accent">Match your plan.</span>
            </h1>
            <p className="lead text-secondary-emphasis col-lg-10">
              SmartGen Fit analyzes a photo to classify your body type, then matches you with a Sri
              Lankan meal plan and workout routine — chosen from a curated database, never invented
              by AI.
            </p>
            <div className="d-flex flex-wrap gap-3 mt-4">
              {isAuthenticated ? (
                <Link to="/dashboard" className="btn btn-primary btn-lg rounded-pill px-4">
                  Go to your dashboard
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn btn-primary btn-lg rounded-pill px-4">
                    Get started free
                  </Link>
                  <Link to="/login" className="btn btn-outline-secondary btn-lg rounded-pill px-4">
                    Log in
                  </Link>
                </>
              )}
            </div>
          </div>

          <div className="col-lg-5">
            <div className="card p-4 shadow-lg">
              <div className="d-flex align-items-center gap-3 mb-4">
                <span className="icon-badge">
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z" />
                  </svg>
                </span>
                <div>
                  <div className="fw-bold">Your Analysis Pipeline</div>
                  <div className="text-secondary small">Classify → Match → Recommend</div>
                </div>
              </div>
              <ul className="list-unstyled mb-4">
                {PIPELINE.map((step) => (
                  <li key={step.label} className="d-flex align-items-center gap-3 py-2">
                    <span
                      className={`d-inline-flex align-items-center justify-content-center rounded-circle ${
                        step.done ? 'bg-success' : 'border border-secondary'
                      }`}
                      style={{ width: 24, height: 24, flexShrink: 0 }}
                    >
                      {step.done && (
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="white"
                          strokeWidth="3"
                        >
                          <path d="M20 6 9 17l-5-5" />
                        </svg>
                      )}
                    </span>
                    <span className={step.done ? '' : 'text-secondary'}>{step.label}</span>
                  </li>
                ))}
              </ul>
              <div className="progress" style={{ height: 6 }}>
                <div className="progress-bar bg-success" style={{ width: '66%' }} />
              </div>
              <p className="text-secondary small mt-2 mb-0">
                2 of 3 steps &mdash; matched plan next
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-5">
        <div className="text-center mb-5">
          <span className="hero-badge mb-3">What you get</span>
          <h2 className="fw-bold mt-3">Everything matched to you</h2>
        </div>
        <div className="row g-4">
          {FEATURES.map((feature) => (
            <div className="col-md-3 col-sm-6" key={feature.title}>
              <div className="card feature-card h-100">
                <div className="card-body">
                  <span className="icon-badge mb-3">{feature.icon}</span>
                  <h3 className="h6 fw-bold">{feature.title}</h3>
                  <p className="card-text text-secondary small mb-0">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="py-5">
        <div className="card col-lg-9 mx-auto p-4 p-md-5 text-center">
          <h2 className="fw-bold">Our AI boundary</h2>
          <p className="text-secondary mb-0">
            Our AI model performs one task only: classifying your body type from a photo. It never
            generates meal plans, workouts, calories, or health advice — every recommendation comes
            from a predefined, rule-based lookup that administrators manage directly.{' '}
            <Link to="/about">Learn more</Link>.
          </p>
        </div>
      </section>
    </div>
  )
}
