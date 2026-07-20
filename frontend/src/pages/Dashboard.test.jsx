import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import Dashboard from './Dashboard'
import { useAuth } from '../context/AuthContext'
import { calculateBmi } from '../services/bmiService'
import { getLatestRecommendation } from '../services/recommendationService'

vi.mock('../context/AuthContext')
vi.mock('../services/bmiService')
vi.mock('../services/recommendationService')

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
  getLatestRecommendation.mockResolvedValue({ recommendation: null })
})

it('renders nothing when there is no logged-in user', () => {
  useAuth.mockReturnValue({ user: null })
  const { container } = renderDashboard()
  expect(container).toBeEmptyDOMElement()
})

it('prompts for height/weight and does not call the BMI service when profile is incomplete', async () => {
  useAuth.mockReturnValue({
    user: { full_name: 'Jane', username: 'jane', age: 28, gender: 'female' },
  })
  renderDashboard()

  expect(await screen.findByText(/add your height and weight/i)).toBeInTheDocument()
  expect(calculateBmi).not.toHaveBeenCalled()
})

it('calculates and displays BMI when the profile has height/weight', async () => {
  useAuth.mockReturnValue({
    user: { full_name: 'Jane', username: 'jane', age: 28, gender: 'female', height_cm: 170, weight_kg: 65 },
  })
  calculateBmi.mockResolvedValue({
    bmi: '22.5',
    category: { category_name: 'Normal weight', min_bmi: 18.5, max_bmi: 25 },
  })
  renderDashboard()

  expect(await screen.findByText('22.5')).toBeInTheDocument()
  expect(screen.getByText('Normal weight')).toBeInTheDocument()
  expect(calculateBmi).toHaveBeenCalledWith({ height_cm: 170, weight_kg: 65 })
})

it('shows a CTA to analyze a photo when no recommendation exists yet', async () => {
  useAuth.mockReturnValue({ user: { full_name: 'Jane', username: 'jane', age: 28, gender: 'female' } })
  renderDashboard()

  expect(await screen.findByText(/analyze a body photo/i)).toBeInTheDocument()
})

it('shows the full matched meal and workout plan when a recommendation exists', async () => {
  useAuth.mockReturnValue({ user: { full_name: 'Jane', username: 'jane', age: 28, gender: 'female' } })
  getLatestRecommendation.mockResolvedValue({
    recommendation: {
      recommendation_id: 1,
      bmi_value: '22.5',
      body_type: { body_type_id: 2, name: 'Normal' },
      meal_record: {
        daily_calories: 1900,
        breakfast: 'Oats',
        morning_snack: 'Fruit',
        lunch: 'Rice and curry',
        evening_snack: 'Nuts',
        dinner: 'Soup',
      },
      workout_record: {
        workout_type: 'Cycling',
        intensity: 'Moderate',
        calories_burned: 400,
        workout_category: 'Cardio',
        duration_min: 40,
        warmup_min: 8,
        cooldown_min: 5,
        days_per_week: 4,
        indoor_outdoor: 'Outdoor',
        target_muscle: 'Full body',
        equipment: 'Bicycle',
        goal: 'Weight maintenance',
      },
    },
  })

  renderDashboard()

  expect(await screen.findByText('Oats')).toBeInTheDocument()
  expect(screen.getByText('Cycling')).toBeInTheDocument()
  expect(screen.getByText(/1900 kcal/)).toBeInTheDocument()
  expect(screen.getByText('View full plan')).toBeInTheDocument()
})
