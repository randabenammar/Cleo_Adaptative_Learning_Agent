import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import Navbar from '../components/Navbar'  // ⭐ AJOUT
import QuizGenerator from '../components/QuizGenerator'
import MCQQuestion from '../components/MCQQuestion'
import OpenQuestion from '../components/OpenQuestion'
import TrueFalseQuestion from '../components/TrueFalseQuestion'
import MatchingQuestion from '../components/MatchingQuestion'
import QuizFeedback from '../components/QuizFeedback'
import BloomLevelUp from '../components/BloomLevelUp'
import EmotionDetector from '../components/EmotionDetector'
import SupportWidget from '../components/SupportWidget'
import { useEmotionSupport } from '../hooks/useEmotionSupport'
import QuotaLimitModal from '../components/QuotaLimitModal' 
import AIHintButton from '../components/AIHintButton'

export default function QuizPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  
  const learnerId = user ? `user_${user.id}` : null
  const [searchParams] = useSearchParams()
  const subjectId = searchParams.get('subject_id')
  const topic = searchParams.get('topic')
  
  const [session, setSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState([])
  const [showFeedback, setShowFeedback] = useState(false)
  const [currentFeedback, setCurrentFeedback] = useState(null)
  const [loading, setLoading] = useState(false)
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [finalResults, setFinalResults] = useState(null)
  const [showLevelUp, setShowLevelUp] = useState(false)
  const [startTime, setStartTime] = useState(null)
  const [quotaError, setQuotaError] = useState(null)

  useEffect(() => {
    if (!user) {
      console.log('❌ User not logged in, redirecting to signin')
      navigate('/signin', { 
        state: { message: 'Please sign in to take a quiz' } 
      })
    }
  }, [user, navigate])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      console.log('✅ Axios configured with token')
    } else {
      console.warn('⚠️ No token found')
    }
  }, [])
  
  if (!user || !learnerId) {
    return (
      <>
        <Navbar />  {/* ⭐ AJOUT */}
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">🔒</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Required</h2>
            <p className="text-gray-600 mb-4">Please sign in to take quizzes</p>
            <button
              onClick={() => navigate('/signin')}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Sign In
            </button>
          </div>
        </div>
      </>
    )
  }

    
      
   

  const { supportWidget, checkIntervention, dismissWidget, submitFeedback } = useEmotionSupport(
    learnerId,
    session?.id
  )

  const currentQuestion = questions[currentQuestionIndex]

  const handleStartQuiz = async (config) => {
    setLoading(true)
    setQuotaError(null)
    try {
      const res = await axios.post('http://localhost:8000/api/quiz/generate', {
        learner_id: learnerId,
        subject_id: parseInt(config.subject_id),
        topic: config.topic,
        bloom_level: config.bloom_level,
        question_type: config.question_type,
        num_questions: config.num_questions
      })
      
      setSession(res.data.session)
      setQuestions(res.data.questions)
      setCurrentQuestionIndex(0)
      setAnswers([])
      setStartTime(Date.now())
    } catch (error) {
      console.error('Error starting quiz:', error)
      // ⭐ VÉRIFIER SI C'EST UNE ERREUR DE QUOTA
      if (error.response?.status === 403 && error.response?.data?.error === 'quota_exceeded') {
        setQuotaError(error.response.data)
      } else {
        alert('Erreur lors du démarrage du quiz')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitAnswer = async (userAnswer) => {
    setLoading(true)
    const timeTaken = Math.floor((Date.now() - startTime) / 1000)
    
    try {
      // ⭐ RÉCUPÉRER LE TOKEN
      const token = localStorage.getItem('access_token')
      const res = await axios.post('http://localhost:8000/api/quiz/submit-answer', {
        session_id: session.session_id,
        question_id: currentQuestion.question_id,
        user_answer: userAnswer,
        time_taken_seconds: timeTaken
      },
      {
        headers: {
          Authorization: `Bearer ${token}`  // ⭐ AJOUTER LE TOKEN
        }
      })
      
      setCurrentFeedback(res.data.evaluation)
      setAnswers([...answers, res.data.answer])
      setShowFeedback(true)
      setSession(res.data.session)
      
      setTimeout(() => {
        checkIntervention()
      }, 2000)
      
    } catch (error) {
      console.error('Error submitting answer:', error)
      alert('Erreur lors de la soumission de la réponse')
    } finally {
      setLoading(false)
    }
  }

  const handleNextQuestion = () => {
    setShowFeedback(false)
    setCurrentFeedback(null)
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setStartTime(Date.now())
    } else {
      completeQuiz()
    }
  }

 
  const completeQuiz = async () => {
  setLoading(true)
  try {
    console.log('🏁 Completing quiz session:', session.session_id)
    
    // ⭐ RÉCUPÉRER LE TOKEN
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      console.error('❌ No token found!')
      alert('Please sign in again')
      navigate('/signin')
      return
    }
    
    const res = await axios.post(
      'http://localhost:8000/api/quiz/complete',
      { session_id: session.session_id },
      {
        headers: {
          Authorization: `Bearer ${token}`  // ⭐ AJOUTER LE TOKEN
        }
      }
    )
    
    console.log('✅ Quiz completed:', res.data)
    
    // ⭐ LOGGER LES QUOTAS
    if (res.data.quota_info) {
      console.log('📊 Quota info:', res.data.quota_info)
      console.log(`   Used: ${res.data.quota_info.quizzes_used}/${res.data.quota_info.quizzes_limit}`)
    }
    
    setFinalResults(res.data)
    setQuizCompleted(true)
    
    if (res.data.bloom_decision.action === 'level_up') {
      setShowLevelUp(true)
      setTimeout(() => setShowLevelUp(false), 3000)
    }
    
  } catch (error) {
    console.error('❌ Error completing quiz:', error)
    console.error('   Response:', error.response?.data)
    alert('Erreur lors de la finalisation du quiz')
  } finally {
    setLoading(false)
  }
}    

  const renderQuestion = () => {
    if (!currentQuestion) return null

    const questionProps = {
      question: currentQuestion,
      onSubmit: handleSubmitAnswer,
      disabled: loading || showFeedback
    }

    switch (currentQuestion.question_type) {
      case 'mcq':
        return <MCQQuestion {...questionProps} />
      case 'open_ended':
        return <OpenQuestion {...questionProps} />
      case 'true_false':
        return <TrueFalseQuestion {...questionProps} />
      case 'matching':
        return <MatchingQuestion {...questionProps} />
      default:
        return <div>Type de question non supporté</div>
    }
  }

  // ========================================
  // SI PAS DE SESSION: Afficher QuizGenerator
  // ========================================
  if (!session) {
    return (
      <>
        <Navbar />  {/* ⭐ AJOUT */}
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 p-6">
          <QuizGenerator 
            onStart={handleStartQuiz} 
            defaultSubjectId={subjectId}
            defaultTopic={topic}
          />
        </div>
      </>
    )
  }

  // ========================================
  // SI QUIZ COMPLÉTÉ: Afficher résultats
  // ========================================
  if (quizCompleted && finalResults) {
    return (
      <>
        <Navbar />  {/* ⭐ AJOUT */}
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 p-6">
          {showLevelUp && (
            <BloomLevelUp 
              oldLevel={finalResults.session.initial_bloom_level}
              newLevel={finalResults.session.final_bloom_level}
            />
          )}
          
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              <div className="text-center mb-8">
                <div className="text-6xl mb-4">🎉</div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Quiz Completed!</h1>
                <p className="text-gray-600">Great job, keep learning!</p>
              </div>

              {/* Score Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
                  <div className="text-4xl font-bold text-green-700 mb-2">
                    {finalResults.final_score.percentage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-600 font-medium">Final Score</div>
                </div>
                
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
                  <div className="text-4xl font-bold text-blue-700 mb-2">
                    {finalResults.final_score.correct_answers}/{finalResults.final_score.total_questions}
                  </div>
                  <div className="text-sm text-blue-600 font-medium">Correct Answers</div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
                  <div className="text-4xl font-bold text-purple-700 mb-2">
                    {Math.floor(finalResults.session.time_spent_seconds / 60)}m {finalResults.session.time_spent_seconds % 60}s
                  </div>
                  <div className="text-sm text-purple-600 font-medium">Time Spent</div>
                </div>
              </div>

              {/* Bloom Level Change */}
              {finalResults.bloom_decision && (
                <div className={`p-6 rounded-xl mb-6 ${
                  finalResults.bloom_decision.action === 'level_up' 
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300'
                    : finalResults.bloom_decision.action === 'level_down'
                    ? 'bg-gradient-to-r from-amber-50 to-yellow-50 border-2 border-amber-300'
                    : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300'
                }`}>
                  <h3 className="text-xl font-bold mb-2">
                    {finalResults.bloom_decision.action === 'level_up' && '🎓 Level Up!'}
                    {finalResults.bloom_decision.action === 'level_down' && '📚 Let\'s Review'}
                    {finalResults.bloom_decision.action === 'maintain' && '✅ Stay at Current Level'}
                  </h3>
                  <p className="text-gray-700">{finalResults.bloom_decision.reason}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => window.location.reload()}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Take Another Quiz
                </button>
                <button
                  onClick={() => navigate('/subjects')}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  Back to Subjects
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    )
  }

  // ========================================
  // QUIZ EN COURS: Afficher questions + SUPPORT ÉMOTIONNEL
  // ========================================
  return (
    <>
      <Navbar />  {/* ⭐ AJOUT */}
      {/* ⭐ MODAL DE QUOTA */}
      {quotaError && (
        <QuotaLimitModal
          error={quotaError}
          onClose={() => setQuotaError(null)}
        />
      )}
      
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 p-6">
        
        {/* EMOTION DETECTOR - Apparaît en haut à droite */}
        {session && (
          <EmotionDetector 
            learnerId={learnerId}
            quizSessionId={session.id}
            onEmotionDetected={(emotions) => {
              console.log('Emotion detected:', emotions)
            }}
          />
        )}

        {/* SUPPORT WIDGET - Apparaît en modal quand nécessaire */}
        {supportWidget && (
          <SupportWidget
            supportData={supportWidget}
            onDismiss={dismissWidget}
            onFeedback={submitFeedback}
          />
        )}

{/*
        {!showFeedback && currentQuestion && (
  <div className="mt-6 flex justify-center">
    <AIHintButton 
      sessionId={session.session_id}
      questionId={currentQuestion.question_id}
    />
  </div>
)} */}

        {/* Contenu principal du quiz */}
        <div className="max-w-4xl mx-auto">
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                Question {currentQuestionIndex + 1} of {questions.length}
              </span>
              <span className="text-sm font-medium text-gray-700">
                Score: {session.total_points_earned}/{session.total_points_possible}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Question Card */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
            {!showFeedback ? (
              renderQuestion()
            ) : (
              <QuizFeedback
                feedback={currentFeedback}
                onNext={handleNextQuestion}
                isLastQuestion={currentQuestionIndex === questions.length - 1}
              />
            )}
          </div>
        </div>
      </div>
    </>
  )
}