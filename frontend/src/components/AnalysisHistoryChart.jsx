import PropTypes from 'prop-types'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const GRID_COLOR = '#2a2a2e'
const TEXT_COLOR = '#a1a1aa'
const BAR_COLOR = '#ff5a1f'

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div
      style={{
        background: '#131315',
        border: '1px solid #232326',
        borderRadius: 8,
        padding: '0.5rem 0.75rem',
      }}
    >
      <div style={{ color: '#fff', fontWeight: 700, fontSize: '0.9rem' }}>
        {point.confidence.toFixed(0)}% confidence
      </div>
      <div style={{ color: TEXT_COLOR, fontSize: '0.75rem' }}>
        {point.bodyType} &middot; {point.fullDate}
      </div>
    </div>
  )
}

ChartTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
}

export default function AnalysisHistoryChart({ history }) {
  const chartData = [...history]
    .slice(0, 10)
    .reverse()
    .map((item) => {
      const date = new Date(item.created_at)
      return {
        label: date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
        fullDate: date.toLocaleString(),
        confidence: Number(item.confidence_score) * 100,
        bodyType: item.predicted_body_type?.name,
      }
    })

  if (chartData.length === 0) {
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barSize={24}>
        <CartesianGrid vertical={false} stroke={GRID_COLOR} />
        <XAxis
          dataKey="label"
          tick={{ fill: TEXT_COLOR, fontSize: 12 }}
          axisLine={{ stroke: GRID_COLOR }}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: TEXT_COLOR, fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          width={48}
          tickFormatter={(value) => `${value}%`}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
        <Bar dataKey="confidence" fill={BAR_COLOR} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

AnalysisHistoryChart.propTypes = {
  history: PropTypes.arrayOf(
    PropTypes.shape({
      analysis_id: PropTypes.number,
      confidence_score: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      created_at: PropTypes.string,
      predicted_body_type: PropTypes.shape({ name: PropTypes.string }),
    }),
  ).isRequired,
}
