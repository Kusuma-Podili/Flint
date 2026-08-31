import { PolicyRule, Severity } from '@nexusops/shared-types';

export interface EvaluationResult {
  ruleId: string;
  ruleName: string;
  passed: boolean;
  severity: Severity;
  message: string;
  remediationAdvice: string;
}

export class PolicyEngine {
  private rules: PolicyRule[] = [];

  public registerRule(rule: PolicyRule): void {
    this.rules.push(rule);
  }

  public evaluateResource(resourceType: string, resourceConfig: Record<string, any>): EvaluationResult[] {
    const results: EvaluationResult[] = [];

    for (const rule of this.rules) {
      if (!rule.enabled) continue;

      // Sample evaluation logic
      if (rule.category === 'CONTAINER' && resourceType === 'k8s_pod') {
        const runAsNonRoot = resourceConfig.securityContext?.runAsNonRoot === true;
        results.push({
          ruleId: rule.id,
          ruleName: rule.name,
          passed: runAsNonRoot,
          severity: rule.severity,
          message: runAsNonRoot ? 'Pod complies with non-root execution' : 'Pod allows container to run as root',
          remediationAdvice: rule.remediationAdvice
        });
      }
    }

    return results;
  }
}
