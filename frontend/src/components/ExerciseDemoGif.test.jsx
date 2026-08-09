import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import ExerciseDemoGif from './ExerciseDemoGif'

it('renders an image pointing at the exercise-gifs asset by id', () => {
  render(<ExerciseDemoGif exerciseId={7} alt="How to perform Bicycle Crunches" />)

  const img = screen.getByAltText('How to perform Bicycle Crunches')
  expect(img).toHaveAttribute('src', '/exercise-gifs/7.gif')
})

it('falls back to a placeholder when the GIF fails to load', () => {
  render(<ExerciseDemoGif exerciseId={999} alt="How to perform Unknown Exercise" />)

  const img = screen.getByAltText('How to perform Unknown Exercise')
  fireEvent.error(img)

  expect(screen.getByText(/no demo available yet/i)).toBeInTheDocument()
  expect(screen.queryByAltText('How to perform Unknown Exercise')).not.toBeInTheDocument()
})
