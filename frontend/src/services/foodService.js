import apiClient from './apiClient'

export async function getFoods({ category, q } = {}) {
  const { data } = await apiClient.get('/v1/foods', { params: { category, q } })
  return data
}

export async function getFoodCategories() {
  const { data } = await apiClient.get('/v1/foods/categories')
  return data
}

export async function getFoodById(foodId) {
  const { data } = await apiClient.get(`/v1/foods/${foodId}`)
  return data
}
