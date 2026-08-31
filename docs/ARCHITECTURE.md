# NexusOps Architecture & System Design Document

## System Components
1. **API Gateway (`apps/api-gateway`)**: Entry point with TLS termination, rate-limiting, and RBAC token decoding.
2. **Control Plane (`apps/control-plane`)**: Core modular microservices domain engine.
3. **DAG Engine (`packages/dag-engine`)**: Graph topological resolution and matrix build scheduling.
4. **IaC Manager (`packages/iac-parser`)**: State diffing and automated drift analysis for Terraform/Tofu.
5. **Security Policy Engine (`packages/policy-engine`)**: OPA Rego governance and Trivy vulnerability analyzer.
6. **Runner Agent (`apps/runner-agent`)**: High-performance isolated execution daemon.
7. **Web Dashboard (`apps/web-dashboard`)**: Next.js 14 real-time visual console.
