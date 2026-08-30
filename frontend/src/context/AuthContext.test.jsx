import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'
import { fetchCurrentUser } from '../services/authService'
import { REFRESH_TOKEN_STORAGE_KEY, TOKEN_STORAGE_KEY } from '../utils/storageKeys'

vi.mock('../services/authService')

function wrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

beforeEach(() => {
  vi.resetAllMocks()
  localStorage.clear()
})

describe('useAuth', () => {
  it('throws when used outside an AuthProvider', () => {
    const { result } = renderHook(() => {
      try {
        return useAuth()
      } catch (error) {
        return error
      }
    })
    expect(result.current).toBeInstanceOf(Error)
    expect(result.current.message).toMatch(/must be used within an AuthProvider/)
  })
})

describe('AuthProvider: no stored token', () => {
  it('starts unauthenticated and not loading', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.user).toBeNull()
    expect(fetchCurrentUser).not.toHaveBeenCalled()
  })
})

describe('AuthProvider: token already stored', () => {
  it('fetches the current user and stops loading on success', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'existing-token')
    fetchCurrentUser.mockResolvedValue({ user: { username: 'jane' } })

    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.isLoading).toBe(true)

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.user).toEqual({ username: 'jane' })
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('clears the stored token and logs out when the token is rejected', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'stale-token')
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'stale-refresh')
    fetchCurrentUser.mockRejectedValue(new Error('401'))

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
    expect(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBeNull()
  })
})

describe('login / logout', () => {
  // login() changes `token` state, which re-triggers the same effect that
  // fetches the current user on mount - so a real /auth/me call follows
  // every login even though the login response already carried the user.
  beforeEach(() => {
    fetchCurrentUser.mockResolvedValue({ user: { username: 'jane' } })
  })

  it('login stores tokens and updates state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    act(() => {
      result.current.login({
        access_token: 'access-1',
        refresh_token: 'refresh-1',
        user: { username: 'jane' },
      })
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual({ username: 'jane' })
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe('access-1')
    expect(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBe('refresh-1')
  })

  it('logout clears tokens and resets state', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    act(() => {
      result.current.login({
        access_token: 'access-1',
        refresh_token: 'refresh-1',
        user: { username: 'jane' },
      })
    })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    act(() => {
      result.current.logout()
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
    expect(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBeNull()
  })
})

describe('refreshUser', () => {
  it('re-fetches and updates the current user', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'existing-token')
    fetchCurrentUser.mockResolvedValue({ user: { username: 'jane', role: 'user' } })
    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    fetchCurrentUser.mockResolvedValue({ user: { username: 'jane', role: 'admin' } })
    await act(async () => {
      await result.current.refreshUser()
    })

    expect(result.current.user).toEqual({ username: 'jane', role: 'admin' })
  })
})
