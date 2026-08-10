import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import FloatingIcons from '../components/FloatingIcons'
import heroBg from '../assets/hero-bg.png'
import bodyTypeAnalysisImg from '../assets/feature-body-type-analysis.jpg'
import sriLankanMealPlansImg from '../assets/feature-sri-lankan-meal-plans.jpg'
import workoutPlansImg from '../assets/feature-workout-plans.jpg'
import bmiTrackingImg from '../assets/feature-bmi-tracking.png'
import aboutSectionImg from '../assets/about-section.jpg'

const FEATURES = [
  {
    title: 'Body Type Analysis',
    description: 'Image-based classification powered by a trained CNN.',
    image: bodyTypeAnalysisImg,
  },
  {
    title: 'Sri Lankan Meal Plans',
    description: 'Nutrition guidance built around local, familiar foods.',
    image: sriLankanMealPlansImg,
  },
  {
    title: 'Workout Plans',
    description: 'Routines matched to your body type, BMI, and age group.',
    image: workoutPlansImg,
  },
  {
    title: 'BMI Tracking',
    description: 'Calculate and track your BMI category over time.',
    image: bmiTrackingImg,
  },
]

const HOW_IT_WORKS = [
  {
    title: '1. Upload a photo',
    description: 'Share a full-body photo so we can analyze your body type.',
  },
  {
    title: '2. AI classifies your body type',
    description: 'A CNN model classifies you as Thin, Normal, or Overweight — nothing more.',
  },
  {
    title: '3. Get your personalized plan',
    description:
      'We look up a meal and workout plan matched to your body type, BMI, age group, and gender from our curated database.',
  },
]

export default function LandingPage() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  useEffect(() => {
    if (location.hash !== '#about') return
    const target = document.getElementById('about')
    if (!target) return
    // Wait a frame so the page has completed its own layout - especially
    // right after navigating here from another page, mid page-transition -
    // before measuring where to scroll to.
    const frame = requestAnimationFrame(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
    return () => cancelAnimationFrame(frame)
  }, [location.hash])

  return (
    <div>
      <section
        className="hero-section hero-section-full animate-in"
        style={{
          backgroundImage: `linear-gradient(rgba(10, 10, 12, 0.82), rgba(10, 10, 12, 0.93)), url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="container">
          <div className="row justify-content-center text-center">
            <div className="col-lg-9">
              <span className="hero-badge mb-4">
                <span className="dot" />
                AI-Powered Body Analysis
              </span>
              <h1 className="hero-display mb-4">
                Know your body.
                <br />
                <span className="text-accent">Match your plan.</span>
              </h1>
              <p className="lead text-secondary-emphasis mx-auto" style={{ maxWidth: 640 }}>
                SmartGen Fit analyzes a photo to classify your body type, then matches you with a
                Sri Lankan meal plan and workout routine — chosen from a curated database, never
                invented by AI.
              </p>
              <div className="d-flex flex-wrap justify-content-center gap-3 mt-4">
                {isAuthenticated ? (
                  <Link to="/dashboard" className="btn btn-primary btn-lg rounded-pill px-4">
                    Go to your dashboard
                  </Link>
                ) : (
                  <>
                    <Link to="/register" className="btn btn-primary btn-lg rounded-pill px-4">
                      Get started free
                    </Link>
                    <Link
                      to="/login"
                      className="btn btn-outline-secondary btn-lg rounded-pill px-4"
                    >
                      Log in
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-5 position-relative">
        <FloatingIcons />
        <div className="text-center mb-5">
          <span className="hero-badge mb-3">What you get</span>
          <h2 className="fw-bold mt-3">Everything matched to you</h2>
        </div>
        <div className="feature-gallery animate-in">
          {FEATURES.map((feature) => (
            <div
              className="feature-gallery-item"
              key={feature.title}
              style={{ backgroundImage: `url(${feature.image})` }}
            >
              <div className="feature-gallery-content">
                <h3 className="feature-gallery-title">{feature.title}</h3>
                <p className="feature-gallery-description">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="py-5" id="about">
        <div className="about-split animate-in">
          <div
            className="about-split-image"
            style={{ backgroundImage: `url(${aboutSectionImg})` }}
          />
          <span className="about-accent about-accent-1" aria-hidden="true" />
          <span className="about-accent about-accent-2" aria-hidden="true" />
          <span className="about-accent about-accent-3" aria-hidden="true" />
          <div className="about-split-content">
            <span className="about-subtitle">About Us</span>
            <h2 className="about-title">Welcome to SmartGen Fit</h2>
            <p className="about-paragraph">
              Welcome to SmartGen Fit, your ultimate personalized fitness companion. We believe
              that health and fitness are not one-size-fits-all, which is why we&apos;ve built a
              platform that adapts specifically to you.
            </p>
            <p className="about-paragraph">
              By combining advanced AI technology with tailored nutrition and exercise science,
              we provide a uniquely customized experience. From our CNN-powered body type
              analysis to authentic Sri Lankan meal plans, we ensure your fitness journey
              perfectly aligns with your lifestyle and local culture.
            </p>
            <p className="about-paragraph">
              Empower yourself with dynamic workout routines, accurate BMI tracking, and a
              supportive system designed to help you achieve your goals safely and effectively.
            </p>
            <Link to="/about" className="about-readmore">
              Read More..
            </Link>
          </div>
        </div>
      </section>

      <section className="py-5">
        <div className="text-center mb-5">
          <span className="hero-badge mb-3">The process</span>
          <h2 className="fw-bold mt-3">How it works</h2>
        </div>
        <div className="row g-4">
          {HOW_IT_WORKS.map((step) => (
            <div className="col-md-4 animate-in" key={step.title}>
              <div className="card card-interactive h-100">
                <div className="card-body">
                  <h3 className="h5 fw-bold">{step.title}</h3>
                  <p className="text-secondary small mb-0">{step.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
