import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'

export default function SignIn() {
  const { signin } = useAuth()
  const navigate = useNavigate()
  
  const [email_or_username, setEmailOrUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  console.log('🎨 SignIn component rendered')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const credentials = { email_or_username, password }

    console.log('🔐 Signing in...', email_or_username)

    if (!email_or_username || !password) {
      setError('Please enter both email/username and password')
      setLoading(false)
      return
    }

    try {
      const result = await signin(credentials)

      console.log('Signin result:', result)

      if (result.success) {
        console.log('✅ Signin successful:', result.user)
        
        await new Promise(resolve => setTimeout(resolve, 100))
        
        if (result.user.role === 'admin') {
          console.log('Redirecting to /admin')
          navigate('/admin', { replace: true })
        } else {
          console.log('Redirecting to /dashboard')
          navigate('/dashboard', { replace: true })
        }
      } else {
        console.error('❌ Signin failed:', result.error)
        setError(result.error || 'Login failed')
      }
    } catch (err) {
      console.error('❌ Signin exception:', err)
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = (username, pwd) => {
    console.log('Quick login triggered:', username)
    setEmailOrUsername(username)
    setPassword(pwd)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🎓</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
          <p className="text-gray-600">Sign in to continue your learning journey</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">❌ {error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Email/Username */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Email or Username
            </label>
            <input
              type="text"
              required
              value={email_or_username}
              onChange={(e) => setEmailOrUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your email or username"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your password"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !email_or_username || !password}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-lg font-semibold text-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Signing In...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Sign Up Link */}
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-indigo-600 font-semibold hover:text-indigo-700">
              Sign Up
            </Link>
          </p>
        </div>

        {/* Quick Login for Testing */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center mb-3">Quick Login (Development)</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => quickLogin('admin', 'Admin123!')}
              className="px-3 py-2 bg-red-50 text-red-700 rounded text-xs font-semibold hover:bg-red-100 transition-colors"
            >
              👑 Admin
            </button>
            <button
              type="button"
              onClick={() => quickLogin('randa_esprim', 'Randa123!')}
              className="px-3 py-2 bg-green-50 text-green-700 rounded text-xs font-semibold hover:bg-green-100 transition-colors"
            >
              🎓 Student
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}