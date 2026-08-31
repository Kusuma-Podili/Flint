# NexusOps Security & Governance Whitepaper

NexusOps employs a zero-trust security architecture:
- AES-256-GCM Envelope Encryption for all secrets at rest.
- Cryptographically verifiable hash-chained immutable audit trail.
- OPA Rego policy enforcement for all pipeline definitions and IaC commits.
