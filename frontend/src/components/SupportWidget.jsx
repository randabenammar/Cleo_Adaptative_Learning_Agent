import React, { useState } from 'react'
import StressTechniques from './StressTechniques'

export default function SupportWidget({ supportData, onDismiss, onFeedback }) {
  const [showTechniques, setShowTechniques] = useState(false)
  const [feedbackGiven, setFeedbackGiven] = useState(false)

  if (!supportData) return null

  const { intervention, supportMessage, decision } = supportData

  const handleFeedback = (wasHelpful, actionTaken) => {
    setFeedbackGiven(true)
    if (onFeedback) {
      onFeedback(intervention.id, wasHelpful, actionTaken)
    }
    
    // Auto-dismiss après 2 secondes
    setTimeout(() => {
      onDismiss()
    }, 2000)
  }

  const severityColors = {
    high: 'border-red-400 bg-red-50',
    medium: 'border-yellow-400 bg-yellow-50',
    low: 'border-blue-400 bg-blue-50'
  }

  const severityIcons = {
    high: '🚨',
    medium: '⚠️',
    low: '💡'
  }

  if (showTechniques) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto">
          <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-900">🧘 Stress Relief Techniques</h3>
            <button
              onClick={() => setShowTechniques(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <StressTechniques onClose={() => setShowTechniques(false)} />
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className={`bg-white rounded-2xl shadow-2xl max-w-lg w-full border-4 ${severityColors[decision.severity]} animate-scale-up`}>
        
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <span className="text-5xl">{severityIcons[decision.severity]}</span>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">CLEO is here for you</h3>
                <p className="text-sm text-gray-600">Emotional Support Check-in</p>
              </div>
            </div>
            <button
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Reasons */}
          {decision.reasons && decision.reasons.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-3 mt-3">
              <p className="text-xs font-semibold text-gray-700 mb-1">Detected:</p>
              <ul className="text-xs text-gray-600 space-y-1">
                {decision.reasons.map((reason, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="text-orange-500">•</span>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Message */}
          <div className="mb-6">
            <p className="text-lg text-gray-800 leading-relaxed">
              {supportMessage.message}
            </p>
          </div>

          {/* Suggestions */}
          {supportMessage.suggestions && supportMessage.suggestions.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>💡</span>
                Suggestions
              </h4>
              <ul className="space-y-2">
                {supportMessage.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-start gap-2 bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                    <span className="text-indigo-600 flex-shrink-0">→</span>
                    <span className="text-sm text-gray-700">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Encouragement */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200 mb-6">
            <p className="text-sm text-gray-800 font-medium text-center">
              ✨ {supportMessage.encouragement}
            </p>
          </div>

          {/* Actions */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {supportMessage.recommended_action === 'break' && (
              <button
                onClick={() => handleFeedback(true, 'break_taken')}
                className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-3 rounded-lg font-semibold hover:from-green-600 hover:to-emerald-600 transition-all shadow-md"
              >
                ✅ Take a Break
              </button>
            )}
            
            <button
              onClick={() => setShowTechniques(true)}
              className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-4 py-3 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-600 transition-all shadow-md"
            >
              🧘 Stress Techniques
            </button>

            <button
              onClick={() => handleFeedback(true, 'continued')}
              className="bg-gray-200 text-gray-700 px-4 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-all"
            >
              Continue Learning
            </button>
          </div>

          {/* Feedback Success */}
          {feedbackGiven && (
            <div className="text-center text-green-600 font-semibold animate-pulse">
              ✓ Thank you for your feedback!
            </div>
          )}
        </div>

      </div>
    </div>
  )
}