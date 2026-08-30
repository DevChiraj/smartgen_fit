import apiClient from './apiClient'

export async function getWeeklyReport() {
  const { data } = await apiClient.get('/v1/reports/weekly')
  return data
}
