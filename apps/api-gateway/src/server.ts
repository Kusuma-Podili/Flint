import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

const app = express();
const PORT = process.env.GATEWAY_PORT || 8080;

app.use(helmet());
app.use(cors({ origin: '*' }));
app.use(express.json());

// Global Rate Limiter: 1000 req/min per IP
const globalLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 1000,
  message: { error: 'Too many requests, please slow down.' }
});
app.use(globalLimiter);

// Health Endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'HEALTHY',
    service: 'nexusops-api-gateway',
    timestamp: new Date().toISOString(),
    uptimeSeconds: process.uptime()
  });
});

// Gateway Routing Table
app.get('/api/v1/routes', (req: Request, res: Response) => {
  res.json({
    routes: [
      { prefix: '/api/v1/auth', service: 'control-plane-auth' },
      { prefix: '/api/v1/pipelines', service: 'control-plane-pipelines' },
      { prefix: '/api/v1/runners', service: 'control-plane-runners' },
      { prefix: '/api/v1/iac', service: 'control-plane-iac' },
      { prefix: '/api/v1/kubernetes', service: 'control-plane-k8s' },
      { prefix: '/api/v1/security', service: 'control-plane-security' },
      { prefix: '/api/v1/observability', service: 'control-plane-observability' }
    ]
  });
});

app.listen(PORT, () => {
  console.log(`[API-GATEWAY] NexusOps API Gateway running on port ${PORT}`);
});
