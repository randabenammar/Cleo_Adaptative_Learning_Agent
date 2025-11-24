import React from 'react'

export default function QuizFeedback({ feedback, onNext, isLastQuestion }) {
  const isCorrect = feedback?.is_correct
  const scorePercentage = feedback?.score_percentage || 0

  return (
    <div className={`p-6 rounded-xl ${
      isCorrect 
        ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300'
        : 'bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-300'
    }`}>
      {/* Icon and Result */}
      <div className="flex items-center gap-4 mb-6">
        <div className={`text-6xl ${isCorrect ? 'animate-bounce' : ''}`}>
          {isCorrect ? '✅' : '❌'}
        </div>
        <div>
          <h3 className={`text-2xl font-bold mb-1 ${
            isCorrect ? 'text-green-700' : 'text-red-700'
          }`}>
            {isCorrect ? 'Correct!' : 'Not Quite Right'}
          </h3>
          <p className="text-gray-700">
            {isCorrect 
              ? 'Great job! You earned ' + (feedback?.points_earned || 0) + ' points!'
              : 'Don\'t worry, learning from mistakes is part of the process!'
            }
          </p>
        </div>
      </div>

      {/* Score for Open-Ended */}
      {scorePercentage > 0 && scorePercentage < 100 && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700">Your Score</span>
            <span className="text-lg font-bold text-indigo-600">{scorePercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                scorePercentage >= 70 ? 'bg-green-500' :
                scorePercentage >= 50 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Feedback Text */}
      <div className="bg-white p-4 rounded-lg mb-4 border border-gray-200">
        <p className="text-gray-800 leading-relaxed">{feedback?.feedback}</p>
      </div>

      {/* Explanation */}
      {feedback?.explanation && (
        <div className="bg-blue-50 p-4 rounded-lg mb-4 border border-blue-200">
          <div className="flex items-start gap-2">
            <span className="text-blue-600 text-xl flex-shrink-0">💡</span>
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Explanation</h4>
              <p className="text-blue-800 text-sm">{feedback.explanation}</p>
            </div>
          </div>
        </div>
      )}

      {/* Strengths and Weaknesses (for open-ended) */}
      {feedback?.strengths && feedback.strengths.length > 0 && (
        <div className="bg-green-50 p-4 rounded-lg mb-4 border border-green-200">
          <h4 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
            <span>💪</span> Strengths
          </h4>
          <ul className="space-y-1">
            {feedback.strengths.map((strength, idx) => (
              <li key={idx} className="text-green-800 text-sm flex items-start gap-2">
                <span className="text-green-600">•</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback?.weaknesses && feedback.weaknesses.length > 0 && (
        <div className="bg-amber-50 p-4 rounded-lg mb-4 border border-amber-200">
          <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
            <span>📈</span> Areas to Improve
          </h4>
          <ul className="space-y-1">
            {feedback.weaknesses.map((weakness, idx) => (
              <li key={idx} className="text-amber-800 text-sm flex items-start gap-2">
                <span className="text-amber-600">•</span>
                {weakness}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggestions */}
      {feedback?.suggestions && (
        <div className="bg-purple-50 p-4 rounded-lg mb-4 border border-purple-200">
          <h4 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
            <span>✨</span> Suggestions
          </h4>
          <p className="text-purple-800 text-sm">{feedback.suggestions}</p>
        </div>
      )}

      {/* Correct Answer (if wrong) */}
      {!isCorrect && feedback?.correct_answer && (
        <div className="bg-gray-100 p-4 rounded-lg mb-4 border border-gray-300">
          <h4 className="font-semibold text-gray-900 mb-1">Correct Answer:</h4>
          <p className="text-gray-800 font-medium">{feedback.correct_answer}</p>
        </div>
      )}

      {/* Next Button */}
      <button
        onClick={onNext}
        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
      >
        {isLastQuestion ? '🎉 Complete Quiz' : '➡️ Next Question'}
      </button>
    </div>
  )
}