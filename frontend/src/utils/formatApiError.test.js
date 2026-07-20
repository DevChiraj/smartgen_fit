import { describe, expect, it } from 'vitest'
import { formatApiError } from './formatApiError'

describe('formatApiError', () => {
  it('returns the fallback when there is no response', () => {
    expect(formatApiError({}, 'fallback message')).toBe('fallback message')
  })

  it('returns a string message directly', () => {
    const error = { response: { data: { message: 'Invalid credentials.' } } }
    expect(formatApiError(error)).toBe('Invalid credentials.')
  })

  it('flattens a field-error object into a readable string', () => {
    const error = {
      response: {
        data: {
          message: {
            email: ['Not a valid email address.'],
            password: ['Shorter than minimum length 8.'],
          },
        },
      },
    }
    const result = formatApiError(error)
    expect(result).toContain('email: Not a valid email address.')
    expect(result).toContain('password: Shorter than minimum length 8.')
  })

  it('joins a single field error that is not an array', () => {
    const error = { response: { data: { message: { identifier: 'Required field.' } } } }
    expect(formatApiError(error)).toBe('identifier: Required field.')
  })

  it('falls back when message is an unexpected type', () => {
    const error = { response: { data: { message: 42 } } }
    expect(formatApiError(error, 'default')).toBe('default')
  })

  it('uses the default fallback text when none is provided', () => {
    expect(formatApiError({})).toBe('Something went wrong. Please try again.')
  })
})
