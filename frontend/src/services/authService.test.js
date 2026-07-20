import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { fetchCurrentUser, login, register } from './authService'

vi.mock('./apiClient')

describe('authService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('register posts to /v1/auth/register and returns the response data', async () => {
    apiClient.post.mockResolvedValue({ data: { user: { username: 'jane' } } })

    const result = await register({ username: 'jane' })

    expect(apiClient.post).toHaveBeenCalledWith('/v1/auth/register', { username: 'jane' })
    expect(result).toEqual({ user: { username: 'jane' } })
  })

  it('login posts to /v1/auth/login', async () => {
    apiClient.post.mockResolvedValue({ data: { access_token: 'abc' } })

    const result = await login({ identifier: 'jane', password: 'secret' })

    expect(apiClient.post).toHaveBeenCalledWith('/v1/auth/login', {
      identifier: 'jane',
      password: 'secret',
    })
    expect(result).toEqual({ access_token: 'abc' })
  })

  it('fetchCurrentUser gets /v1/auth/me', async () => {
    apiClient.get.mockResolvedValue({ data: { user: { username: 'jane' } } })

    const result = await fetchCurrentUser()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/auth/me')
    expect(result).toEqual({ user: { username: 'jane' } })
  })
})
