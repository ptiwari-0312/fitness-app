import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import client from '../api/client'

const todayStr = () => new Date().toISOString().split('T')[0]

export default function FoodLog() {
  const [date, setDate] = useState(todayStr())
  const [foodItems, setFoodItems] = useState([])
  const [logs, setLogs] = useState([])
  const [form, setForm] = useState({ food_item_id: '', quantity_grams: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selectedItem = foodItems.find((f) => f.id === Number(form.food_item_id))
  const previewCals =
    selectedItem && form.quantity_grams
      ? ((selectedItem.calories_per_100g * Number(form.quantity_grams)) / 100).toFixed(1)
      : null

  useEffect(() => {
    client.get('/api/v1/food-items').then(({ data }) => setFoodItems(data))
  }, [])

  useEffect(() => {
    client.get(`/api/v1/food-logs?log_date=${date}`).then(({ data }) => setLogs(data))
  }, [date])

  const handleAdd = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await client.post('/api/v1/food-logs', {
        food_item_id: Number(form.food_item_id),
        quantity_grams: Number(form.quantity_grams),
        log_date: date,
      })
      const { data } = await client.get(`/api/v1/food-logs?log_date=${date}`)
      setLogs(data)
      setForm({ food_item_id: '', quantity_grams: '' })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add entry')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    await client.delete(`/api/v1/food-logs/${id}`)
    setLogs((prev) => prev.filter((l) => l.id !== id))
  }

  const totalCals = logs.reduce(
    (sum, l) => sum + (l.food_item.calories_per_100g * l.quantity_grams) / 100,
    0
  )

  const inputClass = 'w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400'

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-800">Food Log</h1>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      <form onSubmit={handleAdd} className="bg-white shadow rounded-lg p-4 mb-5 flex gap-3 items-end">
        <div className="flex-1">
          <label className="text-xs text-gray-500 block mb-1">Food item</label>
          <select
            value={form.food_item_id}
            onChange={(e) => setForm({ ...form, food_item_id: e.target.value })}
            className={inputClass}
            required
          >
            <option value="">Select…</option>
            {foodItems.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.calories_per_100g} kcal / 100g)
              </option>
            ))}
          </select>
        </div>
        <div className="w-36">
          <label className="text-xs text-gray-500 block mb-1">
            Grams{previewCals && <span className="text-indigo-500 ml-1">≈ {previewCals} kcal</span>}
          </label>
          <input
            type="number"
            min="1"
            value={form.quantity_grams}
            onChange={(e) => setForm({ ...form, quantity_grams: e.target.value })}
            className={inputClass}
            placeholder="e.g. 150"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          Add
        </button>
      </form>

      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

      {logs.length > 0 ? (
        <div className="bg-white shadow rounded-lg divide-y">
          {logs.map((log) => {
            const cals = ((log.food_item.calories_per_100g * log.quantity_grams) / 100).toFixed(1)
            return (
              <div key={log.id} className="flex items-center justify-between px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-gray-800">{log.food_item.name}</p>
                  <p className="text-xs text-gray-400">{log.quantity_grams} g · {cals} kcal</p>
                </div>
                <button
                  onClick={() => handleDelete(log.id)}
                  className="text-xs text-red-400 hover:text-red-600 transition-colors"
                >
                  Remove
                </button>
              </div>
            )
          })}
          <div className="flex justify-between px-4 py-3 text-sm font-semibold text-gray-700">
            <span>Total</span>
            <span>{totalCals.toFixed(1)} kcal</span>
          </div>
        </div>
      ) : (
        <p className="text-center text-gray-400 text-sm mt-10">No food logged for this day.</p>
      )}
    </Layout>
  )
}
