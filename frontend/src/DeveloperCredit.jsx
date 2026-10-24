import { ArrowUpRight } from 'lucide-react'

const LINKEDIN_NAME = 'Mehul Ravi'
const LINKEDIN_URL = 'https://www.linkedin.com/in/mehulravi/?isSelfProfile=true'

function LinkedinIcon(props) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45Z" />
    </svg>
  )
}

export default function DeveloperCredit() {
  return (
    <div className="credit">
      <span className="credit__label">Built by</span>
      <a
        href={LINKEDIN_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="credit__link"
        aria-label={`${LINKEDIN_NAME} on LinkedIn (opens in a new tab)`}
      >
        <LinkedinIcon />
        {LINKEDIN_NAME}
        <ArrowUpRight size={14} strokeWidth={2.25} aria-hidden="true" />
      </a>
    </div>
  )
}
