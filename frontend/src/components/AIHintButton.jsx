import React, { useState } from 'react'
import axios from 'axios'

export default function AIHintButton({ sessionId, questionId }) {
  const [loading, setLoading] = useState(false)
  const [hint, setHint] = useState(null)
  const [error, setError] = useState(null)
  const [showModal, setShowModal] = useState(false)

  const getHint = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('access_token')
      
      const res = await axios.post(
        'http://localhost:8000/api/quiz/get-hint',
        { session_id: sessionId, question_id: questionId },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      console.log('💡 Hint received:', res.data)
      setHint(res.data)
      setShowModal(true)
      
    } catch (err) {
      console.error('❌ Error getting hint:', err)
      
      if (err.response?.status === 403) {
        const errorData = err.response.data
        if (errorData.error === 'quota_exceeded') {
          setError({
            type: 'quota',
            message: errorData.message,
            upgrade_to: errorData.upgrade_to
          })
        } else if (errorData.error === 'feature_locked') {
          setError({
            type: 'locked',
            message: 'AI Hints are only available for premium users',
            upgrade_to: 'bronze'
          })
        }
        setShowModal(true)
      } else {
        alert('Error getting hint')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Hint Button */}
      <button
        onClick={getHint}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-semibold rounded-lg hover:from-yellow-500 hover:to-orange-600 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span className="text-xl">💡</span>
        {loading ? 'Getting hint...' : 'Get AI Hint'}
      </button>

      {/* Hint Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            {error ? (
              // Error state
              <>
                <div className="text-center mb-4">
                  <div className="text-6xl mb-4">
                    {error.type === 'quota' ? '🚫' : '🔒'}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {error.type === 'quota' ? 'Quota Exceeded' : 'Premium Feature'}
                  </h3>
                  <p className="text-gray-600">{error.message}</p>
                </div>
                
                <div className="space-y-3">
                  <a
                    href="/pricing"
                    className="block w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all text-center"
                  >
                    Upgrade to {error.upgrade_to.toUpperCase()}
                  </a>
                  <button
                    onClick={() => setShowModal(false)}
                    className="block w-full px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </>
            ) : (
              // Success state
              <>
                <div className="flex items-center gap-3 mb-4">
                  <div className="text-4xl">💡</div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">AI Hint</h3>
                    <p className="text-sm text-gray-500">
                      {hint.usage.hints_remaining} hints remaining this month
                    </p>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <p className="text-gray-800 leading-relaxed">{hint.hint}</p>
                </div>
                
                <button
                  onClick={() => setShowModal(false)}
                  className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all"
                >
                  Got it, thanks!
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}