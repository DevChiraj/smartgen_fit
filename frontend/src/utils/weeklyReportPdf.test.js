import { beforeEach, expect, it, vi } from 'vitest'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { generateWeeklyReportPdf } from './weeklyReportPdf'

const mockDoc = {
  setFont: vi.fn(),
  setFontSize: vi.fn(),
  setTextColor: vi.fn(),
  setDrawColor: vi.fn(),
  setLineWidth: vi.fn(),
  text: vi.fn(),
  line: vi.fn(),
  save: vi.fn(),
  internal: {
    pageSize: { getWidth: () => 595, getHeight: () => 842 },
  },
  lastAutoTable: { finalY: 100 },
}

vi.mock('jspdf', () => ({
  default: vi.fn(function MockJsPDF() {
    return mockDoc
  }),
}))
vi.mock('jspdf-autotable', () => ({ default: vi.fn() }))

const REPORT_WITH_EVERYTHING = {
  user: {
    full_name: 'Jane Doe',
    age: 28,
    gender: 'female',
    phone_number: '0771234567',
    height_cm: '165.00',
    weight_kg: '58.00',
  },
  bmi_value: '21.3',
  bmi_category: { category_name: 'Normal weight' },
  latest_analysis: {
    predicted_body_type: { name: 'Normal' },
    confidence_score: '0.9200',
    created_at: '2026-08-01T10:00:00',
  },
  recommendation: {
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
      workout_category: 'Cardio',
      duration_min: 40,
      warmup_min: 8,
      cooldown_min: 5,
      days_per_week: 4,
      indoor_outdoor: 'Outdoor',
      target_muscle: 'Full body',
      equipment: 'Bicycle',
      calories_burned: 400,
      goal: 'Weight maintenance',
    },
  },
  totals: {
    start_date: '2026-07-28',
    end_date: '2026-08-03',
    calories_consumed: 12000,
    calories_burned: 2800,
    workouts_logged: 5,
    meals_logged: 18,
    protein_g: '450.00',
  },
}

const REPORT_MINIMAL = {
  user: {
    full_name: 'New User',
    age: 20,
    gender: 'male',
    phone_number: null,
    height_cm: null,
    weight_kg: null,
  },
  bmi_value: null,
  bmi_category: null,
  latest_analysis: null,
  recommendation: null,
  totals: {
    start_date: '2026-07-28',
    end_date: '2026-08-03',
    calories_consumed: 0,
    calories_burned: 0,
    workouts_logged: 0,
    meals_logged: 0,
    protein_g: '0',
  },
}

beforeEach(() => {
  vi.clearAllMocks()
})

it('saves the PDF with a date-stamped filename', () => {
  generateWeeklyReportPdf(REPORT_WITH_EVERYTHING)

  expect(jsPDF).toHaveBeenCalled()
  expect(mockDoc.save).toHaveBeenCalledTimes(1)
  const [filename] = mockDoc.save.mock.calls[0]
  expect(filename).toMatch(/^smartgen-fit-weekly-report-\d{4}-\d{2}-\d{2}\.pdf$/)
})

it('includes the profile and weekly totals in the generated tables', () => {
  generateWeeklyReportPdf(REPORT_WITH_EVERYTHING)

  const bodies = autoTable.mock.calls.map(([, options]) => options.body)
  const heads = autoTable.mock.calls.map(([, options]) => options.head).filter(Boolean)
  const flattened = [...bodies.flat(2), ...heads.flat(2)]
  expect(flattened).toContain('Jane Doe')
  expect(flattened.some((cell) => String(cell).includes('28'))).toBe(true)
  expect(flattened).toContain('Oats')
  expect(flattened.some((cell) => String(cell).includes('Cycling'))).toBe(true)
  expect(flattened.map(String)).toContain('12000')
  expect(flattened.map(String)).toContain('2800')
})

it('falls back to placeholder text when there is no scan or matched plan', () => {
  generateWeeklyReportPdf(REPORT_MINIMAL)

  const textCalls = mockDoc.text.mock.calls.map(([content]) => content)
  expect(textCalls.some((t) => t.includes('No body scan on file yet'))).toBe(true)
  expect(textCalls.some((t) => t.includes('No matched plan yet'))).toBe(true)
})

it('does not crash when height/weight/BMI are missing', () => {
  expect(() => generateWeeklyReportPdf(REPORT_MINIMAL)).not.toThrow()
})
