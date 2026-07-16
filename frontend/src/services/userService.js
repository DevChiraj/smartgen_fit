import apiClient from './apiClient'

export async function getMe() {
  const { data } = await apiClient.get('/v1/users/me')
  return data
}

export async function updateMe(payload) {
  const { data } = await apiClient.put('/v1/users/me', payload)
  return data
}

export async function uploadProfilePicture(file) {
  const formData = new FormData()
  formData.append('profile_picture', file)
  const { data } = await apiClient.post('/v1/users/me/profile-picture', formData)
  return data
}
