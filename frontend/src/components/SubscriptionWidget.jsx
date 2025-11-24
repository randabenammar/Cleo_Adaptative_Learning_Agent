import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function SubscriptionWidget() {
  const [usage, setUsage] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUsage()
  }, [])

  const fetchUsage = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/subscriptions/usage', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUsage(res.data)
    } catch (error) {
      console.error('Error fetching usage:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-6 mb-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-full"></div>
      </div>
    )
  }

  if (!usage) return null

  const quizzesUsed = usage.usage.quizzes_this_month
  const quizzesLimit = usage.limits.quizzes_per_month
  const quizzesRemaining = usage.remaining.quizzes
  const quizzesPercentage = (quizzesUsed / quizzesLimit) * 100

  const getProgressColor = (percentage) => {
    if (percentage >= 90) return 'from-red-500 to-red-600'
    if (percentage >= 70) return 'from-orange-500 to-orange-600'
    if (percentage >= 50) return 'from-yellow-500 to-yellow-600'
    return 'from-green-500 to-green-600'
  }

  const getStatusEmoji = (percentage) => {
    if (percentage >= 90) return '🔴'
    if (percentage >= 70) return '🟠'
    if (percentage >= 50) return '🟡'
    return '🟢'
  }

  const progressGradient = getProgressColor(quizzesPercentage)
  const statusEmoji = getStatusEmoji(quizzesPercentage)

  return (
    <div className="bg-gradient-to-br from-white to-indigo-50 rounded-2xl shadow-xl p-6 mb-6 border border-indigo-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg">
            {usage.tier.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">
              Your Plan: <span className="text-indigo-600 uppercase">{usage.tier}</span>
            </h3>
            <p className="text-xs text-gray-500">Active subscription</p>
          </div>
        </div>
        <a
          href="/pricing"
          className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
        >
          Upgrade
        </a>
      </div>

      {/* Quizzes Usage */}
      <div className="space-y-4">
        {/* Quizzes */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{statusEmoji}</span>
              <span className="text-sm font-semibold text-gray-700">Quizzes This Month</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                {quizzesUsed} <span className="text-gray-400 text-lg">/ {quizzesLimit}</span>
              </div>
              <div className="text-xs text-gray-500">
                {quizzesRemaining} remaining
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
            <div
              className={`h-4 bg-gradient-to-r ${progressGradient} rounded-full transition-all duration-700 ease-out relative overflow-hidden`}
              style={{ width: `${Math.min(quizzesPercentage, 100)}%` }}
            >
              {/* Shine effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
            </div>
            
            {/* Percentage label inside bar */}
            {quizzesPercentage > 15 && (
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold text-white drop-shadow-lg">
                  {Math.round(quizzesPercentage)}%
                </span>
              </div>
            )}
          </div>

          {/* Warning message */}
          {quizzesPercentage >= 80 && quizzesPercentage < 100 && (
            <div className="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-lg flex items-center gap-2">
              <span className="text-orange-600">⚠️</span>
              <span className="text-xs text-orange-700 font-medium">
                You're approaching your monthly limit. Consider upgrading!
              </span>
            </div>
          )}

          {/* Limit reached */}
          {quizzesPercentage >= 100 && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
              <span className="text-red-600">🚫</span>
              <span className="text-xs text-red-700 font-medium">
                You've reached your monthly limit. Upgrade to continue!
              </span>
            </div>
          )}
        </div>

        {/* AI Hints (si disponible) */}
        {usage.limits.ai_hints_per_month > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">💡</span>
                <span className="text-xs font-medium text-gray-600">AI Hints</span>
              </div>
              <span className="text-sm font-bold text-gray-700">
                {usage.usage.ai_hints_this_month} / {usage.limits.ai_hints_per_month}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Reset Date */}
      <div className="mt-6 pt-4 border-t border-gray-200 flex items-center justify-center gap-2">
        <span className="text-gray-400">🔄</span>
        <span className="text-xs text-gray-500">
          Quotas reset on <span className="font-semibold text-gray-700">
            {new Date(usage.reset_date).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            })}
          </span>
        </span>
      </div>
    </div>
  )
}