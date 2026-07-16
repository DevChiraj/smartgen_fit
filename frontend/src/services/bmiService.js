import apiClient from './apiClient'

export async function calculateBmi(payload) {
  const { data } = await apiClient.post('/v1/bmi/calculate', payload)
  return data
}
