import React, { useState } from 'react'

export default function OpenQuestion({ question, onSubmit, disabled }) {
  const [answer, setAnswer] = useState('')
  const wordCount = answer.trim().split(/\s+/).filter(w => w.length > 0).length
  const minWords = question.min_words || 20

  const handleSubmit = () => {
    if (answer.trim().length < 10) {
      alert('Please provide a more detailed answer')
      return
    }
    onSubmit(answer)
  }

  return (
    <div>
      {/* Bloom Level Badge */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-bold text-white ${
            question.bloom_level === 1 ? 'bg-blue-500' :
            question.bloom_level === 2 ? 'bg-green-500' :
            question.bloom_level === 3 ? 'bg-yellow-500' :
            question.bloom_level === 4 ? 'bg-orange-500' :
            question.bloom_level === 5 ? 'bg-red-500' :
            'bg-purple-500'
          }`}>
            Level {question.bloom_level} - {question.bloom_label}
          </span>
          <span className="text-xs text-gray-500">
            {question.points} points
          </span>
        </div>
        
        <span className="text-xs text-gray-500">Open-Ended Question</span>
      </div>

      {/* Question Text */}
      <h3 className="text-xl font-bold text-gray-900 mb-6">
        {question.question_text}
      </h3>

      {/* Answer Textarea */}
      <div className="mb-4">
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={disabled}
          placeholder="Type your detailed answer here..."
          rows="8"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        
        {/* Word Count Indicator */}
        <div className="flex items-center justify-between mt-2">
          <span className={`text-sm font-medium ${
            wordCount >= minWords ? 'text-green-600' : 'text-amber-600'
          }`}>
            {wordCount} / {minWords} words minimum
          </span>
          
          {question.keywords && question.keywords.length > 0 && (
            <div className="text-xs text-gray-500">
              💡 Tip: Include these concepts: {question.keywords.slice(0, 3).join(', ')}
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              wordCount >= minWords ? 'bg-green-500' : 'bg-amber-500'
            }`}
            style={{ width: `${Math.min((wordCount / minWords) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={disabled || answer.trim().length < 10}
        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? 'Evaluating...' : 'Submit Answer'}
      </button>
    </div>
  )
}