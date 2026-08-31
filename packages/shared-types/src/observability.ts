export interface MetricPoint {
  timestamp: number;
  value: number;
  labels: Record<string, string>;
}

export interface TelemetrySpan {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  name: string;
  serviceName: string;
  startTimeUs: number;
  durationUs: number;
  statusCode: 'OK' | 'ERROR';
  attributes: Record<string, string | number | boolean>;
}

export interface AlertRule {
  id: string;
  name: string;
  metricQuery: string;
  threshold: number;
  comparison: 'GT' | 'LT' | 'GTE' | 'LTE' | 'EQ';
  evaluationWindowMinutes: number;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  channels: ('SLACK' | 'PAGERDUTY' | 'EMAIL' | 'WEBHOOK')[];
  enabled: boolean;
}
