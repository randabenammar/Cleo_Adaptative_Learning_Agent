import React, { useState } from 'react'
import BloomProgressRing from './BloomProgressRing'
import LearningPathTimeline from './LearningPathTimeline'

export default function SubjectOverview({ subject, onClose, onEnroll }) {
  const [activeTab, setActiveTab] = useState('overview') // overview, path, concepts

  const bloomLevels = [
    { level: 1, label: 'Remember', color: 'bg-blue-500' },
    { level: 2, label: 'Understand', color: 'bg-green-500' },
    { level: 3, label: 'Apply', color: 'bg-yellow-500' },
    { level: 4, label: 'Analyze', color: 'bg-orange-500' },
    { level: 5, label: 'Evaluate', color: 'bg-red-500' },
    { level: 6, label: 'Create', color: 'bg-purple-500' }
  ]

  const currentBloomData = bloomLevels[subject.current_bloom_level - 1] || bloomLevels[0]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-8 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-all"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-2">{subject.name}</h2>
              <p className="text-indigo-100 mb-4">
                {subject.category} • {subject.estimated_duration_hours}h estimated
              </p>
              
              <div className="flex items-center gap-4">
                {/* Difficulty Stars */}
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`w-5 h-5 ${i < Math.round(subject.difficulty_rating) ? 'text-yellow-300' : 'text-gray-300'}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                  <span className="ml-2 text-sm">Difficulty: {subject.difficulty_rating}/5</span>
                </div>

                {/* Current Bloom Level Badge */}
                <div className={`${currentBloomData.color} px-4 py-1 rounded-full text-sm font-semibold`}>
                  Current Level: {currentBloomData.label}
                </div>
              </div>
            </div>

            {/* Bloom Progress Ring */}
            <div className="ml-6">
              <BloomProgressRing currentLevel={subject.current_bloom_level} />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-gray-50">
          <div className="flex gap-1 px-8">
            {[
              { id: 'overview', label: 'Overview', icon: '📋' },
              { id: 'path', label: 'Learning Path', icon: '🛤️' },
              { id: 'concepts', label: 'Key Concepts', icon: '💡' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-medium transition-all ${
                  activeTab === tab.id
                    ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">About this Subject</h3>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {subject.summary}
                </p>
              </div>

              {subject.prerequisites && subject.prerequisites.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">Prerequisites</h3>
                  <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
                    <ul className="space-y-2">
                      {subject.prerequisites.map((prereq, idx) => (
                        <li key={idx} className="flex items-start">
                          <svg className="w-5 h-5 text-amber-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span className="text-gray-700">{prereq}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {subject.learning_objectives && (
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">Learning Objectives (Bloom's Taxonomy)</h3>
                  <div className="space-y-2">
                    {subject.learning_objectives.map((objective, idx) => {
                      const bloomLevel = bloomLevels[idx] || bloomLevels[0]
                      return (
                        <div key={idx} className="flex items-start p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <div className={`${bloomLevel.color} text-white text-xs font-bold px-3 py-1 rounded-full mr-3 flex-shrink-0`}>
                            L{bloomLevel.level}
                          </div>
                          <p className="text-gray-700 text-sm">{objective}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Learning Path Tab */}
          {activeTab === 'path' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Your Personalized Learning Path</h3>
              <p className="text-gray-600 mb-6">
                Follow this adaptive path designed specifically for your current level. 
                Each module builds upon the previous one following Bloom's Taxonomy.
              </p>
              <LearningPathTimeline modules={subject.learning_path || []} currentModule={1} />
            </div>
          )}

          {/* Key Concepts Tab */}
          {activeTab === 'concepts' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Key Concepts to Master</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(subject.key_concepts || []).map((concept, idx) => (
                  <div
                    key={idx}
                    className="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-lg border border-indigo-200 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start">
                      <div className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                        {idx + 1}
                      </div>
                      <p className="text-gray-800 font-medium">{concept}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 bg-gray-50 p-6 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-6 py-2 text-gray-700 hover:bg-gray-200 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
          <button
            onClick={() => onEnroll(subject.id)}
            className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
          >
            🚀 Enroll in this Subject
          </button>
        </div>
      </div>
    </div>
  )
}