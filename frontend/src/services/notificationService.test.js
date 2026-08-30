import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getSmartNotifications } from './notificationService'

vi.mock('./apiClient')

describe('notificationService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('getSmartNotifications gets /v1/notifications', async () => {
    apiClient.get.mockResolvedValue({ data: { notifications: [] } })

    const result = await getSmartNotifications()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/notifications')
    expect(result).toEqual({ notifications: [] })
  })
})
