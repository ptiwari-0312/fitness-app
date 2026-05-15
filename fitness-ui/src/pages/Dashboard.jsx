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

const WATER_GOAL_ML = 2500

function WaterCard({ totalMl, onAdd }) {
  const pct = Math.min((totalMl / WATER_GOAL_ML) * 100, 100)

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-4">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Water Intake</p>
      <p className="text-2xl font-bold text-blue-500">
        {totalMl} <span className="text-sm font-normal text-gray-400">/ {WATER_GOAL_ML} ml</span>
      </p>
      <p className="text-xs text-gray-400 mb-3">{pct.toFixed(0)}% of daily goal</p>

      <div className="w-full bg-gray-100 rounded-full h-2 mb-4">
        <div
          className="bg-blue-400 h-2 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="flex gap-2">
        {[250, 500, 750].map((ml) => (
          <button
            key={ml}
            onClick={() => onAdd(ml)}
            className="flex-1 text-sm bg-blue-50 text-blue-600 border border-blue-200 rounded py-1 hover:bg-blue-100 transition-colors font-medium"
          >
            +{ml} ml
          </button>
        ))}
      </div>
    </div>
  )
}

const CHART_HALF = 56 // px per side of the baseline

function WeeklyChart({ data }) {
  const maxAbs = Math.max(...data.map((d) => Math.abs(d.net_calories)), 1)

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-6">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-3">7-Day Net Calorie Trend</p>

      <div className="flex gap-1" style={{ height: CHART_HALF * 2 + 1 }}>
        {data.map((day) => {
          const ratio = Math.abs(day.net_calories) / maxAbs
          const barPx = day.net_calories === 0
            ? 0
            : Math.max(Math.round(ratio * CHART_HALF), 2)
          const isSurplus = day.net_calories > 0

          return (
            <div key={day.log_date} className="flex-1 flex flex-col">
              {/* Upper region — surplus bars grow downward from top */}
              <div className="flex items-end justify-center" style={{ height: CHART_HALF }}>
                {isSurplus && day.has_data && (
                  <div
                    className="w-full max-w-[28px] bg-orange-400 rounded-t"
                    style={{ height: barPx }}
                    title={`+${day.net_calories} kcal surplus`}
                  />
                )}
              </div>

              {/* Baseline */}
              <div className="h-px bg-gray-300 w-full" />

              {/* Lower region — deficit bars grow downward from baseline */}
              <div className="flex items-start justify-center" style={{ height: CHART_HALF }}>
                {!isSurplus && day.has_data && (
                  <div
                    className="w-full max-w-[28px] bg-green-400 rounded-b"
                    style={{ height: barPx }}
                    title={`${day.net_calories} kcal deficit`}
                  />
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Day labels */}
      <div className="flex gap-1 mt-1">
        {data.map((day) => {
          const label = new Date(day.log_date + 'T00:00:00').toLocaleDateString('en', {
            weekday: 'short',
          })
          return (
            <div key={day.log_date} className="flex-1 text-center text-xs text-gray-400">
              {label}
            </div>
          )
        })}
      </div>

      <div className="flex justify-between mt-2">
        <span className="text-xs text-green-500">↓ deficit</span>
        <span className="text-xs text-orange-400">↑ surplus</span>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [date, setDate] = useState(todayStr())
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState(null)
  const [waterLogs, setWaterLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchWater = (d) =>
    client.get(`/api/v1/water-logs?log_date=${d}`).then(({ data }) => setWaterLogs(data))

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      client.get(`/api/v1/dashboard/summary?log_date=${date}`),
      client.get('/api/v1/dashboard/weekly-trend'),
      client.get(`/api/v1/water-logs?log_date=${date}`),
    ])
      .then(([{ data: s }, { data: t }, { data: w }]) => {
        setSummary(s)
        setTrend(t)
        setWaterLogs(w)
      })
      .catch(() => setError('Failed to load summary'))
      .finally(() => setLoading(false))
  }, [date])

  const handleAddWater = async (ml) => {
    try {
      await client.post('/api/v1/water-logs', { amount_ml: ml, log_date: date })
      await fetchWater(date)
    } catch {
      setError('Failed to log water')
    }
  }

  const totalWaterMl = waterLogs.reduce((s, l) => s + l.amount_ml, 0)

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

          <WaterCard totalMl={totalWaterMl} onAdd={handleAddWater} />

          {trend && <WeeklyChart data={trend} />}

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
