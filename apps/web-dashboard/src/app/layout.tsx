import React from 'react';
import './globals.css';

export const metadata = {
  title: 'NexusOps | Enterprise DevOps Automation',
  description: 'Enterprise Continuous Delivery, Multi-Cloud IaC, and Kubernetes Orchestration',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen flex flex-col">
        <header className="border-b border-border bg-card/60 backdrop-blur px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded bg-gradient-to-tr from-blue-600 to-emerald-400 flex items-center justify-center font-bold text-white shadow-lg">
              N
            </div>
            <span className="text-xl font-black tracking-wider text-white">Nexus<span className="text-blue-500">Ops</span></span>
          </div>
          <nav className="flex space-x-6 text-sm font-medium text-gray-300">
            <a href="/pipelines" className="hover:text-blue-400 transition">Pipelines</a>
            <a href="/deployments" className="hover:text-blue-400 transition">Deployments</a>
            <a href="/iac" className="hover:text-blue-400 transition">Cloud IaC</a>
            <a href="/clusters" className="hover:text-blue-400 transition">Kubernetes</a>
            <a href="/security" className="hover:text-blue-400 transition">DevSecOps</a>
            <a href="/observability" className="hover:text-blue-400 transition">Observability</a>
          </nav>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </body>
    </html>
  );
}
