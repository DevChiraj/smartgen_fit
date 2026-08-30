import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { calculateAge } from './age'

describe('calculateAge', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2020-06-15T00:00:00'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns the full year difference once the birthday has passed this year', () => {
    expect(calculateAge('2000-01-01')).toBe(20)
  })

  it('subtracts one when the birthday has not happened yet this year', () => {
    expect(calculateAge('2000-12-25')).toBe(19)
  })

  it('counts the birthday itself as already turned', () => {
    expect(calculateAge('2000-06-15')).toBe(20)
  })
})
