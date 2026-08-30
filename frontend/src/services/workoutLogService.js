import apiClient from './apiClient'

export async function logWorkout(payload) {
  const { data } = await apiClient.post('/v1/workout-logs', payload)
  return data
}

export async function getWorkoutLogHistory() {
  const { data } = await apiClient.get('/v1/workout-logs')
  return data
}
