import { useState } from 'react'
import { Hash, Users, MapPin, ShieldCheck, Layers, Flag } from 'lucide-react'

const CATEGORIES = ['GEN', 'EWS', 'OBC', 'SC', 'ST']
const QUOTAS = [
  { value: 'GENERAL', label: 'General' },
  { value: 'PWD', label: 'PwD' },
  { value: 'DEFENCE_CW', label: 'Defence (CW)' },
  { value: 'KASHMIRI_MIGRANT', label: 'Kashmiri Migrant' },
  { value: 'SIKKIM_GOA', label: 'Sikkim / Goa' },
]

const initialForm = {
  rank: '',
  category: 'GEN',
  applicant_gender: 'MALE',
  region: 'DELHI',
  quota: 'GENERAL',
  round: '5',
}

export default function PredictorForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initialForm)

  // These quotas have no home region in the cutoff data, so the region is not sent.
  const regionNotApplicable = ['KASHMIRI_MIGRANT', 'SIKKIM_GOA'].includes(form.quota)

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!form.rank || Number(form.rank) <= 0) return
    onSubmit({
      ...form,
      region: regionNotApplicable ? undefined : form.region,
    })
  }

  return (
    <form className="card form" onSubmit={handleSubmit} aria-labelledby="form-title">
      <div className="form__head">
        <h2 id="form-title" className="form__title">Your details</h2>
        <p className="form__sub">Fields marked * are required.</p>
      </div>

      <div className="field">
        <label htmlFor="rank" className="field__label">
          <Hash size={15} strokeWidth={2.25} aria-hidden="true" />
          JEE Rank (CRL) <span className="req" aria-hidden="true">*</span>
        </label>
        <input
          id="rank"
          type="number"
          min="1"
          required
          inputMode="numeric"
          placeholder="e.g. 15000"
          value={form.rank}
          onChange={(e) => update('rank', e.target.value)}
          className="field__input field__input--rank"
          aria-describedby="rank-help"
        />
        <p id="rank-help" className="field__help">Use your Common Rank List (CRL) rank.</p>
      </div>

      <div className="field" role="group" aria-labelledby="category-label">
        <span id="category-label" className="field__label">
          <Layers size={15} strokeWidth={2.25} aria-hidden="true" /> Category
        </span>
        <div className="pill-group">
          {CATEGORIES.map((c) => (
            <button
              type="button"
              key={c}
              className={`pill ${form.category === c ? 'pill--active' : ''}`}
              onClick={() => update('category', c)}
              aria-pressed={form.category === c}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="field-row">
        <div className="field" role="group" aria-labelledby="gender-label">
          <span id="gender-label" className="field__label">
            <Users size={15} strokeWidth={2.25} aria-hidden="true" /> Gender
          </span>
          <div className="pill-group">
            {['MALE', 'FEMALE'].map((g) => (
              <button
                type="button"
                key={g}
                className={`pill ${form.applicant_gender === g ? 'pill--active' : ''}`}
                onClick={() => update('applicant_gender', g)}
                aria-pressed={form.applicant_gender === g}
              >
                {g === 'MALE' ? 'Male' : 'Female'}
              </button>
            ))}
          </div>
          <p className="field__help">Women-only institutions are shown to female applicants.</p>
        </div>

        <div
          className={`field ${regionNotApplicable ? 'field--disabled' : ''}`}
          role="group"
          aria-labelledby="region-label"
        >
          <span id="region-label" className="field__label">
            <MapPin size={15} strokeWidth={2.25} aria-hidden="true" /> Region
          </span>
          <div className="pill-group">
            {['DELHI', 'OUTSIDE_DELHI'].map((r) => (
              <button
                type="button"
                key={r}
                disabled={regionNotApplicable}
                className={`pill ${form.region === r ? 'pill--active' : ''}`}
                onClick={() => update('region', r)}
                aria-pressed={form.region === r}
              >
                {r === 'DELHI' ? 'Delhi' : 'Outside'}
              </button>
            ))}
          </div>
          <p className="field__help">
            {regionNotApplicable
              ? 'Not applicable for this quota.'
              : 'Delhi or Outside Delhi seat pool.'}
          </p>
        </div>
      </div>

      <div className="field">
        <label htmlFor="quota" className="field__label">
          <ShieldCheck size={15} strokeWidth={2.25} aria-hidden="true" /> Quota
        </label>
        <select
          id="quota"
          className="field__input field__select"
          value={form.quota}
          onChange={(e) => update('quota', e.target.value)}
        >
          {QUOTAS.map((q) => (
            <option key={q.value} value={q.value}>{q.label}</option>
          ))}
        </select>
      </div>

      <div className="field" role="group" aria-labelledby="round-label">
        <span id="round-label" className="field__label">
          <Flag size={15} strokeWidth={2.25} aria-hidden="true" /> Counselling round
        </span>
        <div className="pill-group">
          {['4', '5'].map((r) => (
            <button
              type="button"
              key={r}
              className={`pill ${form.round === r ? 'pill--active' : ''}`}
              onClick={() => update('round', r)}
              aria-pressed={form.round === r}
            >
              Round {r}
            </button>
          ))}
        </div>
        <p className="field__help">The same round is compared across years.</p>
      </div>

      <div className="form__actions">
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner spinner--sm" aria-hidden="true" />
              Checking cutoffs…
            </>
          ) : (
            'Predict my colleges'
          )}
        </button>
        <p className="form__note">
          Checked against both 2024 &amp; 2025 cutoffs automatically.
        </p>
      </div>
    </form>
  )
}
