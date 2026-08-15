import axios from 'axios'
import { REFRESH_TOKEN_STORAGE_KEY, TOKEN_STORAGE_KEY } from '../utils/storageKeys'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '')

export const SESSION_EXPIRED_EVENT = 'smartgen_fit:session-expired'

const AUTH_ENDPOINTS_EXCLUDED_FROM_REFRESH = ['/auth/login', '/auth/register', '/auth/refresh']

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function clearSessionAndNotify() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
  localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
}

// Refresh calls use a bare axios request (not apiClient) because the refresh
// endpoint requires the *refresh* token as the bearer, while apiClient's own
// request interceptor always attaches the access token.
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
  if (!refreshToken) {
    throw new Error('No refresh token available')
  }
  const { data } = await axios.post(`${API_BASE_URL}/v1/auth/refresh`, null, {
    headers: { Authorization: `Bearer ${refreshToken}` },
  })
  localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token)
  return data.access_token
}

// Shared in-flight promise so concurrent 401s (e.g. a page firing several
// requests at once) trigger exactly one refresh call, not one per request.
let refreshPromise = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isExcludedEndpoint = AUTH_ENDPOINTS_EXCLUDED_FROM_REFRESH.some((path) =>
      config?.url?.includes(path),
    )
    const hasRefreshToken = Boolean(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY))

    if (response?.status !== 401 || !config || isExcludedEndpoint || !hasRefreshToken) {
      return Promise.reject(error)
    }

    if (config._retriedAfterRefresh) {
      // The retried request failed again even with a freshly issued access
      // token - treat this as a hard auth failure rather than looping.
      clearSessionAndNotify()
      return Promise.reject(error)
    }
    config._retriedAfterRefresh = true

    try {
      refreshPromise = refreshPromise || refreshAccessToken()
      const newAccessToken = await refreshPromise
      refreshPromise = null
      config.headers.Authorization = `Bearer ${newAccessToken}`
      return apiClient(config)
    } catch {
      refreshPromise = null
      clearSessionAndNotify()
      return Promise.reject(error)
    }
  },
)

export default apiClient
