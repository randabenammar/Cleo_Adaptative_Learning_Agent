import React from 'react'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'

export default function BloomRadarChart({ bloomStats }) {
  const bloomLevels = bloomStats?.by_level || {}

  const data = [
    { level: 'Remember', value: bloomLevels[1]?.accuracy || 0, fullMark: 100 },
    { level: 'Understand', value: bloomLevels[2]?.accuracy || 0, fullMark: 100 },
    { level: 'Apply', value: bloomLevels[3]?.accuracy || 0, fullMark: 100 },
    { level: 'Analyze', value: bloomLevels[4]?.accuracy || 0, fullMark: 100 },
    { level: 'Evaluate', value: bloomLevels[5]?.accuracy || 0, fullMark: 100 },
    { level: 'Create', value: bloomLevels[6]?.accuracy || 0, fullMark: 100 }
  ]

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis 
            dataKey="level" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 10 }}
          />
          <Radar 
            name="Accuracy" 
            dataKey="value" 
            stroke="#6366f1" 
            fill="#6366f1" 
            fillOpacity={0.6}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}