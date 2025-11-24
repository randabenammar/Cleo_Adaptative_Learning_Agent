import React from 'react'

export default function AchievementBadges({ analytics }) {
  const summary = analytics?.summary || {}
  const bloomStats = analytics?.bloom_stats || {}
  const subjectStats = analytics?.subject_stats || []

  // Calculer les badges débloqués
  const badges = []

  // Badge première session
  if (summary.total_sessions >= 1) {
    badges.push({
      id: 'first_session',
      name: 'First Steps',
      description: 'Completed your first quiz session',
      icon: '🎯',
      color: 'bg-blue-100 border-blue-300'
    })
  }

  // Badge 10 sessions
  if (summary.completed_sessions >= 10) {
    badges.push({
      id: 'ten_sessions',
      name: 'Dedicated Learner',
      description: 'Completed 10 quiz sessions',
      icon: '🏆',
      color: 'bg-yellow-100 border-yellow-300'
    })
  }

  // Badge accuracy
  if (summary.overall_accuracy >= 80 && summary.total_questions_answered >= 20) {
    badges.push({
      id: 'high_accuracy',
      name: 'Accuracy Master',
      description: '80%+ accuracy with 20+ questions',
      icon: '🎖️',
      color: 'bg-green-100 border-green-300'
    })
  }

  // Badge perfectionniste
  if (summary.overall_accuracy >= 95 && summary.total_questions_answered >= 10) {
    badges.push({
      id: 'perfectionist',
      name: 'Perfectionist',
      description: '95%+ accuracy',
      icon: '💎',
      color: 'bg-purple-100 border-purple-300'
    })
  }

  // Badge Bloom level
  if (bloomStats.highest_mastered >= 4) {
    badges.push({
      id: 'bloom_master',
      name: 'Critical Thinker',
      description: 'Mastered Bloom Level 4 (Analyze)',
      icon: '🧠',
      color: 'bg-indigo-100 border-indigo-300'
    })
  }

  // Badge multi-sujet
  const masteredSubjects = subjectStats.filter(s => s.accuracy >= 85 && s.total_questions >= 10)
  if (masteredSubjects.length >= 3) {
    badges.push({
      id: 'polymath',
      name: 'Polymath',
      description: 'Mastered 3+ subjects',
      icon: '📚',
      color: 'bg-pink-100 border-pink-300'
    })
  }

  // Badge temps d'étude
  if (summary.total_time_minutes >= 120) {
    badges.push({
      id: 'time_invested',
      name: 'Time Investor',
      description: '2+ hours of study time',
      icon: '⏰',
      color: 'bg-orange-100 border-orange-300'
    })
  }

  // Badge streak (si disponible - à implémenter)
  // if (analytics.streak_days >= 3) { ... }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 mb-8">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>🏅</span>
        Your Achievements
      </h3>

      {badges.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-6xl mb-4">🎯</div>
          <p className="text-gray-600 mb-2">No badges yet!</p>
          <p className="text-sm text-gray-500">Keep learning to unlock achievements</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {badges.map((badge, idx) => (
            <div
              key={badge.id}
              className={`border-2 rounded-xl p-4 text-center transition-all hover:scale-105 hover:shadow-lg ${badge.color} animate-fade-in`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <div className="text-5xl mb-2">{badge.icon}</div>
              <h4 className="font-bold text-gray-900 text-sm mb-1">{badge.name}</h4>
              <p className="text-xs text-gray-600">{badge.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Locked Badges Preview */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">🔒 Upcoming Achievements</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {!badges.find(b => b.id === 'ten_sessions') && summary.completed_sessions < 10 && (
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-center opacity-60">
              <div className="text-3xl mb-1">🏆</div>
              <p className="text-xs text-gray-600">10 Sessions</p>
            </div>
          )}
          {!badges.find(b => b.id === 'high_accuracy') && summary.overall_accuracy < 80 && (
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-center opacity-60">
              <div className="text-3xl mb-1">🎖️</div>
              <p className="text-xs text-gray-600">80% Accuracy</p>
            </div>
          )}
          {!badges.find(b => b.id === 'bloom_master') && bloomStats.highest_mastered < 4 && (
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-center opacity-60">
              <div className="text-3xl mb-1">🧠</div>
              <p className="text-xs text-gray-600">Bloom Level 4</p>
            </div>
          )}
          {!badges.find(b => b.id === 'time_invested') && summary.total_time_minutes < 120 && (
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-3 text-center opacity-60">
              <div className="text-3xl mb-1">⏰</div>
              <p className="text-xs text-gray-600">2h Study Time</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}