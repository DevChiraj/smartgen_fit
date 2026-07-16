import apiClient from './apiClient'

export async function register(payload) {
  const { data } = await apiClient.post('/v1/auth/register', payload)
  return data
}

export async function login(payload) {
  const { data } = await apiClient.post('/v1/auth/login', payload)
  return data
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get('/v1/auth/me')
  return data
}
