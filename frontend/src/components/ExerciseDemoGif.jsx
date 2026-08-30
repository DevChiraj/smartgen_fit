import { useState } from 'react'
import PropTypes from 'prop-types'

export default function ExerciseDemoGif({ exerciseId, alt, className }) {
  const [failed, setFailed] = useState(false)

  if (failed) {
    return (
      <div className={`exercise-demo-gif-placeholder ${className || ''}`}>
        <span className="text-muted small">No demo available yet</span>
      </div>
    )
  }

  return (
    <img
      src={`/exercise-gifs/${exerciseId}.gif`}
      alt={alt}
      className={`exercise-demo-gif ${className || ''}`}
      onError={() => setFailed(true)}
    />
  )
}

ExerciseDemoGif.propTypes = {
  exerciseId: PropTypes.number.isRequired,
  alt: PropTypes.string.isRequired,
  className: PropTypes.string,
}
