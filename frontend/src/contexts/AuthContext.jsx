import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Charger l'utilisateur depuis localStorage au démarrage
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('access_token')
    
    if (storedUser && storedToken) {
      try {
        const parsedUser = JSON.parse(storedUser)
        setUser(parsedUser)
        
        // ⭐ Configurer axios pour inclure le token dans toutes les requêtes
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        
        console.log('✅ User restored from localStorage:', parsedUser.username)
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
      }
    }
    
    setLoading(false)
  }, [])

  const signin = async (credentials) => {
    try {
      console.log('🔐 Signing in...', credentials.email_or_username)
      
      const response = await axios.post('http://localhost:8000/api/auth/signin', credentials)
      
      const { user, access_token } = response.data
      
      // Sauvegarder dans localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('access_token', access_token)
      
      // ⭐ Configurer axios pour inclure le token
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      setUser(user)
      
      console.log('✅ Signed in successfully:', user.username)
      
      return { success: true, user }
    } catch (error) {
      console.error('❌ Signin error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const signup = async (userData) => {
    try {
      console.log('📝 Signing up...', userData.username)
      
      const response = await axios.post('http://localhost:8000/api/auth/signup', userData)
      
      const { user, access_token } = response.data
      
      // Sauvegarder dans localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('access_token', access_token)
      
      // ⭐ Configurer axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      setUser(user)
      
      console.log('✅ Signed up successfully:', user.username)
      
      return { success: true, user }
    } catch (error) {
      console.error('❌ Signup error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      }
    }
  }

  const logout = async () => {
    try {
      console.log('👋 Logging out...')
      
      // Appeler l'API logout (optionnel)
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          await axios.post('http://localhost:8000/api/auth/logout', {}, {
            headers: { Authorization: `Bearer ${token}` }
          })
        } catch (error) {
          console.warn('Logout API call failed (not critical):', error)
        }
      }
      
      // Nettoyer localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      
      // ⭐ Supprimer le token d'axios
      delete axios.defaults.headers.common['Authorization']
      
      setUser(null)
      
      console.log('✅ Logged out successfully')
      
      return { success: true }
    } catch (error) {
      console.error('❌ Logout error:', error)
      
      // Même en cas d'erreur, on nettoie quand même
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
      
      return { success: true } // On retourne success quand même
    }
  }

  const updateProfile = async (updates) => {
    try {
      console.log('📝 Updating profile...', updates)
      
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('No authentication token found')
      }
      
      // Appeler l'API pour mettre à jour le profil
      const response = await axios.put(
        'http://localhost:8000/api/auth/profile', 
        updates,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      
      const updatedUser = response.data.user
      
      // Mettre à jour localStorage
      localStorage.setItem('user', JSON.stringify(updatedUser))
      
      // Mettre à jour le state
      setUser(updatedUser)
      
      console.log('✅ Profile updated successfully')
      
      return { success: true, user: updatedUser }
    } catch (error) {
      console.error('❌ Update profile error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to update profile' 
      }
    }
  }

  const refreshToken = async () => {
    try {
      console.log('🔄 Refreshing token...')
      
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('No token to refresh')
      }
      
      const response = await axios.post(
        'http://localhost:8000/api/auth/refresh',
        { refresh_token: token }
      )
      
      const { access_token } = response.data
      
      // Mettre à jour le token
      localStorage.setItem('access_token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      console.log('✅ Token refreshed successfully')
      
      return { success: true }
    } catch (error) {
      console.error('❌ Token refresh failed:', error)
      
      // Si le refresh échoue, on déconnecte l'utilisateur
      logout()
      
      return { success: false }
    }
  }

  const value = {
    user,
    loading,
    signin,
    signup,
    logout,
    updateProfile,
    refreshToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}