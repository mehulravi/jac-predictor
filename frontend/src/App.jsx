import { useEffect, useRef, useState } from 'react'
import { GraduationCap, Info } from 'lucide-react'
import PredictorForm from './PredictorForm'
import ResultsList from './ResultsList'
import CollegeDock from './CollegeDock'
import CollegeModal from './CollegeModal'
import DeveloperCredit from './DeveloperCredit'
import { predict } from './api'
import './App.css'

export default function App() {
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [activeCollege, setActiveCollege] = useState(null)
  const resultsRef = useRef(null)

  async function handleSubmit(form) {
    setStatus('loading')
    setError(null)
    try {
      const result = await predict(form)
      setData(result)
      setStatus('success')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }

  // Presentation only: on single-column (mobile/tablet) layouts the results sit
  // below the form, so bring them into view once a prediction starts.
  useEffect(() => {
    if (status === 'idle') return
    if (!window.matchMedia('(max-width: 900px)').matches) return
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    resultsRef.current?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' })
  }, [status])

  return (
    <div className="app">
      <a className="skip-link" href="#main">Skip to the predictor</a>

      <div className="masthead">
        <header className="topbar">
          <div className="container topbar__inner">
            <div className="brand">
              <span className="brand__mark" aria-hidden="true">
                <GraduationCap size={18} strokeWidth={2.25} />
              </span>
              <span className="brand__name">JAC Predictor</span>
            </div>
            <CollegeDock onSelect={setActiveCollege} />
          </div>
        </header>

        <div className="container hero">
          <h1 className="hero__title">Find the colleges that fit your rank.</h1>
          <p className="hero__subtitle">
            Enter your JEE rank and category to see which branches you'd be eligible
            for, checked against <strong>both 2024 and 2025</strong> cutoffs so you're
            not betting on a single year's data.
          </p>
          <p className="hero__colleges">Covers DTU, NSUT, IIIT-Delhi and IGDTUW.</p>
        </div>
      </div>

      <main id="main" className="container layout">
        <PredictorForm onSubmit={handleSubmit} loading={status === 'loading'} />
        <section
          className="results"
          ref={resultsRef}
          aria-live="polite"
          aria-label="Prediction results"
        >
          <ResultsList status={status} error={error} data={data} />
        </section>
      </main>

      <CollegeModal collegeCode={activeCollege} onClose={() => setActiveCollege(null)} />

      <footer className="footer">
        <div className="container footer__inner">
          <p className="footer__note">
            <Info size={16} aria-hidden="true" />
            <span>
              Cutoff data sourced from official JAC Delhi counselling bulletins.
              Predictions are estimates based on historical rounds, not guarantees.
              This is an independent tool, not an official JAC Delhi service.
            </span>
          </p>
          <DeveloperCredit />
        </div>
      </footer>
    </div>
  )
}
