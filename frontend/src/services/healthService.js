import apiClient from './apiClient'

export async function getApiHealth() {
  const { data } = await apiClient.get('/health')
  return data
}

export async function getDbHealth() {
  const { data } = await apiClient.get('/health/db')
  return data
}
