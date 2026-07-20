import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { deleteUser, getUsers, updateUser } from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

export default function AdminUsers() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyUserId, setBusyUserId] = useState(null)

  const fetchUsers = () => {
    return getUsers()
      .then((data) => setUsers(data.users))
      .catch((err) => setError(formatApiError(err, 'Could not load users.')))
  }

  useEffect(() => {
    fetchUsers().finally(() => setIsLoading(false))
  }, [])

  const handleRoleChange = async (userId, role) => {
    setBusyUserId(userId)
    setError('')
    try {
      await updateUser(userId, { role })
      await fetchUsers()
    } catch (err) {
      setError(formatApiError(err, 'Could not update role.'))
    } finally {
      setBusyUserId(null)
    }
  }

  const handleDelete = async (userId, username) => {
    if (!window.confirm(`Delete user "${username}"? This cannot be undone.`)) return
    setBusyUserId(userId)
    setError('')
    try {
      await deleteUser(userId)
      await fetchUsers()
    } catch (err) {
      setError(formatApiError(err, 'Could not delete user.'))
    } finally {
      setBusyUserId(null)
    }
  }

  if (isLoading) return <p className="text-muted">Loading...</p>

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>Username</th>
              <th>Full name</th>
              <th>Email</th>
              <th>Age</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.user_id}>
                <td>{user.username}</td>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>{user.age}</td>
                <td>
                  <select
                    className="form-select form-select-sm"
                    style={{ width: 120 }}
                    value={user.role}
                    disabled={busyUserId === user.user_id}
                    onChange={(event) => handleRoleChange(user.user_id, event.target.value)}
                  >
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                  </select>
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    disabled={busyUserId === user.user_id || user.user_id === currentUser?.user_id}
                    onClick={() => handleDelete(user.user_id, user.username)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
