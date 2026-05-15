import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import client from '../api/client'
import useAuthStore from '../store/authStore'

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary (little / no exercise)' },
  { value: 'light', label: 'Light (1–3 days / week)' },
  { value: 'moderate', label: 'Moderate (3–5 days / week)' },
  { value: 'active', label: 'Active (6–7 days / week)' },
  { value: 'very_active', label: 'Very Active (hard daily exercise)' },
]

export default function Register() {
  const [form, setForm] = useState({
    name: '', email: '', password: '',
    age: '', gender: 'male',
    weight_kg: '', height_cm: '',
    activity_level: 'moderate',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const setToken = useAuthStore((s) => s.setToken)
  const navigate = useNavigate()

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await client.post('/api/v1/auth/register', {
        ...form,
        age: Number(form.age),
        weight_kg: Number(form.weight_kg),
        height_cm: Number(form.height_cm),
      })
      setToken(data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const inputClass = 'w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400'
  const labelClass = 'text-xs text-gray-500 block mb-1'

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-10">
      <div className="bg-white shadow rounded-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-indigo-600 mb-1">Fitness App</h1>
        <h2 className="text-base font-semibold text-gray-700 mb-6">Create Account</h2>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={labelClass}>Full name</label>
            <input type="text" value={form.name} onChange={set('name')} className={inputClass} required />
          </div>
          <div>
            <label className={labelClass}>Email</label>
            <input type="email" value={form.email} onChange={set('email')} className={inputClass} required />
          </div>
          <div>
            <label className={labelClass}>Password</label>
            <input type="password" value={form.password} onChange={set('password')} className={inputClass} required />
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
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>
        <p className="text-sm text-gray-500 mt-5 text-center">
          Have an account?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
