import React from 'react';

export function ClusterTopologyViewer() {
  return (
    <div className="p-4 bg-card rounded-xl border border-border">
      <h3 className="text-sm font-bold text-white mb-2">Multi-Cluster Mesh Topology</h3>
      <div className="flex space-x-4 text-xs text-gray-400">
        <span>Production-US-East (12 nodes)</span>
        <span>Staging-EU-West (4 nodes)</span>
      </div>
    </div>
  );
}
