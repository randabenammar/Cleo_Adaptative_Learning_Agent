import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function StressTechniques({ onClose }) {
  const [techniques, setTechniques] = useState([])
  const [selectedTechnique, setSelectedTechnique] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(0)

  useEffect(() => {
    fetchTechniques()
  }, [])

  const fetchTechniques = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/emotion-support/stress-techniques')
      setTechniques(res.data.techniques)
    } catch (error) {
      console.error('Error fetching techniques:', error)
      // Fallback techniques
      setTechniques([
        {
          id: 'breathing_478',
          name: '4-7-8 Breathing',
          description: 'Breathe in for 4, hold for 7, exhale for 8',
          duration_seconds: 60,
          icon: '🫁',
          steps: [
            'Sit comfortably and close your eyes',
            'Breathe in through your nose for 4 seconds',
            'Hold your breath for 7 seconds',
            'Exhale slowly through your mouth for 8 seconds',
            'Repeat 3-4 times'
          ]
        }
      ])
    }
  }

  const startTechnique = (technique) => {
    setSelectedTechnique(technique)
    setCurrentStep(0)
    setTimeRemaining(technique.duration_seconds)
    setIsRunning(true)
  }

  useEffect(() => {
    if (isRunning && timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1)
        
        // Auto-advance steps
        const stepDuration = selectedTechnique.duration_seconds / selectedTechnique.steps.length
        const newStep = Math.floor((selectedTechnique.duration_seconds - timeRemaining) / stepDuration)
        if (newStep !== currentStep && newStep < selectedTechnique.steps.length) {
          setCurrentStep(newStep)
        }
      }, 1000)

      return () => clearTimeout(timer)
    } else if (isRunning && timeRemaining === 0) {
      setIsRunning(false)
      // Félicitations
    }
  }, [isRunning, timeRemaining, selectedTechnique, currentStep])

  const stopTechnique = () => {
    setIsRunning(false)
    setSelectedTechnique(null)
  }

  if (selectedTechnique && isRunning) {
    const progress = ((selectedTechnique.duration_seconds - timeRemaining) / selectedTechnique.duration_seconds) * 100

    return (
      <div className="p-6">
        <div className="text-center mb-6">
          <div className="text-7xl mb-4 animate-pulse">{selectedTechnique.icon}</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">{selectedTechnique.name}</h3>
          <p className="text-gray-600">{selectedTechnique.description}</p>
        </div>

        {/* Progress Ring */}
        <div className="flex justify-center mb-6">
          <div className="relative w-48 h-48">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="#6366f1"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 88}`}
                strokeDashoffset={`${2 * Math.PI * 88 * (1 - progress / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl font-bold text-indigo-600">{timeRemaining}</div>
                <div className="text-sm text-gray-600">seconds</div>
              </div>
            </div>
          </div>
        </div>

        {/* Current Step */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 mb-6 border border-indigo-200">
          <p className="text-sm text-gray-600 mb-2">Step {currentStep + 1} of {selectedTechnique.steps.length}</p>
          <p className="text-lg font-semibold text-gray-900">{selectedTechnique.steps[currentStep]}</p>
        </div>

        {/* All Steps */}
        <div className="space-y-2 mb-6">
          {selectedTechnique.steps.map((step, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border-2 transition-all ${
                idx === currentStep
                  ? 'border-indigo-500 bg-indigo-50'
                  : idx < currentStep
                  ? 'border-green-300 bg-green-50 opacity-60'
                  : 'border-gray-200 bg-gray-50 opacity-40'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                  idx === currentStep
                    ? 'bg-indigo-600 text-white'
                    : idx < currentStep
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {idx < currentStep ? '✓' : idx + 1}
                </div>
                <span className="text-sm text-gray-700">{step}</span>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={stopTechnique}
          className="w-full py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition-colors"
        >
          Stop Exercise
        </button>

        {timeRemaining === 0 && (
          <div className="mt-4 text-center">
            <div className="text-5xl mb-2">🎉</div>
            <p className="text-lg font-semibold text-green-600">Great job! You completed the exercise!</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {techniques.map((technique) => (
          <div
            key={technique.id}
            className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-indigo-400 hover:shadow-lg transition-all cursor-pointer"
            onClick={() => startTechnique(technique)}
          >
            <div className="text-5xl mb-4">{technique.icon}</div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">{technique.name}</h4>
            <p className="text-sm text-gray-600 mb-4">{technique.description}</p>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">
                ⏱️ {Math.floor(technique.duration_seconds / 60)}:{(technique.duration_seconds % 60).toString().padStart(2, '0')} min
              </span>
              <button className="text-sm font-semibold text-indigo-600 hover:text-indigo-700">
                Start →
              </button>
            </div>
          </div>
        ))}
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className="mt-6 w-full py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
        >
          Close
        </button>
      )}
    </div>
  )
}