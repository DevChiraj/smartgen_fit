import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { ThemeProvider, useTheme } from './ThemeContext'
import { THEME_STORAGE_KEY } from '../utils/storageKeys'

function wrapper({ children }) {
  return <ThemeProvider>{children}</ThemeProvider>
}

beforeEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-bs-theme')
})

describe('useTheme', () => {
  it('throws when used outside a ThemeProvider', () => {
    const { result } = renderHook(() => {
      try {
        return useTheme()
      } catch (error) {
        return error
      }
    })
    expect(result.current).toBeInstanceOf(Error)
    expect(result.current.message).toMatch(/must be used within a ThemeProvider/)
  })
})

describe('ThemeProvider', () => {
  it('defaults to dark when nothing is stored', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })

    expect(result.current.theme).toBe('dark')
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('dark')
  })

  it('reads a previously stored light preference', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'light')

    const { result } = renderHook(() => useTheme(), { wrapper })

    expect(result.current.theme).toBe('light')
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('light')
  })

  it('toggleTheme flips the theme and persists it', () => {
    const { result } = renderHook(() => useTheme(), { wrapper })

    act(() => result.current.toggleTheme())
    expect(result.current.theme).toBe('light')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('light')

    act(() => result.current.toggleTheme())
    expect(result.current.theme).toBe('dark')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark')
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('dark')
  })
})
