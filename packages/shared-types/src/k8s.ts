export type RolloutStrategyType = 'CANARY' | 'BLUE_GREEN' | 'ROLLING_UPDATE' | 'RECREATE';
export type ClusterHealthStatus = 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'UNREACHABLE';

export interface K8sCluster {
  id: string;
  tenantId: string;
  name: string;
  environment: 'PRODUCTION' | 'STAGING' | 'QA' | 'DEV';
  apiEndpoint: string;
  version: string;
  nodeCount: number;
  health: ClusterHealthStatus;
  namespaces: string[];
  installedOperators: string[];
  lastPing: string;
}

export interface RolloutSpec {
  serviceName: string;
  namespace: string;
  clusterId: string;
  strategy: RolloutStrategyType;
  targetImage: string;
  targetReplicas: number;
  canaryStepPercentage: number;
  canaryAnalysisIntervalSeconds: number;
  maxFailureThreshold: number;
  autoRollback: boolean;
}

export interface RolloutStatus {
  serviceName: string;
  strategy: RolloutStrategyType;
  currentPhase: 'PROMOTING' | 'ANALYZING' | 'STABLE' | 'ROLLING_BACK' | 'FAILED';
  activeWeightPercentage: number;
  canaryWeightPercentage: number;
  healthyReplicas: number;
  errorRatePercentage: number;
  updatedAt: string;
}
