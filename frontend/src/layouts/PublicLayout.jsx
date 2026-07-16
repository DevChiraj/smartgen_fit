import PropTypes from 'prop-types'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'

export default function PublicLayout({ children }) {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />
      <main className="container py-4 flex-grow-1">{children}</main>
      <Footer />
    </div>
  )
}

PublicLayout.propTypes = {
  children: PropTypes.node.isRequired,
}
