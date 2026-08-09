import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import NotificationBell from './NotificationBell'
import { getAnalysisHistory } from '../services/imageAnalysisService'
import { getSmartNotifications } from '../services/notificationService'

vi.mock('../services/imageAnalysisService')
vi.mock('../services/notificationService')

function renderBell() {
  return render(
    <MemoryRouter>
      <NotificationBell />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
  getAnalysisHistory.mockResolvedValue({ history: [] })
  getSmartNotifications.mockResolvedValue({ notifications: [] })
})

it('shows no badge when there are no alerts or recent activity', async () => {
  renderBell()
  await screen.findByRole('button', { name: /notifications/i })

  expect(screen.queryByText(/^\d+$/)).not.toBeInTheDocument()
})

it('shows a combined badge count and lists alerts above recent activity', async () => {
  getSmartNotifications.mockResolvedValue({
    notifications: [
      { type: 'exercise_inactivity', severity: 'warning', message: "You haven't exercised for 4 days." },
    ],
  })
  getAnalysisHistory.mockResolvedValue({
    history: [
      {
        analysis_id: 1,
        predicted_body_type: { name: 'Normal' },
        confidence_score: '0.9000',
        created_at: '2026-08-01T10:00:00Z',
      },
    ],
  })
  const user = userEvent.setup()
  renderBell()

  await screen.findByText('2')
  await user.click(screen.getByRole('button', { name: /notifications/i }))

  expect(screen.getByText('Alerts')).toBeInTheDocument()
  expect(screen.getByText("You haven't exercised for 4 days.")).toBeInTheDocument()
  expect(screen.getByText('Recent activity')).toBeInTheDocument()
  expect(screen.getByText(/Body type analyzed/)).toBeInTheDocument()
})

it('shows the empty-activity prompt when there is no analysis history', async () => {
  const user = userEvent.setup()
  renderBell()
  await screen.findByRole('button', { name: /notifications/i })

  await user.click(screen.getByRole('button', { name: /notifications/i }))

  expect(await screen.findByText(/no activity yet/i)).toBeInTheDocument()
})
