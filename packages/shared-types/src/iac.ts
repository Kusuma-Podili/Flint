export type IaCTool = 'TERRAFORM' | 'OPENTOFU' | 'PULUMI' | 'CLOUDFORMATION';
export type IaCAction = 'PLAN' | 'APPLY' | 'DESTROY' | 'DRIFT_DETECT';
export type DriftStatus = 'IN_SYNC' | 'DRIFT_DETECTED' | 'SCAN_FAILED' | 'UNKNOWN';

export interface IaCWorkspace {
  id: string;
  tenantId: string;
  name: string;
  provider: 'AWS' | 'GCP' | 'AZURE' | 'KUBERNETES';
  tool: IaCTool;
  workingDirectory: string;
  repositoryUrl: string;
  branch: string;
  stateBackend: 'S3' | 'GCS' | 'AZURE_BLOB' | 'POSTGRES';
  isLocked: boolean;
  lockedBy?: string;
  driftStatus: DriftStatus;
  lastDriftScanAt?: string;
  resourceCount: number;
  estimatedMonthlyCostUsd: number;
  createdAt: string;
  updatedAt: string;
}

export interface IaCPlanSummary {
  workspaceId: string;
  action: IaCAction;
  resourcesToAdd: number;
  resourcesToChange: number;
  resourcesToDestroy: number;
  planOutput: string;
  costDeltaUsd: number;
  hasBreakingChanges: boolean;
  generatedAt: string;
}
