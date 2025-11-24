import React, { useRef, useEffect, useState } from 'react'
import axios from 'axios'

export default function EmotionDetector({ learnerId, quizSessionId, onEmotionDetected }) {
  const [isActive, setIsActive] = useState(false)
  const [currentEmotion, setCurrentEmotion] = useState(null)
  const intervalRef = useRef(null)

  // Simuler détection d'émotions
  const detectEmotion = async () => {
    // Simulation: générer émotions aléatoires
    const emotions = {
      happy: Math.random() * 0.4 + 0.3,
      sad: Math.random() * 0.2,
      angry: Math.random() * 0.15,
      fear: Math.random() * 0.15,
      disgust: Math.random() * 0.1,
      surprise: Math.random() * 0.2,
      neutral: Math.random() * 0.3
    }

    // Normaliser
    const total = Object.values(emotions).reduce((a, b) => a + b, 0)
    Object.keys(emotions).forEach(key => {
      emotions[key] = emotions[key] / total
    })

    setCurrentEmotion(emotions)

    if (onEmotionDetected) {
      onEmotionDetected(emotions)
    }

    // Log vers backend
    try {
      await axios.post('http://localhost:8000/api/emotion-support/log-emotion', {
        learner_id: learnerId,
        quiz_session_id: quizSessionId,
        ...emotions,
        detection_method: 'webcam_simulation'
      })
      console.log('✅ Emotion logged:', emotions)
    } catch (error) {
      console.error('❌ Error logging emotion:', error)
    }
  }

  useEffect(() => {
    if (isActive) {
      // Détecter toutes les 5 secondes
      intervalRef.current = setInterval(detectEmotion, 5000)
      detectEmotion() // Première détection immédiate
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, learnerId, quizSessionId])

  const getDominantEmotion = () => {
    if (!currentEmotion) return { label: 'Neutral', emoji: '😐', color: 'bg-gray-100 text-gray-600' }

    const max = Math.max(...Object.values(currentEmotion))
    const dominant = Object.entries(currentEmotion).find(([_, value]) => value === max)

    const emotionMap = {
      happy: { label: 'Happy', emoji: '😊', color: 'bg-green-100 text-green-600' },
      sad: { label: 'Sad', emoji: '😢', color: 'bg-blue-100 text-blue-600' },
      angry: { label: 'Frustrated', emoji: '😠', color: 'bg-red-100 text-red-600' },
      fear: { label: 'Anxious', emoji: '😰', color: 'bg-yellow-100 text-yellow-600' },
      disgust: { label: 'Uncomfortable', emoji: '😖', color: 'bg-purple-100 text-purple-600' },
      surprise: { label: 'Surprised', emoji: '😲', color: 'bg-orange-100 text-orange-600' },
      neutral: { label: 'Neutral', emoji: '😐', color: 'bg-gray-100 text-gray-600' }
    }

    return emotionMap[dominant[0]] || emotionMap.neutral
  }

  const emotion = getDominantEmotion()

  return (
    <div className="fixed top-20 right-4 z-40">
      <div className={`rounded-lg shadow-xl border-2 transition-all ${
        isActive 
          ? 'bg-white border-green-400' 
          : 'bg-white border-gray-300 hover:border-indigo-400 hover:shadow-2xl'
      }`}>
        
        {/* Toggle Button */}
        <button
          onClick={() => setIsActive(!isActive)}
          className={`w-full p-4 flex items-center gap-3 transition-all ${
            isActive ? 'bg-green-50' : 'hover:bg-gray-50'
          }`}
        >
          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl transition-all ${
            isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-200'
          }`}>
            {isActive ? '📹' : '📷'}
          </div>

          <div className="text-left flex-1">
            <p className={`text-sm font-bold ${isActive ? 'text-green-700' : 'text-gray-700'}`}>
              {isActive ? 'Emotion Detection ON' : 'Enable Emotion Tracking'}
            </p>
            <p className="text-xs text-gray-500">
              {isActive ? 'Monitoring your emotions...' : 'Click to activate'}
            </p>
          </div>

          {/* Indicator */}
          <div className={`w-3 h-3 rounded-full ${
            isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
          }`} />
        </button>

        {/* Current Emotion Display */}
        {isActive && currentEmotion && (
          <div className={`p-4 border-t-2 ${emotion.color} transition-all`}>
            <div className="flex items-center gap-3">
              <span className="text-3xl animate-bounce">{emotion.emoji}</span>
              <div className="flex-1">
                <p className="font-bold text-sm">{emotion.label}</p>
                <div className="flex gap-1 mt-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full ${
                        i < Math.floor(Math.max(...Object.values(currentEmotion)) * 5)
                          ? 'bg-current'
                          : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Info Text */}
        {!isActive && (
          <div className="px-4 pb-4 text-xs text-gray-500 text-center">
            💡 Get personalized support based on your emotions
          </div>
        )}
      </div>
    </div>
  )
}