import React, { useState } from 'react'

export default function MCQQuestion({ question, onSubmit, disabled }) {
  const [selectedOption, setSelectedOption] = useState(null)

  const handleSubmit = () => {
    if (!selectedOption) {
      alert('Please select an answer')
      return
    }
    onSubmit(selectedOption)
  }

  const optionLabels = ['A', 'B', 'C', 'D']
  const options = question.options || question.question_data?.options || []

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
        
        <span className="text-xs text-gray-500">
          {question.question_type === 'mcq' ? 'Multiple Choice' : 'True/False'}
        </span>
      </div>

      {/* Question Text */}
      <h3 className="text-xl font-bold text-gray-900 mb-6">
        {question.question_text}
      </h3>

      {/* Options */}
      <div className="space-y-3 mb-6">
        {options.map((option, idx) => {
          const optionKey = option.key || optionLabels[idx]
          const isSelected = selectedOption === optionKey
          
          return (
            <button
              key={idx}
              onClick={() => !disabled && setSelectedOption(optionKey)}
              disabled={disabled}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                isSelected
                  ? 'bg-indigo-50 border-indigo-500 shadow-md'
                  : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
              } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
            >
              <div className="flex items-start gap-3">
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                  isSelected
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}>
                  {optionKey}
                </div>
                <span className="text-gray-800 flex-1">{option.text}</span>
              </div>
            </button>
          )
        })}
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={disabled || !selectedOption}
        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? 'Submitting...' : 'Submit Answer'}
      </button>
    </div>
  )
}