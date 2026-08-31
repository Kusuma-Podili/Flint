export type RunnerType = 'SELF_HOSTED' | 'MANAGED_K8S' | 'DOCKER_ISOLATED' | 'CLOUD_VM';
export type RunnerStatus = 'ONLINE' | 'BUSY' | 'OFFLINE' | 'DRAINING';

export interface RunnerInfo {
  id: string;
  tenantId: string;
  name: string;
  type: RunnerType;
  status: RunnerStatus;
  version: string;
  os: string;
  arch: string;
  ipAddress: string;
  tags: string[];
  currentJobId?: string;
  totalJobsExecuted: number;
  lastHeartbeat: string;
  registeredAt: string;
}

export interface RunnerJobPayload {
  jobId: string;
  runId: string;
  pipelineId: string;
  stepId: string;
  image: string;
  script: string;
  environment: Record<string, string>;
  timeoutSeconds: number;
  secrets: Record<string, string>;
  artifactUploadUrl?: string;
}
