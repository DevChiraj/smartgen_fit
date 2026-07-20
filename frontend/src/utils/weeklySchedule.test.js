import { describe, expect, it } from 'vitest'
import { getSuggestedWorkoutDays, WEEK_DAYS } from './weeklySchedule'

function workoutDaysFor(n) {
  return getSuggestedWorkoutDays(n)
    .filter((d) => d.isWorkoutDay)
    .map((d) => d.day)
}

describe('getSuggestedWorkoutDays', () => {
  it('always returns all 7 days of the week, each with an isWorkoutDay flag', () => {
    const result = getSuggestedWorkoutDays(3)
    expect(result).toHaveLength(7)
    expect(result.map((d) => d.day)).toEqual(WEEK_DAYS)
  })

  it.each([
    [1, ['Mon']],
    [2, ['Mon', 'Thu']],
    [3, ['Mon', 'Wed', 'Fri']],
    [4, ['Mon', 'Tue', 'Thu', 'Sat']],
    [5, ['Mon', 'Tue', 'Wed', 'Fri', 'Sat']],
    [6, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']],
    [7, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']],
  ])('spreads %i days/week as %j', (n, expected) => {
    expect(workoutDaysFor(n)).toEqual(expected)
  })

  it('clamps values above 7 down to 7 days', () => {
    expect(workoutDaysFor(10)).toHaveLength(7)
  })

  it('clamps values below 1 up to 1 day', () => {
    expect(workoutDaysFor(0)).toHaveLength(1)
  })

  it('treats a non-numeric input as 0 and still returns exactly 1 day', () => {
    expect(workoutDaysFor(undefined)).toHaveLength(1)
  })
})
