export type UserRole = 'SUPER_ADMIN' | 'ORG_ADMIN' | 'DEVOPS_ENGINEER' | 'DEVELOPER' | 'SECURITY_AUDITOR' | 'VIEWER';

export interface UserSession {
  userId: string;
  tenantId: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: string[];
  mfaVerified: boolean;
  issuedAt: number;
  expiresAt: number;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: 'FREE' | 'TEAM' | 'ENTERPRISE';
  concurrencyLimit: number;
  maxRunners: number;
  createdAt: string;
  updatedAt: string;
}

export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  hashedSecret: string;
  tenantId: string;
  userId: string;
  scopes: string[];
  lastUsedAt?: string;
  expiresAt?: string;
  createdAt: string;
}

export interface PermissionDefinition {
  action: string;
  resource: string;
  description: string;
}
