import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getMe, updateMe, uploadProfilePicture } from './userService'

vi.mock('./apiClient')

describe('userService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('getMe gets /v1/users/me', async () => {
    apiClient.get.mockResolvedValue({ data: { user: { username: 'jane' } } })

    const result = await getMe()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/users/me')
    expect(result).toEqual({ user: { username: 'jane' } })
  })

  it('updateMe puts the payload to /v1/users/me', async () => {
    apiClient.put.mockResolvedValue({ data: { user: { full_name: 'Jane Doe' } } })

    const result = await updateMe({ full_name: 'Jane Doe' })

    expect(apiClient.put).toHaveBeenCalledWith('/v1/users/me', { full_name: 'Jane Doe' })
    expect(result).toEqual({ user: { full_name: 'Jane Doe' } })
  })

  it('uploadProfilePicture wraps the file in FormData under "profile_picture"', async () => {
    apiClient.post.mockResolvedValue({ data: { user: {} } })
    const file = new File(['data'], 'photo.png', { type: 'image/png' })

    await uploadProfilePicture(file)

    expect(apiClient.post).toHaveBeenCalledWith(
      '/v1/users/me/profile-picture',
      expect.any(FormData),
    )
    const formData = apiClient.post.mock.calls[0][1]
    expect(formData.get('profile_picture')).toBe(file)
  })
})
