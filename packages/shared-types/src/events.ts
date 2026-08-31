export type NexusEventType = 
  | 'PIPELINE_TRIGGERED'
  | 'PIPELINE_COMPLETED'
  | 'STEP_STARTED'
  | 'STEP_FINISHED'
  | 'RUNNER_ONLINE'
  | 'RUNNER_OFFLINE'
  | 'IAC_DRIFT_DETECTED'
  | 'K8S_ROLLOUT_CANARY_PROMOTED'
  | 'SECURITY_CRITICAL_CVE_DETECTED'
  | 'ALERT_TRIGGERED';

export interface NexusEvent<T = any> {
  eventId: string;
  eventType: NexusEventType;
  tenantId: string;
  timestamp: string;
  payload: T;
}
