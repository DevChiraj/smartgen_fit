import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getFoodById, getFoodCategories, getFoods } from './foodService'

vi.mock('./apiClient')

describe('foodService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('getFoods passes category and q as query params', async () => {
    apiClient.get.mockResolvedValue({ data: { foods: [] } })

    await getFoods({ category: 'Fruit', q: 'rice' })

    expect(apiClient.get).toHaveBeenCalledWith('/v1/foods', {
      params: { category: 'Fruit', q: 'rice' },
    })
  })

  it('getFoods works with no filters', async () => {
    apiClient.get.mockResolvedValue({ data: { foods: [] } })

    await getFoods()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/foods', {
      params: { category: undefined, q: undefined },
    })
  })

  it('getFoodCategories gets /v1/foods/categories', async () => {
    apiClient.get.mockResolvedValue({ data: { categories: ['Grain'] } })

    const result = await getFoodCategories()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/foods/categories')
    expect(result).toEqual({ categories: ['Grain'] })
  })

  it('getFoodById gets /v1/foods/:id', async () => {
    apiClient.get.mockResolvedValue({ data: { food: { food_id: 5 } } })

    await getFoodById(5)

    expect(apiClient.get).toHaveBeenCalledWith('/v1/foods/5')
  })
})
