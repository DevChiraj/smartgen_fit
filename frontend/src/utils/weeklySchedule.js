export const WEEK_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

/**
 * Spreads `daysPerWeek` workout days evenly across a 7-day week. There is
 * no real per-day data anywhere in the dataset (workout_recommendation_records
 * only has a days_per_week count) - this is a deterministic, clearly-labeled
 * suggestion, not an authoritative schedule from the source data.
 */
export function getSuggestedWorkoutDays(daysPerWeek) {
  const n = Math.max(1, Math.min(Number(daysPerWeek) || 0, 7))
  const indices = new Set()
  for (let i = 0; i < n; i += 1) {
    indices.add(Math.floor((i * 7) / n))
  }
  return WEEK_DAYS.map((day, index) => ({ day, isWorkoutDay: indices.has(index) }))
}
