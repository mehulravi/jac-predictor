import { useState, useEffect, useRef } from 'react'
import { MapPin, Trophy, Wallet, Briefcase, ExternalLink, X } from 'lucide-react'
import { COLLEGES } from './collegeData'

const TABS = [
  { key: 'reach', label: 'How to Reach', icon: MapPin },
  { key: 'ranking', label: 'Ranking', icon: Trophy },
  { key: 'fees', label: 'Fees', icon: Wallet },
  { key: 'placement', label: 'Placement', icon: Briefcase },
]

export default function CollegeModal({ collegeCode, onClose }) {
  const [tab, setTab] = useState('reach')
  const college = collegeCode ? COLLEGES[collegeCode] : null
  const closeRef = useRef(null)

  useEffect(() => {
    setTab('reach') // reset to first tab whenever a new college is opened
  }, [collegeCode])

  useEffect(() => {
    if (collegeCode) closeRef.current?.focus() // move focus into the dialog when it opens
  }, [collegeCode])

  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  if (!college) return null

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="college-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal__close" onClick={onClose} aria-label="Close" ref={closeRef}>
          <X size={18} aria-hidden="true" />
        </button>

        <div className="modal__header">
          <span className="modal__badge">{college.shortCode}</span>
          <h2 className="modal__title" id="college-modal-title">{college.name}</h2>
        </div>

        <div className="modal__tabs" role="tablist" aria-label="College information">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={tab === key}
              className={`modal__tab ${tab === key ? 'modal__tab--active' : ''}`}
              onClick={() => setTab(key)}
            >
              <Icon size={15} strokeWidth={2.25} aria-hidden="true" />
              {label}
            </button>
          ))}
        </div>

        <div className="modal__body" role="tabpanel">
          {tab === 'reach' && (
            <div className="modal__section">
              <p className="modal__address">{college.howToReach.address}</p>
              <ul className="modal__list">
                {college.howToReach.details.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </div>
          )}

          {tab === 'ranking' && (
            <div className="modal__section">
              <div className="modal__rank-grid">
                {college.ranking.items.map((r, i) => (
                  <div key={i} className="modal__rank-item">
                    <span className="modal__rank-value">{r.value}</span>
                    <span className="modal__rank-label">{r.label}</span>
                  </div>
                ))}
              </div>
              <p className="modal__source">Source: {college.ranking.source}</p>
            </div>
          )}

          {tab === 'fees' && (
            <div className="modal__section">
              <div className="modal__fee-row">
                <span className="modal__fee-label">Tuition (B.Tech)</span>
                <span className="modal__fee-value">{college.fees.tuition}</span>
              </div>
              <div className="modal__fee-row">
                <span className="modal__fee-label">Hostel</span>
                <span className="modal__fee-value">{college.fees.hostel}</span>
              </div>
              <p className="modal__source">Approximate — confirm exact figures on the official website.</p>
            </div>
          )}

          {tab === 'placement' && (
            <div className="modal__section">
              <p className="modal__companies">{college.placement.companiesVisited}</p>
              <div className="modal__fee-row">
                <span className="modal__fee-label">Highest package</span>
                <span className="modal__fee-value">{college.placement.highest}</span>
              </div>
              <div className="modal__fee-row">
                <span className="modal__fee-label">Average package</span>
                <span className="modal__fee-value">{college.placement.average}</span>
              </div>
              <span className="modal__subhead">Recruiters seen on campus</span>
              <div className="modal__recruiters">
                {college.placement.recruiters.map((r) => (
                  <span key={r} className="modal__recruiter-chip">{r}</span>
                ))}
              </div>
              <p className="modal__source">{college.placement.note}</p>
            </div>
          )}
        </div>

        <a
          href={college.website}
          target="_blank"
          rel="noopener noreferrer"
          className="modal__website-link"
        >
          Visit official website <ExternalLink size={15} strokeWidth={2.25} aria-hidden="true" />
        </a>
      </div>
    </div>
  )
}
