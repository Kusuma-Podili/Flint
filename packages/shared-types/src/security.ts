export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface SecurityVulnerability {
  id: string;
  package: string;
  installedVersion: string;
  fixedVersion?: string;
  severity: Severity;
  title: string;
  cveId: string;
  cvssScore: number;
  description: string;
  primaryUrl: string;
}

export interface PolicyRule {
  id: string;
  name: string;
  category: 'INFRASTRUCTURE' | 'CONTAINER' | 'IAM' | 'NETWORK' | 'SECRETS';
  severity: Severity;
  regoCode: string;
  description: string;
  remediationAdvice: string;
  enabled: boolean;
}

export interface ComplianceScore {
  tenantId: string;
  overallScore: number; // 0 - 100
  passedRules: number;
  failedRules: number;
  criticalVulnerabilities: number;
  highVulnerabilities: number;
  frameworks: {
    cisBenchmark: number;
    soc2: number;
    hipaa: number;
    pciDss: number;
  };
  calculatedAt: string;
}
