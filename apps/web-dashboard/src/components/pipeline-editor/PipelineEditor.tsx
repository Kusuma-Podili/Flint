import React, { useState } from 'react';
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 50, y: 100 }, data: { label: 'git-checkout' }, type: 'input' },
  { id: '2', position: { x: 250, y: 50 }, data: { label: 'unit-tests' } },
  { id: '3', position: { x: 250, y: 150 }, data: { label: 'trivy-security-scan' } },
  { id: '4', position: { x: 450, y: 100 }, data: { label: 'docker-build-push' } },
  { id: '5', position: { x: 650, y: 100 }, data: { label: 'k8s-canary-deploy' }, type: 'output' }
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3', animated: true },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e3-4', source: '3', target: '4' },
  { id: 'e4-5', source: '4', target: '5', animated: true }
];

export function VisualPipelineEditor() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  return (
    <div className="h-[600px] w-full bg-[#0d131f] border border-border rounded-xl overflow-hidden relative shadow-2xl">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background color="#1f2937" gap={16} />
        <Controls />
        <MiniMap nodeColor="#3b82f6" />
      </ReactFlow>
    </div>
  );
}
