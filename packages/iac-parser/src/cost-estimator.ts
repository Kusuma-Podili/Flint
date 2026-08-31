export class CloudCostEstimator {
  private static readonly HOURLY_RATES: Record<string, number> = {
    'aws_instance.t3.medium': 0.0416,
    'aws_instance.m5.large': 0.096,
    'aws_eks_cluster': 0.10,
    'aws_rds_cluster': 0.25,
    'google_container_cluster': 0.10,
    'azurerm_kubernetes_cluster': 0.10
  };

  public static estimateMonthlyDelta(resourceType: string, count: number): number {
    const hourly = CloudCostEstimator.HOURLY_RATES[resourceType] || 0.05;
    return hourly * 730 * count;
  }
}
