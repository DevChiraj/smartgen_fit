import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import PageTransition from './PageTransition'

it('renders its children', () => {
  render(
    <PageTransition>
      <p>Page content</p>
    </PageTransition>,
  )

  expect(screen.getByText('Page content')).toBeInTheDocument()
})
