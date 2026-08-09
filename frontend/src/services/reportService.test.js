import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './apiClient'
import { getWeeklyReport } from './reportService'

vi.mock('./apiClient')

describe('reportService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('getWeeklyReport gets /v1/reports/weekly', async () => {
    apiClient.get.mockResolvedValue({ data: { report: { totals: {} } } })

    const result = await getWeeklyReport()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/reports/weekly')
    expect(result).toEqual({ report: { totals: {} } })
  })
})
