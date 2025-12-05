import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Login from './pages/Login';
import Signup from './pages/Signup';
import FarmerDashboard from './pages/FarmerDashboard';
import VetDashboard from './pages/VetDashboard';
import AdminDashboard from './pages/AdminDashboard';
import VideoCall from './pages/VideoCall';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            
            <Route
              path="/farmer"
              element={
                <ProtectedRoute allowedRoles={['farmer']}>
                  <FarmerDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/vet"
              element={
                <ProtectedRoute allowedRoles={['vet']}>
                  <VetDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/video-call"
              element={
                <ProtectedRoute>
                  <VideoCall />
                </ProtectedRoute>
              }
            />
            
            <Route path="/unauthorized" element={<div className="min-h-screen flex items-center justify-center">
              <h1 className="text-2xl">Unauthorized Access</h1>
            </div>} />
            
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
