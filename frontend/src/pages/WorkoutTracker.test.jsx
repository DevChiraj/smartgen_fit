import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import WorkoutTracker from './WorkoutTracker'
import { useNotifications } from '../context/NotificationContext'
import { getExercises } from '../services/exerciseService'
import { getWorkoutLogHistory, logWorkout } from '../services/workoutLogService'

vi.mock('../context/NotificationContext')
vi.mock('../services/exerciseService')
vi.mock('../services/workoutLogService')

const PUSH_UP = {
  exercise_id: 1,
  exercise_name: 'Push Up',
  calories_per_30min: 180,
}

const EXISTING_LOG = {
  log_id: 1,
  log_date: '2026-08-01',
  duration_minutes: 20,
  calories_burned: 120,
  notes: 'Good session',
  exercise: { exercise_id: 1, exercise_name: 'Push Up', target_muscle: 'Chest' },
}

function renderTracker() {
  return render(
    <MemoryRouter>
      <WorkoutTracker />
    </MemoryRouter>,
  )
}

const showToast = vi.fn()

beforeEach(() => {
  vi.resetAllMocks()
  useNotifications.mockReturnValue({ showToast })
  getExercises.mockResolvedValue({ exercises: [PUSH_UP] })
  getWorkoutLogHistory.mockResolvedValue({ history: [] })
})

it('loads and displays existing workout history', async () => {
  getWorkoutLogHistory.mockResolvedValue({ history: [EXISTING_LOG] })
  renderTracker()

  expect(await screen.findByRole('cell', { name: 'Push Up' })).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: '2026-08-01' })).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: '120' })).toBeInTheDocument()
})

it('shows an empty state when there is no history yet', async () => {
  renderTracker()

  expect(await screen.findByText(/no workouts logged yet/i)).toBeInTheDocument()
})

it('logs a workout and prepends it to the history', async () => {
  const user = userEvent.setup()
  logWorkout.mockResolvedValue({ log: EXISTING_LOG })
  renderTracker()

  await screen.findByText(/no workouts logged yet/i)

  await user.selectOptions(screen.getByLabelText(/exercise/i), '1')
  await user.type(screen.getByLabelText(/duration/i), '20')
  await user.click(screen.getByRole('button', { name: /log workout/i }))

  await waitFor(() =>
    expect(logWorkout).toHaveBeenCalledWith(
      expect.objectContaining({ exercise_id: 1, duration_minutes: 20 }),
    ),
  )
  expect(await screen.findByText('Good session')).toBeInTheDocument()
  expect(showToast).toHaveBeenCalledWith('Workout logged!', 'success')
})

it('shows an error message when logging fails', async () => {
  const user = userEvent.setup()
  logWorkout.mockRejectedValue({ response: { data: { message: 'No exercise with id 1.' } } })
  renderTracker()

  await screen.findByText(/no workouts logged yet/i)
  await user.selectOptions(screen.getByLabelText(/exercise/i), '1')
  await user.type(screen.getByLabelText(/duration/i), '20')
  await user.click(screen.getByRole('button', { name: /log workout/i }))

  expect(await screen.findByText('No exercise with id 1.')).toBeInTheDocument()
})
