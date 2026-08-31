import { PolicyRule } from '@nexusops/shared-types';

export const CIS_BENCHMARK_RULES: PolicyRule[] = [
  {
    id: 'CIS-AWS-1.1',
    name: 'Avoid the use of the "root" account',
    category: 'IAM',
    severity: 'CRITICAL',
    regoCode: 'package nexusops.cis.aws
default allow = false
allow { not input.is_root_user }',
    description: 'The root account has complete unrestricted access to all resources in AWS.',
    remediationAdvice: 'Create individual IAM users with least privilege access and lock down the root credentials.',
    enabled: true
  },
  {
    id: 'CIS-K8S-5.2.1',
    name: 'Minimize the admission of privileged containers',
    category: 'CONTAINER',
    severity: 'HIGH',
    regoCode: 'package nexusops.cis.k8s
default allow = false
allow { not input.securityContext.privileged }',
    description: 'Privileged containers have all root capabilities on the host node.',
    remediationAdvice: 'Set securityContext.privileged to false in the pod specification.',
    enabled: true
  }
];
