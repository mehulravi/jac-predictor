import { useEffect, useRef, useState } from 'react'
import { ChevronDown, GraduationCap } from 'lucide-react'
import { COLLEGES, COLLEGE_ORDER } from './collegeData'

export default function CollegeDock({ onSelect }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef(null)

  useEffect(() => {
    if (!open) return
    function onPointerDown(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false)
    }
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div className="colleges" ref={rootRef}>
      <button
        type="button"
        className="colleges__trigger"
        aria-expanded={open}
        aria-controls="colleges-menu"
        onClick={() => setOpen((v) => !v)}
      >
        <GraduationCap size={16} strokeWidth={2.25} aria-hidden="true" />
        Colleges
        <ChevronDown size={16} className="colleges__chevron" aria-hidden="true" />
      </button>

      {open && (
        <ul id="colleges-menu" className="colleges__menu">
          {COLLEGE_ORDER.map((code) => {
            const college = COLLEGES[code]
            return (
              <li key={code}>
                <button
                  type="button"
                  className="colleges__item"
                  onClick={() => {
                    onSelect(code)
                    setOpen(false)
                  }}
                  aria-label={`About ${college.name}`}
                >
                  <span className="colleges__badge">{college.shortCode}</span>
                  <span className="colleges__name">{college.name}</span>
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
