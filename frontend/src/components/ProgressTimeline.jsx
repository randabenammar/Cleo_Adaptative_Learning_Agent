import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ProgressTimeline({ temporalStats }) {
  const dailyActivity = temporalStats?.daily_activity || []

  if (dailyActivity.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>📈</span>
          Activity Timeline
        </h3>
        <p className="text-sm text-gray-500 text-center py-8">
          No activity data yet
        </p>
      </div>
    )
  }

  const chartData = dailyActivity.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    questions: day.questions,
    sessions: day.sessions
  }))

  const trend = temporalStats?.weekly_trend || 'stable'
  const trendEmoji = {
    'increasing': '📈',
    'decreasing': '📉',
    'stable': '➡️',
    'insufficient_data': '❓'
  }[trend] || '➡️'

  const trendText = {
    'increasing': 'Your activity is increasing! Keep it up!',
    'decreasing': 'Your activity decreased. Try to stay consistent.',
    'stable': 'Your activity is stable. Great consistency!',
    'insufficient_data': 'Not enough data yet to determine trend'
  }[trend] || ''

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span>📈</span>
          Activity Timeline (Last 7 Days)
        </h3>
        <div className="text-sm">
          <span className="text-2xl mr-2">{trendEmoji}</span>
          <span className="text-gray-600">{trendText}</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="questions" 
            stroke="#6366f1" 
            strokeWidth={3}
            dot={{ fill: '#6366f1', r: 4 }}
            name="Questions Answered"
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="bg-indigo-50 rounded-lg p-3">
          <p className="text-sm text-gray-600 mb-1">Total Days Active</p>
          <p className="text-2xl font-bold text-indigo-600">{temporalStats.total_days_active || 0}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-sm text-gray-600 mb-1">Most Active Day</p>
          <p className="text-2xl font-bold text-green-600">
            {dailyActivity.reduce((max, day) => day.questions > max.questions ? day : max, dailyActivity[0])?.day_name?.slice(0, 3) || 'N/A'}
          </p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <p className="text-sm text-gray-600 mb-1">Avg Questions/Day</p>
          <p className="text-2xl font-bold text-purple-600">
            {Math.round(dailyActivity.reduce((sum, day) => sum + day.questions, 0) / dailyActivity.length) || 0}
          </p>
        </div>
      </div>
    </div>
  )
}