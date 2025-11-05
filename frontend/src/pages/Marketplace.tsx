import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/Marketplace.css';

const Marketplace: React.FC = () => {
  const [offers, setOffers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [requestForm, setRequestForm] = useState({
    ram_gb: 32,
    vram_gb: 12,
    duration_sec: 3600,
    max_price_per_gb_sec: 0.000002,
    prefer_local: true,
  });

  useEffect(() => {
    loadOffers();
  }, []);

  const loadOffers = async () => {
    try {
      const data = await api.browseMarketplace();
      setOffers(data.offers);
    } catch (error) {
      console.error('Failed to load marketplace:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await api.requestMemory(requestForm);
      alert(`Found ${result.matches.length} matching nodes!`);
      setShowRequestForm(false);
    } catch (error) {
      console.error('Request failed:', error);
      alert('Failed to request memory');
    }
  };

  if (loading) {
    return <div className="loading">Loading marketplace...</div>;
  }

  return (
    <div className="marketplace-container">
      <div className="marketplace-header">
        <h1>Memory Marketplace</h1>
        <button onClick={() => setShowRequestForm(!showRequestForm)} className="btn btn-primary">
          {showRequestForm ? 'Hide Request Form' : 'Request Memory'}
        </button>
      </div>

      {showRequestForm && (
        <div className="request-form">
          <h3>Request Memory</h3>
          <form onSubmit={handleRequest}>
            <div className="form-row">
              <label>RAM (GB):</label>
              <input
                type="number"
                value={requestForm.ram_gb}
                onChange={(e) => setRequestForm({...requestForm, ram_gb: Number(e.target.value)})}
              />
            </div>
            <div className="form-row">
              <label>VRAM (GB):</label>
              <input
                type="number"
                value={requestForm.vram_gb}
                onChange={(e) => setRequestForm({...requestForm, vram_gb: Number(e.target.value)})}
              />
            </div>
            <div className="form-row">
              <label>Duration (seconds):</label>
              <input
                type="number"
                value={requestForm.duration_sec}
                onChange={(e) => setRequestForm({...requestForm, duration_sec: Number(e.target.value)})}
              />
            </div>
            <button type="submit" className="btn btn-primary">Find Matches</button>
          </form>
        </div>
      )}

      <div className="offers-grid">
        {offers.map((offer, index) => (
          <div key={index} className="offer-card">
            <h3>{offer.node_name}</h3>
            <div className="node-type">{offer.node_type}</div>
            <div className="stat">
              <span>Region:</span>
              <strong>{offer.region}</strong>
            </div>
            <div className="stat">
              <span>Available RAM:</span>
              <strong>{offer.available_ram_gb} GB</strong>
            </div>
            <div className="stat">
              <span>Available VRAM:</span>
              <strong>{offer.available_vram_gb} GB</strong>
            </div>
            <div className="stat">
              <span>Price:</span>
              <strong>${(offer.price_per_gb_sec * 1000000).toFixed(3)}/GB/μs</strong>
            </div>
            <div className="stat">
              <span>Uptime:</span>
              <strong>{offer.uptime_score}%</strong>
            </div>
            {offer.distance_km && (
              <div className="stat">
                <span>Distance:</span>
                <strong>{offer.distance_km.toFixed(1)} km</strong>
              </div>
            )}
          </div>
        ))}
      </div>

      {offers.length === 0 && (
        <div className="no-results">
          <p>No offers available at the moment.</p>
        </div>
      )}
    </div>
  );
};

export default Marketplace;
