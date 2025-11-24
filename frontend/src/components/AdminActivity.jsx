import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminActivity() {
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchActivity()
  }, [])

  const fetchActivity = async () => {
    setLoading(true)
    try {
      const res = await axios.get('http://localhost:8000/api/admin/activity?limit=50')
      setActivities(res.data.activities)
    } catch (error) {
      console.error('Error fetching activity:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (type) => {
    const icons = {
      quiz_session: '📝',
      badge_earned: '🏆',
      level_up: '⬆️',
      comment: '💬',
      follow: '👥'
    }
    return icons[type] || '🔔'
  }

  const getActivityColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 bg-opacity-20 text-green-300'
      case 'in_progress':
        return 'bg-blue-500 bg-opacity-20 text-blue-300'
      case 'abandoned':
        return 'bg-red-500 bg-opacity-20 text-red-300'
      default:
        return 'bg-gray-500 bg-opacity-20 text-gray-300'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-white mx-auto mb-4"></div>
        <p className="text-white">Loading activity...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Recent Activity</h2>
            <p className="text-gray-300">Live feed of platform activity</p>
          </div>
          <button
            onClick={fetchActivity}
            className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg font-semibold hover:bg-opacity-20 transition-all"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="space-y-3">
        {activities.length === 0 ? (
          <div className="bg-white bg-opacity-10 rounded-xl p-12 backdrop-blur-sm border border-white border-opacity-20 text-center">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-white text-lg font-semibold mb-2">No activity yet</p>
            <p className="text-gray-400">Activity will appear here as users interact with the platform</p>
          </div>
        ) : (
          activities.map((activity, index) => (
            <div
              key={index}
              className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20 hover:bg-opacity-15 transition-all"
            >
              <div className="flex items-start gap-4">
                
                {/* Icon */}
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-2xl">
                  {getActivityIcon(activity.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div>
                      <p className="text-white font-semibold">
                        {activity.user?.username || 'Unknown User'}
                      </p>
                      <p className="text-gray-400 text-sm">
                        {activity.type === 'quiz_session' && (
                          <>
                            Completed <span className="text-indigo-400 font-semibold">{activity.data.subject}</span> quiz
                          </>
                        )}
                      </p>
                    </div>
                    <span className="text-gray-400 text-sm whitespace-nowrap">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>

                  {/* Quiz Details */}
                  {activity.type === 'quiz_session' && (
                    <div className="flex items-center gap-4 mt-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getActivityColor(activity.data.status)}`}>
                        {activity.data.status}
                      </span>
                      
                      {activity.data.score !== null && activity.data.score !== undefined && (
                        <span className={`text-lg font-bold ${getScoreColor(activity.data.score)}`}>
                          {activity.data.score.toFixed(0)}%
                        </span>
                      )}
                      
                      <span className="text-gray-400 text-sm">
                        Level {activity.data.bloom_level}
                      </span>
                    </div>
                  )}
                </div>

              </div>
            </div>
          ))
        )}
      </div>

    </div>
  )
}