import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { getSubjectIcon } from '../utils/subjectIcons'
import SubjectSelector from '../components/SubjectSelector'
import Navbar from '../components/Navbar' 

export default function SubjectExplorer() {
  const navigate = useNavigate()
  const [subjects, setSubjects] = useState([])
  const [lockedSubjects, setLockedSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [needsSelection, setNeedsSelection] = useState(false)
  const [maxSubjects, setMaxSubjects] = useState(2)
  const [activeFilter, setActiveFilter] = useState('all')
  const [categories, setCategories] = useState([])
  const [showSelector, setShowSelector] = useState(false)  // ⭐ NOUVEAU
  const [subscription, setSubscription] = useState(null)     // ⭐ NOUVEAU

  useEffect(() => {
    fetchSubjects()
    fetchSubscription()  // ⭐ NOUVEAU
  }, [])

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/subscriptions/current', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSubscription(res.data.subscription)
    } catch (error) {
      console.error('Error fetching subscription:', error)
    }
  }

  const fetchSubjects = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      const res = await axios.get('http://localhost:8000/api/subjects/list', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      console.log('📚 Subjects response:', res.data)
      
      setSubjects(res.data.subjects || [])
      setLockedSubjects(res.data.locked_subjects || [])
      setMaxSubjects(res.data.access_limit || 2)
      setNeedsSelection(res.data.needs_favorites_selection || false)
      
      const allSubjects = [...(res.data.subjects || []), ...(res.data.locked_subjects || [])]
      const uniqueCategories = [...new Set(allSubjects.map(s => s.category).filter(Boolean))]
      setCategories(uniqueCategories)
      
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectionComplete = () => {
    console.log('✅ Selection completed, reloading subjects...')
    setNeedsSelection(false)
    setShowSelector(false)  // ⭐ FERMER LE MODAL
    fetchSubjects()
    fetchSubscription()
  }

  const handleStartLearning = (subjectId, subjectName) => {
    navigate(`/quiz?subject_id=${subjectId}&topic=${encodeURIComponent(subjectName)}`)
  }

  const filteredSubjects = activeFilter === 'all' 
    ? subjects 
    : subjects.filter(s => s.category === activeFilter)

  if (loading) {
    return (
      <>
        <Navbar />
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading subjects...</p>
        </div>
      </div>
      </>
    )
  }

  return (
    <>
        <Navbar />
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      {/* Modal de sélection */}
      {(needsSelection || showSelector) && (
        <SubjectSelector 
          maxSubjects={maxSubjects}
          onComplete={handleSelectionComplete}
        />
      )}

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            📚 Explore Subjects
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            Choose a subject to start your adaptive learning journey
          </p>
          
          {/* ⭐ Info sur les sujets disponibles */}
          {subscription && (
            <div className="inline-flex items-center gap-4 bg-white rounded-xl shadow-lg p-4 mb-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600">
                  {subjects.length} / {maxSubjects}
                </div>
                <div className="text-sm text-gray-600">Subjects Selected</div>
              </div>
             
              {subjects.length < maxSubjects && (
                <button
                  onClick={() => setShowSelector(true)}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-lg hover:shadow-xl transition-all"
                >
                  ➕ Add More Subjects ({maxSubjects - subjects.length} left)
                </button>
              )}
              
              {subjects.length > 0 && (
                <button
                  onClick={() => setShowSelector(true)}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-xl transition-all"
                >
                  🔄 Change Subjects
                </button>
              )}
            </div>
          )}
        </div>

        {/* Filtres par catégorie */}
        {categories.length > 0 && (
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                activeFilter === 'all'
                  ? 'bg-indigo-600 text-white shadow-lg scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              🌐 All Subjects
            </button>
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setActiveFilter(category)}
                className={`px-6 py-2 rounded-full font-semibold transition-all ${
                  activeFilter === category
                    ? 'bg-indigo-600 text-white shadow-lg scale-105'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        )}

        {/* Grid des sujets disponibles */}
        {subjects.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📚</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              No Subjects Selected
            </h3>
            <p className="text-gray-600 mb-6">
              You can select up to {maxSubjects} subjects with your plan
            </p>
            <button
              onClick={() => setShowSelector(true)}
              className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-lg rounded-xl hover:shadow-xl transition-all"
            >
              Select Your Subjects
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {filteredSubjects.map(subject => (
              <div
                key={subject.id}
                className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all transform hover:scale-105 overflow-hidden"
              >
                <div className="p-8">
                  <div className="text-6xl mb-4 text-center">
                    {getSubjectIcon(subject.name, subject.category)}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-900 mb-2 text-center">
                    {subject.name}
                  </h3>
                  
                  {subject.category && (
                    <div className="flex justify-center mb-3">
                      <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 text-sm font-semibold rounded-full">
                        {subject.category}
                      </span>
                    </div>
                  )}
                  
                  {subject.description && (
                    <p className="text-gray-600 text-center mb-6 line-clamp-2">
                      {subject.description}
                    </p>
                  )}
                  
                  <button
                    onClick={() => handleStartLearning(subject.id, subject.name)}
                    className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
                  >
                    Start Learning 🚀
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Sujets verrouillés */}
        {lockedSubjects.length > 0 && (
          <div className="mt-12">
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-2xl p-6 mb-6">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">🔒</span>
                <h2 className="text-2xl font-bold text-gray-900">
                  Unlock More Subjects
                </h2>
              </div>
              <p className="text-gray-700 mb-4">
                Upgrade your plan to access {lockedSubjects.length} more subjects
              </p>
              <a
                href="/pricing"
                className="inline-block px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-all shadow-md hover:shadow-lg"
              >
                View Plans 💎
              </a>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {lockedSubjects.map(subject => (
                <div
                  key={subject.id}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden opacity-60 relative"
                >
                  <div className="absolute inset-0 bg-gray-900 bg-opacity-10 backdrop-blur-sm flex items-center justify-center z-10">
                    <div className="text-center">
                      <div className="text-5xl mb-2">🔒</div>
                      <p className="text-gray-900 font-bold">Premium Only</p>
                    </div>
                  </div>
                  
                  <div className="p-8">
                    <div className="text-6xl mb-4 text-center blur-sm">
                      {getSubjectIcon(subject.name, subject.category)}
                    </div>
                    
                    <h3 className="text-2xl font-bold text-gray-900 mb-2 text-center">
                      {subject.name}
                    </h3>
                    
                    {subject.category && (
                      <div className="flex justify-center mb-3">
                        <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-sm font-semibold rounded-full">
                          {subject.category}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
     </>
  )
}