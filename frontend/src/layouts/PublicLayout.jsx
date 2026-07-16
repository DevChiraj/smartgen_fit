import PropTypes from 'prop-types'

export default function PublicLayout({ children }) {
  return (
    <div className="container py-4">
      <main>{children}</main>
    </div>
  )
}

PublicLayout.propTypes = {
  children: PropTypes.node.isRequired,
}
