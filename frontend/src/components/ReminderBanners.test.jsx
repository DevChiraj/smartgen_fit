import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import ReminderBanners from './ReminderBanners'
import { getWorkoutLogHistory } from '../services/workoutLogService'
import {
  HYDRATION_REMINDER_NEXT_AT_KEY,
  WORKOUT_REMINDER_DISMISSED_DATE_KEY,
} from '../utils/storageKeys'

vi.mock('../services/workoutLogService')

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

function renderBanners(initialPath = '/dashboard') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <ReminderBanners />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
  localStorage.clear()
  getWorkoutLogHistory.mockResolvedValue({ history: [] })
})

it('shows a workout reminder when nothing is logged today', async () => {
  renderBanners()

  expect(
    await screen.findByText(/haven't logged a workout today/i),
  ).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /log a workout/i })).toHaveAttribute(
    'href',
    '/workout-tracker',
  )
})

it('does not show a workout reminder when a workout was already logged today', async () => {
  getWorkoutLogHistory.mockResolvedValue({
    history: [{ log_id: 1, log_date: todayIsoDate() }],
  })
  renderBanners()

  await waitFor(() => expect(getWorkoutLogHistory).toHaveBeenCalled())
  expect(screen.queryByText(/haven't logged a workout today/i)).not.toBeInTheDocument()
})

it('does not show a workout reminder while already on the workout tracker page', async () => {
  renderBanners('/workout-tracker')

  await new Promise((resolve) => setTimeout(resolve, 50))
  expect(getWorkoutLogHistory).not.toHaveBeenCalled()
  expect(screen.queryByText(/haven't logged a workout today/i)).not.toBeInTheDocument()
})

it('shows a hydration reminder on first visit', async () => {
  renderBanners()

  expect(await screen.findByText(/remember to drink water/i)).toBeInTheDocument()
  expect(localStorage.getItem(HYDRATION_REMINDER_NEXT_AT_KEY)).not.toBeNull()
})

it('does not re-show the hydration reminder before its next scheduled time', async () => {
  localStorage.setItem(HYDRATION_REMINDER_NEXT_AT_KEY, String(Date.now() + 60 * 60 * 1000))
  renderBanners()

  await waitFor(() => expect(getWorkoutLogHistory).toHaveBeenCalled())
  expect(screen.queryByText(/remember to drink water/i)).not.toBeInTheDocument()
})

it('dismisses the workout reminder and persists the dismissal for today', async () => {
  const user = userEvent.setup()
  renderBanners()
  const message = await screen.findByText(/haven't logged a workout today/i)
  const workoutBanner = message.closest('.reminder-banner-item')

  await user.click(within(workoutBanner).getByRole('button', { name: /dismiss reminder/i }))

  await waitFor(
    () => expect(screen.queryByText(/haven't logged a workout today/i)).not.toBeInTheDocument(),
    { timeout: 1000 },
  )
  expect(localStorage.getItem(WORKOUT_REMINDER_DISMISSED_DATE_KEY)).toBe(todayIsoDate())
})

it('does not show a workout reminder again after being dismissed today', async () => {
  localStorage.setItem(WORKOUT_REMINDER_DISMISSED_DATE_KEY, todayIsoDate())
  renderBanners()

  await new Promise((resolve) => setTimeout(resolve, 50))
  expect(screen.queryByText(/haven't logged a workout today/i)).not.toBeInTheDocument()
})
