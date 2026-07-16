import { createContext, useContext, useMemo, useState } from 'react'
import PropTypes from 'prop-types'

const AuthContext = createContext(null)

const TOKEN_STORAGE_KEY = 'smartgen_fit_token'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY))

  const login = (newToken) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, newToken)
    setToken(newToken)
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setToken(null)
  }

  const value = useMemo(
    () => ({ token, isAuthenticated: Boolean(token), login, logout }),
    [token],
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
