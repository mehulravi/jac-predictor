import {
  CheckCircle2, AlertTriangle, XCircle,
  TrendingUp, TrendingDown, Minus, Search, Info,
} from 'lucide-react'

const CHANCE_ICON = {
  Safe: CheckCircle2,
  Moderate: AlertTriangle,
  Tough: XCircle,
}
const CHANCE_CLASS = {
  Safe: 'chance--safe',
  Moderate: 'chance--moderate',
  Tough: 'chance--tough',
}

const RELIABILITY_LABEL = {
  consistent: 'Consistent across years',
  moderate_swing: 'Moderate year-to-year swing',
  volatile: 'Volatile — cutoff swung a lot',
  single_year: 'Only one year of data',
}

function ChanceBadge({ chance }) {
  const Icon = CHANCE_ICON[chance]
  return (
    <span className={`chance ${CHANCE_CLASS[chance] || ''}`}>
      <Icon size={14} strokeWidth={2.5} aria-hidden="true" />
      {chance}
    </span>
  )
}

function YearRank({ year, rank }) {
  return (
    <div className="year">
      <span className="year__label">{year}</span>
      <span className="year__rank">{rank.toLocaleString('en-IN')}</span>
    </div>
  )
}

function YearTrend({ years }) {
  if (years.length < 2) {
    return (
      <div className="years">
        <YearRank year={years[0].year} rank={years[0].closing_rank} />
        <span className="years__note">New branch / single year</span>
      </div>
    )
  }
  const [first, second] = years
  const rising = second.closing_rank > first.closing_rank
  const flat = second.closing_rank === first.closing_rank
  const TrendIcon = flat ? Minus : rising ? TrendingUp : TrendingDown
  const trendTitle = flat
    ? 'Cutoff unchanged year over year'
    : rising
      ? 'Cutoff relaxed (higher rank number admitted) — better odds than last year'
      : 'Cutoff tightened (lower rank number required) — tougher than last year'

  return (
    <div className="years">
      <YearRank year={first.year} rank={first.closing_rank} />
      <span
        className={`trend ${rising ? 'trend--up' : flat ? '' : 'trend--down'}`}
        title={trendTitle}
        role="img"
        aria-label={trendTitle}
      >
        <TrendIcon size={16} strokeWidth={2.25} aria-hidden="true" />
      </span>
      <YearRank year={second.year} rank={second.closing_rank} />
    </div>
  )
}

function State({ icon: Icon, title, children, variant, role }) {
  return (
    <div className={`card state ${variant ? `state--${variant}` : ''}`} role={role}>
      <span className="state__icon" aria-hidden="true">{Icon ? <Icon size={22} strokeWidth={2} /> : <span className="spinner" />}</span>
      <p className="state__title">{title}</p>
      {children}
    </div>
  )
}

export default function ResultsList({ status, error, data }) {
  if (status === 'idle') {
    return (
      <State icon={Search} title="Your results will appear here">
        <ol className="steps">
          <li>Enter your JEE rank and pick your category.</li>
          <li>Choose gender, region, quota and counselling round.</li>
          <li>Select <strong>Predict my colleges</strong> to see eligible branches.</li>
        </ol>
      </State>
    )
  }

  if (status === 'loading') {
    return (
      <State title="Checking cutoffs across 2024 &amp; 2025…" role="status" />
    )
  }

  if (status === 'error') {
    return (
      <State icon={XCircle} title="Couldn't load results." variant="error" role="alert">
        <p className="state__text">{error}</p>
      </State>
    )
  }

  if (!data || data.count === 0) {
    return (
      <State icon={Search} title="No branches matched this rank and category in the selected round.">
        <p className="state__text">Try a different round, or double-check the category and region.</p>
      </State>
    )
  }

  return (
    <div className="card panel">
      <div className="panel__head">
        <h2 className="panel__title">Your results</h2>
        <span className="panel__count">
          {data.count} eligible {data.count === 1 ? 'branch' : 'branches'} found
        </span>
      </div>

      <ul className="result-list">
        {data.results.map((r, i) => (
          <li key={`${r.university}-${r.branch_code}-${i}`} className="result">
            <div className="result__info">
              <span className="result__uni">{r.university}</span>
              <h3 className="result__branch">
                {r.branch_name}
                {r.campus_name ? <span className="result__campus"> · {r.campus_name} Campus</span> : null}
              </h3>
              <span className="reliability">{RELIABILITY_LABEL[r.reliability]}</span>
            </div>

            <div className="result__side">
              <ChanceBadge chance={r.chance} />
              <YearTrend years={r.years} />
              <span className="result__conservative">
                Worst-case rank <strong>{r.conservative_rank.toLocaleString('en-IN')}</strong>
              </span>
            </div>
          </li>
        ))}
      </ul>

      <p className="disclaimer">
        <Info size={16} aria-hidden="true" />
        <span>{data.disclaimer}</span>
      </p>
    </div>
  )
}
