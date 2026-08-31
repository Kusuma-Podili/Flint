export type PipelineStatus = 'QUEUED' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'CANCELLED' | 'BLOCKED';
export type StepStatus = 'PENDING' | 'WAITING_DEPS' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'SKIPPED';

export interface PipelineTrigger {
  type: 'MANUAL' | 'GIT_PUSH' | 'GIT_PR' | 'CRON_SCHEDULE' | 'WEBHOOK' | 'API';
  actor: string;
  branch?: string;
  commitSha?: string;
  pullRequestId?: number;
  parameters?: Record<string, string>;
}

export interface PipelineStep {
  id: string;
  name: string;
  image?: string;
  command?: string[];
  script?: string;
  environment?: Record<string, string>;
  dependsOn?: string[];
  timeoutSeconds?: number;
  retryCount?: number;
  allowFailure?: boolean;
  condition?: string;
}

export interface PipelineDefinition {
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  repositoryUrl?: string;
  defaultBranch: string;
  variables: Record<string, string>;
  steps: PipelineStep[];
  concurrencyGroup?: string;
  timeoutMinutes: number;
  createdAt: string;
  updatedAt: string;
}

export interface PipelineRun {
  id: string;
  pipelineId: string;
  tenantId: string;
  runNumber: number;
  status: PipelineStatus;
  trigger: PipelineTrigger;
  durationMs: number;
  startedAt?: string;
  finishedAt?: string;
  stepResults: Record<string, StepExecutionResult>;
}

export interface StepExecutionResult {
  stepId: string;
  name: string;
  status: StepStatus;
  exitCode: number;
  durationMs: number;
  runnerId?: string;
  logChunkCount: number;
  startedAt?: string;
  finishedAt?: string;
  errorMessage?: string;
}
