import React from 'react'

export default function SubjectCard({ icon, name, category, onClick }) {
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer bg-white rounded-xl shadow-md hover:shadow-2xl transition-all duration-300 p-6 border border-gray-100 hover:border-indigo-300 hover:-translate-y-1"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="text-5xl">{icon}</div>
        <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
          {category}
        </span>
      </div>
      
      <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
        {name}
      </h3>
      
      <p className="text-sm text-gray-500">
        Click to explore learning path
      </p>
      
      <div className="mt-4 flex items-center text-indigo-600 text-sm font-medium">
        <span>Start Learning</span>
        <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  )
}