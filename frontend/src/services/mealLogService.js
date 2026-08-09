import apiClient from './apiClient'

export async function logMeal(payload) {
  const { data } = await apiClient.post('/v1/meal-logs', payload)
  return data
}

export async function getMealLogHistory() {
  const { data } = await apiClient.get('/v1/meal-logs')
  return data
}
