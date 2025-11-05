import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Clusters: React.FC = () => {
  const [clusters, setClusters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClusters();
  }, []);

  const loadClusters = async () => {
    try {
      const data = await api.listClusters();
      setClusters(data.clusters);
    } catch (error) {
      console.error('Failed to load clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading clusters...</div>;
  }

  return (
    <div className="page-container">
      <h1>Geographic Clusters</h1>
      <p className="subtitle">Memory meshes across regions with network effects</p>

      <div className="clusters-grid">
        {clusters.map((cluster, index) => (
          <div key={index} className="cluster-card">
            <h3>{cluster.region}</h3>
            <div className="cluster-stat">
              <span>Total Nodes:</span>
              <strong>{cluster.total_nodes}</strong>
            </div>
            <div className="node-composition">
              <div>Datacenters: {cluster.node_composition.datacenter}</div>
              <div>Edge Clusters: {cluster.node_composition.edge_cluster}</div>
              <div>Mist Nodes: {cluster.node_composition.mist_node}</div>
            </div>
            <div className="cluster-stat">
              <span>Total RAM:</span>
              <strong>{cluster.total_ram_gb} GB</strong>
            </div>
            <div className="cluster-stat">
              <span>Available RAM:</span>
              <strong>{cluster.available_ram_gb} GB</strong>
            </div>
            <div className="cluster-stat">
              <span>Total VRAM:</span>
              <strong>{cluster.total_vram_gb} GB</strong>
            </div>
            <div className="cluster-stat">
              <span>Available VRAM:</span>
              <strong>{cluster.available_vram_gb} GB</strong>
            </div>
            {cluster.avg_price_per_gb_sec && (
              <div className="cluster-stat">
                <span>Avg Price:</span>
                <strong>${(cluster.avg_price_per_gb_sec * 1000000).toFixed(3)}/GB/μs</strong>
              </div>
            )}
            <div className="cluster-location">
              📍 {cluster.center.lat?.toFixed(2)}, {cluster.center.lng?.toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      {clusters.length === 0 && (
        <div className="empty-state">
          <p>No clusters available yet.</p>
        </div>
      )}
    </div>
  );
};

export default Clusters;
