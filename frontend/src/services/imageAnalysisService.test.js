import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { analyzeImage, getAnalysisHistory } from './imageAnalysisService'

vi.mock('./apiClient')

describe('imageAnalysisService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('analyzeImage wraps the file in FormData under "image"', async () => {
    apiClient.post.mockResolvedValue({ data: { analysis: {} } })
    const file = new File(['data'], 'body.png', { type: 'image/png' })

    await analyzeImage(file)

    expect(apiClient.post).toHaveBeenCalledWith('/v1/image-analysis', expect.any(FormData))
    const formData = apiClient.post.mock.calls[0][1]
    expect(formData.get('image')).toBe(file)
  })

  it('getAnalysisHistory gets /v1/image-analysis/history', async () => {
    apiClient.get.mockResolvedValue({ data: { history: [] } })

    const result = await getAnalysisHistory()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/image-analysis/history')
    expect(result).toEqual({ history: [] })
  })
})
