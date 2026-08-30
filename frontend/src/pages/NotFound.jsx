import { Link } from 'react-router-dom'
import FloatingIcons from '../components/FloatingIcons'

export default function NotFound() {
  return (
    <div className="position-relative text-center py-5">
      <FloatingIcons />
      <span className="hero-badge mb-3">404</span>
      <h1 className="mt-3">Page not found</h1>
      <p className="lead text-muted mx-auto" style={{ maxWidth: 480 }}>
        The page you&apos;re looking for doesn&apos;t exist or may have moved.
      </p>
      <Link to="/" className="btn btn-primary rounded-pill px-4 mt-3">
        Back to Home
      </Link>
    </div>
  )
}
