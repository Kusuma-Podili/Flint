import { PolicyRule } from '@nexusops/shared-types';

export const K8S_POD_SECURITY_RULES: PolicyRule[] = [
  {
    id: 'PSS-BASELINE-01',
    name: 'Disallow Host Namespaces',
    category: 'CONTAINER',
    severity: 'HIGH',
    regoCode: 'package nexusops.pss
default allow = true
allow = false { input.hostNetwork == true }',
    description: 'Host network and IPC namespaces share host network configuration and memory.',
    remediationAdvice: 'Ensure hostNetwork, hostPID, and hostIPC are set to false.',
    enabled: true
  }
];
