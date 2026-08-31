import { IaCPlanSummary } from '@nexusops/shared-types';

export interface ResourceChange {
  address: string;
  type: string;
  action: 'create' | 'update' | 'delete' | 'no-op';
  before?: Record<string, any>;
  after?: Record<string, any>;
}

export class TerraformPlanAnalyzer {
  public static analyzePlanJson(planJson: any): IaCPlanSummary {
    let toAdd = 0;
    let toChange = 0;
    let toDestroy = 0;

    const resourceChanges: ResourceChange[] = planJson.resource_changes || [];

    for (const change of resourceChanges) {
      const actions: string[] = change.change?.actions || [];
      if (actions.includes('create') && actions.includes('delete')) {
        toChange++;
      } else if (actions.includes('create')) {
        toAdd++;
      } else if (actions.includes('delete')) {
        toDestroy++;
      } else if (actions.includes('update')) {
        toChange++;
      }
    }

    return {
      workspaceId: planJson.workspace_id || 'ws-default',
      action: 'PLAN',
      resourcesToAdd: toAdd,
      resourcesToChange: toChange,
      resourcesToDestroy: toDestroy,
      planOutput: `Plan: ${toAdd} to add, ${toChange} to change, ${toDestroy} to destroy.`,
      costDeltaUsd: (toAdd * 15.5) - (toDestroy * 12.0),
      hasBreakingChanges: toDestroy > 0,
      generatedAt: new Date().toISOString()
    };
  }
}
