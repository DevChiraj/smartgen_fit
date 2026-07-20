import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import BMICalculator from './BMICalculator'
import { useAuth } from '../context/AuthContext'
import { calculateBmi } from '../services/bmiService'

vi.mock('../context/AuthContext')
vi.mock('../services/bmiService')

beforeEach(() => {
  vi.resetAllMocks()
  useAuth.mockReturnValue({ user: null })
})

it('pre-fills height/weight from the logged-in user profile when available', () => {
  useAuth.mockReturnValue({ user: { height_cm: 170, weight_kg: 65 } })
  render(<BMICalculator />)

  expect(screen.getByLabelText('Height (cm)')).toHaveValue(170)
  expect(screen.getByLabelText('Weight (kg)')).toHaveValue(65)
})

it('submits the form and displays the result', async () => {
  const user = userEvent.setup()
  calculateBmi.mockResolvedValue({
    bmi: '22.5',
    category: { category_name: 'Normal weight' },
  })
  render(<BMICalculator />)

  await user.type(screen.getByLabelText('Height (cm)'), '170')
  await user.type(screen.getByLabelText('Weight (kg)'), '65')
  await user.click(screen.getByRole('button', { name: /calculate bmi/i }))

  await waitFor(() => expect(screen.getByText('22.5')).toBeInTheDocument())
  expect(screen.getByText('Normal weight')).toBeInTheDocument()
  expect(calculateBmi).toHaveBeenCalledWith({ height_cm: '170', weight_kg: '65' })
})

it('shows an error message when the request fails', async () => {
  const user = userEvent.setup()
  calculateBmi.mockRejectedValue({
    response: { data: { message: 'height_cm: Must be between 50 and 250.' } },
  })
  render(<BMICalculator />)

  await user.type(screen.getByLabelText('Height (cm)'), '5')
  await user.type(screen.getByLabelText('Weight (kg)'), '65')
  await user.click(screen.getByRole('button', { name: /calculate bmi/i }))

  await waitFor(() =>
    expect(screen.getByText(/height_cm: Must be between 50 and 250\./)).toBeInTheDocument(),
  )
  expect(screen.queryByText(/display-6/)).not.toBeInTheDocument()
})
