import { afterEach, describe, expect, it } from 'vitest'
import apiClient, { API_ORIGIN } from './apiClient'
import { TOKEN_STORAGE_KEY } from '../utils/storageKeys'

function runRequestInterceptor(config) {
  const fulfilled = apiClient.interceptors.request.handlers[0].fulfilled
  return fulfilled(config)
}

describe('apiClient request interceptor', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('attaches a Bearer token from localStorage when one is present', () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'my-token')

    const result = runRequestInterceptor({ headers: {} })

    expect(result.headers.Authorization).toBe('Bearer my-token')
  })

  it('does not attach an Authorization header when no token is stored', () => {
    const result = runRequestInterceptor({ headers: {} })

    expect(result.headers.Authorization).toBeUndefined()
  })
})

describe('API_ORIGIN', () => {
  it('strips the /api suffix from the base URL', () => {
    expect(API_ORIGIN.endsWith('/api')).toBe(false)
  })
})
