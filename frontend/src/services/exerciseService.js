import apiClient from './apiClient'

export async function getExercises({ difficulty, q } = {}) {
  const { data } = await apiClient.get('/v1/exercises', { params: { difficulty, q } })
  return data
}

export async function getExerciseDifficulties() {
  const { data } = await apiClient.get('/v1/exercises/difficulties')
  return data
}

export async function getExerciseById(exerciseId) {
  const { data } = await apiClient.get(`/v1/exercises/${exerciseId}`)
  return data
}
