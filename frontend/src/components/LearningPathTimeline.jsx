import React from 'react'

export default function LearningPathTimeline({ modules, currentModule }) {
  const bloomColors = {
    1: 'bg-blue-500',
    2: 'bg-green-500',
    3: 'bg-yellow-500',
    4: 'bg-orange-500',
    5: 'bg-red-500',
    6: 'bg-purple-500'
  }

  const bloomBorders = {
    1: 'border-blue-500',
    2: 'border-green-500',
    3: 'border-yellow-500',
    4: 'border-orange-500',
    5: 'border-red-500',
    6: 'border-purple-500'
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-gray-300"></div>

      <div className="space-y-8">
        {modules.map((module, idx) => {
          const isActive = module.module_number === currentModule
          const isCompleted = module.module_number < currentModule
          const bloomColor = bloomColors[module.bloom_level] || bloomColors[1]
          const bloomBorder = bloomBorders[module.bloom_level] || bloomBorders[1]

          return (
            <div key={idx} className="relative flex items-start">
              {/* Timeline dot */}
              <div className={`absolute left-0 w-12 h-12 rounded-full border-4 ${bloomBorder} flex items-center justify-center z-10 ${
                isCompleted ? bloomColor + ' text-white' : 'bg-white'
              } ${isActive ? 'ring-4 ring-indigo-200 scale-110' : ''} transition-all`}>
                {isCompleted ? (
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <span className="text-sm font-bold text-gray-600">{module.module_number}</span>
                )}
              </div>

              {/* Module content */}
              <div className={`ml-20 flex-1 p-6 rounded-lg border-2 ${
                isActive ? 'bg-indigo-50 border-indigo-300 shadow-lg' : 'bg-white border-gray-200'
              } transition-all hover:shadow-md`}>
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-lg font-bold text-gray-900">{module.title}</h4>
                  <div className="flex items-center gap-2">
                    <span className={`${bloomColor} text-white text-xs font-semibold px-3 py-1 rounded-full`}>
                      {module.bloom_label}
                    </span>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {module.estimated_hours}h
                    </span>
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-3">{module.description}</p>

                {module.key_activities && module.key_activities.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">Key Activities:</p>
                    <ul className="space-y-1">
                      {module.key_activities.map((activity, actIdx) => (
                        <li key={actIdx} className="flex items-start text-sm text-gray-600">
                          <svg className="w-4 h-4 text-indigo-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                          {activity}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {isActive && (
                  <div className="mt-4 pt-4 border-t border-indigo-200">
                    <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors text-sm">
                      Start this Module →
                    </button>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}