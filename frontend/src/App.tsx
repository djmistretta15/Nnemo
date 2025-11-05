import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Services
import api from './services/api';
import wsClient from './services/websocket';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Marketplace from './pages/Marketplace';
import MyNodes from './pages/MyNodes';
import MyContracts from './pages/MyContracts';
import Clusters from './pages/Clusters';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('mnemo_token');
      if (token) {
        const userData = await api.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);

        // Connect WebSocket
        wsClient.connect(userData.id, token);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      api.clearToken();
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await api.login(email, password);
      setUser(response.user);
      setIsAuthenticated(true);

      // Connect WebSocket
      const token = localStorage.getItem('mnemo_token');
      if (token) {
        wsClient.connect(response.user.id, token);
      }

      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const handleLogout = () => {
    api.clearToken();
    wsClient.disconnect();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading MNEMO...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        {isAuthenticated && (
          <nav className="navbar">
            <div className="nav-brand">
              <h2>🧠 MNEMO</h2>
            </div>
            <div className="nav-links">
              <a href="/">Dashboard</a>
              <a href="/marketplace">Marketplace</a>
              <a href="/nodes">My Nodes</a>
              <a href="/contracts">Contracts</a>
              <a href="/clusters">Clusters</a>
            </div>
            <div className="nav-user">
              <span>{user?.email}</span>
              <button onClick={handleLogout} className="btn-logout">Logout</button>
            </div>
          </nav>
        )}

        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />

          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Dashboard user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          <Route
            path="/marketplace"
            element={
              isAuthenticated ? (
                <Marketplace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          <Route
            path="/nodes"
            element={
              isAuthenticated ? (
                <MyNodes user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          <Route
            path="/contracts"
            element={
              isAuthenticated ? (
                <MyContracts />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          <Route
            path="/clusters"
            element={
              isAuthenticated ? (
                <Clusters />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
