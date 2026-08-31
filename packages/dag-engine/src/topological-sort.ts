import { DependencyGraph } from './graph';
import { CycleDetector } from './cycle-detector';

export interface ExecutionStage {
  stageIndex: number;
  parallelSteps: string[];
}

export class TopologicalSorter {
  public static computeExecutionStages(graph: DependencyGraph): ExecutionStage[] {
    const cycleCheck = CycleDetector.hasCycle(graph);
    if (cycleCheck.hasCycle) {
      throw new Error(`Circular dependency detected in pipeline graph: ${cycleCheck.cyclePath?.join(' -> ')}`);
    }

    // In-degree calculation
    const inDegree: Map<string, number> = new Map();
    for (const node of graph.getAllNodes()) {
      inDegree.set(node.id, node.dependencies.length);
    }

    const stages: ExecutionStage[] = [];
    let currentLevel: string[] = [];

    for (const [id, deg] of inDegree.entries()) {
      if (deg === 0) currentLevel.push(id);
    }

    let stageIdx = 0;
    while (currentLevel.length > 0) {
      stages.push({
        stageIndex: stageIdx++,
        parallelSteps: [...currentLevel]
      });

      const nextLevel: string[] = [];
      for (const nodeId of currentLevel) {
        const node = graph.getNode(nodeId);
        if (node) {
          for (const depId of node.dependents) {
            const cur = (inDegree.get(depId) || 0) - 1;
            inDegree.set(depId, cur);
            if (cur === 0) {
              nextLevel.push(depId);
            }
          }
        }
      }
      currentLevel = nextLevel;
    }

    return stages;
  }
}
