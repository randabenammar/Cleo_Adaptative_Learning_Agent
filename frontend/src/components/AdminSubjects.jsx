import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminSubjects() {
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    setLoading(true)
    try {
      const res = await axios.get('http://localhost:8000/api/admin/subjects')
      setSubjects(res.data.subjects)
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-white mx-auto mb-4"></div>
        <p className="text-white">Loading subjects...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Subject Analytics</h2>
            <p className="text-gray-300">Performance metrics by subject</p>
          </div>
          <button
            onClick={fetchSubjects}
            className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg font-semibold hover:bg-opacity-20 transition-all"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects.map((subject) => (
          <div
            key={subject.id}
            className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20 hover:bg-opacity-15 transition-all"
          >
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
              <div className="text-5xl">{subject.icon}</div>
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-bold text-white truncate">{subject.name}</h3>
                <p className="text-gray-400 text-sm">Subject #{subject.id}</p>
              </div>
            </div>

            {/* Stats */}
            <div className="space-y-4">
              
              {/* Total Sessions */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-300 text-sm">Total Sessions</span>
                  <span className="text-white font-bold">{subject.total_sessions}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-400 to-indigo-500 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min((subject.total_sessions / 100) * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Completion Rate */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-300 text-sm">Completed</span>
                  <span className="text-green-400 font-bold">{subject.completed_sessions}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full transition-all"
                    style={{ 
                      width: `${subject.total_sessions > 0 ? (subject.completed_sessions / subject.total_sessions) * 100 : 0}%` 
                    }}
                  />
                </div>
              </div>

              {/* Average Score */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-300 text-sm">Average Score</span>
                  <span className={`font-bold ${
                    subject.average_score >= 80 ? 'text-green-400' :
                    subject.average_score >= 60 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {subject.average_score.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      subject.average_score >= 80 ? 'bg-gradient-to-r from-green-400 to-emerald-500' :
                      subject.average_score >= 60 ? 'bg-gradient-to-r from-yellow-400 to-orange-500' :
                      'bg-gradient-to-r from-red-400 to-pink-500'
                    }`}
                    style={{ width: `${subject.average_score}%` }}
                  />
                </div>
              </div>

              {/* Popularity Badge */}
              <div className="pt-4 border-t border-white border-opacity-20">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 text-sm">Popularity</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    subject.popularity >= 50 ? 'bg-green-500 bg-opacity-20 text-green-300' :
                    subject.popularity >= 20 ? 'bg-yellow-500 bg-opacity-20 text-yellow-300' :
                    'bg-gray-500 bg-opacity-20 text-gray-300'
                  }`}>
                    {subject.popularity >= 50 ? '🔥 Hot' :
                     subject.popularity >= 20 ? '⭐ Popular' :
                     '📚 New'}
                  </span>
                </div>
              </div>

            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      {subjects.length > 0 && (
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <h3 className="text-xl font-bold text-white mb-4">Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-white mb-1">{subjects.length}</p>
              <p className="text-sm text-gray-300">Total Subjects</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-400 mb-1">
                {subjects.reduce((sum, s) => sum + s.total_sessions, 0)}
              </p>
              <p className="text-sm text-gray-300">Total Sessions</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-400 mb-1">
                {subjects.reduce((sum, s) => sum + s.completed_sessions, 0)}
              </p>
              <p className="text-sm text-gray-300">Completed</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-400 mb-1">
                {(subjects.reduce((sum, s) => sum + s.average_score, 0) / subjects.length).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-300">Avg Score</p>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}