export class NexusError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly details?: any;

  constructor(code: string, message: string, statusCode: number = 500, details?: any) {
    super(message);
    this.name = 'NexusError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    Object.setPrototypeOf(this, NexusError.prototype);
  }
}

export class AuthenticationError extends NexusError {
  constructor(message: string = 'Authentication failed') {
    super('AUTH_UNAUTHORIZED', message, 401);
  }
}

export class AuthorizationError extends NexusError {
  constructor(message: string = 'Access forbidden: Insufficient permissions') {
    super('AUTH_FORBIDDEN', message, 403);
  }
}

export class NotFoundError extends NexusError {
  constructor(resource: string, id: string) {
    super('NOT_FOUND', `${resource} with ID '${id}' was not found`, 404);
  }
}

export class ValidationError extends NexusError {
  constructor(message: string, details?: any) {
    super('VALIDATION_ERROR', message, 400, details);
  }
}

export class ConflictError extends NexusError {
  constructor(message: string) {
    super('RESOURCE_CONFLICT', message, 409);
  }
}
