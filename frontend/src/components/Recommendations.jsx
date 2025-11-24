import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Recommendations({ recommendations }) {
  const navigate = useNavigate()

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>💡</span>
          Recommendations
        </h3>
        <p className="text-sm text-gray-500 text-center py-8">
          Complete more activities to get personalized recommendations
        </p>
      </div>
    )
  }

  const priorityColors = {
    high: 'border-red-300 bg-red-50',
    medium: 'border-yellow-300 bg-yellow-50',
    low: 'border-blue-300 bg-blue-50'
  }

  const priorityIcons = {
    high: '🔥',
    medium: '⚡',
    low: '💡'
  }

  const handleAction = (recommendation) => {
    // Router vers l'action appropriée
    if (recommendation.type === 'getting_started') {
      navigate('/')
    } else if (recommendation.type === 'bloom_level' || recommendation.type === 'level_up') {
      navigate('/quiz')
    } else if (recommendation.type === 'subject_review') {
      navigate('/')
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>💡</span>
        Personalized Recommendations
      </h3>

      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <div
            key={idx}
            className={`border-2 rounded-lg p-4 transition-all hover:shadow-md ${
              priorityColors[rec.priority] || priorityColors.low
            }`}
          >
            <div className="flex items-start gap-3">
              <span className="text-3xl flex-shrink-0">
                {priorityIcons[rec.priority] || '💡'}
              </span>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-gray-900">{rec.title}</h4>
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                    rec.priority === 'high' ? 'bg-red-200 text-red-800' :
                    rec.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-blue-200 text-blue-800'
                  }`}>
                    {rec.priority?.toUpperCase()}
                  </span>
                </div>

                <p className="text-sm text-gray-700 mb-3">
                  {rec.description}
                </p>

                <button
                  onClick={() => handleAction(rec)}
                  className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1 transition-colors"
                >
                  {rec.action}
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}