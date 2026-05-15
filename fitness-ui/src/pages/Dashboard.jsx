import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import client from '../api/client'

const todayStr = () => new Date().toISOString().split('T')[0]

function StatCard({ label, value, color = 'text-gray-800', description }) {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>
        {value ?? '—'} <span className="text-sm font-normal text-gray-400">kcal</span>
      </p>
      {description && <p className="text-xs text-gray-400 mt-1">{description}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [date, setDate] = useState(todayStr())
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    client
      .get(`/api/v1/dashboard/summary?log_date=${date}`)
      .then(({ data }) => setSummary(data))
      .catch(() => setError('Failed to load summary'))
      .finally(() => setLoading(false))
  }, [date])

  const deficit = summary ? summary.tdee - summary.net_calories : null
  const isOver = deficit !== null && deficit < 0

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-800">Dashboard</h1>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : summary && (
        <>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <StatCard label="BMR" value={summary.bmr} description="Calories your body burns at complete rest to sustain basic functions." />
            <StatCard label="TDEE" value={summary.tdee} description="Total calories you burn per day including your activity level." />
            <StatCard label="Consumed" value={summary.calories_consumed} color="text-orange-500" />
            <StatCard label="Burned" value={summary.calories_burned} color="text-teal-600" />
          </div>

          <div className="bg-white shadow rounded-lg p-5 mb-6">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Net Calories</p>
            <p className={`text-3xl font-bold ${isOver ? 'text-red-500' : 'text-green-500'}`}>
              {summary.net_calories}{' '}
              <span className="text-sm font-normal text-gray-400">kcal</span>
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {isOver
                ? `${Math.abs(deficit).toFixed(0)} kcal over TDEE`
                : `${deficit.toFixed(0)} kcal under TDEE`}
            </p>
            <p className="text-xs text-gray-400 mt-2">Calories consumed minus calories burned. Negative means a deficit; positive means a surplus.</p>
          </div>

          <div className="flex gap-3">
            <Link
              to="/food-log"
              className="flex-1 text-center bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 text-sm font-medium transition-colors"
            >
              Log Food
            </Link>
            <Link
              to="/activity-log"
              className="flex-1 text-center bg-teal-600 text-white py-2 rounded hover:bg-teal-700 text-sm font-medium transition-colors"
            >
              Log Activity
            </Link>
          </div>
        </>
      )}
    </Layout>
  )
}
