import React from 'react';

export default function PipelinesPage() {
  const items = [1, 2, 3, 4, 5, 6, 7, 8];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Pipelines Studio & Execution Timeline</h1>
          <p className="text-sm text-gray-400">Enterprise management console for pipelines.</p>
        </div>
        <div className="flex space-x-3">
          <button className="bg-card hover:bg-card/80 text-gray-300 px-3 py-1.5 rounded-lg text-xs font-medium border border-border transition">
            Export Report
          </button>
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition shadow-lg shadow-blue-500/20">
            + Action
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card p-5 rounded-xl border border-border col-span-2">
          <h2 className="text-base font-semibold text-white mb-4">Active Resources (pipelines)</h2>
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item} className="p-3 bg-background/50 rounded-lg border border-border/60 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-sm text-gray-200">pipelines-resource-0{item}</div>
                  <div className="text-xs text-gray-500">Last synchronized 2 minutes ago by GitOps worker</div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  HEALTHY
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card p-5 rounded-xl border border-border">
          <h2 className="text-base font-semibold text-white mb-4">Subsystem Metrics</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-gray-400">Resource Utilization</span>
                <span className="text-gray-200">42%</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: '42%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-gray-400">Compliance Pass Rate</span>
                <span className="text-emerald-400">98.5%</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: '98.5%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
