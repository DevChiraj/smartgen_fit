import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import apiClient, { API_ORIGIN, SESSION_EXPIRED_EVENT } from './apiClient'
import { REFRESH_TOKEN_STORAGE_KEY, TOKEN_STORAGE_KEY } from '../utils/storageKeys'

// Real axios instances are callable (`apiClient(config)` retries a request)
// and carry `.interceptors`, so the mock instance must be built entirely
// inside the factory (no outer-scope reference) to avoid a TDZ error from
// vi.mock's hoisting.
vi.mock('axios', () => {
  const instance = Object.assign(vi.fn(), {
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  })
  return {
    default: {
      create: vi.fn(() => instance),
      post: vi.fn(),
    },
  }
})

// apiClient.js calls axios.create() once at module load time, so the
// instance it wired its interceptors onto is whatever the mocked create()
// returned on that first call.
const mockInstance = axios.create.mock.results[0].value
mockInstance.mockResolvedValue({ data: 'retried' })

const requestInterceptor = mockInstance.interceptors.request.use.mock.calls[0][0]
const [, responseErrorInterceptor] = mockInstance.interceptors.response.use.mock.calls[0]

function make401Error(url, overrides = {}) {
  return {
    response: { status: 401 },
    config: { url, headers: {}, ...overrides },
  }
}

beforeEach(() => {
  localStorage.clear()
  axios.post.mockReset()
  mockInstance.mockClear()
})

describe('request interceptor', () => {
  it('attaches the access token when present', () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'access-1')
    const config = requestInterceptor({ headers: {} })
    expect(config.headers.Authorization).toBe('Bearer access-1')
  })

  it('leaves the Authorization header untouched when no token is stored', () => {
    const config = requestInterceptor({ headers: {} })
    expect(config.headers.Authorization).toBeUndefined()
  })
})

describe('response interceptor: non-401 or non-retryable errors', () => {
  it('passes through non-401 errors unchanged', async () => {
    const error = { response: { status: 500 }, config: { url: '/v1/foods' } }
    await expect(responseErrorInterceptor(error)).rejects.toBe(error)
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('does not attempt a refresh for the login endpoint', async () => {
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'refresh-1')
    const error = make401Error('/v1/auth/login')
    await expect(responseErrorInterceptor(error)).rejects.toBe(error)
    expect(axios.post).not.toHaveBeenCalled()
  })

  it('does not attempt a refresh when no refresh token is stored', async () => {
    const error = make401Error('/v1/meal-plan')
    await expect(responseErrorInterceptor(error)).rejects.toBe(error)
    expect(axios.post).not.toHaveBeenCalled()
  })
})

describe('response interceptor: refresh flow', () => {
  it('refreshes the access token and retries the original request once', async () => {
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'refresh-1')
    axios.post.mockResolvedValue({ data: { access_token: 'access-new' } })

    const error = make401Error('/v1/meal-plan')
    await responseErrorInterceptor(error).catch(() => {})

    expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/v1/auth/refresh'), null, {
      headers: { Authorization: 'Bearer refresh-1' },
    })
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe('access-new')
    expect(error.config.headers.Authorization).toBe('Bearer access-new')
    expect(error.config._retriedAfterRefresh).toBe(true)
  })

  it('shares one in-flight refresh across concurrent 401s', async () => {
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'refresh-1')
    let resolveRefresh
    axios.post.mockReturnValue(
      new Promise((resolve) => {
        resolveRefresh = resolve
      }),
    )

    const errorA = make401Error('/v1/meal-plan')
    const errorB = make401Error('/v1/workout-tracker')
    const callA = responseErrorInterceptor(errorA).catch(() => {})
    const callB = responseErrorInterceptor(errorB).catch(() => {})

    resolveRefresh({ data: { access_token: 'access-new' } })
    await Promise.all([callA, callB])

    expect(axios.post).toHaveBeenCalledTimes(1)
  })

  it('clears the session and dispatches the expired event when refresh itself fails', async () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'access-old')
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'refresh-1')
    axios.post.mockRejectedValue(new Error('refresh token expired'))
    const listener = vi.fn()
    window.addEventListener(SESSION_EXPIRED_EVENT, listener)

    const error = make401Error('/v1/meal-plan')
    await expect(responseErrorInterceptor(error)).rejects.toBe(error)

    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
    expect(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBeNull()
    expect(listener).toHaveBeenCalledOnce()
    window.removeEventListener(SESSION_EXPIRED_EVENT, listener)
  })

  it('clears the session when the retried request 401s again instead of looping', async () => {
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'refresh-1')
    const listener = vi.fn()
    window.addEventListener(SESSION_EXPIRED_EVENT, listener)

    const error = make401Error('/v1/meal-plan', { _retriedAfterRefresh: true })
    await expect(responseErrorInterceptor(error)).rejects.toBe(error)

    expect(axios.post).not.toHaveBeenCalled()
    expect(listener).toHaveBeenCalledOnce()
    window.removeEventListener(SESSION_EXPIRED_EVENT, listener)
  })
})

describe('apiClient export', () => {
  it('exports the created axios instance', () => {
    expect(apiClient).toBe(mockInstance)
  })
})

describe('API_ORIGIN', () => {
  it('strips the /api suffix from the base URL', () => {
    expect(API_ORIGIN.endsWith('/api')).toBe(false)
  })
})
