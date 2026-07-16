import PropTypes from 'prop-types'

const STATUS_VARIANT = {
  ok: 'success',
  error: 'danger',
  checking: 'secondary',
}

export default function HealthStatusCard({ label, status }) {
  const variant = STATUS_VARIANT[status] ?? 'secondary'

  return (
    <div className="d-flex align-items-center gap-2 mb-2">
      <span className={`badge text-bg-${variant}`}>{status}</span>
      <span>{label}</span>
    </div>
  )
}

HealthStatusCard.propTypes = {
  label: PropTypes.string.isRequired,
  status: PropTypes.string.isRequired,
}
