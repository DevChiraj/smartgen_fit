import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import PropTypes from 'prop-types'
import { fetchCurrentUser } from '../services/authService'
import { SESSION_EXPIRED_EVENT } from '../services/apiClient'
import { REFRESH_TOKEN_STORAGE_KEY, TOKEN_STORAGE_KEY } from '../utils/storageKeys'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY))
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      return
    }
    fetchCurrentUser()
      .then((data) => setUser(data.user))
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY)
        localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
        setToken(null)
      })
      .finally(() => setIsLoading(false))
  }, [token])

  // apiClient dispatches this once it's tried (and failed) to silently
  // refresh an expired session, so the app's auth state - and therefore
  // ProtectedRoute's redirect - stays in sync without a page reload.
  useEffect(() => {
    const handleSessionExpired = () => {
      setToken(null)
      setUser(null)
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
  }, [])

  const login = (authResponse) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, authResponse.access_token)
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, authResponse.refresh_token)
    setToken(authResponse.access_token)
    setUser(authResponse.user)
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
    setToken(null)
    setUser(null)
  }

  const refreshUser = async () => {
    const data = await fetchCurrentUser()
    setUser(data.user)
    return data.user
  }

  const value = useMemo(
    () => ({ token, user, isAuthenticated: Boolean(token), isLoading, login, logout, refreshUser }),
    [token, user, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
