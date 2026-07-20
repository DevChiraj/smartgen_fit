import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/about', label: 'About' },
  { to: '/healthy-foods', label: 'Healthy Foods' },
  { to: '/workouts', label: 'Workouts' },
  { to: '/bmi-calculator', label: 'BMI Calculator' },
  { to: '/contact', label: 'Contact' },
]

function LogoMark() {
  return (
    <span
      className="d-inline-flex align-items-center justify-content-center rounded-3 me-2"
      style={{ width: 34, height: 34, background: 'var(--sgf-orange)', flexShrink: 0 }}
      aria-hidden="true"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
        <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z" />
      </svg>
    </span>
  )
}

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()
  const closeMenu = () => setIsOpen(false)

  return (
    <nav
      className="navbar navbar-expand-lg border-bottom"
      style={{ borderColor: 'var(--bs-border-color)' }}
    >
      <div className="container">
        <Link
          className="navbar-brand d-flex align-items-center fw-bold text-uppercase"
          to="/"
          onClick={closeMenu}
          style={{ fontFamily: 'var(--sgf-heading-font)', letterSpacing: '-0.01em' }}
        >
          <LogoMark />
          SmartGen<span className="text-accent">Fit</span>
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className={`collapse navbar-collapse ${isOpen ? 'show' : ''}`}>
          <ul className="navbar-nav mx-lg-auto mb-2 mb-lg-0 gap-lg-4">
            {NAV_LINKS.map((link) => (
              <li className="nav-item" key={link.to}>
                <NavLink className="nav-link" to={link.to} end={link.end} onClick={closeMenu}>
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
          <div className="d-flex gap-2">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="btn btn-outline-primary" onClick={closeMenu}>
                  {user?.username}
                </Link>
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => {
                    logout()
                    closeMenu()
                  }}
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="btn btn-outline-secondary text-uppercase fw-semibold"
                  onClick={closeMenu}
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="btn btn-primary rounded-pill px-3 text-uppercase fw-semibold"
                  onClick={closeMenu}
                >
                  Start Free
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
