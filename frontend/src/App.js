import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage    from './pages/LoginPage';
import Dashboard    from './pages/Dashboard';
import GoldPage     from './pages/GoldPage';
import FraudPage    from './pages/FraudPage';
import SpamPage     from './pages/SpamPage';
import RainfallPage from './pages/RainfallPage';

// Protected route wrapper
function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login"     element={<LoginPage />} />
        <Route path="/"          element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/gold"      element={<PrivateRoute><GoldPage /></PrivateRoute>} />
        <Route path="/fraud"     element={<PrivateRoute><FraudPage /></PrivateRoute>} />
        <Route path="/spam"      element={<PrivateRoute><SpamPage /></PrivateRoute>} />
        <Route path="/rainfall"  element={<PrivateRoute><RainfallPage /></PrivateRoute>} />
        <Route path="*"          element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
