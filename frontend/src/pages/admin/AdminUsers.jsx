import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { createUser, deleteUser, getUsers, updateUser } from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

const EMPTY_FORM = {
  full_name: '',
  date_of_birth: '',
  gender: 'female',
  email: '',
  username: '',
  password: '',
  phone_number: '',
}

export default function AdminUsers() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyUserId, setBusyUserId] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [isSaving, setIsSaving] = useState(false)
  const [search, setSearch] = useState('')

  const fetchUsers = () => {
    return getUsers()
      .then((data) => setUsers(data.users))
      .catch((err) => setError(formatApiError(err, 'Could not load users.')))
  }

  useEffect(() => {
    fetchUsers().finally(() => setIsLoading(false))
  }, [])

  const openCreateForm = () => {
    setForm(EMPTY_FORM)
    setError('')
    setShowForm(true)
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')
    setIsSaving(true)
    try {
      const payload = { ...form }
      if (!payload.phone_number) delete payload.phone_number
      await createUser(payload)
      setShowForm(false)
      await fetchUsers()
    } catch (err) {
      setError(formatApiError(err, 'Could not create user.'))
    } finally {
      setIsSaving(false)
    }
  }

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

  const filteredUsers = users.filter((user) =>
    user.full_name.toLowerCase().includes(search.trim().toLowerCase()),
  )

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="d-flex flex-wrap align-items-center gap-2 mb-3">
        <button type="button" className="btn btn-primary" onClick={openCreateForm}>
          Add user
        </button>
        <input
          type="search"
          className="form-control"
          style={{ maxWidth: 280 }}
          placeholder="Search users by name..."
          aria-label="Search users by name"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      {filteredUsers.length === 0 ? (
        <p className="text-muted">No users match &quot;{search}&quot;.</p>
      ) : (
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
              {filteredUsers.map((user) => (
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
                      disabled={
                        busyUserId === user.user_id || user.user_id === currentUser?.user_id
                      }
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
      )}

      {showForm && (
        <div
          className="modal d-block"
          tabIndex={-1}
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowForm(false)}
        >
          <div
            className="modal-dialog modal-dialog-centered"
            onClick={(event) => event.stopPropagation()}
          >
            <form className="modal-content" onSubmit={handleCreate}>
              <div className="modal-header">
                <h2 className="modal-title h5">Add user</h2>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowForm(false)}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                <div className="row g-2">
                  <div className="col-12">
                    <label className="form-label" htmlFor="new_full_name">
                      Full name
                    </label>
                    <input
                      id="new_full_name"
                      className="form-control"
                      required
                      value={form.full_name}
                      onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="new_date_of_birth">
                      Date of birth
                    </label>
                    <input
                      id="new_date_of_birth"
                      type="date"
                      className="form-control"
                      required
                      value={form.date_of_birth}
                      onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="new_gender">
                      Gender
                    </label>
                    <select
                      id="new_gender"
                      className="form-select"
                      value={form.gender}
                      onChange={(e) => setForm({ ...form, gender: e.target.value })}
                    >
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="col-12">
                    <label className="form-label" htmlFor="new_email">
                      Email
                    </label>
                    <input
                      id="new_email"
                      type="email"
                      className="form-control"
                      required
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="new_username">
                      Username
                    </label>
                    <input
                      id="new_username"
                      className="form-control"
                      required
                      minLength={3}
                      maxLength={50}
                      pattern="[a-zA-Z0-9_]+"
                      title="Letters, numbers, and underscores only"
                      value={form.username}
                      onChange={(e) => setForm({ ...form, username: e.target.value })}
                    />
                  </div>
                  <div className="col-6">
                    <label className="form-label" htmlFor="new_password">
                      Password
                    </label>
                    <input
                      id="new_password"
                      type="password"
                      className="form-control"
                      required
                      minLength={8}
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                    />
                  </div>
                  <div className="col-12">
                    <label className="form-label" htmlFor="new_phone_number">
                      Phone number (optional)
                    </label>
                    <input
                      id="new_phone_number"
                      className="form-control"
                      value={form.phone_number}
                      onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={isSaving}>
                  {isSaving ? 'Creating...' : 'Create user'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
