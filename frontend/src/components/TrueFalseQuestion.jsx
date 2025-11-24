import React, { useState } from 'react'

export default function TrueFalseQuestion({ question, onSubmit, disabled }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null)

  const handleSubmit = () => {
    if (selectedAnswer === null) {
      alert('Please select True or False')
      return
    }
    onSubmit(selectedAnswer)
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
        
        <span className="text-xs text-gray-500">True/False</span>
      </div>

      {/* Question Text */}
      <h3 className="text-xl font-bold text-gray-900 mb-8">
        {question.question_text}
      </h3>

      {/* True/False Buttons */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <button
          onClick={() => !disabled && setSelectedAnswer(true)}
          disabled={disabled}
          className={`p-6 rounded-xl border-2 transition-all ${
            selectedAnswer === true
              ? 'bg-green-50 border-green-500 shadow-lg scale-105'
              : 'bg-white border-gray-200 hover:border-green-300 hover:shadow-md'
          } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
        >
          <div className="text-center">
            <div className="text-5xl mb-3">✓</div>
            <div className={`text-2xl font-bold ${
              selectedAnswer === true ? 'text-green-700' : 'text-gray-700'
            }`}>
              TRUE
            </div>
          </div>
        </button>

        <button
          onClick={() => !disabled && setSelectedAnswer(false)}
          disabled={disabled}
          className={`p-6 rounded-xl border-2 transition-all ${
            selectedAnswer === false
              ? 'bg-red-50 border-red-500 shadow-lg scale-105'
              : 'bg-white border-gray-200 hover:border-red-300 hover:shadow-md'
          } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
        >
          <div className="text-center">
            <div className="text-5xl mb-3">✗</div>
            <div className={`text-2xl font-bold ${
              selectedAnswer === false ? 'text-red-700' : 'text-gray-700'
            }`}>
              FALSE
            </div>
          </div>
        </button>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={disabled || selectedAnswer === null}
        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? 'Submitting...' : 'Submit Answer'}
      </button>
    </div>
  )
}