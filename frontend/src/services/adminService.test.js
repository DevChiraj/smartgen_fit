import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import * as adminService from './adminService'

vi.mock('./apiClient')

beforeEach(() => {
  vi.resetAllMocks()
})

describe('adminService: users', () => {
  it('getUsers gets /v1/admin/users', async () => {
    apiClient.get.mockResolvedValue({ data: { users: [] } })
    await adminService.getUsers()
    expect(apiClient.get).toHaveBeenCalledWith('/v1/admin/users')
  })

  it('updateUser puts to /v1/admin/users/:id', async () => {
    apiClient.put.mockResolvedValue({ data: { user: {} } })
    await adminService.updateUser(7, { role: 'admin' })
    expect(apiClient.put).toHaveBeenCalledWith('/v1/admin/users/7', { role: 'admin' })
  })

  it('deleteUser deletes /v1/admin/users/:id', async () => {
    apiClient.delete.mockResolvedValue({})
    await adminService.deleteUser(7)
    expect(apiClient.delete).toHaveBeenCalledWith('/v1/admin/users/7')
  })
})

describe('adminService: foods', () => {
  it('createFood posts to /v1/admin/foods', async () => {
    apiClient.post.mockResolvedValue({ data: { food: {} } })
    await adminService.createFood({ food_name: 'Rice' })
    expect(apiClient.post).toHaveBeenCalledWith('/v1/admin/foods', { food_name: 'Rice' })
  })

  it('updateFood puts to /v1/admin/foods/:id', async () => {
    apiClient.put.mockResolvedValue({ data: { food: {} } })
    await adminService.updateFood(3, { calories: 100 })
    expect(apiClient.put).toHaveBeenCalledWith('/v1/admin/foods/3', { calories: 100 })
  })

  it('deleteFood deletes /v1/admin/foods/:id', async () => {
    apiClient.delete.mockResolvedValue({})
    await adminService.deleteFood(3)
    expect(apiClient.delete).toHaveBeenCalledWith('/v1/admin/foods/3')
  })
})

describe('adminService: exercises', () => {
  it('createExercise posts to /v1/admin/exercises', async () => {
    apiClient.post.mockResolvedValue({ data: { exercise: {} } })
    await adminService.createExercise({ exercise_name: 'Squats' })
    expect(apiClient.post).toHaveBeenCalledWith('/v1/admin/exercises', {
      exercise_name: 'Squats',
    })
  })

  it('updateExercise puts to /v1/admin/exercises/:id', async () => {
    apiClient.put.mockResolvedValue({ data: { exercise: {} } })
    await adminService.updateExercise(4, { sets: 4 })
    expect(apiClient.put).toHaveBeenCalledWith('/v1/admin/exercises/4', { sets: 4 })
  })

  it('deleteExercise deletes /v1/admin/exercises/:id', async () => {
    apiClient.delete.mockResolvedValue({})
    await adminService.deleteExercise(4)
    expect(apiClient.delete).toHaveBeenCalledWith('/v1/admin/exercises/4')
  })
})

describe('adminService: body types', () => {
  it('getBodyTypes gets /v1/admin/body-types', async () => {
    apiClient.get.mockResolvedValue({ data: { body_types: [] } })
    await adminService.getBodyTypes()
    expect(apiClient.get).toHaveBeenCalledWith('/v1/admin/body-types')
  })

  it('updateBodyType puts to /v1/admin/body-types/:id', async () => {
    apiClient.put.mockResolvedValue({ data: { body_type: {} } })
    await adminService.updateBodyType(1, { description: 'new' })
    expect(apiClient.put).toHaveBeenCalledWith('/v1/admin/body-types/1', {
      description: 'new',
    })
  })
})

describe('adminService: BMI categories', () => {
  it('getBmiCategories gets /v1/admin/bmi-categories', async () => {
    apiClient.get.mockResolvedValue({ data: { bmi_categories: [] } })
    await adminService.getBmiCategories()
    expect(apiClient.get).toHaveBeenCalledWith('/v1/admin/bmi-categories')
  })

  it('createBmiCategory posts to /v1/admin/bmi-categories', async () => {
    apiClient.post.mockResolvedValue({ data: { bmi_category: {} } })
    await adminService.createBmiCategory({ category_name: 'Test' })
    expect(apiClient.post).toHaveBeenCalledWith('/v1/admin/bmi-categories', {
      category_name: 'Test',
    })
  })

  it('updateBmiCategory puts to /v1/admin/bmi-categories/:id', async () => {
    apiClient.put.mockResolvedValue({ data: { bmi_category: {} } })
    await adminService.updateBmiCategory(2, { max_bmi: 25 })
    expect(apiClient.put).toHaveBeenCalledWith('/v1/admin/bmi-categories/2', { max_bmi: 25 })
  })

  it('deleteBmiCategory deletes /v1/admin/bmi-categories/:id', async () => {
    apiClient.delete.mockResolvedValue({})
    await adminService.deleteBmiCategory(2)
    expect(apiClient.delete).toHaveBeenCalledWith('/v1/admin/bmi-categories/2')
  })
})
