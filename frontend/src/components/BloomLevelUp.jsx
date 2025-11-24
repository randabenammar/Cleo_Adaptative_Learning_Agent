import React from 'react'

export default function BloomLevelUp({ oldLevel, newLevel }) {
  const bloomLabels = {
    1: 'Remember',
    2: 'Understand',
    3: 'Apply',
    4: 'Analyze',
    5: 'Evaluate',
    6: 'Create'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-white rounded-2xl p-12 text-center max-w-md animate-scale-up shadow-2xl">
        <div className="text-8xl mb-6 animate-bounce">🎓</div>
        
        <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-4">
          Level Up!
        </h2>
        
        <div className="flex items-center justify-center gap-6 mb-6">
          <div className="text-center">
            <div className="text-5xl font-bold text-gray-400 mb-2">{oldLevel}</div>
            <div className="text-sm text-gray-600">{bloomLabels[oldLevel]}</div>
          </div>
          
          <div className="text-4xl text-indigo-600 animate-pulse">→</div>
          
          <div className="text-center">
            <div className="text-6xl font-bold text-indigo-600 mb-2">{newLevel}</div>
            <div className="text-sm font-semibold text-indigo-600">{bloomLabels[newLevel]}</div>
          </div>
        </div>
        
        <p className="text-gray-700 text-lg">
          Your skills are growing! You're now ready for more advanced challenges.
        </p>
      </div>
    </div>
  )
}