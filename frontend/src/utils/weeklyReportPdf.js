import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

const ORANGE = [255, 90, 31]
const BLACK = [10, 10, 10]
const GRAY = [90, 90, 90]
const WHITE = [255, 255, 255]

function formatDate(isoString) {
  if (!isoString) return '—'
  return new Date(isoString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function capitalize(value) {
  if (!value) return '—'
  return value.charAt(0).toUpperCase() + value.slice(1)
}

function sectionHeading(doc, text, x, y) {
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(13)
  doc.setTextColor(...ORANGE)
  doc.text(text.toUpperCase(), x, y)
  doc.setDrawColor(...ORANGE)
  doc.setLineWidth(0.75)
  doc.line(x, y + 4, doc.internal.pageSize.getWidth() - x, y + 4)
  return y + 22
}

export function generateWeeklyReportPdf(report) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()
  const margin = 40
  let y = 50

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(20)
  doc.setTextColor(...BLACK)
  doc.text('SmartGen Fit', margin, y)
  doc.setTextColor(...ORANGE)
  doc.setFontSize(12)
  doc.text('WEEKLY HEALTH REPORT', margin, y + 18)
  doc.setDrawColor(...ORANGE)
  doc.setLineWidth(2)
  doc.line(margin, y + 28, pageWidth - margin, y + 28)

  y += 50
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(...GRAY)
  doc.text(
    `Report period: ${formatDate(report.totals.start_date)} - ${formatDate(report.totals.end_date)}    |    Generated: ${formatDate(new Date().toISOString())}`,
    margin,
    y,
  )
  y += 25

  y = sectionHeading(doc, 'Profile', margin, y)
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    theme: 'plain',
    styles: { fontSize: 10, textColor: BLACK },
    columnStyles: { 0: { fontStyle: 'bold', cellWidth: 90 }, 2: { fontStyle: 'bold', cellWidth: 90 } },
    body: [
      ['Name', report.user.full_name, 'Age', String(report.user.age)],
      [
        'Gender',
        capitalize(report.user.gender),
        'Contact',
        report.user.phone_number || 'Not on file',
      ],
      [
        'Height',
        report.user.height_cm ? `${report.user.height_cm} cm` : 'Not on file',
        'Weight',
        report.user.weight_kg ? `${report.user.weight_kg} kg` : 'Not on file',
      ],
      [
        'BMI',
        report.bmi_value
          ? `${report.bmi_value} (${report.bmi_category?.category_name})`
          : 'Add height/weight to calculate',
        '',
        '',
      ],
    ],
  })
  y = doc.lastAutoTable.finalY + 20

  y = sectionHeading(doc, 'Latest Body Scan Result', margin, y)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  if (report.latest_analysis) {
    doc.setTextColor(...BLACK)
    const confidence = (Number(report.latest_analysis.confidence_score) * 100).toFixed(0)
    doc.text(
      `Body type: ${report.latest_analysis.predicted_body_type?.name} (confidence ${confidence}%) — scanned ${formatDate(report.latest_analysis.created_at)}`,
      margin,
      y,
    )
  } else {
    doc.setTextColor(...GRAY)
    doc.text('No body scan on file yet.', margin, y)
  }
  y += 24

  y = sectionHeading(doc, 'Current Meal & Workout Plan', margin, y)
  if (report.recommendation) {
    const meal = report.recommendation.meal_record
    const workout = report.recommendation.workout_record

    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      theme: 'grid',
      head: [['Meal Plan', `${meal.daily_calories} kcal/day`]],
      headStyles: { fillColor: ORANGE, textColor: WHITE },
      styles: { fontSize: 9, textColor: BLACK },
      body: [
        ['Breakfast', meal.breakfast],
        ['Morning snack', meal.morning_snack],
        ['Lunch', meal.lunch],
        ['Evening snack', meal.evening_snack],
        ['Dinner', meal.dinner],
      ],
    })
    y = doc.lastAutoTable.finalY + 10

    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      theme: 'grid',
      head: [['Workout Plan', `${workout.workout_type} (${workout.intensity})`]],
      headStyles: { fillColor: ORANGE, textColor: WHITE },
      styles: { fontSize: 9, textColor: BLACK },
      body: [
        ['Category', workout.workout_category],
        [
          'Duration',
          `${workout.duration_min} min (${workout.warmup_min} min warm-up, ${workout.cooldown_min} min cool-down)`,
        ],
        ['Schedule', `${workout.days_per_week} days/week, ${workout.indoor_outdoor}`],
        ['Target muscle', workout.target_muscle],
        ['Equipment', workout.equipment || 'None'],
        ['Calories burned (per session)', String(workout.calories_burned)],
        ['Goal', workout.goal],
      ],
    })
    y = doc.lastAutoTable.finalY + 20
  } else {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(...GRAY)
    doc.text('No matched plan yet — analyze a body photo to get one.', margin, y)
    y += 24
  }

  y = sectionHeading(doc, "This Week's Activity", margin, y)
  const totals = report.totals
  autoTable(doc, {
    startY: y,
    margin: { left: margin, right: margin },
    theme: 'grid',
    head: [['Metric', 'Value']],
    headStyles: { fillColor: ORANGE, textColor: WHITE },
    styles: { fontSize: 10, textColor: BLACK },
    body: [
      ['Calories consumed (logged meals)', String(totals.calories_consumed)],
      ['Calories burned (logged workouts)', String(totals.calories_burned)],
      [
        'Net calories (consumed − burned)',
        String(totals.calories_consumed - totals.calories_burned),
      ],
      ['Workouts logged', String(totals.workouts_logged)],
      ['Meals logged', String(totals.meals_logged)],
      ['Protein logged (g)', String(totals.protein_g)],
    ],
  })
  y = doc.lastAutoTable.finalY + 30

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(8)
  doc.setTextColor(...GRAY)
  doc.text(
    'This report reflects data you have logged in SmartGen Fit and is not medical advice.',
    margin,
    doc.internal.pageSize.getHeight() - 30,
  )

  // Reuses the report's own end_date (the backend's local "today") rather
  // than deriving one independently on the client - a client-side
  // `toISOString()` slice is UTC, which can silently disagree with the
  // server's local date by a day and make the filename and the report's
  // own "Report period" line look inconsistent.
  doc.save(`smartgen-fit-weekly-report-${report.totals.end_date}.pdf`)
}
