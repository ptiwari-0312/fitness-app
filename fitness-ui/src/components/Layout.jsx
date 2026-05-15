import { NavLink, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const navClass = ({ isActive }) =>
  `text-sm font-medium hover:text-indigo-200 transition-colors ${isActive ? 'text-white underline underline-offset-4' : 'text-indigo-100'}`

export default function Layout({ children }) {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-indigo-600 px-6 py-3 flex items-center justify-between">
        <div className="flex gap-6">
          <NavLink to="/dashboard" className={navClass}>Dashboard</NavLink>
          <NavLink to="/food-log" className={navClass}>Food Log</NavLink>
          <NavLink to="/activity-log" className={navClass}>Activity</NavLink>
          <NavLink to="/profile" className={navClass}>Profile</NavLink>
        </div>
        <button
          onClick={handleLogout}
          className="text-xs bg-indigo-700 hover:bg-indigo-800 text-white px-3 py-1.5 rounded transition-colors"
        >
          Logout
        </button>
      </nav>
      <main className="max-w-2xl mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
