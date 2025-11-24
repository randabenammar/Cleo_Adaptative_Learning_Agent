import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function ProtectedRoute({ children, requiredRole }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  console.log('🛡️ ProtectedRoute check:')
  console.log('  loading:', loading)
  console.log('  user:', user)
  console.log('  requiredRole:', requiredRole)
  console.log('  current path:', location.pathname)

  // ⭐ Attendre que le chargement soit terminé
  if (loading) {
    console.log('  ⏳ Still loading, showing spinner...')
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // ⭐ Si pas d'utilisateur, rediriger vers signin
  if (!user) {
    console.log('  ❌ No user, redirecting to /signin')
    return <Navigate to="/signin" state={{ from: location }} replace />
  }

  // ⭐ Si un rôle spécifique est requis
  if (requiredRole && user.role !== requiredRole) {
    console.log(`  ❌ User role '${user.role}' does not match required '${requiredRole}'`)
    return <Navigate to="/" replace />
  }

  console.log('  ✅ Access granted')
  return children
}