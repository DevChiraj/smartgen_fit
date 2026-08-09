import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import MealDiary from './MealDiary'
import { useNotifications } from '../context/NotificationContext'
import { getFoods } from '../services/foodService'
import { getMealLogHistory, logMeal } from '../services/mealLogService'

vi.mock('../context/NotificationContext')
vi.mock('../services/foodService')
vi.mock('../services/mealLogService')

const RICE = {
  food_id: 1,
  food_name: 'White Rice',
  calories: 110,
}

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

const EXISTING_LOG = {
  log_id: 1,
  log_date: todayIsoDate(),
  meal_type: 'lunch',
  quantity_servings: '1.00',
  calories: 110,
  protein_g: '2.00',
  notes: 'Ate well',
  food: { food_id: 1, food_name: 'White Rice', category: 'Grain' },
}

function renderDiary() {
  return render(
    <MemoryRouter>
      <MealDiary />
    </MemoryRouter>,
  )
}

const showToast = vi.fn()

beforeEach(() => {
  vi.resetAllMocks()
  useNotifications.mockReturnValue({ showToast })
  getFoods.mockResolvedValue({ foods: [RICE] })
  getMealLogHistory.mockResolvedValue({ history: [] })
})

it('loads and displays existing meal history', async () => {
  getMealLogHistory.mockResolvedValue({ history: [EXISTING_LOG] })
  renderDiary()

  expect(await screen.findByRole('cell', { name: 'White Rice' })).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: 'Lunch' })).toBeInTheDocument()
})

it('shows an empty state when there is no history yet', async () => {
  renderDiary()

  expect(await screen.findByText(/no meals logged yet/i)).toBeInTheDocument()
})

it("summarizes today's logged meals", async () => {
  getMealLogHistory.mockResolvedValue({ history: [EXISTING_LOG] })
  renderDiary()

  expect(await screen.findByText('1', { selector: '.display-6' })).toBeInTheDocument()
  expect(screen.getByText('110', { selector: '.display-6' })).toBeInTheDocument()
})

it('logs a meal and prepends it to the history', async () => {
  const user = userEvent.setup()
  logMeal.mockResolvedValue({ log: EXISTING_LOG })
  renderDiary()

  await screen.findByText(/no meals logged yet/i)

  await user.selectOptions(screen.getByLabelText(/food/i), '1')
  await user.selectOptions(screen.getByLabelText(/meal/i), 'lunch')
  await user.click(screen.getByRole('button', { name: /log meal/i }))

  await waitFor(() =>
    expect(logMeal).toHaveBeenCalledWith(
      expect.objectContaining({ food_id: 1, meal_type: 'lunch', quantity_servings: 1 }),
    ),
  )
  expect(await screen.findByText('Ate well')).toBeInTheDocument()
  expect(showToast).toHaveBeenCalledWith('Meal logged!', 'success')
})

it('shows an error message when logging fails', async () => {
  const user = userEvent.setup()
  logMeal.mockRejectedValue({ response: { data: { message: 'No food with id 1.' } } })
  renderDiary()

  await screen.findByText(/no meals logged yet/i)
  await user.selectOptions(screen.getByLabelText(/food/i), '1')
  await user.click(screen.getByRole('button', { name: /log meal/i }))

  expect(await screen.findByText('No food with id 1.')).toBeInTheDocument()
})
