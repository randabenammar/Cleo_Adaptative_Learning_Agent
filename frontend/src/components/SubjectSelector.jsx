import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { getSubjectIcon } from '../utils/SubjectIcons'  // ⭐ AJOUTER

export default function SubjectSelector({ maxSubjects = 2, onComplete }) {
  const [allSubjects, setAllSubjects] = useState([])
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchAllSubjects()
  }, [])

  const fetchAllSubjects = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      const res = await axios.get('http://localhost:8000/api/subjects/all', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setAllSubjects(res.data.subjects || [])
      
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSubject = (subjectId) => {
    if (selected.includes(subjectId)) {
      setSelected(selected.filter(id => id !== subjectId))
    } else {
      if (selected.length < maxSubjects) {
        setSelected([...selected, subjectId])
      } else {
        alert(`You can only select up to ${maxSubjects} subjects with your FREE plan`)
      }
    }
  }

  const handleSave = async () => {
    if (selected.length === 0) {
      alert(`Please select at least 1 subject`)
      return
    }

    setSaving(true)
    
    try {
      const token = localStorage.getItem('access_token')
      
      await axios.post(
        'http://localhost:8000/api/subscriptions/favorites',
        { subject_ids: selected },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      console.log('✅ Favorites saved successfully')
      onComplete()
      
    } catch (error) {
      console.error('❌ Error saving favorites:', error)
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        alert(detail.message || 'Error saving your selection')
      } else {
        alert('Error saving your selection')
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full p-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🎯</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Choose Your Learning Subjects
          </h2>
          <p className="text-gray-600 text-lg mb-2">
            Select <span className="font-bold text-indigo-600">{maxSubjects} subjects</span> you want to focus on
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border-2 border-indigo-200 rounded-lg">
            <span className="text-2xl">{selected.length}/{maxSubjects}</span>
            <span className="font-semibold text-indigo-700">selected</span>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Loading subjects...</p>
          </div>
        ) : (
          <>
            {/* Grid des sujets */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {allSubjects.map(subject => {
                const isSelected = selected.includes(subject.id)
                const isDisabled = !isSelected && selected.length >= maxSubjects
                
                return (
                  <button
                    key={subject.id}
                    onClick={() => !isDisabled && toggleSubject(subject.id)}
                    disabled={isDisabled}
                    className={`p-6 rounded-xl border-2 text-left transition-all transform ${
                      isSelected
                        ? 'bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-500 shadow-xl scale-105'
                        : 'bg-white border-gray-200 hover:border-indigo-300 hover:shadow-lg'
                    } ${
                      isDisabled
                        ? 'opacity-40 cursor-not-allowed'
                        : 'cursor-pointer hover:scale-102'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* ⭐ UTILISER getSubjectIcon */}
                      <div className="text-4xl">
                        {getSubjectIcon(subject.name, subject.category)}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-gray-900 mb-1">
                          {subject.name}
                        </h3>
                        {subject.description && (
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {subject.description}
                          </p>
                        )}
                        {subject.category && (
                          <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded font-medium">
                            {subject.category}
                          </span>
                        )}
                      </div>
                      {isSelected && (
                        <div className="text-green-500 text-3xl font-bold">✓</div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Bouton de sauvegarde */}
            <div className="sticky bottom-0 bg-white pt-6 border-t-2 border-gray-200">
              <button
                onClick={handleSave}
                disabled={saving || selected.length === 0 || selected.length > maxSubjects}
                className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-xl rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
              >
                {saving ? (
                  <span className="flex items-center justify-center gap-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    Saving...
                  </span>
                ) : (
                  `✓ Save My ${selected.length} Subject${selected.length !== 1 ? 's' : ''}`
                )}
              </button>
              
              {selected.length === 0 && (
                <p className="text-center text-gray-500 text-sm mt-3">
                  Please select at least 1 subject
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}