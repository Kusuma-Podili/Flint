import { PipelineStep } from '@nexusops/shared-types';

export interface DAGNode {
  id: string;
  step: PipelineStep;
  dependencies: string[];
  dependents: string[];
  level: number;
}

export class DependencyGraph {
  private nodes: Map<string, DAGNode> = new Map();

  constructor(steps: PipelineStep[]) {
    this.buildGraph(steps);
  }

  private buildGraph(steps: PipelineStep[]): void {
    // Initialize nodes
    for (const step of steps) {
      this.nodes.set(step.id, {
        id: step.id,
        step,
        dependencies: [...(step.dependsOn || [])],
        dependents: [],
        level: 0
      });
    }

    // Connect dependents
    for (const [id, node] of this.nodes.entries()) {
      for (const depId of node.dependencies) {
        const parent = this.nodes.get(depId);
        if (!parent) {
          throw new Error(`Step '${id}' depends on non-existent step '${depId}'`);
        }
        parent.dependents.push(id);
      }
    }
  }

  public getNode(id: string): DAGNode | undefined {
    return this.nodes.get(id);
  }

  public getAllNodes(): DAGNode[] {
    return Array.from(this.nodes.values());
  }

  public getRootNodes(): DAGNode[] {
    return Array.from(this.nodes.values()).filter(n => n.dependencies.length === 0);
  }

  public getLeafNodes(): DAGNode[] {
    return Array.from(this.nodes.values()).filter(n => n.dependents.length === 0);
  }
}
