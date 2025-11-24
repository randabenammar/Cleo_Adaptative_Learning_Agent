import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import axios from 'axios'
import Navbar from '../components/Navbar'

export default function PaymentSuccess() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [verifying, setVerifying] = useState(true)
  const [subscription, setSubscription] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const sessionId = searchParams.get('session_id')
    
    if (sessionId) {
      verifyPayment(sessionId)
    } else {
      setError('No session ID found')
      setVerifying(false)
    }
  }, [searchParams])

  const verifyPayment = async (sessionId) => {
    try {
      const token = localStorage.getItem('access_token')
      
      const res = await axios.get(
        `http://localhost:8000/api/payment/verify-session/${sessionId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )

      console.log('✅ Payment verified:', res.data)
      
      if (res.data.subscription) {
        setSubscription(res.data.subscription)
      }

      // Attendre 2 secondes pour l'effet
      setTimeout(() => {
        setVerifying(false)
      }, 2000)

    } catch (err) {
      console.error('❌ Error verifying payment:', err)
      setError('Error verifying payment. Please contact support.')
      setVerifying(false)
    }
  }

  if (verifying) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50">
          <div className="text-center">
            <div className="text-8xl mb-6 animate-bounce">✓</div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Verifying Payment...
            </h1>
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-green-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Please wait a moment</p>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-orange-50 px-4">
          <div className="text-center max-w-md">
            <div className="text-8xl mb-6">⚠️</div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Something went wrong
            </h1>
            <p className="text-gray-600 mb-8">{error}</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/pricing')}
                className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-colors"
              >
                Back to Pricing
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-8 py-4 bg-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-300 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 py-12 px-4">
        <div className="max-w-2xl w-full">
          
          {/* Success Card */}
          <div className="bg-white rounded-3xl shadow-2xl p-12 mb-8 text-center">
            
            {/* Success Animation */}
            <div className="mb-6">
              <div className="text-8xl mb-4 animate-bounce">🎉</div>
              <div className="flex justify-center gap-2 text-4xl">
                <span className="animate-pulse">✨</span>
                <span className="animate-pulse delay-100">⭐</span>
                <span className="animate-pulse delay-200">💫</span>
              </div>
            </div>
            
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Payment Successful!
            </h1>
            
            <p className="text-xl text-gray-600 mb-8">
              Welcome to your new{' '}
              <span className="font-bold text-indigo-600 uppercase">
                {subscription?.tier || 'PREMIUM'}
              </span>{' '}
              plan!
            </p>

            {/* Benefits */}
            {subscription && (
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  🎁 Your New Benefits:
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                  <div className="flex items-center gap-3">
                    <span className="text-green-500 text-2xl">✓</span>
                    <span className="text-gray-700">More quizzes per month</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-green-500 text-2xl">✓</span>
                    <span className="text-gray-700">AI-powered hints</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-green-500 text-2xl">✓</span>
                    <span className="text-gray-700">Extended analytics</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-green-500 text-2xl">✓</span>
                    <span className="text-gray-700">Export your data</span>
                  </div>
                  {subscription.tier !== 'bronze' && (
                    <>
                      <div className="flex items-center gap-3">
                        <span className="text-green-500 text-2xl">✓</span>
                        <span className="text-gray-700">All subjects access</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-green-500 text-2xl">✓</span>
                        <span className="text-gray-700">Priority support</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-10 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-lg rounded-xl hover:shadow-xl hover:scale-105 transition-all transform"
              >
                📊 Go to Dashboard
              </button>
              <button
                onClick={() => navigate('/quiz')}
                className="px-10 py-4 bg-white text-indigo-600 border-2 border-indigo-600 font-bold text-lg rounded-xl hover:bg-indigo-50 hover:scale-105 transition-all transform"
              >
                🚀 Start a Quiz
              </button>
            </div>

            <p className="text-gray-500 text-sm">
              A confirmation email has been sent to your inbox
            </p>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">📧</div>
              <h4 className="font-bold text-gray-900 mb-1">Check Email</h4>
              <p className="text-sm text-gray-600">Receipt sent</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">💳</div>
              <h4 className="font-bold text-gray-900 mb-1">Manage Billing</h4>
              <p className="text-sm text-gray-600">Via dashboard</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">💬</div>
              <h4 className="font-bold text-gray-900 mb-1">Need Help?</h4>
              <p className="text-sm text-gray-600">support@cleo.com</p>
            </div>
          </div>

        </div>
      </div>
    </>
  )
}