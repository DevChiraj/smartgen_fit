import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import HealthyFoods from './HealthyFoods'
import { getFoodCategories, getFoods } from '../services/foodService'

vi.mock('../services/foodService')

const RICE = {
  food_id: 1,
  food_name: 'Red Rice',
  category: 'Grain',
  serving_size: '80g',
  calories: 112,
  protein_g: '2.40',
  carbs_g: '23.00',
  fat_g: '0.80',
  fiber_g: null,
  vitamins: null,
  minerals: null,
}

const BANANA = {
  food_id: 2,
  food_name: 'Banana',
  category: 'Fruit',
  serving_size: '100g',
  calories: 95,
  protein_g: '1.00',
  carbs_g: '27.00',
  fat_g: '0.30',
  fiber_g: '2.60',
  vitamins: 'C',
  minerals: 'Potassium',
}

beforeEach(() => {
  vi.resetAllMocks()
  getFoodCategories.mockResolvedValue({ categories: ['Fruit', 'Grain'] })
  getFoods.mockResolvedValue({ foods: [RICE, BANANA] })
})

it('loads and displays all foods on mount', async () => {
  render(<HealthyFoods />)

  expect(await screen.findByText('Red Rice')).toBeInTheDocument()
  expect(screen.getByText('Banana')).toBeInTheDocument()
  await waitFor(() =>
    expect(getFoods).toHaveBeenCalledWith({ category: undefined, q: undefined }),
  )
})

it('shows an empty state when no foods match', async () => {
  getFoods.mockResolvedValue({ foods: [] })
  render(<HealthyFoods />)

  expect(await screen.findByText(/no foods match your search/i)).toBeInTheDocument()
})

it('re-fetches with the category filter after selecting one', async () => {
  const user = userEvent.setup()
  render(<HealthyFoods />)
  await screen.findByText('Red Rice')
  getFoods.mockClear()
  getFoods.mockResolvedValue({ foods: [BANANA] })

  await user.selectOptions(screen.getByRole('combobox'), 'Fruit')

  await waitFor(() =>
    expect(getFoods).toHaveBeenCalledWith({ category: 'Fruit', q: undefined }),
    { timeout: 1000 },
  )
  expect(await screen.findByText('Banana')).toBeInTheDocument()
})

it('re-fetches with the search query after typing', async () => {
  const user = userEvent.setup()
  render(<HealthyFoods />)
  await screen.findByText('Red Rice')
  getFoods.mockClear()
  getFoods.mockResolvedValue({ foods: [RICE] })

  await user.type(screen.getByPlaceholderText(/search foods/i), 'rice')

  await waitFor(() => expect(getFoods).toHaveBeenCalledWith({ category: undefined, q: 'rice' }), {
    timeout: 1000,
  })
})

it('opens a detail modal with the full nutrition breakdown when a row is clicked', async () => {
  const user = userEvent.setup()
  render(<HealthyFoods />)
  await screen.findByText('Banana')

  await user.click(screen.getByText('Banana'))

  expect(screen.getByRole('heading', { name: 'Banana' })).toBeInTheDocument()
  expect(screen.getByText('95 kcal')).toBeInTheDocument()
  expect(screen.getByText('Potassium')).toBeInTheDocument()
})

it('shows an error message when loading foods fails', async () => {
  getFoods.mockRejectedValue({ response: { data: { message: 'Server error.' } } })
  render(<HealthyFoods />)

  expect(await screen.findByText('Server error.')).toBeInTheDocument()
})
