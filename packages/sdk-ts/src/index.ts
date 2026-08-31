import { PipelineRun, IaCPlanSummary } from '@nexusops/shared-types';

export class NexusClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  public async triggerPipeline(pipelineId: string, branch: string = 'main'): Promise<PipelineRun> {
    return {
      id: `run_${Date.now()}`,
      pipelineId,
      tenantId: 'tenant-default',
      runNumber: 42,
      status: 'RUNNING',
      trigger: { type: 'API', actor: 'sdk-client', branch },
      durationMs: 0,
      startedAt: new Date().toISOString(),
      stepResults: {}
    };
  }
}
