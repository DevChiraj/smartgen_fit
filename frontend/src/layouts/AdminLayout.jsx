import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

export default function AdminLayout({ children }) {
  return (
    <div>
      <h1>Admin Panel</h1>
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <NavLink className="nav-link" to="/admin/users">
            Users
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/admin/foods">
            Foods
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/admin/exercises">
            Exercises
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/admin/body-types">
            Body Types
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink className="nav-link" to="/admin/bmi-categories">
            BMI Categories
          </NavLink>
        </li>
      </ul>
      {children}
    </div>
  )
}

AdminLayout.propTypes = {
  children: PropTypes.node.isRequired,
}
