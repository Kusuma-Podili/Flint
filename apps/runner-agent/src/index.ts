import { RunnerJobPayload } from '@nexusops/shared-types';

export class NexusRunnerAgent {
  private agentId: string;
  private serverUrl: string;

  constructor(agentId: string, serverUrl: string) {
    this.agentId = agentId;
    this.serverUrl = serverUrl;
  }

  public async start(): Promise<void> {
    console.log(`[NEXUS-AGENT] Starting worker agent ${this.agentId} connected to ${this.serverUrl}`);
  }

  public async executeJob(job: RunnerJobPayload): Promise<{ exitCode: number; logs: string[] }> {
    console.log(`[NEXUS-AGENT] Executing step: ${job.stepId} in image: ${job.image}`);
    return {
      exitCode: 0,
      logs: [`Starting step ${job.stepId}`, 'Command executed successfully.']
    };
  }
}
