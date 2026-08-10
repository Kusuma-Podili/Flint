# Flint - Enterprise Cloud Automation & Continuous Delivery Platform

Flint is a unified, enterprise-grade cloud automation, continuous deployment, and multi-cloud infrastructure orchestration platform. It provides topological DAG pipeline execution, zero-downtime progressive Canary rollouts, OPA Rego governance, and automated drift detection.

---

## Architecture Overview

```
                          +------------------------------------------+
                          |   Flint Web Console & Management Studio  |
                          +--------------------+---------------------+
                                               |
                                               v
                          +--------------------+---------------------+
                          |   API Gateway & Cryptographic Envelope   |
                          +--------------------+---------------------+
                                               |
         +--------------------+----------------+-------------------+--------------------+
         |                    |                                    |                    |
         v                    v                                    v                    v
  +--------------+   +-------------------+                +-----------------+   +------------------+
  |  DAG Engine  |   | Multi-Cloud IaC   |                | OPA Rego Engine |   |  Runner Daemons  |
  | (Topological)|   | (Terraform/Tofu)  |                | & Vulnerability |   | (Isolated Agent) |
  +--------------+   +-------------------+                +-----------------+   +------------------+
```

---

## Dependencies

- **Node.js**: >= 18.0.0
- **Python**: >= 3.10.0
- **Docker**: >= 24.0.0
- **Kubernetes**: >= 1.28
- **PostgreSQL**: >= 15.0
- **Redis**: >= 7.0

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Kusuma-Podili/Flint.git
cd Flint
```

### 2. Node & TypeScript dependencies
```bash
npm install
```

### 3. Python control-plane virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
```

---

## Build

### Build TypeScript services and frontend packages
```bash
npm run build
```

### Build multi-stage production Docker image
```bash
docker build -t flint-platform:latest .
```

---

## Run

### Start the local platform service
```bash
python server.py
# Or start via npm:
npm start
```
The web dashboard will be available at: `http://localhost:8080`

### Start full stack with Docker Compose
```bash
docker compose up -d
```

---

## Usage & API Endpoints

- **Web Dashboard**: `http://localhost:8080/`
- **Health Check API**: `GET /api/v1/health`
- **Trigger Pipeline API**: `POST /api/v1/pipelines/trigger`
- **Prometheus Metrics**: `GET /api/v1/metrics`

---

## Testing

Run the automated test suite covering unit, integration, security guardrails, and full lifecycle E2E tests:
```bash
python tests/test_runner.py
```

---

## Security & Compliance

- **Zero-Secret Guarantee**: Cryptographic envelope encryption prevents plaintext credential exposure.
- **Audit Trails**: SHA-256 hash-chained immutable logging for SOC2 / ISO 27001 compliance.
- **Policy Guardrails**: Built-in Open Policy Agent (OPA) Rego evaluation against CIS benchmarks.

---

## License

Apache License 2.0 - See LICENSE for details.
