import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

export default function ComingSoon({ title, description }) {
  return (
    <div className="text-center py-5">
      <h1>{title}</h1>
      <p className="text-muted col-lg-6 mx-auto">{description}</p>
      <p className="fst-italic">This section is under construction and will arrive in a future update.</p>
      <Link to="/" className="btn btn-primary mt-3">
        Back to home
      </Link>
    </div>
  )
}

ComingSoon.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
}
