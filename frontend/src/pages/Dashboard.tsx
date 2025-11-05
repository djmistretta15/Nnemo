import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/Dashboard.css';

interface DashboardProps {
  user: any;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <h1>Dashboard</h1>
      <div className="welcome-section">
        <h2>Welcome back, {user?.full_name || user?.email}</h2>
        <p>Role: <span className="badge">{user?.role}</span></p>
      </div>

      <div className="stats-grid">
        {/* Provider Stats */}
        {stats?.provider && (
          <div className="stat-card provider-card">
            <h3>Provider Stats</h3>
            <div className="stat-row">
              <span>Total Nodes:</span>
              <strong>{stats.provider.total_nodes}</strong>
            </div>
            <div className="stat-row">
              <span>Total RAM:</span>
              <strong>{stats.provider.total_ram_gb} GB</strong>
            </div>
            <div className="stat-row">
              <span>Available RAM:</span>
              <strong>{stats.provider.available_ram_gb} GB</strong>
            </div>
            <div className="stat-row">
              <span>Total VRAM:</span>
              <strong>{stats.provider.total_vram_gb} GB</strong>
            </div>
            <div className="stat-row">
              <span>Available VRAM:</span>
              <strong>{stats.provider.available_vram_gb} GB</strong>
            </div>
            <div className="stat-row highlight">
              <span>Total Earnings:</span>
              <strong>${stats.provider.total_earnings.toFixed(2)}</strong>
            </div>
            <div className="stat-row">
              <span>Active Contracts:</span>
              <strong>{stats.provider.active_contracts}</strong>
            </div>
          </div>
        )}

        {/* Client Stats */}
        {stats?.client && (
          <div className="stat-card client-card">
            <h3>Client Stats</h3>
            <div className="stat-row">
              <span>Organization:</span>
              <strong>{stats.client.org_name}</strong>
            </div>
            <div className="stat-row highlight">
              <span>Total Spending:</span>
              <strong>${stats.client.total_spending.toFixed(2)}</strong>
            </div>
            <div className="stat-row">
              <span>Current Spend:</span>
              <strong>${stats.client.current_spend.toFixed(2)}</strong>
            </div>
            {stats.client.budget_monthly && (
              <div className="stat-row">
                <span>Monthly Budget:</span>
                <strong>${stats.client.budget_monthly.toFixed(2)}</strong>
              </div>
            )}
            <div className="stat-row">
              <span>Active Contracts:</span>
              <strong>{stats.client.active_contracts}</strong>
            </div>
          </div>
        )}

        {/* Market Overview */}
        {stats?.market && (
          <div className="stat-card market-card">
            <h3>Market Overview</h3>
            <div className="stat-row">
              <span>Total Nodes:</span>
              <strong>{stats.market.total_nodes}</strong>
            </div>
            <div className="stat-row">
              <span>Total RAM:</span>
              <strong>{stats.market.total_ram_gb} GB</strong>
            </div>
            <div className="stat-row">
              <span>Available RAM:</span>
              <strong>{stats.market.available_ram_gb} GB</strong>
            </div>
            <div className="stat-row">
              <span>Utilization Rate:</span>
              <strong>{stats.market.utilization_rate.toFixed(1)}%</strong>
            </div>
          </div>
        )}
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <a href="/marketplace" className="btn btn-primary">
            Browse Memory
          </a>
          <a href="/contracts" className="btn btn-secondary">
            View Contracts
          </a>
          <a href="/clusters" className="btn btn-secondary">
            View Clusters
          </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
