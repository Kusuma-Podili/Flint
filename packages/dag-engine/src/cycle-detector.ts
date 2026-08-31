import { DependencyGraph } from './graph';

export class CycleDetector {
  public static hasCycle(graph: DependencyGraph): { hasCycle: boolean; cyclePath?: string[] } {
    const visited = new Set<string>();
    const recStack = new Set<string>();
    const path: string[] = [];

    const dfs = (nodeId: string): boolean => {
      visited.add(nodeId);
      recStack.add(nodeId);
      path.push(nodeId);

      const node = graph.getNode(nodeId);
      if (node) {
        for (const neighbor of node.dependents) {
          if (!visited.has(neighbor)) {
            if (dfs(neighbor)) return true;
          } else if (recStack.has(neighbor)) {
            path.push(neighbor);
            return true;
          }
        }
      }

      recStack.delete(nodeId);
      path.pop();
      return false;
    };

    for (const node of graph.getAllNodes()) {
      if (!visited.has(node.id)) {
        if (dfs(node.id)) {
          return { hasCycle: true, cyclePath: [...path] };
        }
      }
    }

    return { hasCycle: false };
  }
}
