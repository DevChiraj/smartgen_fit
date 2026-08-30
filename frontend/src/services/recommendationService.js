import apiClient from './apiClient'

export async function getLatestRecommendation() {
  const { data } = await apiClient.get('/v1/recommendations/latest')
  return data
}
