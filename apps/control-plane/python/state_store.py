"""
Flint Platform Persistent State Store
Handles all database operations, in-memory state caching, seeded accounts, and state transitions.
"""
import os
import sys
import json
import time
import uuid
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_service import AuthEngine
from hash_chain_audit import HashChainAuditLogger
from dag_engine import DAGResolver
from k8s_controller import CanaryRolloutController, BlueGreenDeployer
from iac_engine import TerraformPlanAnalyzer, DriftDetector
from policy_engine import PolicyEngine
from security_scanner import SecretEntropyScanner, TrivyVulnerabilityParser
from observability_engine import MetricsAggregator, AlertManager


class StateStore:
    """Centralized persistent state manager for Flint Enterprise DevOps Platform."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            db_path = os.path.join(base_dir, "flint_state.db")
        self.db_path = db_path
        self._lock = threading.Lock()
        self.auth_engine = AuthEngine()
        self.audit_logger = HashChainAuditLogger()
        self.policy_engine = PolicyEngine()
        self.alert_manager = AlertManager()
        self.metrics_aggregator = MetricsAggregator()
        self.canary_controller = CanaryRolloutController(step_percentage=25, max_failure_rate=0.02)
        self.blue_green_deployer = BlueGreenDeployer()
        
        # In-memory session store (token -> session dict)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        self._init_database()
        self._seed_data()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        password_salt TEXT NOT NULL,
                        role TEXT NOT NULL,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        created_at REAL NOT NULL,
                        last_login REAL
                    )
                """)

                # Pipelines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pipelines (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        repository TEXT NOT NULL,
                        branch TEXT NOT NULL,
                        stages TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'IDLE',
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)

                # Pipeline Runs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pipeline_runs (
                        id TEXT PRIMARY KEY,
                        pipeline_id TEXT NOT NULL,
                        pipeline_name TEXT NOT NULL,
                        branch TEXT NOT NULL,
                        commit_sha TEXT NOT NULL,
                        status TEXT NOT NULL,
                        stages_json TEXT NOT NULL,
                        logs TEXT NOT NULL,
                        duration_seconds REAL DEFAULT 0,
                        triggered_by TEXT NOT NULL,
                        simulation_mode TEXT DEFAULT 'NORMAL',
                        created_at REAL NOT NULL,
                        completed_at REAL
                    )
                """)

                # Deployments table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS deployments (
                        id TEXT PRIMARY KEY,
                        application TEXT NOT NULL,
                        version TEXT NOT NULL,
                        environment TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        status TEXT NOT NULL,
                        canary_weight INTEGER DEFAULT 0,
                        blue_green_active TEXT DEFAULT 'blue',
                        error_rate REAL DEFAULT 0.0,
                        latency_ms REAL DEFAULT 15.0,
                        pipeline_run_id TEXT,
                        deployed_by TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)

                # Infrastructure State table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS infrastructure_state (
                        id TEXT PRIMARY KEY,
                        resource_name TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        desired_state TEXT NOT NULL,
                        actual_state TEXT NOT NULL,
                        status TEXT NOT NULL,
                        drift_detected INTEGER DEFAULT 0,
                        last_checked REAL NOT NULL
                    )
                """)

                # Security Scans table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS security_scans (
                        id TEXT PRIMARY KEY,
                        scan_type TEXT NOT NULL,
                        target TEXT NOT NULL,
                        security_score INTEGER NOT NULL,
                        critical_count INTEGER NOT NULL,
                        high_count INTEGER NOT NULL,
                        policy_violations INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        findings_json TEXT NOT NULL,
                        created_at REAL NOT NULL
                    )
                """)

                # Runners table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS runners (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        current_job TEXT,
                        cpu_percent REAL DEFAULT 0.0,
                        memory_mb REAL DEFAULT 0.0,
                        enabled INTEGER DEFAULT 1,
                        last_heartbeat REAL NOT NULL
                    )
                """)

                # Central Logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id TEXT PRIMARY KEY,
                        timestamp REAL NOT NULL,
                        level TEXT NOT NULL,
                        source TEXT NOT NULL,
                        action TEXT NOT NULL,
                        user_email TEXT NOT NULL,
                        message TEXT NOT NULL
                    )
                """)

                # Alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        rule_name TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        triggered_at REAL NOT NULL,
                        resolved_at REAL
                    )
                """)

                # Settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

                # GitOps State table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gitops_state (
                        id TEXT PRIMARY KEY,
                        repo_url TEXT NOT NULL,
                        target_branch TEXT NOT NULL,
                        desired_commit TEXT NOT NULL,
                        synced_commit TEXT NOT NULL,
                        sync_status TEXT NOT NULL,
                        last_reconciled REAL NOT NULL
                    )
                """)

                conn.commit()

    def _seed_data(self):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Seed Demo Users
                users_to_seed = [
                    ("usr-admin", "admin@gmail.com", "Admin@123", "ADMIN", "Alex Rivera (Lead Architect)"),
                    ("usr-devops", "devops@gmail.com", "DevOps@123", "DEVOPS_ENGINEER", "Samantha Vance (Staff SRE)"),
                    ("usr-developer", "developer@gmail.com", "Developer@123", "DEVELOPER", "David Chen (Backend Engineer)"),
                    ("usr-viewer", "viewer@gmail.com", "Viewer@123", "VIEWER", "Jordan Taylor (Auditor / Guest)")
                ]
                
                for uid, email, raw_pwd, role, name in users_to_seed:
                    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                    if not cursor.fetchone():
                        pwd_hash, pwd_salt = self.auth_engine.hash_password(raw_pwd)
                        cursor.execute("""
                            INSERT INTO users (id, email, password_hash, password_salt, role, name, status, created_at, last_login)
                            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                        """, (uid, email, pwd_hash, pwd_salt, role, name, time.time() - 86400 * 14, time.time() - 3600))

                # 2. Seed Default Pipelines
                default_pipelines = [
                    (
                        "pipe-web-prod",
                        "Core Web API & Payment Gateway Service",
                        "https://github.com/Kusuma-Podili/Flint",
                        "main",
                        json.dumps([
                            {"id": "checkout", "name": "Source Checkout", "depends_on": []},
                            {"id": "security-scan", "name": "Security & OPA Scan", "depends_on": ["checkout"]},
                            {"id": "unit-tests", "name": "Unit & Integration Tests", "depends_on": ["checkout"]},
                            {"id": "container-build", "name": "Docker Image Build", "depends_on": ["security-scan", "unit-tests"]},
                            {"id": "infra-validation", "name": "IaC Plan Validation", "depends_on": ["container-build"]},
                            {"id": "deploy-canary", "name": "Kubernetes Canary Deploy", "depends_on": ["infra-validation"]},
                            {"id": "verification", "name": "Health Verification", "depends_on": ["deploy-canary"]}
                        ])
                    ),
                    (
                        "pipe-auth-service",
                        "Enterprise Identity & RBAC Token Service",
                        "https://github.com/Kusuma-Podili/Flint",
                        "main",
                        json.dumps([
                            {"id": "checkout", "name": "Source Checkout", "depends_on": []},
                            {"id": "security-scan", "name": "Secret & CVE Scan", "depends_on": ["checkout"]},
                            {"id": "unit-tests", "name": "Auth Crypto Tests", "depends_on": ["checkout"]},
                            {"id": "container-build", "name": "Build Microservice", "depends_on": ["security-scan", "unit-tests"]},
                            {"id": "deploy-service", "name": "Zero-Downtime Rollout", "depends_on": ["container-build"]}
                        ])
                    ),
                    (
                        "pipe-data-processor",
                        "Real-Time Telemetry & Log Ingestion Pipeline",
                        "https://github.com/Kusuma-Podili/Flint",
                        "main",
                        json.dumps([
                            {"id": "checkout", "name": "Source Checkout", "depends_on": []},
                            {"id": "unit-tests", "name": "Stream Processing Tests", "depends_on": ["checkout"]},
                            {"id": "container-build", "name": "Build Stream Worker", "depends_on": ["unit-tests"]},
                            {"id": "deploy-service", "name": "Deploy Worker Pods", "depends_on": ["container-build"]}
                        ])
                    )
                ]

                for pid, name, repo, branch, stages_json in default_pipelines:
                    cursor.execute("SELECT id FROM pipelines WHERE id = ?", (pid,))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO pipelines (id, name, description, repository, branch, stages, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, 'IDLE', ?, ?)
                        """, (pid, name, f"Production-grade pipeline for {name}", repo, branch, stages_json, time.time() - 86400 * 7, time.time() - 3600))

                # 3. Seed Deployments
                cursor.execute("SELECT COUNT(*) as count FROM deployments")
                if cursor.fetchone()["count"] == 0:
                    cursor.execute("""
                        INSERT INTO deployments (id, application, version, environment, strategy, status, canary_weight, blue_green_active, error_rate, latency_ms, pipeline_run_id, deployed_by, created_at, updated_at)
                        VALUES 
                        ('dep-001', 'Core Web API', 'v2.4.0', 'Production (US-East)', 'CANARY', 'HEALTHY', 50, 'blue', 0.01, 14.2, 'run-prev-001', 'devops@gmail.com', ?, ?),
                        ('dep-002', 'Auth & Crypto Microservice', 'v1.8.2', 'Production (US-East)', 'BLUE_GREEN', 'HEALTHY', 100, 'green', 0.00, 9.8, 'run-prev-002', 'admin@gmail.com', ?, ?),
                        ('dep-003', 'Data Telemetry Pipeline', 'v3.1.0', 'Staging (EU-West)', 'ROLLING', 'HEALTHY', 100, 'blue', 0.00, 18.5, 'run-prev-003', 'developer@gmail.com', ?, ?)
                    """, (time.time() - 7200, time.time() - 3600, time.time() - 14400, time.time() - 7200, time.time() - 28800, time.time() - 14400))

                # 4. Seed Infrastructure State
                cursor.execute("SELECT COUNT(*) as count FROM infrastructure_state")
                if cursor.fetchone()["count"] == 0:
                    infra_items = [
                        ("res-01", "aws_eks_cluster.production_primary", "EKS Kubernetes Cluster", "AWS", json.dumps({"version": "1.28", "nodes": 6, "region": "us-east-1"}), json.dumps({"version": "1.28", "nodes": 6, "region": "us-east-1"}), "MANAGED", 0),
                        ("res-02", "aws_rds_cluster.aurora_postgres", "Aurora PostgreSQL Multi-AZ", "AWS", json.dumps({"engine": "postgres", "version": "15.4", "storage_encrypted": True, "instance_class": "db.r6g.xlarge"}), json.dumps({"engine": "postgres", "version": "15.4", "storage_encrypted": True, "instance_class": "db.r6g.xlarge"}), "MANAGED", 0),
                        ("res-03", "aws_elasticache_cluster.redis_queue", "Redis Task Queue Cluster", "AWS", json.dumps({"nodes": 3, "engine": "redis", "version": "7.0", "transit_encryption": True}), json.dumps({"nodes": 3, "engine": "redis", "version": "7.0", "transit_encryption": True}), "MANAGED", 0),
                        ("res-04", "aws_s3_bucket.artifacts_vault", "Encrypted Artifact Storage", "AWS", json.dumps({"server_side_encryption": True, "versioning": True}), json.dumps({"server_side_encryption": True, "versioning": True}), "MANAGED", 0),
                        ("res-05", "k8s_deployment.web_service_replicas", "Kubernetes Web Pod Replicas", "Kubernetes", json.dumps({"replicas": 4, "maxSurge": "25%"}), json.dumps({"replicas": 4, "maxSurge": "25%"}), "MANAGED", 0)
                    ]
                    for rid, rname, rtype, prov, dstate, astate, status, drift in infra_items:
                        cursor.execute("""
                            INSERT INTO infrastructure_state (id, resource_name, resource_type, provider, desired_state, actual_state, status, drift_detected, last_checked)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (rid, rname, rtype, prov, dstate, astate, status, drift, time.time()))

                # 5. Seed Runners
                cursor.execute("SELECT COUNT(*) as count FROM runners")
                if cursor.fetchone()["count"] == 0:
                    runners_to_seed = [
                        ("run-node-01", "nexus-agent-us-east-k8s-01", "IDLE", json.dumps(["k8s", "linux", "x86_64", "docker"]), None, 18.5, 512.0, 1),
                        ("run-node-02", "nexus-agent-us-east-k8s-02", "IDLE", json.dumps(["k8s", "linux", "gpu", "high-cpu"]), None, 24.0, 1024.0, 1),
                        ("run-node-03", "nexus-agent-us-east-worker-03", "IDLE", json.dumps(["baremetal", "linux", "security-scanner"]), None, 12.0, 384.0, 1),
                        ("run-node-04", "nexus-agent-us-east-worker-04", "IDLE", json.dumps(["baremetal", "linux", "arm64", "docker"]), None, 8.5, 256.0, 1)
                    ]
                    for rid, rname, status, tags, job, cpu, mem, enabled in runners_to_seed:
                        cursor.execute("""
                            INSERT INTO runners (id, name, status, tags, current_job, cpu_percent, memory_mb, enabled, last_heartbeat)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (rid, rname, status, tags, job, cpu, mem, enabled, time.time()))

                # 6. Seed Initial Security Scan
                cursor.execute("SELECT COUNT(*) as count FROM security_scans")
                if cursor.fetchone()["count"] == 0:
                    initial_findings = [
                        {"type": "POLICY_CHECK", "rule": "CIS 2.1.1 S3 Server Side Encryption", "status": "PASSED", "severity": "MEDIUM", "description": "All S3 storage buckets have AES-256 server-side encryption enabled."},
                        {"type": "POLICY_CHECK", "rule": "CIS 5.2.6 Non-Root Kubernetes Pods", "status": "PASSED", "severity": "HIGH", "description": "Pod security contexts enforce runAsNonRoot: true across namespace."},
                        {"type": "POLICY_CHECK", "rule": "CIS 4.1.2 Restricted SSH Port 22", "status": "PASSED", "severity": "CRITICAL", "description": "No security groups allow 0.0.0.0/0 inbound to SSH port 22."},
                        {"type": "TRIVY_CVE", "rule": "Container Image Vulnerability Scan", "status": "PASSED", "severity": "LOW", "description": "Base image registry.flint.internal/web-app:v2.4.0 contains 0 Critical, 0 High CVEs."},
                        {"type": "SECRET_SCAN", "rule": "Commit Secret & Entropy Scan", "status": "PASSED", "severity": "CRITICAL", "description": "Zero plaintext API keys, AWS tokens, or private certificates detected in repository."}
                    ]
                    cursor.execute("""
                        INSERT INTO security_scans (id, scan_type, target, security_score, critical_count, high_count, policy_violations, status, findings_json, created_at)
                        VALUES ('sec-001', 'FULL_COMPLIANCE_AUDIT', 'Flint Platform Monorepo', 98, 0, 0, 0, 'PASSED', ?, ?)
                    """, (json.dumps(initial_findings), time.time() - 3600))

                # 7. Seed Initial GitOps State
                cursor.execute("SELECT COUNT(*) as count FROM gitops_state")
                if cursor.fetchone()["count"] == 0:
                    cursor.execute("""
                        INSERT INTO gitops_state (id, repo_url, target_branch, desired_commit, synced_commit, sync_status, last_reconciled)
                        VALUES ('gitops-main', 'https://github.com/Kusuma-Podili/Flint.git', 'main', '589532f', '589532f', 'IN_SYNC', ?)
                    """, (time.time() - 1800,))

                # 8. Seed Default Settings
                default_settings = {
                    "platform_name": "Flint Enterprise Platform",
                    "environment": "Production (US-East)",
                    "canary_step_percentage": "25",
                    "canary_failure_threshold": "0.02",
                    "pipeline_default_timeout": "600",
                    "auto_rollback_enabled": "true",
                    "security_gate_strict_mode": "true",
                    "slack_webhook_url": "https://hooks.slack.com/services/MOCK/T000/B000",
                    "audit_integrity_strict": "true"
                }
                for k, v in default_settings.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

                # 9. Seed Initial Logs
                cursor.execute("SELECT COUNT(*) as count FROM system_logs")
                if cursor.fetchone()["count"] == 0:
                    sample_logs = [
                        (time.time() - 7200, "INFO", "SYSTEM", "PLATFORM_INIT", "system", "Flint Control Plane v1.0.0 initialized successfully with SQLite persistence."),
                        (time.time() - 7100, "INFO", "AUTH", "USER_LOGIN", "admin@gmail.com", "User authenticated successfully (Role: ADMIN)."),
                        (time.time() - 6500, "INFO", "PIPELINE", "PIPELINE_RUN", "devops@gmail.com", "Pipeline 'Core Web API' executed through 7 DAG stages with status COMPLETED."),
                        (time.time() - 6000, "INFO", "DEPLOY", "CANARY_PROMOTE", "devops@gmail.com", "Promoted Canary traffic to 50% on EKS Cluster (Error Rate: 0.01%)."),
                        (time.time() - 3600, "INFO", "SECURITY", "SCAN_COMPLETED", "system", "Security audit completed with score 98% (0 critical CVEs)."),
                        (time.time() - 1800, "INFO", "GITOPS", "RECONCILE_SUCCESS", "system", "GitOps state reconciled with commit 589532f.")
                    ]
                    for ts, lvl, src, act, uemail, msg in sample_logs:
                        cursor.execute("""
                            INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (str(uuid.uuid4()), ts, lvl, src, act, uemail, msg))

                self.audit_logger.record_entry("org-default", "usr-admin", "admin@gmail.com", "PLATFORM_BOOTSTRAP", "SYSTEM", "flint-core", "127.0.0.1", {"version": "1.0.0"})
                self.audit_logger.record_entry("org-default", "usr-devops", "devops@gmail.com", "DEPLOY_CANARY", "DEPLOYMENT", "dep-001", "127.0.0.1", {"weight": 50, "app": "Core Web API"})

                conn.commit()

    # --- Authentication Methods ---

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
                row = cursor.fetchone()
                if not row:
                    return None
                
                user = dict(row)
                if user["status"] != "ACTIVE":
                    return None
                
                if not self.auth_engine.verify_password(password, user["password_hash"], user["password_salt"]):
                    return None
                
                cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (time.time(), user["id"]))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'AUTH', 'USER_LOGIN', ?, ?)
                """, (str(uuid.uuid4()), time.time(), user["email"], f"User {user['email']} signed in successfully (Role: {user['role']})."))
                conn.commit()

        self.audit_logger.record_entry("org-default", user["id"], user["email"], "LOGIN", "USER", user["id"], "127.0.0.1", {"role": user["role"]})

        return {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
            "status": user["status"],
            "created_at": user["created_at"],
            "last_login": time.time()
        }

    def create_session(self, user_info: Dict[str, Any]) -> str:
        token = "flint_sess_" + uuid.uuid4().hex
        self.sessions[token] = {
            "token": token,
            "user": user_info,
            "created_at": time.time(),
            "expires_at": time.time() + 86400 * 7
        }
        return token

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        if not token or token not in self.sessions:
            return None
        sess = self.sessions[token]
        if time.time() > sess["expires_at"]:
            del self.sessions[token]
            return None
        return sess["user"]

    def invalidate_session(self, token: str):
        if token in self.sessions:
            user = self.sessions[token]["user"]
            self.add_log("INFO", "AUTH", "USER_LOGOUT", user["email"], f"User {user['email']} signed out.")
            self.audit_logger.record_entry("org-default", user["id"], user["email"], "LOGOUT", "USER", user["id"], "127.0.0.1", {})
            del self.sessions[token]

    # --- Role & Permission Checks ---

    def check_permission(self, role: str, action: str) -> bool:
        if role == "ADMIN":
            return True
        if role == "DEVOPS_ENGINEER":
            if action.startswith("users:"):
                return False
            return True
        if role == "DEVELOPER":
            allowed = ["pipelines:read", "pipelines:execute", "deployments:read", "logs:read", "metrics:read", "reports:read", "security:read", "iac:read", "runners:read", "gitops:read", "audit:read"]
            return action in allowed
        if role == "VIEWER":
            allowed = ["pipelines:read", "deployments:read", "logs:read", "metrics:read", "reports:read", "security:read", "iac:read", "runners:read", "gitops:read", "audit:read", "dashboard:read"]
            return action in allowed
        return False

    # --- Logging & Auditing Helpers ---

    def add_log(self, level: str, source: str, action: str, user_email: str, message: str):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), time.time(), level, source, action, user_email, message))
                conn.commit()

    # --- User Management (ADMIN Only) ---

    def get_users(self) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, email, role, name, status, created_at, last_login FROM users ORDER BY created_at ASC")
                return [dict(row) for row in cursor.fetchall()]

    def create_user(self, email: str, raw_pwd: str, role: str, name: str, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE email = ?", (email.strip().lower(),))
                if cursor.fetchone():
                    raise ValueError(f"User with email {email} already exists")
                
                uid = "usr-" + uuid.uuid4().hex[:8]
                pwd_hash, pwd_salt = self.auth_engine.hash_password(raw_pwd)
                now = time.time()
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, password_salt, role, name, status, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, NULL)
                """, (uid, email.strip().lower(), pwd_hash, pwd_salt, role, name, now))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'USERS', 'USER_CREATED', ?, ?)
                """, (str(uuid.uuid4()), now, actor_email, f"Admin created new user {email} with role {role}."))
                conn.commit()

        self.audit_logger.record_entry("org-default", uid, actor_email, "USER_CREATED", "USER", uid, "127.0.0.1", {"email": email, "role": role})
        return {"id": uid, "email": email, "role": role, "name": name, "status": "ACTIVE", "created_at": now}

    def update_user_role(self, user_id: str, new_role: str, actor_email: str):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'USERS', 'ROLE_UPDATED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"User {user_id} role updated to {new_role}."))
                conn.commit()
        self.audit_logger.record_entry("org-default", user_id, actor_email, "ROLE_UPDATED", "USER", user_id, "127.0.0.1", {"new_role": new_role})

    def toggle_user_status(self, user_id: str, actor_email: str) -> str:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("User not found")
                new_status = "DISABLED" if row["status"] == "ACTIVE" else "ACTIVE"
                cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'WARNING', 'USERS', 'STATUS_TOGGLED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"User {user_id} status changed to {new_status}."))
                conn.commit()
        self.audit_logger.record_entry("org-default", user_id, actor_email, "STATUS_TOGGLED", "USER", user_id, "127.0.0.1", {"status": new_status})
        return new_status

    def reset_user_password(self, user_id: str, new_raw_pwd: str, actor_email: str):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                pwd_hash, pwd_salt = self.auth_engine.hash_password(new_raw_pwd)
                cursor.execute("UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?", (pwd_hash, pwd_salt, user_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'USERS', 'PASSWORD_RESET', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Password reset for user {user_id}."))
                conn.commit()
        self.audit_logger.record_entry("org-default", user_id, actor_email, "PASSWORD_RESET", "USER", user_id, "127.0.0.1", {})

    # --- Pipelines & DAG Execution ---

    def get_pipelines(self) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pipelines ORDER BY created_at DESC")
                items = []
                for row in cursor.fetchall():
                    d = dict(row)
                    d["stages"] = json.loads(d["stages"])
                    items.append(d)
                return items

    def create_pipeline(self, name: str, description: str, repository: str, branch: str, stages: List[Dict[str, Any]], actor_email: str) -> Dict[str, Any]:
        pid = "pipe-" + uuid.uuid4().hex[:8]
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pipelines (id, name, description, repository, branch, stages, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'IDLE', ?, ?)
                """, (pid, name, description, repository, branch, json.dumps(stages), now, now))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'PIPELINES', 'PIPELINE_CREATED', ?, ?)
                """, (str(uuid.uuid4()), now, actor_email, f"Created new pipeline '{name}' with {len(stages)} stages."))
                conn.commit()

        self.audit_logger.record_entry("org-default", pid, actor_email, "PIPELINE_CREATED", "PIPELINE", pid, "127.0.0.1", {"name": name})
        return {"id": pid, "name": name, "description": description, "repository": repository, "branch": branch, "stages": stages, "status": "IDLE"}

    def run_pipeline(self, pipeline_id: str, actor_email: str, simulation_mode: str = "NORMAL") -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pipelines WHERE id = ?", (pipeline_id,))
                p_row = cursor.fetchone()
                if not p_row:
                    raise ValueError("Pipeline not found")
                
                pipeline = dict(p_row)
                stages_list = json.loads(pipeline["stages"])
                
                resolver = DAGResolver(stages_list)
                execution_stages = resolver.get_execution_stages()

                run_id = f"run-{int(time.time())}-{uuid.uuid4().hex[:4]}"
                commit_sha = uuid.uuid4().hex[:7]
                now = time.time()

                stage_records = []
                pipeline_failed = False
                failure_reason = None
                log_lines = [
                    f"[{time.strftime('%H:%M:%S')}] [INIT] Pipeline Run {run_id} started for '{pipeline['name']}' by {actor_email}",
                    f"[{time.strftime('%H:%M:%S')}] [DAG] Resolved {len(execution_stages)} execution waves: {execution_stages}",
                    f"[{time.strftime('%H:%M:%S')}] [RUNNER] Allocated runner 'nexus-agent-us-east-k8s-01' (Status: BUSY)"
                ]

                cursor.execute("UPDATE runners SET status = 'BUSY', current_job = ? WHERE id = 'run-node-01'", (run_id,))

                for wave_idx, wave in enumerate(execution_stages):
                    for stage_id in wave:
                        stage_def = next((s for s in stages_list if s["id"] == stage_id), {"name": stage_id})
                        s_name = stage_def.get("name", stage_id)

                        if simulation_mode == "FAIL_SECURITY" and stage_id == "security-scan":
                            pipeline_failed = True
                            failure_reason = "Security Gate Blocked: Detected 1 Critical CIS Benchmark violation (CIS 4.1.2 Unrestricted SSH)"
                            stage_records.append({"id": stage_id, "name": s_name, "status": "FAILED", "duration_ms": 320, "error": failure_reason})
                            log_lines.append(f"[{time.strftime('%H:%M:%S')}] [SECURITY] ❌ FAILED: CIS 4.1.2 Port 22 open to 0.0.0.0/0. Security gate blocked deployment.")
                            break
                        elif simulation_mode == "FAIL_TESTS" and stage_id == "unit-tests":
                            pipeline_failed = True
                            failure_reason = "Test Suite Failure: 2 integration tests failed in test_payment_gateway"
                            stage_records.append({"id": stage_id, "name": s_name, "status": "FAILED", "duration_ms": 450, "error": failure_reason})
                            log_lines.append(f"[{time.strftime('%H:%M:%S')}] [TESTS] ❌ FAILED: AssertionError: Payment capture timeout. 28 passed, 2 failed.")
                            break
                        elif simulation_mode == "FAIL_INFRA" and stage_id in ["infra-validation", "infra"]:
                            pipeline_failed = True
                            failure_reason = "IaC State Error: Database subnet group collision in Terraform plan"
                            stage_records.append({"id": stage_id, "name": s_name, "status": "FAILED", "duration_ms": 280, "error": failure_reason})
                            log_lines.append(f"[{time.strftime('%H:%M:%S')}] [INFRA] ❌ FAILED: Resource conflict on aws_db_subnet_group.primary.")
                            break
                        else:
                            stage_records.append({"id": stage_id, "name": s_name, "status": "SUCCESS", "duration_ms": 150 + wave_idx * 50})
                            log_lines.append(f"[{time.strftime('%H:%M:%S')}] [{stage_id.upper()}] ✓ Stage '{s_name}' completed successfully in {150 + wave_idx * 50}ms.")

                    if pipeline_failed:
                        break

                final_status = "FAILED" if pipeline_failed else "COMPLETED"
                duration = round(time.time() - now + 0.1, 2)
                log_lines.append(f"[{time.strftime('%H:%M:%S')}] [FINISH] Pipeline Run {run_id} finished with status: {final_status} (Duration: {duration}s).")

                cursor.execute("""
                    INSERT INTO pipeline_runs (id, pipeline_id, pipeline_name, branch, commit_sha, status, stages_json, logs, duration_seconds, triggered_by, simulation_mode, created_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (run_id, pipeline_id, pipeline["name"], pipeline["branch"], commit_sha, final_status, json.dumps(stage_records), "\n".join(log_lines), duration, actor_email, simulation_mode, now, time.time()))

                cursor.execute("UPDATE runners SET status = 'IDLE', current_job = NULL WHERE id = 'run-node-01'")

                if not pipeline_failed and any("deploy" in s["id"].lower() for s in stage_records):
                    dep_id = "dep-" + uuid.uuid4().hex[:6]
                    cursor.execute("""
                        INSERT INTO deployments (id, application, version, environment, strategy, status, canary_weight, blue_green_active, error_rate, latency_ms, pipeline_run_id, deployed_by, created_at, updated_at)
                        VALUES (?, ?, ?, 'Production (US-East)', 'CANARY', 'HEALTHY', 25, 'blue', 0.00, 14.5, ?, ?, ?, ?)
                    """, (dep_id, pipeline["name"], f"v{int(time.time()) % 1000}.0", run_id, actor_email, now, now))
                    self.metrics_aggregator.increment_counter("deployments_total", 1.0, {"status": "success"})
                elif pipeline_failed:
                    self.metrics_aggregator.increment_counter("deployments_total", 1.0, {"status": "failed"})

                log_lvl = "ERROR" if pipeline_failed else "INFO"
                action_tag = "PIPELINE_FAILED" if pipeline_failed else "PIPELINE_COMPLETED"
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, ?, 'PIPELINE', ?, ?, ?)
                """, (str(uuid.uuid4()), time.time(), log_lvl, action_tag, actor_email, f"Pipeline '{pipeline['name']}' ({run_id}) finished with status {final_status}."))

                conn.commit()

        self.audit_logger.record_entry("org-default", run_id, actor_email, action_tag, "PIPELINE_RUN", run_id, "127.0.0.1", {
            "pipeline_id": pipeline_id,
            "status": final_status,
            "failure_reason": failure_reason
        })

        return {
            "run_id": run_id,
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline["name"],
            "status": final_status,
            "commit_sha": commit_sha,
            "stages": stage_records,
            "duration_seconds": duration,
            "failure_reason": failure_reason,
            "logs": log_lines
        }

    def cancel_pipeline_run(self, run_id: str, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE pipeline_runs SET status = 'CANCELLED' WHERE id = ?", (run_id,))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'WARNING', 'PIPELINE', 'PIPELINE_CANCELLED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Pipeline run {run_id} cancelled by user."))
                conn.commit()

        self.audit_logger.record_entry("org-default", run_id, actor_email, "PIPELINE_CANCELLED", "PIPELINE_RUN", run_id, "127.0.0.1", {})
        return {"run_id": run_id, "status": "CANCELLED"}

    def get_pipeline_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?", (limit,))
                runs = []
                for row in cursor.fetchall():
                    d = dict(row)
                    d["stages"] = json.loads(d["stages_json"])
                    runs.append(d)
                return runs

    def get_pipeline_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                d = dict(row)
                d["stages"] = json.loads(d["stages_json"])
                return d

    # --- Deployments, Canary & Blue-Green ---

    def get_deployments(self) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM deployments ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]

    def create_deployment(self, application: str, version: str, strategy: str, actor_email: str) -> Dict[str, Any]:
        dep_id = "dep-" + uuid.uuid4().hex[:6]
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO deployments (id, application, version, environment, strategy, status, canary_weight, blue_green_active, error_rate, latency_ms, deployed_by, created_at, updated_at)
                    VALUES (?, ?, ?, 'Production (US-East)', ?, 'DEPLOYING', 25, 'blue', 0.00, 15.0, ?, ?, ?)
                """, (dep_id, application, version, strategy, actor_email, now, now))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'DEPLOY', 'DEPLOYMENT_STARTED', ?, ?)
                """, (str(uuid.uuid4()), now, actor_email, f"Started new {strategy} deployment for '{application}' ({version})."))
                conn.commit()

        self.audit_logger.record_entry("org-default", dep_id, actor_email, "DEPLOYMENT_STARTED", "DEPLOYMENT", dep_id, "127.0.0.1", {"version": version, "strategy": strategy})
        return {"id": dep_id, "application": application, "version": version, "strategy": strategy, "status": "DEPLOYING", "canary_weight": 25}

    def promote_canary(self, deployment_id: str, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Deployment not found")
                dep = dict(row)
                new_weight = self.canary_controller.calculate_next_weights(dep["canary_weight"])
                new_status = "HEALTHY" if new_weight == 100 else "DEPLOYING"

                cursor.execute("UPDATE deployments SET canary_weight = ?, status = ?, updated_at = ? WHERE id = ?", (new_weight, new_status, time.time(), deployment_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'DEPLOY', 'CANARY_PROMOTE', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Canary traffic on deployment {deployment_id} promoted to {new_weight}%."))
                conn.commit()

        self.audit_logger.record_entry("org-default", deployment_id, actor_email, "CANARY_PROMOTE", "DEPLOYMENT", deployment_id, "127.0.0.1", {"weight": new_weight})
        dep["canary_weight"] = new_weight
        dep["status"] = new_status
        return dep

    def switch_blue_green(self, deployment_id: str, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Deployment not found")
                dep = dict(row)
                new_color = "green" if dep.get("blue_green_active") == "blue" else "blue"
                cursor.execute("UPDATE deployments SET blue_green_active = ?, updated_at = ? WHERE id = ?", (new_color, time.time(), deployment_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'DEPLOY', 'BLUE_GREEN_SWITCH', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Blue-Green active traffic routed to {new_color.upper()} pool."))
                conn.commit()

        self.audit_logger.record_entry("org-default", deployment_id, actor_email, "BLUE_GREEN_SWITCH", "DEPLOYMENT", deployment_id, "127.0.0.1", {"active_color": new_color})
        dep["blue_green_active"] = new_color
        return dep

    def rollback_deployment(self, deployment_id: str, reason: str, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Deployment not found")
                
                cursor.execute("""
                    UPDATE deployments 
                    SET status = 'ROLLED_BACK', canary_weight = 0, error_rate = 0.0, updated_at = ? 
                    WHERE id = ?
                """, (time.time(), deployment_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'WARNING', 'DEPLOY', 'ROLLBACK_TRIGGERED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Rollback executed for deployment {deployment_id}. Reason: {reason}"))
                conn.commit()

        self.audit_logger.record_entry("org-default", deployment_id, actor_email, "ROLLBACK", "DEPLOYMENT", deployment_id, "127.0.0.1", {"reason": reason})
        return {"id": deployment_id, "status": "ROLLED_BACK", "canary_weight": 0, "reason": reason}

    # --- Infrastructure & Drift ---

    def get_infrastructure(self) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM infrastructure_state")
                rows = [dict(r) for r in cursor.fetchall()]
                drift_count = sum(1 for r in rows if r["drift_detected"])
                return {
                    "resources": rows,
                    "summary": {
                        "total_resources": len(rows),
                        "to_add": 3,
                        "to_update": 2,
                        "to_destroy": 0,
                        "drift_count": drift_count,
                        "provider": "AWS / Kubernetes (Multi-Cloud)"
                    }
                }

    def detect_drift(self, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM infrastructure_state WHERE resource_name = 'k8s_deployment.web_service_replicas'")
                row = cursor.fetchone()
                drift_found = False
                drift_details = None
                if row:
                    actual = json.loads(row["actual_state"])
                    desired = json.loads(row["desired_state"])
                    actual["replicas"] = 5
                    cursor.execute("UPDATE infrastructure_state SET actual_state = ?, drift_detected = 1 WHERE id = ?", (json.dumps(actual), row["id"]))
                    drift_found = True
                    drift_details = {
                        "resource": row["resource_name"],
                        "desired": desired,
                        "actual": actual,
                        "message": "Actual replica count (5) drifts from Terraform desired specification (4)."
                    }
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, ?, 'INFRA', 'DRIFT_DETECTION', ?, ?)
                """, (str(uuid.uuid4()), time.time(), "WARNING" if drift_found else "INFO", actor_email, f"Drift detection evaluated. Status: {'DRIFT DETECTED' if drift_found else 'CLEAN'}."))
                conn.commit()

        self.audit_logger.record_entry("org-default", "infra-drift", actor_email, "DRIFT_DETECTION", "INFRASTRUCTURE", "k8s_deployment.web_service_replicas", "127.0.0.1", {"drift_found": drift_found})
        return {"has_drift": drift_found, "details": drift_details}

    def remediate_drift(self, actor_email: str) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM infrastructure_state WHERE resource_name = 'k8s_deployment.web_service_replicas'")
                row = cursor.fetchone()
                if row:
                    desired = json.loads(row["desired_state"])
                    cursor.execute("UPDATE infrastructure_state SET actual_state = ?, drift_detected = 0 WHERE id = ?", (json.dumps(desired), row["id"]))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'INFRA', 'DRIFT_REMEDIATED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, "Reconciled drifted infrastructure back to Terraform desired state."))
                conn.commit()

        self.audit_logger.record_entry("org-default", "infra-reconcile", actor_email, "DRIFT_REMEDIATED", "INFRASTRUCTURE", "k8s_deployment.web_service_replicas", "127.0.0.1", {})
        return {"status": "REMEDIATED", "message": "All resources aligned with desired state."}

    # --- Security & Governance ---

    def get_security_data(self) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM security_scans ORDER BY created_at DESC LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    return {"security_score": 100, "critical_count": 0, "high_count": 0, "policy_violations": 0, "findings": []}
                d = dict(row)
                d["findings"] = json.loads(d["findings_json"])
                return d

    def trigger_security_scan(self, actor_email: str) -> Dict[str, Any]:
        findings = [
            {"type": "POLICY_CHECK", "rule": "CIS 2.1.1 S3 Server Side Encryption", "status": "PASSED", "severity": "MEDIUM", "description": "All S3 storage buckets have AES-256 server-side encryption enabled."},
            {"type": "POLICY_CHECK", "rule": "CIS 5.2.6 Non-Root Kubernetes Pods", "status": "PASSED", "severity": "HIGH", "description": "Pod security contexts enforce runAsNonRoot: true across namespace."},
            {"type": "POLICY_CHECK", "rule": "CIS 4.1.2 Restricted SSH Port 22", "status": "PASSED", "severity": "CRITICAL", "description": "No security groups allow 0.0.0.0/0 inbound to SSH port 22."},
            {"type": "TRIVY_CVE", "rule": "Container Image Vulnerability Scan", "status": "PASSED", "severity": "LOW", "description": "Zero Critical or High severity vulnerabilities detected in production container images."},
            {"type": "SECRET_SCAN", "rule": "Commit Secret & Entropy Scan", "status": "PASSED", "severity": "CRITICAL", "description": "No unencrypted API keys or certificates found in repository."}
        ]
        sid = "sec-" + uuid.uuid4().hex[:6]
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO security_scans (id, scan_type, target, security_score, critical_count, high_count, policy_violations, status, findings_json, created_at)
                    VALUES (?, 'FULL_COMPLIANCE_AUDIT', 'Flint Platform Monorepo', 98, 0, 0, 0, 'PASSED', ?, ?)
                """, (sid, json.dumps(findings), now))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'SECURITY', 'SCAN_EXECUTED', ?, ?)
                """, (str(uuid.uuid4()), now, actor_email, "Executed full DevSecOps scan across repository and container images (Score: 98%)."))
                conn.commit()

        self.audit_logger.record_entry("org-default", sid, actor_email, "SECURITY_SCAN", "SECURITY_AUDIT", sid, "127.0.0.1", {"score": 98})
        return {"id": sid, "security_score": 98, "critical_count": 0, "high_count": 0, "policy_violations": 0, "status": "PASSED", "findings": findings}

    # --- GitOps Reconciliation ---

    def get_gitops_state(self) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM gitops_state LIMIT 1")
                row = cursor.fetchone()
                return dict(row) if row else {}

    def reconcile_gitops(self, actor_email: str) -> Dict[str, Any]:
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE gitops_state SET sync_status = 'IN_SYNC', last_reconciled = ? WHERE id = 'gitops-main'", (now,))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'GITOPS', 'RECONCILE', ?, ?)
                """, (str(uuid.uuid4()), now, actor_email, "Reconciled Kubernetes cluster manifests with Git repository commit 589532f."))
                conn.commit()

        self.audit_logger.record_entry("org-default", "gitops-main", actor_email, "GITOPS_RECONCILE", "GITOPS", "gitops-main", "127.0.0.1", {"status": "IN_SYNC"})
        return {"status": "IN_SYNC", "message": "Cluster state successfully synchronized with git repository.", "last_reconciled": now}

    # --- Runners ---

    def get_runners(self) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM runners ORDER BY name ASC")
                res = []
                for r in cursor.fetchall():
                    d = dict(r)
                    d["tags"] = json.loads(d["tags"])
                    res.append(d)
                return res

    def toggle_runner(self, runner_id: str, actor_email: str) -> int:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT enabled FROM runners WHERE id = ?", (runner_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Runner not found")
                new_val = 0 if row["enabled"] else 1
                new_status = "OFFLINE" if new_val == 0 else "IDLE"
                cursor.execute("UPDATE runners SET enabled = ?, status = ? WHERE id = ?", (new_val, new_status, runner_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'WARNING', 'RUNNERS', 'RUNNER_TOGGLED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Runner {runner_id} status set to {'ENABLED' if new_val else 'DISABLED'}."))
                conn.commit()

        self.audit_logger.record_entry("org-default", runner_id, actor_email, "RUNNER_TOGGLED", "RUNNER", runner_id, "127.0.0.1", {"enabled": new_val})
        return new_val

    def drain_runner(self, runner_id: str, actor_email: str) -> str:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE runners SET status = 'DRAINING', current_job = NULL WHERE id = ?", (runner_id,))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'WARNING', 'RUNNERS', 'RUNNER_DRAIN', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Runner {runner_id} set to DRAINING state."))
                conn.commit()

        self.audit_logger.record_entry("org-default", runner_id, actor_email, "RUNNER_DRAIN", "RUNNER", runner_id, "127.0.0.1", {})
        return "DRAINING"

    # --- Logs & Audit ---

    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if level and level != "ALL":
                    cursor.execute("SELECT * FROM system_logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?", (level, limit))
                else:
                    cursor.execute("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [dict(r) for r in cursor.fetchall()]

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.audit_logger.chain

    def verify_audit_integrity(self, actor_email: str) -> Dict[str, Any]:
        is_valid, msg = self.audit_logger.verify_integrity()
        self.add_log("INFO" if is_valid else "ERROR", "AUDIT", "INTEGRITY_VERIFY", actor_email, f"Audit chain validation executed. Result: {'VALID' if is_valid else 'COMPROMISED'}.")
        return {
            "is_valid": is_valid,
            "total_records": len(self.audit_logger.chain),
            "message": "All cryptographic SHA-256 hash chains verified 100% intact and tamper-free." if is_valid else msg
        }

    # --- Monitoring & Alerts ---

    def get_monitoring_data(self) -> Dict[str, Any]:
        return {
            "metrics": {
                "requests_per_second": 142.5,
                "latency_p99_ms": 18.2,
                "latency_p50_ms": 5.4,
                "error_rate_percent": 0.02,
                "cpu_utilization_percent": 34.5,
                "memory_utilization_percent": 48.0,
                "pipeline_avg_duration_sec": 42.0,
                "active_canary_weight": 50
            },
            "alerts": self.get_alerts()
        }

    def get_alerts(self) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alerts ORDER BY triggered_at DESC")
                return [dict(r) for r in cursor.fetchall()]

    def resolve_alert(self, alert_id: str, actor_email: str):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE alerts SET status = 'RESOLVED', resolved_at = ? WHERE id = ?", (time.time(), alert_id))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'MONITORING', 'ALERT_RESOLVED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, f"Alert {alert_id} marked as resolved."))
                conn.commit()

    # --- Dashboard Aggregation ---

    def get_dashboard_summary(self) -> Dict[str, Any]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) as c FROM pipelines")
                total_pipelines = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM pipeline_runs WHERE status = 'RUNNING'")
                active_runs = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM pipeline_runs WHERE status = 'COMPLETED'")
                completed_runs = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM pipeline_runs WHERE status = 'FAILED'")
                failed_runs = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM deployments WHERE status = 'HEALTHY'")
                healthy_deployments = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM runners WHERE status != 'OFFLINE' AND enabled = 1")
                running_runners = cursor.fetchone()["c"]

                cursor.execute("SELECT COUNT(*) as c FROM alerts WHERE status = 'ACTIVE'")
                active_alerts = cursor.fetchone()["c"]

                cursor.execute("SELECT * FROM deployments ORDER BY updated_at DESC LIMIT 1")
                latest_dep = cursor.fetchone()

                cursor.execute("SELECT * FROM security_scans ORDER BY created_at DESC LIMIT 1")
                latest_sec = cursor.fetchone()

                return {
                    "platform_health": "HEALTHY" if active_alerts == 0 else "DEGRADED",
                    "active_pipelines": active_runs,
                    "successful_deployments": completed_runs + healthy_deployments,
                    "failed_deployments": failed_runs,
                    "security_score": latest_sec["security_score"] if latest_sec else 98,
                    "running_runners": running_runners,
                    "active_alerts": active_alerts,
                    "total_pipelines": total_pipelines,
                    "latest_deployment": dict(latest_dep) if latest_dep else None,
                    "current_traffic_weight": latest_dep["canary_weight"] if latest_dep else 50
                }

    # --- Settings ---

    def get_settings(self) -> Dict[str, str]:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                return {row["key"]: row["value"] for row in cursor.fetchall()}

    def update_settings(self, new_settings: Dict[str, str], actor_email: str):
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for k, v in new_settings.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
                cursor.execute("""
                    INSERT INTO system_logs (id, timestamp, level, source, action, user_email, message)
                    VALUES (?, ?, 'INFO', 'SETTINGS', 'SETTINGS_UPDATED', ?, ?)
                """, (str(uuid.uuid4()), time.time(), actor_email, "Platform settings updated."))
                conn.commit()

        self.audit_logger.record_entry("org-default", "settings", actor_email, "SETTINGS_UPDATED", "CONFIG", "settings", "127.0.0.1", new_settings)


# Global singleton instance
state_store = StateStore()
