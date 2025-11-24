import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [showProfileMenu, setShowProfileMenu] = useState(false)

  // Fermer le menu quand on clique ailleurs
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showProfileMenu && !event.target.closest('.profile-dropdown')) {
        setShowProfileMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showProfileMenu])

  const handleLogout = async () => {
    if (confirm('Are you sure you want to logout?')) {
      setShowProfileMenu(false)
      await logout()
      navigate('/signin')
    }
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <nav className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 shadow-xl">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          
          {/* Left: Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="text-5xl group-hover:scale-110 transition-transform">
              🎓
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">CLEO</h1>
              <p className="text-xs text-white text-opacity-80">Adaptive Learning Platform</p>
            </div>
          </Link>

          {/* Center: Navigation Links */}
          <div className="hidden md:flex items-center gap-2">
            
            <Link
              to="/home"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/home')
                  ? 'bg-white text-indigo-600 shadow-lg'
                  : 'text-white hover:bg-white hover:bg-opacity-20'
              }`}
            >
              🏠 Home
            </Link>

            <Link
  to="/pricing"
  className={`px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 ${
    isActive('/pricing')
      ? 'bg-white text-indigo-600 shadow-lg transform scale-105'
      : 'text-white hover:bg-white hover:bg-opacity-20'
  }`}
>
  💎 Pricing
</Link>

            {user && (
              <>
                <Link
                  to="/dashboard"
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    isActive('/dashboard')
                      ? 'bg-white text-indigo-600 shadow-lg'
                      : 'text-white hover:bg-white hover:bg-opacity-20'
                  }`}
                >
                  📊 Dashboard
                </Link>

                <Link
                  to="/subjects"
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    isActive('/subjects')
                      ? 'bg-white text-indigo-600 shadow-lg'
                      : 'text-white hover:bg-white hover:bg-opacity-20'
                  }`}
                >
                  📚 Subjects
                </Link>

                <Link
                  to="/quiz"
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    isActive('/quiz')
                      ? 'bg-white text-indigo-600 shadow-lg'
                      : 'text-white hover:bg-white hover:bg-opacity-20'
                  }`}
                >
                  📝 Quiz
                </Link>

                {user.role === 'admin' && (
                  <Link
                    to="/admin"
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      isActive('/admin')
                        ? 'bg-white text-red-600 shadow-lg'
                        : 'text-white hover:bg-white hover:bg-opacity-20'
                    }`}
                  >
                    👑 Admin
                  </Link>
                )}
              </>
            )}
          </div>

          {/* Right: User Profile / Auth Buttons */}
          <div className="flex items-center gap-4">
            
            {user ? (
              // ⭐ Logged In: Avatar + Dropdown
              <div className="profile-dropdown relative">
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  className="flex items-center gap-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-xl px-4 py-2 transition-all group"
                >
                  {/* Avatar */}
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg ${
                    user.role === 'admin'
                      ? 'bg-gradient-to-br from-yellow-400 to-orange-500'
                      : 'bg-gradient-to-br from-indigo-500 to-purple-500'
                  }`}>
                    {user.username[0].toUpperCase()}
                  </div>

                  {/* Username (hidden on mobile) */}
                  <span className="text-white font-semibold hidden lg:block">
                    {user.username}
                  </span>

                  {/* Dropdown Arrow */}
                  <svg 
                    className={`w-4 h-4 text-white transition-transform ${showProfileMenu ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* ⭐ Dropdown Menu */}
                {showProfileMenu && (
                  <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-2xl overflow-hidden z-50 animate-fadeIn">
                    
                    {/* User Info Header */}
                    <div className={`p-4 ${
                      user.role === 'admin'
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500'
                        : 'bg-gradient-to-r from-indigo-600 to-purple-600'
                    }`}>
                      <div className="flex items-center gap-3">
                        <div className="h-14 w-14 bg-white rounded-full flex items-center justify-center text-indigo-600 font-bold text-2xl shadow-lg">
                          {user.username[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-white font-bold text-lg">{user.full_name || user.username}</p>
                          <p className="text-white text-opacity-90 text-sm">{user.email}</p>
                        </div>
                      </div>
                      <div className="mt-3">
                        <span className={`inline-block text-white text-xs px-3 py-1 rounded-full font-semibold ${
                          user.role === 'admin' ? 'bg-red-600' : 'bg-indigo-600'
                        }`}>
                          {user.role === 'admin' ? '👑 ADMIN' : '🎓 STUDENT'}
                        </span>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <div className="p-2">
                      
                      <button
                        onClick={() => {
                          setShowProfileMenu(false)
                          navigate('/profile')
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-indigo-50 rounded-lg transition-colors text-left"
                      >
                        <span className="text-2xl">👤</span>
                        <div>
                          <p className="text-gray-900 font-semibold">My Profile</p>
                          <p className="text-gray-500 text-xs">View and edit your profile</p>
                        </div>
                      </button>

                      <button
                        onClick={() => {
                          setShowProfileMenu(false)
                          navigate('/dashboard')
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-indigo-50 rounded-lg transition-colors text-left"
                      >
                        <span className="text-2xl">📊</span>
                        <div>
                          <p className="text-gray-900 font-semibold">Dashboard</p>
                          <p className="text-gray-500 text-xs">View your learning stats</p>
                        </div>
                      </button>

                      <button
                        onClick={() => {
                          setShowProfileMenu(false)
                          navigate('/subjects')
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-indigo-50 rounded-lg transition-colors text-left"
                      >
                        <span className="text-2xl">📚</span>
                        <div>
                          <p className="text-gray-900 font-semibold">Explore Subjects</p>
                          <p className="text-gray-500 text-xs">Browse learning topics</p>
                        </div>
                      </button>

                      {user.role === 'admin' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false)
                            navigate('/admin')
                          }}
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-orange-50 rounded-lg transition-colors text-left"
                        >
                          <span className="text-2xl">👑</span>
                          <div>
                            <p className="text-orange-600 font-semibold">Admin Dashboard</p>
                            <p className="text-gray-500 text-xs">Platform management</p>
                          </div>
                        </button>
                      )}

                      <hr className="my-2" />

                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-50 rounded-lg transition-colors text-left"
                      >
                        <span className="text-2xl">🚪</span>
                        <div>
                          <p className="text-red-600 font-semibold">Logout</p>
                          <p className="text-gray-500 text-xs">Sign out of your account</p>
                        </div>
                      </button>

                    </div>
                  </div>
                )}
              </div>
            ) : (
              // ⭐ Not Logged In: Sign In / Sign Up
              <>
                <Link
                  to="/signin"
                  className="px-6 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-semibold rounded-lg transition-all"
                >
                  Sign In
                </Link>
                <Link
                  to="/signup"
                  className="px-6 py-2 bg-white text-indigo-600 font-semibold rounded-lg hover:shadow-xl transition-all"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

        </div>

        {/* Mobile Menu (optional) */}
        {user && (
          <div className="md:hidden mt-4 flex flex-wrap gap-2">
            <Link to="/dashboard" className="flex-1 text-center px-3 py-2 bg-white bg-opacity-20 text-white rounded-lg text-sm font-semibold">
              📊 Dashboard
            </Link>
            <Link to="/subjects" className="flex-1 text-center px-3 py-2 bg-white bg-opacity-20 text-white rounded-lg text-sm font-semibold">
              📚 Subjects
            </Link>
            <Link to="/quiz" className="flex-1 text-center px-3 py-2 bg-white bg-opacity-20 text-white rounded-lg text-sm font-semibold">
              📝 Quiz
            </Link>
          </div>
        )}

      </div>
    </nav>
  )
}