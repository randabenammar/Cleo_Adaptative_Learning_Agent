import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Navbar from '../components/Navbar'  // ⭐ IMPORT
import AdminStats from '../components/AdminStats'
import AdminUserManagement from '../components/AdminUserManagement'
import AdminSubjectManagement from '../components/AdminSubjectManagement'

export default function AdminDashboard() {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (authLoading) return
    
    if (!user) {
      navigate('/signin', { replace: true })
      return
    }
    
    if (user.role !== 'admin') {
      navigate('/', { replace: true })
      return
    }
    
    fetchStats()
  }, [user, authLoading, navigate])

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('access_token')
      
      const res = await axios.get('http://localhost:8000/api/admin/stats', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setStats(res.data.stats)
    } catch (error) {
      console.error('Error fetching stats:', error)
      
      if (error.response?.status === 401) {
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
        navigate('/signin', { replace: true })
      } else {
        setError(error.response?.data?.detail || 'Failed to load stats')
      }
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'users', label: 'User Management', icon: '👥' },
    { id: 'subjects', label: 'Subject Management', icon: '📚' }
  ]

  if (authLoading || loading) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-white mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading admin dashboard...</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchStats}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600">
      
      {/* ⭐ Navbar unifié */}
      <Navbar />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">

        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <span>👑</span>
            Admin Dashboard
          </h1>
          <p className="text-white text-opacity-90">
            Welcome back, {user?.full_name || user?.username}
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white bg-opacity-10 rounded-xl p-2 mb-6 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-indigo-600 shadow-lg'
                    : 'text-white hover:bg-white hover:bg-opacity-10'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && <AdminStats stats={stats} />}
          {activeTab === 'users' && <AdminUserManagement />}
          {activeTab === 'subjects' && <AdminSubjectManagement />}
        </div>

      </div>
    </div>
  )
}