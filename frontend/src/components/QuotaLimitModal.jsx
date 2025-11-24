import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function QuotaLimitModal({ error, onClose }) {
  const navigate = useNavigate()

  if (!error || error.error !== 'quota_exceeded') return null

  const handleUpgrade = () => {
    onClose()
    navigate('/pricing')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-fadeIn">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-orange-500 p-6 text-center">
          <div className="text-6xl mb-2">⚠️</div>
          <h2 className="text-2xl font-bold text-white">Quota Limit Reached</h2>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-gray-700 text-lg mb-4 text-center">
            {error.message}
          </p>

          {/* Usage Stats */}
          <div className="bg-red-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 font-semibold">Your Usage:</span>
              <span className="text-red-600 font-bold text-xl">
                {error.current_usage} / {error.limit}
              </span>
            </div>
            <div className="w-full bg-red-200 rounded-full h-2 mt-2">
              <div
                className="bg-red-600 h-2 rounded-full"
                style={{ width: '100%' }}
              />
            </div>
          </div>

          {/* Upgrade Suggestion */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mb-6 border-2 border-indigo-200">
            <p className="text-sm text-gray-700 text-center mb-2">
              💡 <strong>Upgrade to {error.upgrade_to.toUpperCase()}</strong> for more {error.quota_type}!
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleUpgrade}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-xl transition-all"
            >
              Upgrade Now
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}