import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getLatestRecommendation } from './recommendationService'

vi.mock('./apiClient')

describe('recommendationService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('gets /v1/recommendations/latest', async () => {
    apiClient.get.mockResolvedValue({ data: { recommendation: null } })

    const result = await getLatestRecommendation()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/recommendations/latest')
    expect(result).toEqual({ recommendation: null })
  })
})
