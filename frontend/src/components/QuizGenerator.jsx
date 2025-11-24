import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function QuizGenerator({ onStart, defaultSubjectId, defaultTopic }) {
  const [subjects, setSubjects] = useState([])
  const [selectedSubject, setSelectedSubject] = useState(defaultSubjectId || '')
  const [topic, setTopic] = useState(defaultTopic || '')
  const [bloomLevel, setBloomLevel] = useState(2)
  const [questionType, setQuestionType] = useState('mcq')
  const [numQuestions, setNumQuestions] = useState(5)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    try {
      // ⭐ AJOUTER LE TOKEN
      const token = localStorage.getItem('access_token')
      
      const res = await axios.get('http://localhost:8000/api/subjects/list', {
        headers: {
          Authorization: `Bearer ${token}`  // ⭐ IMPORTANT
        }
      })
      
      console.log('Subjects loaded:', res.data)
      
      // ⭐ Adapter à la nouvelle structure de réponse
      if (res.data.subjects) {
        setSubjects(res.data.subjects)
        if (res.data.subjects.length > 0 && !selectedSubject) {
          setSelectedSubject(res.data.subjects[0].id.toString())
        }
      } else if (Array.isArray(res.data)) {
        // Fallback si l'ancien format
        setSubjects(res.data)
        if (res.data.length > 0 && !selectedSubject) {
          setSelectedSubject(res.data[0].id.toString())
        }
      }
    } catch (error) {
      console.error('Error fetching subjects:', error)
      if (error.response?.status === 401) {
        console.error('❌ Unauthorized - redirecting to signin')
        window.location.href = '/signin'
      }
    }
  }

  const handleStart = () => {
    if (!selectedSubject || !topic.trim()) {
      alert('Please select a subject and enter a topic')
      return
    }

    onStart({
      subject_id: selectedSubject,
      topic: topic.trim(),
      bloom_level: bloomLevel,
      question_type: questionType,
      num_questions: numQuestions
    })
  }

  const bloomLevels = [
    { level: 1, label: 'Remember', color: 'bg-blue-500', description: 'Recall facts and basic concepts' },
    { level: 2, label: 'Understand', color: 'bg-green-500', description: 'Explain ideas or concepts' },
    { level: 3, label: 'Apply', color: 'bg-yellow-500', description: 'Use information in new situations' },
    { level: 4, label: 'Analyze', color: 'bg-orange-500', description: 'Draw connections among ideas' },
    { level: 5, label: 'Evaluate', color: 'bg-red-500', description: 'Justify decisions or actions' },
    { level: 6, label: 'Create', color: 'bg-purple-500', description: 'Produce new or original work' }
  ]

  const questionTypes = [
    { value: 'mcq', label: 'Multiple Choice', icon: '☑️', description: 'Choose from 4 options', enabled: true },
    { value: 'open_ended', label: 'Open-Ended', icon: '✍️', description: 'Write detailed answers', enabled: true },
    { value: 'true_false', label: 'True/False', icon: '✓✗', description: 'Simple true or false', enabled: true },
    { value: 'matching', label: 'Matching', icon: '🔗', description: 'Match pairs', enabled: true }
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">📝</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Generate Adaptive Quiz</h1>
          <p className="text-gray-600">Configure your personalized learning assessment</p>
        </div>

        <div className="space-y-6">
          {/* Subject Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Subject
            </label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Select a subject...</option>
              {subjects.map(subject => (
                <option key={subject.id} value={subject.id}>
                  {subject.icon && `${subject.icon} `}{subject.name} {subject.category && `(${subject.category})`}
                </option>
              ))}
            </select>
            {subjects.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">Loading subjects...</p>
            )}
          </div>

          {/* Topic Input */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Topic / Chapter
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., MapReduce, Neural Networks, Cloud Architecture..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Bloom Level Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Bloom's Taxonomy Level
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {bloomLevels.map(level => (
                <button
                  key={level.level}
                  onClick={() => setBloomLevel(level.level)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    bloomLevel === level.level
                      ? `${level.color} border-transparent text-white shadow-lg scale-105`
                      : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="font-bold text-lg mb-1">L{level.level}</div>
                  <div className="text-sm font-semibold">{level.label}</div>
                  <div className="text-xs mt-1 opacity-80">{level.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Question Type Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Question Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              {questionTypes.map(type => (
                <button
                  key={type.value}
                  onClick={() => setQuestionType(type.value)}
                  disabled={!type.enabled}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    questionType === type.value
                      ? 'bg-indigo-50 border-indigo-500 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  } ${!type.enabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{type.icon}</span>
                    <span className="font-bold text-gray-900">{type.label}</span>
                  </div>
                  <div className="text-xs text-gray-600">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Number of Questions */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Number of Questions: <span className="text-indigo-600 font-bold">{numQuestions}</span>
            </label>
            <input
              type="range"
              min="3"
              max="10"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>3 (Quick)</span>
              <span>10 (Comprehensive)</span>
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStart}
            disabled={loading || !selectedSubject || !topic.trim()}
            className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-bold text-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Generating Quiz...
              </span>
            ) : (
              '🚀 Start Quiz'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}