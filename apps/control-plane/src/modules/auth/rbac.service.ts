export class RbacService {
  private static readonly ROLE_PERMISSIONS: Record<string, string[]> = {
    SUPER_ADMIN: ['*'],
    ORG_ADMIN: [
      'pipelines:create', 'pipelines:read', 'pipelines:update', 'pipelines:delete', 'pipelines:execute',
      'runners:register', 'runners:read', 'runners:manage',
      'iac:plan', 'iac:apply', 'iac:drift', 'iac:manage',
      'k8s:deploy', 'k8s:rollback', 'k8s:manage',
      'secrets:create', 'secrets:read', 'secrets:update', 'secrets:delete',
      'security:audit', 'security:manage_policy',
      'users:manage', 'apikeys:manage', 'tenant:settings'
    ],
    DEVOPS_ENGINEER: [
      'pipelines:create', 'pipelines:read', 'pipelines:update', 'pipelines:execute',
      'runners:read',
      'iac:plan', 'iac:apply', 'iac:drift',
      'k8s:deploy', 'k8s:rollback',
      'secrets:create', 'secrets:read',
      'security:audit'
    ],
    DEVELOPER: [
      'pipelines:read', 'pipelines:execute',
      'runners:read',
      'iac:plan',
      'k8s:read',
      'security:read'
    ],
    SECURITY_AUDITOR: [
      'pipelines:read',
      'iac:read',
      'k8s:read',
      'security:audit', 'security:manage_policy',
      'audit:read'
    ],
    VIEWER: [
      'pipelines:read',
      'runners:read',
      'iac:read',
      'k8s:read',
      'security:read'
    ]
  };

  public hasPermission(role: string, requiredPermission: string): boolean {
    const permissions = RbacService.ROLE_PERMISSIONS[role] || [];
    if (permissions.includes('*')) {
      return true;
    }
    if (permissions.includes(requiredPermission)) {
      return true;
    }
    const [scope] = requiredPermission.split(':');
    return permissions.includes(`${scope}:*`);
  }

  public getPermissionsForRole(role: string): string[] {
    return RbacService.ROLE_PERMISSIONS[role] || [];
  }
}
