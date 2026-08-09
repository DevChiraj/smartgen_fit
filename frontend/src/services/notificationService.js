import apiClient from './apiClient'

export async function getSmartNotifications() {
  const { data } = await apiClient.get('/v1/notifications')
  return data
}
