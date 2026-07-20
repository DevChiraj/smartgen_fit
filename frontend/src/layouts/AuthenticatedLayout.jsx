import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

export default function AuthenticatedLayout({ children }) {
  return (
    <div>
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <NavLink className="nav-link" to="/dashboard" end>
            Dashboard
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/profile">
            My Profile
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/analyze">
            Analyze Photo
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/meal-plan">
            My Meal Plan
          </NavLink>
        </li>
      </ul>
      {children}
    </div>
  )
}

AuthenticatedLayout.propTypes = {
  children: PropTypes.node.isRequired,
}
