import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'


// Pages
import Home from './pages/Home'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'
import SubjectExplorer from './pages/SubjectExplorer'
import QuizPage from './pages/QuizPage'
import Profile from './pages/Profile'
import Pricing from './pages/Pricing'
import PaymentSuccess from './pages/PaymentSuccess'

function App() {
  console.log('🚀 App component rendered')

  return (
    <div className="App">
      <Routes>
        {/* Public Routes */}
        <Route path="/"  />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/pricing" element={<Pricing />} /> 
        
        <Route path="/home" element={<Home />} /> 
        
        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/subjects" 
          element={
            <ProtectedRoute>
              <SubjectExplorer />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/quiz" 
          element={
            <ProtectedRoute>
              <QuizPage />
            </ProtectedRoute>
          } 
        />
        
        {/* ⭐ Payment success page */}
          <Route
            path="/payment/success"
            element={
              <ProtectedRoute>
                <PaymentSuccess />
              </ProtectedRoute>
            }
          />

        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </div>
  )
}

export default App