import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdminUserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          limit: 100,
          search: searchTerm || undefined,
          role: roleFilter || undefined,
          is_active: statusFilter ? (statusFilter === 'active') : undefined
        }
      })
      setUsers(res.data.users)
    } catch (error) {
      console.error('Error fetching users:', error)
      alert('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleChangeRole = async (userId, newRole) => {
    if (!confirm(`Change user role to ${newRole}?`)) return

    setActionLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.put(
        `http://localhost:8000/api/admin/users/${userId}/role`,
        { role: newRole },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('Role changed successfully!')
      fetchUsers()
    } catch (error) {
      console.error('Error changing role:', error)
      alert(error.response?.data?.detail || 'Failed to change role')
    } finally {
      setActionLoading(false)
    }
  }

  const handleSuspend = async (userId) => {
    const reason = prompt('Enter suspension reason:')
    if (!reason) return

    setActionLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.put(
        `http://localhost:8000/api/admin/users/${userId}/suspend`,
        { reason },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('User suspended successfully!')
      fetchUsers()
    } catch (error) {
      console.error('Error suspending user:', error)
      alert(error.response?.data?.detail || 'Failed to suspend user')
    } finally {
      setActionLoading(false)
    }
  }

  const handleActivate = async (userId) => {
    if (!confirm('Activate this user?')) return

    setActionLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.put(
        `http://localhost:8000/api/admin/users/${userId}/activate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('User activated successfully!')
      fetchUsers()
    } catch (error) {
      console.error('Error activating user:', error)
      alert(error.response?.data?.detail || 'Failed to activate user')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (userId) => {
    if (!confirm('⚠️ DELETE this user permanently? This cannot be undone!')) return

    setActionLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.delete(
        `http://localhost:8000/api/admin/users/${userId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('User deleted successfully!')
      fetchUsers()
    } catch (error) {
      console.error('Error deleting user:', error)
      alert(error.response?.data?.detail || 'Failed to delete user')
    } finally {
      setActionLoading(false)
    }
  }

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-700'
      case 'teacher': return 'bg-blue-100 text-blue-700'
      case 'student': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
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

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">User Management</h2>
        <div className="text-white">
          <span className="text-3xl font-bold">{users.length}</span>
          <span className="text-sm ml-2">Total Users</span>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Search */}
        <div>
          <input
            type="text"
            placeholder="Search by name, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchUsers()}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-white focus:border-transparent"
          />
        </div>

        {/* Role Filter */}
        <div>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-white focus:border-transparent"
          >
            <option value="">All Roles</option>
            <option value="student">Students</option>
            <option value="teacher">Teachers</option>
            <option value="admin">Admins</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-white focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Suspended</option>
          </select>
        </div>
      </div>

      {/* Apply Filters Button */}
      <button
        onClick={fetchUsers}
        className="bg-white text-indigo-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
      >
        Apply Filters
      </button>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stats
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                        {user.username[0].toUpperCase()}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username}
                        </div>
                        <div className="text-sm text-gray-500">
                          {user.full_name || 'No name set'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? '✓ Active' : '✗ Suspended'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>{user.stats?.total_sessions || 0} sessions</div>
                    <div>{user.stats?.average_score || 0}% avg score</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      {/* Change Role Dropdown */}
                      <select
                        onChange={(e) => handleChangeRole(user.id, e.target.value)}
                        disabled={actionLoading}
                        className="text-xs border border-gray-300 rounded px-2 py-1 hover:border-indigo-500"
                        defaultValue=""
                      >
                        <option value="" disabled>Change Role</option>
                        <option value="student">→ Student</option>
                        <option value="teacher">→ Teacher</option>
                        <option value="admin">→ Admin</option>
                      </select>

                      {/* Suspend/Activate */}
                      {user.is_active ? (
                        <button
                          onClick={() => handleSuspend(user.id)}
                          disabled={actionLoading}
                          className="text-orange-600 hover:text-orange-900 disabled:opacity-50"
                          title="Suspend User"
                        >
                          🚫
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivate(user.id)}
                          disabled={actionLoading}
                          className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          title="Activate User"
                        >
                          ✓
                        </button>
                      )}

                      {/* Delete */}
                      <button
                        onClick={() => handleDelete(user.id)}
                        disabled={actionLoading}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        title="Delete User"
                      >
                        🗑️
                      </button>

                      {/* View Details */}
                      <button
                        onClick={() => {
                          setSelectedUser(user)
                          setShowModal(true)
                        }}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="View Details"
                      >
                        👁️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {users.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No users found</p>
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {showModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-8">
              {/* Close Button */}
              <button
                onClick={() => setShowModal(false)}
                className="float-right text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>

              {/* User Info */}
              <div className="flex items-center gap-4 mb-6">
                <div className="h-20 w-20 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-3xl">
                  {selectedUser.username[0].toUpperCase()}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedUser.username}
                  </h2>
                  <p className="text-gray-600">{selectedUser.email}</p>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-500">Full Name</p>
                  <p className="font-semibold">{selectedUser.full_name || 'Not set'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Role</p>
                  <p className="font-semibold capitalize">{selectedUser.role}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className={`font-semibold ${selectedUser.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {selectedUser.is_active ? 'Active' : 'Suspended'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Verified</p>
                  <p className="font-semibold">{selectedUser.is_verified ? 'Yes ✓' : 'No ✗'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Joined</p>
                  <p className="font-semibold">
                    {selectedUser.created_at ? new Date(selectedUser.created_at).toLocaleDateString() : 'Unknown'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Last Login</p>
                  <p className="font-semibold">
                    {selectedUser.last_login ? new Date(selectedUser.last_login).toLocaleDateString() : 'Never'}
                  </p>
                </div>
              </div>

              {/* Stats */}
              {selectedUser.stats && (
                <div className="bg-indigo-50 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Learning Statistics</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-indigo-600">
                        {selectedUser.stats.total_sessions || 0}
                      </p>
                      <p className="text-sm text-gray-600">Total Sessions</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">
                        {selectedUser.stats.completed_sessions || 0}
                      </p>
                      <p className="text-sm text-gray-600">Completed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">
                        {selectedUser.stats.average_score || 0}%
                      </p>
                      <p className="text-sm text-gray-600">Avg Score</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}