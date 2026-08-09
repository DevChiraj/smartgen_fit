import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getMealLogHistory, logMeal } from './mealLogService'

vi.mock('./apiClient')

describe('mealLogService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('logMeal posts the payload to /v1/meal-logs', async () => {
    apiClient.post.mockResolvedValue({ data: { log: { log_id: 1 } } })

    const payload = { food_id: 3, meal_type: 'lunch' }
    const result = await logMeal(payload)

    expect(apiClient.post).toHaveBeenCalledWith('/v1/meal-logs', payload)
    expect(result).toEqual({ log: { log_id: 1 } })
  })

  it('getMealLogHistory gets /v1/meal-logs', async () => {
    apiClient.get.mockResolvedValue({ data: { history: [] } })

    const result = await getMealLogHistory()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/meal-logs')
    expect(result).toEqual({ history: [] })
  })
})
