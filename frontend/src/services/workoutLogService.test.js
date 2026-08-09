import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getWorkoutLogHistory, logWorkout } from './workoutLogService'

vi.mock('./apiClient')

describe('workoutLogService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('logWorkout posts the payload to /v1/workout-logs', async () => {
    apiClient.post.mockResolvedValue({ data: { log: { log_id: 1 } } })

    const payload = { exercise_id: 3, duration_minutes: 20 }
    const result = await logWorkout(payload)

    expect(apiClient.post).toHaveBeenCalledWith('/v1/workout-logs', payload)
    expect(result).toEqual({ log: { log_id: 1 } })
  })

  it('getWorkoutLogHistory gets /v1/workout-logs', async () => {
    apiClient.get.mockResolvedValue({ data: { history: [] } })

    const result = await getWorkoutLogHistory()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/workout-logs')
    expect(result).toEqual({ history: [] })
  })
})
