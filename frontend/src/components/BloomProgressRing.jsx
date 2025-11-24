import React from 'react'

export default function BloomProgressRing({ currentLevel }) {
  const totalLevels = 6
  const percentage = (currentLevel / totalLevels) * 100
  const circumference = 2 * Math.PI * 45 // rayon de 45
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const levelColors = {
    1: '#3B82F6', // blue
    2: '#10B981', // green
    3: '#F59E0B', // yellow
    4: '#F97316', // orange
    5: '#EF4444', // red
    6: '#A855F7'  // purple
  }

  const currentColor = levelColors[currentLevel] || levelColors[1]

  return (
    <div className="relative w-28 h-28">
      {/* Background circle */}
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="56"
          cy="56"
          r="45"
          stroke="rgba(255,255,255,0.3)"
          strokeWidth="8"
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx="56"
          cy="56"
          r="45"
          stroke={currentColor}
          strokeWidth="8"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-3xl font-bold text-white">{currentLevel}</div>
        <div className="text-xs text-white opacity-90">/ {totalLevels}</div>
      </div>
    </div>
  )
}