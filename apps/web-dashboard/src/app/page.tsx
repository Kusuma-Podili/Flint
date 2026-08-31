import React from 'react';

export default function DashboardHome() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Platform Overview</h1>
          <p className="text-sm text-gray-400">Real-time status of multi-cloud deployments, CI/CD pipelines, and security gates.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-lg shadow-blue-500/20">
          + New Pipeline
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-5 rounded-xl border border-border">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Pipelines</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-black text-white">24</span>
            <span className="text-xs text-emerald-400 font-medium">99.4% Success</span>
          </div>
        </div>
        <div className="bg-card p-5 rounded-xl border border-border">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Connected Clusters</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-black text-white">8</span>
            <span className="text-xs text-emerald-400 font-medium">All Healthy</span>
          </div>
        </div>
        <div className="bg-card p-5 rounded-xl border border-border">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Runners</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-black text-white">16</span>
            <span className="text-xs text-blue-400 font-medium">4 Busy</span>
          </div>
        </div>
        <div className="bg-card p-5 rounded-xl border border-border">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Security Score</span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-3xl font-black text-emerald-400">96/100</span>
            <span className="text-xs text-emerald-400 font-medium">SOC2 Compliant</span>
          </div>
        </div>
      </div>
    </div>
  );
}
