import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminUserList() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [totalUsers, setTotalUsers] = useState(0)
  const [page, setPage] = useState(0)
  const [selectedUser, setSelectedUser] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)
  
  const limit = 20

  useEffect(() => {
    fetchUsers()
  }, [page])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`http://localhost:8000/api/admin/users?limit=${limit}&offset=${page * limit}`)
      setUsers(res.data.users)
      setTotalUsers(res.data.total)
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSuspend = async (userId, username) => {
    if (!confirm(`Are you sure you want to suspend ${username}?`)) return
    
    const reason = prompt('Reason for suspension:')
    if (!reason) return
    
    setActionLoading(true)
    try {
      await axios.post('http://localhost:8000/api/admin/users/suspend', {
        user_id: userId,
        reason
      })
      alert(`User ${username} has been suspended`)
      fetchUsers()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to suspend user')
    } finally {
      setActionLoading(false)
    }
  }

  const handleActivate = async (userId, username) => {
    if (!confirm(`Are you sure you want to activate ${username}?`)) return
    
    setActionLoading(true)
    try {
      await axios.post(`http://localhost:8000/api/admin/users/${userId}/activate`)
      alert(`User ${username} has been activated`)
      fetchUsers()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to activate user')
    } finally {
      setActionLoading(false)
    }
  }

  const handleChangeRole = async (userId, username, currentRole) => {
    const newRole = prompt(`Change role for ${username}.\nCurrent: ${currentRole}\nEnter new role (student/teacher/admin):`)
    if (!newRole || !['student', 'teacher', 'admin'].includes(newRole.toLowerCase())) {
      alert('Invalid role')
      return
    }
    
    if (!confirm(`Change ${username} role from ${currentRole} to ${newRole}?`)) return
    
    setActionLoading(true)
    try {
      await axios.post('http://localhost:8000/api/admin/users/change-role', {
        user_id: userId,
        new_role: newRole.toLowerCase()
      })
      alert(`Role changed successfully`)
      fetchUsers()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to change role')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-white mx-auto mb-4"></div>
        <p className="text-white">Loading users...</p>
      </div>
    )
  }

  const totalPages = Math.ceil(totalUsers / limit)

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white bg-opacity-10 rounded-xl p-6 backdrop-blur-sm border border-white border-opacity-20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">User Management</h2>
            <p className="text-gray-300">Total: {totalUsers} users</p>
          </div>
          <button
            onClick={fetchUsers}
            className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg font-semibold hover:bg-opacity-20 transition-all"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white bg-opacity-10 rounded-xl backdrop-blur-sm border border-white border-opacity-20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white bg-opacity-10">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">User</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">Email</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">Role</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">Status</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">Stats</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white">Joined</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-white">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white divide-opacity-10">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-white hover:bg-opacity-5 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold">
                        {user.username?.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-white font-semibold">{user.username}</p>
                        <p className="text-gray-400 text-sm">{user.full_name || 'N/A'}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-300">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      user.role === 'admin' ? 'bg-red-500 bg-opacity-20 text-red-300' :
                      user.role === 'teacher' ? 'bg-blue-500 bg-opacity-20 text-blue-300' :
                      'bg-green-500 bg-opacity-20 text-green-300'
                    }`}>
                      {user.role?.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      user.is_active
                        ? 'bg-green-500 bg-opacity-20 text-green-300'
                        : 'bg-red-500 bg-opacity-20 text-red-300'
                    }`}>
                      {user.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <p className="text-white">{user.stats.completed_sessions} quizzes</p>
                      <p className="text-gray-400">{user.stats.average_score.toFixed(0)}% avg</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-300 text-sm">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {user.is_active ? (
                        <button
                          onClick={() => handleSuspend(user.id, user.username)}
                          disabled={actionLoading || user.role === 'admin'}
                          className="px-3 py-1 bg-red-500 bg-opacity-20 text-red-300 rounded-lg text-sm font-semibold hover:bg-opacity-30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Suspend
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivate(user.id, user.username)}
                          disabled={actionLoading}
                          className="px-3 py-1 bg-green-500 bg-opacity-20 text-green-300 rounded-lg text-sm font-semibold hover:bg-opacity-30 transition-colors disabled:opacity-50"
                        >
                          Activate
                        </button>
                      )}
                      
                      <button
                        onClick={() => handleChangeRole(user.id, user.username, user.role)}
                        disabled={actionLoading}
                        className="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-300 rounded-lg text-sm font-semibold hover:bg-opacity-30 transition-colors disabled:opacity-50"
                      >
                        Change Role
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm border border-white border-opacity-20">
          <p className="text-gray-300 text-sm">
            Showing {page * limit + 1} to {Math.min((page + 1) * limit, totalUsers)} of {totalUsers}
          </p>
          
          <div className="flex gap-2">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
              className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg font-semibold hover:bg-opacity-20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <span className="px-4 py-2 text-white font-semibold">
              Page {page + 1} of {totalPages}
            </span>
            
            <button
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
              className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg font-semibold hover:bg-opacity-20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

    </div>
  )
}