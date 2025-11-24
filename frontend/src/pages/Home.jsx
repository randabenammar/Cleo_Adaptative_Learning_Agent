import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Navbar from '../components/Navbar'

export default function Home() {
  const { user } = useAuth()

  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-400 rounded-full blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-400 rounded-full blur-3xl opacity-20 animate-pulse delay-1000"></div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
          
          {/* Main Content */}
          <div className="text-center mb-16">
            <div className="text-8xl mb-6 animate-bounce">🎓</div>
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl">
              Welcome to <span className="text-yellow-300">CLEO</span>
            </h1>
            <p className="text-2xl md:text-3xl font-semibold text-yellow-200 mb-8 drop-shadow-lg">
              Your Adaptive Learning Companion
            </p>
            <p className="text-lg md:text-xl text-white font-medium max-w-3xl mx-auto mb-12 drop-shadow-lg leading-relaxed bg-black bg-opacity-20 backdrop-blur-sm rounded-2xl p-6">
              Experience personalized learning powered by AI. CLEO adapts to your knowledge level 
              using Bloom's Taxonomy to help you master any subject efficiently.
            </p>

            {/* CTA Buttons */}
            {user ? (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/dashboard"
                  className="bg-white text-indigo-600 px-10 py-5 rounded-2xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all transform"
                >
                  🚀 Go to Dashboard
                </Link>
                <Link
                  to="/subjects"
                  className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-10 py-5 rounded-2xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all transform"
                >
                  📚 Browse Subjects
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/signup"
                  className="bg-white text-indigo-600 px-10 py-5 rounded-2xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all transform"
                >
                  ✨ Get Started Free
                </Link>
                <Link
                  to="/signin"
                  className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-10 py-5 rounded-2xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all transform"
                >
                  🔑 Sign In
                </Link>
              </div>
            )}
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
            
            <div className="bg-white rounded-2xl p-8 text-center shadow-2xl hover:scale-105 transition-transform transform">
              <div className="text-6xl mb-4">🧠</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Adaptive Learning</h3>
              <p className="text-gray-600 leading-relaxed">
                Questions adapt to your knowledge level in real-time using Bloom's Taxonomy
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 text-center shadow-2xl hover:scale-105 transition-transform transform">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Detailed Analytics</h3>
              <p className="text-gray-600 leading-relaxed">
                Track your progress with comprehensive insights and recommendations
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 text-center shadow-2xl hover:scale-105 transition-transform transform">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Personalized Path</h3>
              <p className="text-gray-600 leading-relaxed">
                Get tailored recommendations based on your strengths and weaknesses
              </p>
            </div>

          </div>

          {/* How It Works Section */}
          <div className="mt-24 bg-white rounded-3xl shadow-2xl p-12">
            <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">
              How CLEO Works
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              
              <div className="text-center">
                <div className="bg-gradient-to-br from-indigo-100 to-purple-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">1️⃣</span>
                </div>
                <h3 className="font-bold text-lg text-gray-900 mb-2">Choose Subject</h3>
                <p className="text-gray-600 text-sm">
                  Select from various topics and subjects
                </p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-purple-100 to-pink-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">2️⃣</span>
                </div>
                <h3 className="font-bold text-lg text-gray-900 mb-2">Take Quiz</h3>
                <p className="text-gray-600 text-sm">
                  Answer adaptive questions at your level
                </p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-pink-100 to-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">3️⃣</span>
                </div>
                <h3 className="font-bold text-lg text-gray-900 mb-2">Get Feedback</h3>
                <p className="text-gray-600 text-sm">
                  Receive instant analysis of your performance
                </p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-orange-100 to-yellow-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">4️⃣</span>
                </div>
                <h3 className="font-bold text-lg text-gray-900 mb-2">Level Up</h3>
                <p className="text-gray-600 text-sm">
                  Progress through Bloom's taxonomy levels
                </p>
              </div>

            </div>
          </div>

          {/* Stats Section */}
          <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
            
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 text-center shadow-2xl">
              <div className="text-5xl font-bold text-white mb-2">6</div>
              <p className="text-white text-lg font-semibold">Bloom's Levels</p>
              <p className="text-white text-opacity-80 text-sm mt-2">From Remember to Create</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-8 text-center shadow-2xl">
              <div className="text-5xl font-bold text-white mb-2">AI</div>
              <p className="text-white text-lg font-semibold">Powered Learning</p>
              <p className="text-white text-opacity-80 text-sm mt-2">Smart question generation</p>
            </div>

            <div className="bg-gradient-to-br from-pink-500 to-orange-600 rounded-2xl p-8 text-center shadow-2xl">
              <div className="text-5xl font-bold text-white mb-2">∞</div>
              <p className="text-white text-lg font-semibold">Unlimited Potential</p>
              <p className="text-white text-opacity-80 text-sm mt-2">Grow at your own pace</p>
            </div>

          </div>

          {/* CTA Bottom Section */}
          {!user && (
            <div className="mt-24 bg-white rounded-3xl shadow-2xl p-12 text-center">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Ready to Start Learning?
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Join thousands of learners improving their skills with CLEO
              </p>
              <Link
                to="/signup"
                className="inline-block bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-12 py-5 rounded-2xl font-bold text-xl hover:shadow-2xl hover:scale-105 transition-all transform"
              >
                🚀 Create Free Account
              </Link>
              <p className="text-gray-500 text-sm mt-4">
                No credit card required • Start in 30 seconds
              </p>
            </div>
          )}

        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            <div>
              <h3 className="text-2xl font-bold mb-4">🎓 CLEO</h3>
              <p className="text-gray-400">
                Adaptive learning platform powered by AI and Bloom's Taxonomy
              </p>
            </div>

            <div>
              <h4 className="font-bold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/subjects" className="hover:text-white transition-colors">Browse Subjects</Link></li>
                <li><Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-400">
                <li>📧 support@cleo.com</li>
                <li>🌐 www.cleo.com</li>
                <li>📱 Follow us on social media</li>
              </ul>
            </div>

          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 CLEO. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </>
  )
}