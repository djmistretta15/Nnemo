import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface MyNodesProps {
  user: any;
}

const MyNodes: React.FC<MyNodesProps> = ({ user }) => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNodes();
  }, []);

  const loadNodes = async () => {
    try {
      const data = await api.listNodes();
      setNodes(data.filter((n: any) => n.owner_id === user.id));
    } catch (error) {
      console.error('Failed to load nodes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading your nodes...</div>;
  }

  return (
    <div className="page-container">
      <h1>My Nodes</h1>

      {nodes.length === 0 ? (
        <div className="empty-state">
          <p>You don't have any nodes yet.</p>
          <p>Install the node agent to start earning!</p>
        </div>
      ) : (
        <div className="nodes-grid">
          {nodes.map((node) => (
            <div key={node.id} className="node-card">
              <h3>{node.name}</h3>
              <div className="node-status">{node.status}</div>
              <p>Type: {node.node_type}</p>
              <p>Region: {node.region}</p>
              <p>RAM: {node.available_ram_gb}/{node.total_ram_gb} GB</p>
              <p>VRAM: {node.available_vram_gb}/{node.total_vram_gb} GB</p>
              <p>Uptime: {node.uptime_score}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyNodes;
