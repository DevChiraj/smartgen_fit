import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getExerciseById, getExerciseDifficulties, getExercises } from './exerciseService'

vi.mock('./apiClient')

describe('exerciseService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('getExercises passes difficulty and q as query params', async () => {
    apiClient.get.mockResolvedValue({ data: { exercises: [] } })

    await getExercises({ difficulty: 'Beginner', q: 'squat' })

    expect(apiClient.get).toHaveBeenCalledWith('/v1/exercises', {
      params: { difficulty: 'Beginner', q: 'squat' },
    })
  })

  it('getExerciseDifficulties gets /v1/exercises/difficulties', async () => {
    apiClient.get.mockResolvedValue({ data: { difficulties: ['Beginner'] } })

    const result = await getExerciseDifficulties()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/exercises/difficulties')
    expect(result).toEqual({ difficulties: ['Beginner'] })
  })

  it('getExerciseById gets /v1/exercises/:id', async () => {
    apiClient.get.mockResolvedValue({ data: { exercise: { exercise_id: 3 } } })

    await getExerciseById(3)

    expect(apiClient.get).toHaveBeenCalledWith('/v1/exercises/3')
  })
})
