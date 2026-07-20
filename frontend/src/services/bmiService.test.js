import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { calculateBmi } from './bmiService'

vi.mock('./apiClient')

describe('bmiService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('posts height/weight to /v1/bmi/calculate', async () => {
    apiClient.post.mockResolvedValue({ data: { bmi: '22.5', category: { category_name: 'Normal weight' } } })

    const result = await calculateBmi({ height_cm: 170, weight_kg: 65 })

    expect(apiClient.post).toHaveBeenCalledWith('/v1/bmi/calculate', { height_cm: 170, weight_kg: 65 })
    expect(result.bmi).toBe('22.5')
  })
})
