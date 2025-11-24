import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function RecentActivity({ learnerId }) {
  const [recentSessions, setRecentSessions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRecentActivity()
  }, [learnerId])

  const fetchRecentActivity = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/quiz/history/${learnerId}?limit=5`)
      setRecentSessions(res.data.sessions || [])
    } catch (error) {
      console.error('Error fetching recent activity:', error)
      setRecentSessions([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📜 Recent Activity</h3>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  if (recentSessions.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>📜</span>
          Recent Activity
        </h3>
        <p className="text-sm text-gray-500 text-center py-8">
          No recent activity. Start a quiz to see your history!
        </p>
      </div>
    )
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>📜</span>
        Recent Activity
      </h3>

      <div className="space-y-3">
        {recentSessions.map((session, idx) => {
          const scorePercentage = session.score_percentage || 0
          const isCompleted = session.status === 'completed'

          return (
            <div
              key={session.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-bold text-gray-900">{session.subject_name}</h4>
                    {isCompleted && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
                        Completed
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{session.topic}</p>
                </div>

                <div className="text-right">
                  <p className={`text-2xl font-bold ${
                    scorePercentage >= 80 ? 'text-green-600' :
                    scorePercentage >= 60 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {scorePercentage.toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-500">{formatDate(session.started_at)}</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-2 text-xs text-gray-600">
                <div>
                  <span className="font-semibold">{session.questions_answered}</span>/{session.total_questions} Q
                </div>
                <div>
                  <span className="font-semibold">{session.correct_answers}</span> correct
                </div>
                <div>
                  Bloom <span className="font-semibold">L{session.bloom_level}</span>
                </div>
                <div>
                  {Math.floor(session.time_spent_seconds / 60)}m {session.time_spent_seconds % 60}s
                </div>
              </div>

              {/* Mini Progress Bar */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      scorePercentage >= 80 ? 'bg-green-500' :
                      scorePercentage >= 60 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${scorePercentage}%` }}
                  />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}