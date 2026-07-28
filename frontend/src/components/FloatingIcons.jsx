import { Bike, Brain, Dumbbell, HeartPulse, Salad } from 'lucide-react'
import PropTypes from 'prop-types'

const ICONS = [Dumbbell, HeartPulse, Brain, Salad, Bike]

// Percentage-based positions scattered toward the edges/corners, leaving the
// center clear for real content. Alternates left/right and varies size so
// icons don't read as a single mechanical grid.
const LAYOUT = [
  { top: '10%', left: '5%', size: 30 },
  { top: '15%', right: '7%', size: 38 },
  { top: '62%', left: '3%', size: 26 },
  { top: '70%', right: '5%', size: 34 },
  { top: '38%', right: '15%', size: 24 },
]

/** Purely decorative, non-interactive icon layer. Mount inside a
 * `position: relative` container - fills it via `inset: 0` and clips to
 * its bounds, so pass a bounded-height wrapper (e.g. a page's hero
 * section) rather than an entire long/table-heavy page. */
export default function FloatingIcons({ count = 5 }) {
  const icons = ICONS.slice(0, count)

  return (
    <div className="floating-icons" aria-hidden="true">
      {icons.map((Icon, index) => {
        const { size, ...position } = LAYOUT[index % LAYOUT.length]
        return (
          <span
            key={index}
            className="floating-icon"
            style={{
              ...position,
              '--float-duration': `${5 + (index % 3)}s`,
              '--float-delay': `${index * 0.6}s`,
            }}
          >
            <Icon size={size} strokeWidth={1.5} />
          </span>
        )
      })}
    </div>
  )
}

FloatingIcons.propTypes = {
  count: PropTypes.number,
}
