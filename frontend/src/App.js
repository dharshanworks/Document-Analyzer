import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Analyze from './components/Analyze';
import About from './components/About';
import Navigation from './components/Navigation';
import ScrollToTop from './components/ScrollToTop';
import { clearAuthToken, getToken } from './api';
import { ToastProvider } from './components/Toast';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

function KeyboardShortcuts() {
  useKeyboardShortcuts();
  return null;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getToken()));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsAuthenticated(Boolean(getToken()));
    setLoading(false);

    const onStorage = () => setIsAuthenticated(Boolean(getToken()));
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    clearAuthToken();
    setIsAuthenticated(false);
  };

  const PrivateRoute = ({ children }) => {
    if (loading) {
      return <div className="da-loading-screen">Loading workspace...</div>;
    }

    return isAuthenticated ? children : <Navigate to="/login" replace />;
  };

  const PublicRoute = ({ children }) => {
    if (loading) {
      return <div className="da-loading-screen">Loading workspace...</div>;
    }

    return children;
  };

  const withShell = (page) => (
    <div className="da-shell">
      <Navigation onLogout={handleLogout} />
      <main className="da-shell-main">{page}</main>
    </div>
  );

  return (
    <ToastProvider>
      <Router>
        <div className="da-app">
          <KeyboardShortcuts />
          <ScrollToTop />
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <Home />
              }
            />

            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <PublicRoute><Login onLoginSuccess={handleLogin} /></PublicRoute>
                )
              }
            />

            <Route
              path="/register"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <PublicRoute><Register onRegisterSuccess={handleLogin} /></PublicRoute>
                )
              }
            />

            <Route
              path="/dashboard"
              element={<PrivateRoute>{withShell(<Dashboard onLogout={handleLogout} />)}</PrivateRoute>}
            />

            <Route
              path="/analyze"
              element={<PrivateRoute>{withShell(<Analyze />)}</PrivateRoute>}
            />

            <Route path="/about" element={<PublicRoute><About /></PublicRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </ToastProvider>
  );
}

export default App;
