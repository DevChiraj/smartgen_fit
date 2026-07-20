import apiClient from './apiClient'

// Users
export async function getUsers() {
  const { data } = await apiClient.get('/v1/admin/users')
  return data
}

export async function updateUser(userId, payload) {
  const { data } = await apiClient.put(`/v1/admin/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId) {
  await apiClient.delete(`/v1/admin/users/${userId}`)
}

// Foods
export async function createFood(payload) {
  const { data } = await apiClient.post('/v1/admin/foods', payload)
  return data
}

export async function updateFood(foodId, payload) {
  const { data } = await apiClient.put(`/v1/admin/foods/${foodId}`, payload)
  return data
}

export async function deleteFood(foodId) {
  await apiClient.delete(`/v1/admin/foods/${foodId}`)
}

// Exercises
export async function createExercise(payload) {
  const { data } = await apiClient.post('/v1/admin/exercises', payload)
  return data
}

export async function updateExercise(exerciseId, payload) {
  const { data } = await apiClient.put(`/v1/admin/exercises/${exerciseId}`, payload)
  return data
}

export async function deleteExercise(exerciseId) {
  await apiClient.delete(`/v1/admin/exercises/${exerciseId}`)
}

// Body types
export async function getBodyTypes() {
  const { data } = await apiClient.get('/v1/admin/body-types')
  return data
}

export async function updateBodyType(bodyTypeId, payload) {
  const { data } = await apiClient.put(`/v1/admin/body-types/${bodyTypeId}`, payload)
  return data
}

// BMI categories
export async function getBmiCategories() {
  const { data } = await apiClient.get('/v1/admin/bmi-categories')
  return data
}

export async function createBmiCategory(payload) {
  const { data } = await apiClient.post('/v1/admin/bmi-categories', payload)
  return data
}

export async function updateBmiCategory(bmiCategoryId, payload) {
  const { data } = await apiClient.put(`/v1/admin/bmi-categories/${bmiCategoryId}`, payload)
  return data
}

export async function deleteBmiCategory(bmiCategoryId) {
  await apiClient.delete(`/v1/admin/bmi-categories/${bmiCategoryId}`)
}
