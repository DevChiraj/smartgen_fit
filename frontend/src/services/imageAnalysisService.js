import apiClient from './apiClient'

export async function analyzeImage(file) {
  const formData = new FormData()
  formData.append('image', file)
  const { data } = await apiClient.post('/v1/image-analysis', formData)
  return data
}

export async function getAnalysisHistory() {
  const { data } = await apiClient.get('/v1/image-analysis/history')
  return data
}
