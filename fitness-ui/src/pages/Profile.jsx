import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import client from '../api/client'

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary (little / no exercise)' },
  { value: 'light', label: 'Light (1–3 days / week)' },
  { value: 'moderate', label: 'Moderate (3–5 days / week)' },
  { value: 'active', label: 'Active (6–7 days / week)' },
  { value: 'very_active', label: 'Very Active (hard daily exercise)' },
]

const inputClass = 'w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400'
const labelClass = 'text-xs text-gray-500 block mb-1'

export default function Profile() {
  const [form, setForm] = useState(null)
  const [bmr, setBmr] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      client.get('/api/v1/users/me'),
      client.get('/api/v1/users/me/bmr'),
    ]).then(([{ data: user }, { data: metrics }]) => {
      setForm({
        name: user.name,
        age: user.age,
        gender: user.gender,
        weight_kg: user.weight_kg,
        height_cm: user.height_cm,
        activity_level: user.activity_level,
      })
      setBmr(metrics)
    })
  }, [])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setSuccess('')
    setError('')
    try {
      await client.put('/api/v1/users/me', {
        ...form,
        age: Number(form.age),
        weight_kg: Number(form.weight_kg),
        height_cm: Number(form.height_cm),
      })
      const { data: metrics } = await client.get('/api/v1/users/me/bmr')
      setBmr(metrics)
      setSuccess('Profile updated.')
    } catch {
      setError('Failed to update profile.')
    } finally {
      setLoading(false)
    }
  }

  if (!form) return <Layout><p className="text-gray-400 text-sm">Loading…</p></Layout>

  return (
    <Layout>
      <h1 className="text-xl font-bold text-gray-800 mb-6">My Profile</h1>

      {bmr && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white shadow rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">BMR</p>
            <p className="text-2xl font-bold text-gray-800">
              {bmr.bmr} <span className="text-sm font-normal text-gray-400">kcal/day</span>
            </p>
          </div>
          <div className="bg-white shadow rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">TDEE</p>
            <p className="text-2xl font-bold text-indigo-600">
              {bmr.tdee} <span className="text-sm font-normal text-gray-400">kcal/day</span>
            </p>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg p-6">
        {success && <p className="text-green-600 text-sm mb-4">{success}</p>}
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={labelClass}>Full name</label>
            <input type="text" value={form.name} onChange={set('name')} className={inputClass} required />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Age</label>
              <input type="number" min="10" max="100" value={form.age} onChange={set('age')} className={inputClass} required />
            </div>
            <div>
              <label className={labelClass}>Gender</label>
              <select value={form.gender} onChange={set('gender')} className={inputClass}>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Weight (kg)</label>
              <input type="number" step="0.1" min="20" value={form.weight_kg} onChange={set('weight_kg')} className={inputClass} required />
            </div>
            <div>
              <label className={labelClass}>Height (cm)</label>
              <input type="number" min="100" max="250" value={form.height_cm} onChange={set('height_cm')} className={inputClass} required />
            </div>
          </div>

          <div>
            <label className={labelClass}>Activity level</label>
            <select value={form.activity_level} onChange={set('activity_level')} className={inputClass}>
              {ACTIVITY_LEVELS.map((l) => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            {loading ? 'Saving…' : 'Save Changes'}
          </button>
        </form>
      </div>
    </Layout>
  )
}
