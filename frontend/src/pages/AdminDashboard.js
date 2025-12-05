import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [analyticsRes, usersRes] = await Promise.all([
        api.get('/admin/analytics?days=30'),
        api.get('/admin/users?limit=50')
      ]);
      setAnalytics(analyticsRes.data);
      setUsers(usersRes.data.users);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">{user?.full_name}</span>
            <button onClick={logout} className="text-red-600 hover:text-red-800">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Reports</h3>
            <p className="text-3xl font-bold text-gray-900">
              {Object.values(analytics?.reports_by_status || {}).reduce((a, b) => a + b, 0)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">New Users (30d)</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics?.new_users || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Pending Cases</h3>
            <p className="text-3xl font-bold text-yellow-600">
              {analytics?.reports_by_status?.pending || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Avg Resolution</h3>
            <p className="text-3xl font-bold text-green-600">
              {analytics?.avg_resolution_hours ? `${analytics.avg_resolution_hours}h` : 'N/A'}
            </p>
          </div>
        </div>

        {/* Top Diseases */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-bold">Top Diseases (Last 30 Days)</h2>
          </div>
          <div className="p-6">
            {analytics?.top_diseases?.length > 0 ? (
              <div className="space-y-3">
                {analytics.top_diseases.map((item, idx) => (
                  <div key={idx} className="flex items-center">
                    <div className="w-32 text-sm font-medium">{item.disease}</div>
                    <div className="flex-1">
                      <div className="bg-gray-200 rounded-full h-4">
                        <div
                          className="bg-blue-600 h-4 rounded-full"
                          style={{
                            width: `${(item.count / analytics.top_diseases[0].count) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                    <div className="w-16 text-right text-sm text-gray-600">{item.count}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No data available</p>
            )}
          </div>
        </div>

        {/* User Management */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-bold">Users</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.full_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                        user.role === 'vet' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
