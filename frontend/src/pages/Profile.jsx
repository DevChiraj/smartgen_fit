import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { API_ORIGIN } from '../services/apiClient'
import { updateMe, uploadProfilePicture } from '../services/userService'
import { formatApiError } from '../utils/formatApiError'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    phone_number: user?.phone_number || '',
    height_cm: user?.height_cm || '',
    weight_kg: user?.weight_kg || '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setIsSaving(true)
    try {
      const payload = { ...form }
      if (!payload.phone_number) delete payload.phone_number
      if (!payload.height_cm) delete payload.height_cm
      if (!payload.weight_kg) delete payload.weight_kg

      await updateMe(payload)
      await refreshUser()
      setSuccess('Profile updated.')
    } catch (err) {
      setError(formatApiError(err, 'Could not update profile.'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setError('')
    setSuccess('')
    setIsUploading(true)
    try {
      await uploadProfilePicture(file)
      await refreshUser()
      setSuccess('Profile picture updated.')
    } catch (err) {
      setError(formatApiError(err, 'Could not upload profile picture.'))
    } finally {
      setIsUploading(false)
      event.target.value = ''
    }
  }

  if (!user) {
    return null
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <h1>My profile</h1>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="d-flex align-items-center gap-3 mb-4">
        {user.profile_picture_url ? (
          <img
            src={`${API_ORIGIN}${user.profile_picture_url}`}
            alt="Profile"
            width={80}
            height={80}
            style={{ objectFit: 'cover', borderRadius: '50%' }}
          />
        ) : (
          <div
            className="bg-secondary-subtle d-flex align-items-center justify-content-center text-center small"
            style={{ width: 80, height: 80, borderRadius: '50%' }}
          >
            No photo
          </div>
        )}
        <div>
          <label htmlFor="profile_picture" className="btn btn-outline-secondary btn-sm">
            {isUploading ? 'Uploading...' : 'Change photo'}
          </label>
          <input
            id="profile_picture"
            type="file"
            accept="image/png, image/jpeg, image/webp"
            onChange={handleFileChange}
            disabled={isUploading}
            hidden
          />
        </div>
      </div>

      <dl className="row">
        <dt className="col-sm-4">Username</dt>
        <dd className="col-sm-8">{user.username}</dd>
        <dt className="col-sm-4">Email</dt>
        <dd className="col-sm-8">{user.email}</dd>
        <dt className="col-sm-4">Gender</dt>
        <dd className="col-sm-8">{user.gender}</dd>
        <dt className="col-sm-4">Age</dt>
        <dd className="col-sm-8">{user.age}</dd>
      </dl>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label" htmlFor="full_name">
            Full name
          </label>
          <input
            id="full_name"
            name="full_name"
            className="form-control"
            value={form.full_name}
            onChange={handleChange}
          />
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="phone_number">
            Phone number
          </label>
          <input
            id="phone_number"
            name="phone_number"
            className="form-control"
            value={form.phone_number}
            onChange={handleChange}
          />
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="height_cm">
            Height (cm)
          </label>
          <input
            id="height_cm"
            name="height_cm"
            type="number"
            step="0.1"
            className="form-control"
            value={form.height_cm}
            onChange={handleChange}
          />
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="weight_kg">
            Weight (kg)
          </label>
          <input
            id="weight_kg"
            name="weight_kg"
            type="number"
            step="0.1"
            className="form-control"
            value={form.weight_kg}
            onChange={handleChange}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save changes'}
        </button>
      </form>
    </div>
  )
}
