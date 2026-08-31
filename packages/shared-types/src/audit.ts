export interface AuditLogEntry {
  id: string;
  sequenceNumber: number;
  tenantId: string;
  userId: string;
  userEmail: string;
  action: string;
  resourceType: string;
  resourceId: string;
  ipAddress: string;
  userAgent: string;
  details: Record<string, any>;
  previousHash: string;
  currentHash: string;
  timestamp: string;
}
