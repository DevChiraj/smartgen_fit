import { useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { Dumbbell, Moon, Sun } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import NotificationBell from './NotificationBell'

const NAV_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/#about', label: 'About', anchorId: 'about' },
  { to: '/healthy-foods', label: 'Healthy Foods' },
  { to: '/workouts', label: 'Workouts' },
  { to: '/bmi-calculator', label: 'BMI Calculator' },
  { to: '/analyze', label: '[ SCANNER ]' },
  { to: '/contact', label: 'Contact' },
]

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const closeMenu = () => setIsOpen(false)

  const handleAnchorClick = (event, anchorId) => {
    closeMenu()
    if (location.pathname === '/') {
      // Already on the Home page - scroll directly rather than round-tripping
      // through a navigation, since a hash-only URL change wouldn't remount
      // the page for LandingPage's own scroll effect to react to.
      event.preventDefault()
      document.getElementById(anchorId)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    // Elsewhere: let the Link navigate to `/#anchorId` normally; LandingPage's
    // own mount effect picks up the hash and smooth-scrolls once it renders.
  }

  return (
    <nav
      className={`navbar navbar-expand-lg ${theme === 'dark' ? 'navbar-dark' : 'navbar-light'} border-bottom`}
    >
      <div className="container">
        <Link
          className="navbar-brand fw-bold d-flex align-items-center gap-2"
          to="/"
          onClick={closeMenu}
        >
          <span className="navbar-brand-icon">
            <Dumbbell size={17} strokeWidth={2.5} />
          </span>
          SmartGen Fit
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
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {NAV_LINKS.map((link) =>
              link.anchorId ? (
                <li className="nav-item" key={link.to}>
                  <Link
                    className="nav-link"
                    to={link.to}
                    onClick={(event) => handleAnchorClick(event, link.anchorId)}
                  >
                    {link.label}
                  </Link>
                </li>
              ) : (
                <li className="nav-item" key={link.to}>
                  <NavLink className="nav-link" to={link.to} end={link.end} onClick={closeMenu}>
                    {link.label}
                  </NavLink>
                </li>
              ),
            )}
          </ul>
          <div className="d-flex align-items-center gap-2">
            <button
              type="button"
              className="btn btn-outline-secondary theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            {isAuthenticated ? (
              <>
                <NotificationBell />
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
                <Link to="/login" className="btn btn-outline-primary" onClick={closeMenu}>
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary" onClick={closeMenu}>
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
