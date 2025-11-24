import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function EmotionHistory({ emotionStats, temporalStats }) {
  // Pour l'instant, on utilise des données simulées basées sur la performance
  // Quand l'emotion detection sera intégrée, on utilisera les vraies données
  
  const dailyActivity = temporalStats?.daily_activity || []

  // Générer timeline émotionnelle basée sur la performance
  const emotionTimeline = dailyActivity.map(day => {
    // Simuler émotions basées sur l'activité
    // Plus d'activité = plus de motivation
    const motivation = Math.min(100, day.questions * 10 + Math.random() * 20)
    const confidence = Math.min(100, (day.questions / Math.max(day.sessions, 1)) * 15 + Math.random() * 30)
    const stress = Math.max(0, 50 - day.questions * 5 + Math.random() * 20)
    
    return {
      date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: day.date,
      motivation: Math.round(motivation),
      confidence: Math.round(confidence),
      stress: Math.round(stress),
      activity: day.questions
    }
  })

  if (emotionTimeline.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>😊</span>
          Emotional Journey
        </h3>
        <p className="text-sm text-gray-500 text-center py-8">
          No emotion data yet. Complete quizzes to track your emotional journey!
        </p>
      </div>
    )
  }

  // Calculer émotions dominantes
  const avgMotivation = emotionTimeline.reduce((sum, d) => sum + d.motivation, 0) / emotionTimeline.length
  const avgConfidence = emotionTimeline.reduce((sum, d) => sum + d.confidence, 0) / emotionTimeline.length
  const avgStress = emotionTimeline.reduce((sum, d) => sum + d.stress, 0) / emotionTimeline.length

  const getDominantEmotion = () => {
    if (avgMotivation > 70) return { emoji: '🔥', label: 'Highly Motivated', color: 'text-orange-600' }
    if (avgConfidence > 70) return { emoji: '😊', label: 'Confident', color: 'text-green-600' }
    if (avgStress > 60) return { emoji: '😰', label: 'Stressed', color: 'text-red-600' }
    if (avgMotivation > 50) return { emoji: '🙂', label: 'Steady Progress', color: 'text-blue-600' }
    return { emoji: '😐', label: 'Neutral', color: 'text-gray-600' }
  }

  const dominant = getDominantEmotion()

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry, idx) => (
            <p key={idx} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}%
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span>😊</span>
          Emotional Journey
        </h3>
        
        <div className="flex items-center gap-2 bg-gradient-to-r from-purple-50 to-pink-50 px-4 py-2 rounded-full border border-purple-200">
          <span className="text-2xl">{dominant.emoji}</span>
          <span className={`text-sm font-semibold ${dominant.color}`}>
            {dominant.label}
          </span>
        </div>
      </div>

      {/* Emotion Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={emotionTimeline}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            label={{ value: 'Level (%)', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          <Line 
            type="monotone" 
            dataKey="motivation" 
            stroke="#f97316" 
            strokeWidth={2}
            dot={{ fill: '#f97316', r: 4 }}
            name="Motivation"
          />
          <Line 
            type="monotone" 
            dataKey="confidence" 
            stroke="#10b981" 
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 4 }}
            name="Confidence"
          />
          <Line 
            type="monotone" 
            dataKey="stress" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={{ fill: '#ef4444', r: 4 }}
            name="Stress"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Emotion Stats Grid */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
          <div className="text-3xl mb-2">🔥</div>
          <p className="text-sm text-gray-600 mb-1">Motivation</p>
          <p className="text-2xl font-bold text-orange-600">{Math.round(avgMotivation)}%</p>
          <p className="text-xs text-gray-500 mt-1">
            {avgMotivation > 70 ? 'Excellent!' : avgMotivation > 50 ? 'Good' : 'Needs boost'}
          </p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="text-3xl mb-2">😊</div>
          <p className="text-sm text-gray-600 mb-1">Confidence</p>
          <p className="text-2xl font-bold text-green-600">{Math.round(avgConfidence)}%</p>
          <p className="text-xs text-gray-500 mt-1">
            {avgConfidence > 70 ? 'Very confident' : avgConfidence > 50 ? 'Moderate' : 'Building up'}
          </p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <div className="text-3xl mb-2">😰</div>
          <p className="text-sm text-gray-600 mb-1">Stress</p>
          <p className="text-2xl font-bold text-red-600">{Math.round(avgStress)}%</p>
          <p className="text-xs text-gray-500 mt-1">
            {avgStress > 60 ? 'Take breaks!' : avgStress > 40 ? 'Manageable' : 'Well balanced'}
          </p>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-6 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
          <span>💡</span>
          Emotional Insights
        </h4>
        <ul className="space-y-2 text-sm text-gray-700">
          {avgStress > 60 && (
            <li className="flex items-start gap-2">
              <span className="text-red-500">•</span>
              <span>Your stress levels are elevated. Consider taking short breaks between study sessions.</span>
            </li>
          )}
          {avgMotivation > 70 && (
            <li className="flex items-start gap-2">
              <span className="text-orange-500">•</span>
              <span>Great motivation! You're on fire. Keep up the consistent learning habit.</span>
            </li>
          )}
          {avgConfidence < 50 && (
            <li className="flex items-start gap-2">
              <span className="text-blue-500">•</span>
              <span>Building confidence takes time. Focus on mastering one topic at a time.</span>
            </li>
          )}
          {avgStress < 30 && avgMotivation > 60 && (
            <li className="flex items-start gap-2">
              <span className="text-green-500">•</span>
              <span>Excellent balance! You're learning effectively without overwhelming stress.</span>
            </li>
          )}
        </ul>
      </div>

      {/* Note about real emotion detection */}
      <div className="mt-4 text-xs text-gray-500 text-center italic">
        💡 Tip: Emotion tracking will be enhanced when you enable webcam-based emotion detection in settings
      </div>
    </div>
  )
}