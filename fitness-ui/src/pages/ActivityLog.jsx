import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import client from '../api/client'

const todayStr = () => new Date().toISOString().split('T')[0]

export default function ActivityLog() {
  const [date, setDate] = useState(todayStr())
  const [logs, setLogs] = useState([])
  const [steps, setSteps] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchLogs = (d) =>
    client.get(`/api/v1/activity-logs?log_date=${d}`).then(({ data }) => setLogs(data))

  useEffect(() => { fetchLogs(date) }, [date])

  const handleAdd = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await client.post('/api/v1/activity-logs', {
        steps_count: Number(steps),
        log_date: date,
      })
      await fetchLogs(date)
      setSteps('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to log activity')
    } finally {
      setLoading(false)
    }
  }

  const totalSteps = logs.reduce((s, l) => s + l.steps_count, 0)
  const totalBurned = logs.reduce((s, l) => s + l.calories_burned, 0)

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-800">Activity Log</h1>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      <form onSubmit={handleAdd} className="bg-white shadow rounded-lg p-4 mb-5 flex gap-3 items-end">
        <div className="flex-1">
          <label className="text-xs text-gray-500 block mb-1">Steps count</label>
          <input
            type="number"
            min="1"
            value={steps}
            onChange={(e) => setSteps(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400"
            placeholder="e.g. 8000"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          Log Steps
        </button>
      </form>

      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

      {logs.length > 0 ? (
        <div className="bg-white shadow rounded-lg divide-y">
          {logs.map((log) => (
            <div key={log.id} className="flex items-center justify-between px-4 py-3">
              <p className="text-sm font-medium text-gray-800">
                {log.steps_count.toLocaleString()} steps
              </p>
              <p className="text-sm text-teal-600 font-semibold">{log.calories_burned} kcal</p>
            </div>
          ))}
          <div className="flex justify-between px-4 py-3 text-sm font-semibold text-gray-700">
            <span>{totalSteps.toLocaleString()} steps total</span>
            <span>{totalBurned.toFixed(1)} kcal burned</span>
          </div>
        </div>
      ) : (
        <p className="text-center text-gray-400 text-sm mt-10">No activity logged for this day.</p>
      )}
    </Layout>
  )
}
