import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import BloomRadarChart from '../components/BloomRadarChart'
import ProgressTimeline from '../components/ProgressTimeline'
import SubjectStats from '../components/SubjectStats'
import RecentActivity from '../components/RecentActivity'
import Recommendations from '../components/Recommendations'
import AchievementBadges from '../components/AchievementBadges'
import EmotionHistory from '../components/EmotionHistory'
import Navbar from '../components/Navbar' 
import SubscriptionWidget from '../components/SubscriptionWidget'  

export default function Dashboard() {
  const { user } = useAuth()
  
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const learnerId = user ? `user_${user.id}` : 'demo_learner'

  useEffect(() => {
    if (user) {
      fetchDashboard()
    }
  }, [user])

  const fetchDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Fetching dashboard for:', learnerId)
      const res = await axios.get(`http://localhost:8000/api/dashboard/${learnerId}`)
      console.log('Dashboard response:', res.data)
      setAnalytics(res.data.analytics)
    } catch (error) {
      console.error('Error fetching dashboard:', error)
      setError(error.message)
      setAnalytics(null)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <>
        {/* ⭐ Navbar AVANT le contenu */}
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">Loading your dashboard...</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchDashboard}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </>
    )
  }

  if (!analytics) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome, {user?.username}!</h2>
            <p className="text-gray-600 mb-6">Start taking quizzes to see your analytics!</p>
            <button
              onClick={() => window.location.href = '/quiz'}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Take Your First Quiz
            </button>
          </div>
        </div>
      </>
    )
  }

  const summary = analytics.summary || {}
  const bloomStats = analytics.bloom_stats || {}
  const subjectStats = analytics.subject_stats || []
  const temporalStats = analytics.temporal_stats || {}
  const strengths = analytics.strengths || []
  const weaknesses = analytics.weaknesses || []
  const recommendations = analytics.recommendations || []

  return (
    <>
      {/* ⭐ Navbar EN DEHORS du conteneur principal */}
      <Navbar />
      
      {/* Contenu principal */}
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
        <div className="max-w-7xl mx-auto">
          
          {/* Header avec nom utilisateur */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              📊 {user?.full_name || user?.username}'s Dashboard
            </h1>
            <p className="text-gray-600">
              Track your progress, identify strengths, and get personalized recommendations
            </p>
          </div>

          {/* ⭐ WIDGET D'ABONNEMENT */}
          <div className="mb-8">
            <SubscriptionWidget />
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Questions</p>
                  <p className="text-3xl font-bold text-gray-900">{summary.total_questions_answered || 0}</p>
                </div>
                <div className="text-4xl">📝</div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Accuracy</p>
                  <p className="text-3xl font-bold text-green-600">{summary.overall_accuracy?.toFixed(1) || 0}%</p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Study Time</p>
                  <p className="text-3xl font-bold text-purple-600">{Math.round(summary.total_time_minutes || 0)}m</p>
                </div>
                <div className="text-4xl">⏱️</div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Sessions</p>
                  <p className="text-3xl font-bold text-orange-600">{summary.completed_sessions || 0}</p>
                </div>
                <div className="text-4xl">🚀</div>
              </div>
            </div>
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            
            {/* Left Column - Bloom Radar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <span>🎓</span>
                  Bloom's Taxonomy
                </h3>
                <BloomRadarChart bloomStats={bloomStats} />
                <div className="mt-4 text-sm text-gray-600">
                  <p className="mb-2">
                    <strong>Current Level:</strong> {bloomStats.current_average_level || 1} / 6
                  </p>
                  <p>
                    <strong>Highest Mastered:</strong> Level {bloomStats.highest_mastered || 1}
                  </p>
                </div>
              </div>
            </div>

            {/* Middle Column - Subjects */}
            <div className="lg:col-span-2">
              <SubjectStats subjectStats={subjectStats} />
            </div>
          </div>

          {/* Progress Timeline */}
          <div className="mb-8">
            <ProgressTimeline temporalStats={temporalStats} />
          </div>

          {/* Emotional Journey */}
          <div className="mb-8">
            <EmotionHistory 
              emotionStats={analytics.emotion_stats} 
              temporalStats={temporalStats} 
            />
          </div>

          {/* Strengths, Weaknesses, Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            
            {/* Strengths & Weaknesses */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span>💪</span>
                Strengths & Areas to Improve
              </h3>
              
              {strengths.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-green-700 mb-2 uppercase">Strengths</h4>
                  <ul className="space-y-2">
                    {strengths.map((strength, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-green-500 flex-shrink-0">✓</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {weaknesses.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-amber-700 mb-2 uppercase">Areas to Improve</h4>
                  <ul className="space-y-2">
                    {weaknesses.map((weakness, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-amber-500 flex-shrink-0">→</span>
                        <span>{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {strengths.length === 0 && weaknesses.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-8">
                  Complete more quizzes to see your strengths and areas to improve
                </p>
              )}
            </div>

            {/* Recommendations */}
            <Recommendations recommendations={recommendations} />
          </div>

          {/* Achievement Badges */}
          <AchievementBadges analytics={analytics} />

          {/* Recent Activity */}
          <RecentActivity learnerId={learnerId} />

        </div>
      </div>
    </>
  )
}