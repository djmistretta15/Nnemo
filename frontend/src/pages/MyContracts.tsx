import React, { useState, useEffect } from 'react';
import api from '../services/api';

const MyContracts: React.FC = () => {
  const [contracts, setContracts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      const data = await api.listContracts();
      setContracts(data);
    } catch (error) {
      console.error('Failed to load contracts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading contracts...</div>;
  }

  return (
    <div className="page-container">
      <h1>My Contracts</h1>

      {contracts.length === 0 ? (
        <div className="empty-state">
          <p>No contracts yet.</p>
        </div>
      ) : (
        <div className="contracts-list">
          {contracts.map((contract) => (
            <div key={contract.id} className="contract-card">
              <div className="contract-header">
                <h3>Contract {contract.id.substring(0, 8)}...</h3>
                <span className={`status-badge status-${contract.status}`}>
                  {contract.status}
                </span>
              </div>
              <div className="contract-details">
                <p>RAM: {contract.ram_gb} GB</p>
                <p>VRAM: {contract.vram_gb} GB</p>
                <p>Duration: {contract.duration_sec}s</p>
                <p>Cost: ${contract.total_cost_usd}</p>
                <p>Start: {new Date(contract.start_time).toLocaleString()}</p>
                <p>End: {new Date(contract.end_time).toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyContracts;
