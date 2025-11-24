import React from 'react'

export default function AdminStats({ stats }) {
  if (!stats) return null

  const { users, quizzes, content } = stats

  return (
    <div className="space-y-6">
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Total Users */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <div className="flex items-center justify-between mb-4">
            <div className="text-5xl">👥</div>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              users.growth_rate > 0 ? 'bg-green-500 bg-opacity-20 text-green-300' : 'bg-gray-500 bg-opacity-20 text-gray-300'
            }`}>
              {users.growth_rate > 0 ? '+' : ''}{users.growth_rate.toFixed(1)}%
            </div>
          </div>
          <p className="text-sm text-gray-300 mb-1">Total Users</p>
          <p className="text-4xl font-bold text-white mb-2">{users.total}</p>
          <p className="text-xs text-gray-400">
            {users.new_this_week} new this week
          </p>
        </div>

        {/* Active Users */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <div className="flex items-center justify-between mb-4">
            <div className="text-5xl">🟢</div>
            <div className="px-3 py-1 rounded-full text-sm font-semibold bg-blue-500 bg-opacity-20 text-blue-300">
              {((users.active_last_month / users.total) * 100).toFixed(0)}%
            </div>
          </div>
          <p className="text-sm text-gray-300 mb-1">Active Users</p>
          <p className="text-4xl font-bold text-white mb-2">{users.active_last_month}</p>
          <p className="text-xs text-gray-400">
            Last 30 days
          </p>
        </div>

        {/* Total Quizzes */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <div className="flex items-center justify-between mb-4">
            <div className="text-5xl">📝</div>
            <div className="px-3 py-1 rounded-full text-sm font-semibold bg-purple-500 bg-opacity-20 text-purple-300">
              {quizzes.completion_rate.toFixed(0)}%
            </div>
          </div>
          <p className="text-sm text-gray-300 mb-1">Quiz Sessions</p>
          <p className="text-4xl font-bold text-white mb-2">{quizzes.total_sessions}</p>
          <p className="text-xs text-gray-400">
            {quizzes.sessions_24h} in last 24h
          </p>
        </div>

        {/* Average Score */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <div className="flex items-center justify-between mb-4">
            <div className="text-5xl">🎯</div>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              quizzes.average_score >= 70 ? 'bg-green-500 bg-opacity-20 text-green-300' : 'bg-yellow-500 bg-opacity-20 text-yellow-300'
            }`}>
              {quizzes.average_score >= 70 ? 'Good' : 'Fair'}
            </div>
          </div>
          <p className="text-sm text-gray-300 mb-1">Average Score</p>
          <p className="text-4xl font-bold text-white mb-2">{quizzes.average_score}%</p>
          <p className="text-xs text-gray-400">
            Across all quizzes
          </p>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* User Breakdown */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>👥</span>
            User Statistics
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total Registered</span>
              <span className="text-white font-bold text-xl">{users.total}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Active Accounts</span>
              <span className="text-green-400 font-bold text-xl">{users.active}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Verified Users</span>
              <span className="text-blue-400 font-bold text-xl">{users.verified}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">New This Week</span>
              <span className="text-purple-400 font-bold text-xl">{users.new_this_week}</span>
            </div>

            <div className="pt-4 border-t border-white border-opacity-20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-300 text-sm">Engagement Rate</span>
                <span className="text-white font-semibold">
                  {((users.active_last_month / users.total) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${(users.active_last_month / users.total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Quiz Breakdown */}
        <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📊</span>
            Quiz Statistics
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total Sessions</span>
              <span className="text-white font-bold text-xl">{quizzes.total_sessions}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Completed</span>
              <span className="text-green-400 font-bold text-xl">{quizzes.completed_sessions}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Average Score</span>
              <span className="text-blue-400 font-bold text-xl">{quizzes.average_score}%</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Last 24 Hours</span>
              <span className="text-purple-400 font-bold text-xl">{quizzes.sessions_24h}</span>
            </div>

            <div className="pt-4 border-t border-white border-opacity-20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-300 text-sm">Completion Rate</span>
                <span className="text-white font-semibold">
                  {quizzes.completion_rate.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-purple-400 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: `${quizzes.completion_rate}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Stats */}
      <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span>📚</span>
          Content Library
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-4xl mb-2">📚</div>
            <p className="text-3xl font-bold text-white mb-1">{content.total_subjects}</p>
            <p className="text-sm text-gray-300">Subjects</p>
          </div>
          
          <div className="text-center">
            <div className="text-4xl mb-2">❓</div>
            <p className="text-3xl font-bold text-white mb-1">{content.total_questions}</p>
            <p className="text-sm text-gray-300">Questions</p>
          </div>
          
          <div className="text-center">
            <div className="text-4xl mb-2">📈</div>
            <p className="text-3xl font-bold text-white mb-1">
              {Math.round(content.total_questions / content.total_subjects)}
            </p>
            <p className="text-sm text-gray-300">Avg per Subject</p>
          </div>
          
          <div className="text-center">
            <div className="text-4xl mb-2">🎯</div>
            <p className="text-3xl font-bold text-white mb-1">6</p>
            <p className="text-sm text-gray-300">Bloom Levels</p>
          </div>
        </div>
      </div>

    </div>
  )
}