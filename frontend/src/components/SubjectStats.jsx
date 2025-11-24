import React from 'react'

export default function SubjectStats({ subjectStats }) {
  if (!subjectStats || subjectStats.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>📚</span>
          Subject Performance
        </h3>
        <p className="text-sm text-gray-500 text-center py-8">
          No subject data yet. Start a quiz to see your performance by subject!
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>📚</span>
        Subject Performance
      </h3>
      
      <div className="space-y-4">
        {subjectStats.map((subject, idx) => (
          <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-bold text-gray-900">{subject.subject_name}</h4>
              <span className={`text-2xl font-bold ${
                subject.accuracy >= 80 ? 'text-green-600' :
                subject.accuracy >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {subject.accuracy}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mb-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    subject.accuracy >= 80 ? 'bg-green-500' :
                    subject.accuracy >= 60 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${subject.accuracy}%` }}
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Sessions</p>
                <p className="font-semibold text-gray-900">{subject.sessions_count}</p>
              </div>
              <div>
                <p className="text-gray-500">Questions</p>
                <p className="font-semibold text-gray-900">{subject.total_questions}</p>
              </div>
              <div>
                <p className="text-gray-500">Bloom Level</p>
                <p className="font-semibold text-indigo-600">L{subject.current_bloom_level}</p>
              </div>
              <div>
                <p className="text-gray-500">Time</p>
                <p className="font-semibold text-gray-900">{Math.round(subject.total_time_minutes)}m</p>
              </div>
            </div>

            {/* Completion Badge */}
            {subject.completion_percentage > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Course Progress</span>
                  <span className="font-semibold text-indigo-600">{Math.round(subject.completion_percentage)}%</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}