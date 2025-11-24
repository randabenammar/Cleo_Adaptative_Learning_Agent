import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminSubjectManagement() {
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingSubject, setEditingSubject] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    summary: '',
    key_concepts: '',
    prerequisites: '',
    learning_objectives: '',
    estimated_duration_hours: 10,
    difficulty_rating: 3.0
  })

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    setLoading(true)
    try {
      const res = await axios.get('http://localhost:8000/api/subjects/list')
      setSubjects(res.data.subjects)
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingSubject(null)
    setFormData({
      name: '',
      category: '',
      summary: '',
      key_concepts: '',
      prerequisites: '',
      learning_objectives: '',
      estimated_duration_hours: 10,
      difficulty_rating: 3.0
    })
    setShowModal(true)
  }

  const handleEdit = (subject) => {
    setEditingSubject(subject)
    setFormData({
      name: subject.name,
      category: subject.category,
      summary: subject.description || subject.summary || '',
      key_concepts: Array.isArray(subject.key_concepts) ? subject.key_concepts.join(', ') : '',
      prerequisites: Array.isArray(subject.prerequisites) ? subject.prerequisites.join(', ') : '',
      learning_objectives: Array.isArray(subject.learning_objectives) ? subject.learning_objectives.join(', ') : '',
      estimated_duration_hours: subject.estimated_duration_hours || 10,
      difficulty_rating: subject.difficulty_rating || 3.0
    })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setActionLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      
      const payload = {
        name: formData.name,
        category: formData.category,
        summary: formData.summary,
        key_concepts: formData.key_concepts.split(',').map(s => s.trim()).filter(Boolean),
        prerequisites: formData.prerequisites.split(',').map(s => s.trim()).filter(Boolean),
        learning_objectives: formData.learning_objectives.split(',').map(s => s.trim()).filter(Boolean),
        estimated_duration_hours: parseInt(formData.estimated_duration_hours),
        difficulty_rating: parseFloat(formData.difficulty_rating)
      }

      if (editingSubject) {
        // Update
        await axios.put(
          `http://localhost:8000/api/subjects/${editingSubject.id}`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        )
        alert('Subject updated successfully!')
      } else {
        // Create
        await axios.post(
          'http://localhost:8000/api/subjects/',
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        )
        alert('Subject created successfully!')
      }

      setShowModal(false)
      fetchSubjects()
    } catch (error) {
      console.error('Error saving subject:', error)
      alert(error.response?.data?.detail || 'Failed to save subject')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (subjectId, subjectName) => {
    if (!confirm(`⚠️ DELETE "${subjectName}"? This cannot be undone!`)) return

    setActionLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.delete(
        `http://localhost:8000/api/subjects/${subjectId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('Subject deleted successfully!')
      fetchSubjects()
    } catch (error) {
      console.error('Error deleting subject:', error)
      alert(error.response?.data?.detail || 'Failed to delete subject')
    } finally {
      setActionLoading(false)
    }
  }

  const getDifficultyColor = (rating) => {
    if (rating <= 2) return 'text-green-600'
    if (rating <= 3.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-white mx-auto mb-4"></div>
        <p className="text-white">Loading subjects...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Subject Management</h2>
        <button
          onClick={handleCreate}
          className="bg-white text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors flex items-center gap-2"
        >
          <span className="text-xl">+</span>
          Create New Subject
        </button>
      </div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects.map((subject) => (
          <div
            key={subject.id}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
          >
            {/* Icon & Title */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="text-4xl mb-2">{subject.icon}</div>
                <h3 className="text-xl font-bold text-gray-900">{subject.name}</h3>
                <p className="text-sm text-gray-600">{subject.category}</p>
              </div>
              <span className={`text-2xl font-bold ${getDifficultyColor(subject.difficulty_rating)}`}>
                {subject.difficulty_rating.toFixed(1)}
              </span>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-700 mb-4 line-clamp-2">
              {subject.description || subject.summary || 'No description'}
            </p>

            {/* Meta */}
            <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
              <span>⏱️ {subject.estimated_duration_hours}h</span>
              <span>📊 {subject.difficulty_level}</span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleEdit(subject)}
                disabled={actionLoading}
                className="flex-1 bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg font-semibold hover:bg-indigo-100 transition-colors disabled:opacity-50"
              >
                ✏️ Edit
              </button>
              <button
                onClick={() => handleDelete(subject.id, subject.name)}
                disabled={actionLoading}
                className="flex-1 bg-red-50 text-red-600 px-4 py-2 rounded-lg font-semibold hover:bg-red-100 transition-colors disabled:opacity-50"
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {subjects.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl">
          <p className="text-gray-500">No subjects found. Create your first one!</p>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full my-8">
            <form onSubmit={handleSubmit} className="p-8">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingSubject ? 'Edit Subject' : 'Create New Subject'}
                </h2>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>

              {/* Form Fields */}
              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Subject Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., Machine Learning"
                  />
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Category *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., AI, Programming, Data Science"
                  />
                </div>

                {/* Summary */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Summary
                  </label>
                  <textarea
                    value={formData.summary}
                    onChange={(e) => setFormData({...formData, summary: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Brief description of the subject..."
                  />
                </div>

                {/* Key Concepts */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Key Concepts (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.key_concepts}
                    onChange={(e) => setFormData({...formData, key_concepts: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., Neural Networks, Deep Learning, NLP"
                  />
                </div>

                {/* Prerequisites */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Prerequisites (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.prerequisites}
                    onChange={(e) => setFormData({...formData, prerequisites: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., Python basics, Statistics"
                  />
                </div>

                {/* Learning Objectives */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Learning Objectives (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.learning_objectives}
                    onChange={(e) => setFormData({...formData, learning_objectives: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., Build ML models, Deploy AI systems"
                  />
                </div>

                {/* Duration & Difficulty */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Duration (hours)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="200"
                      value={formData.estimated_duration_hours}
                      onChange={(e) => setFormData({...formData, estimated_duration_hours: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Difficulty (1-5)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="5"
                      step="0.1"
                      value={formData.difficulty_rating}
                      onChange={(e) => setFormData({...formData, difficulty_rating: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-4 mt-6">
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50"
                >
                  {actionLoading ? 'Saving...' : (editingSubject ? 'Update Subject' : 'Create Subject')}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}