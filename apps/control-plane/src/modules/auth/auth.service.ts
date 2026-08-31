import { RbacService } from './rbac.service';
import { AuthenticationError, AuthorizationError } from '@nexusops/shared-types';
import * as crypto from 'crypto';

export class AuthService {
  private rbacService: RbacService;

  constructor() {
    this.rbacService = new RbacService();
  }

  public hashPassword(password: string): string {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    return `${salt}:${hash}`;
  }

  public verifyPassword(password: string, storedHash: string): boolean {
    const [salt, originalHash] = storedHash.split(':');
    if (!salt || !originalHash) return false;
    const testHash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    return crypto.timingSafeEqual(Buffer.from(testHash, 'hex'), Buffer.from(originalHash, 'hex'));
  }

  public generateApiKey(tenantId: string, userId: string, name: string): { key: string; prefix: string; hashedSecret: string } {
    const rawSecret = crypto.randomBytes(32).toString('hex');
    const prefix = `nx_${crypto.randomBytes(4).toString('hex')}`;
    const fullKey = `${prefix}_${rawSecret}`;
    const hashedSecret = crypto.createHash('sha256').update(fullKey).digest('hex');
    return { key: fullKey, prefix, hashedSecret };
  }

  public verifyApiKey(providedKey: string, storedHashedSecret: string): boolean {
    const computedHash = crypto.createHash('sha256').update(providedKey).digest('hex');
    return crypto.timingSafeEqual(Buffer.from(computedHash, 'hex'), Buffer.from(storedHashedSecret, 'hex'));
  }
}
