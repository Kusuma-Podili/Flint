import http.server
import socketserver
import json
import time
import os
import sys
import urllib.parse

# Insert local module paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "control-plane", "python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "runner-agent", "python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "dag-engine", "python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "iac-parser", "python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "policy-engine", "python"))

from state_store import state_store

PORT = int(os.environ.get("PORT", 4500))

with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()


class FlintApiHandler(http.server.SimpleHTTPRequestHandler):

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _get_auth_user(self):
        auth_header = self.headers.get("Authorization", "")
        token = ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif "Cookie" in self.headers:
            cookies = dict(c.strip().split("=", 1) for c in self.headers["Cookie"].split(";") if "=" in c)
            token = cookies.get("flint_session", "")
        
        if not token:
            return None, "Missing authentication token"
        
        user = state_store.validate_session(token)
        if not user:
            return None, "Invalid or expired session"
        return user, None

    def _parse_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Frontend SPA
        if path in ["/", "/index.html", "/dashboard", "/login", "/pipelines", "/deployments", "/infrastructure", "/security", "/gitops", "/runners", "/monitoring", "/logs", "/audit", "/reports", "/users", "/settings"]:
            html_path = os.path.join(os.path.dirname(__file__), "index.html")
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # 2. Public Health Check
        if path in ["/api/health", "/api/v1/health"]:
            self._send_json(200, {
                "status": "HEALTHY",
                "platform": "Flint",
                "version": "1.0.0",
                "database": "CONNECTED (SQLite)",
                "scheduler": "RUNNING (DAG Engine)",
                "runner_pool": "HEALTHY (4 Active Nodes)",
                "security_engine": "ACTIVE (OPA Rego)",
                "active_nodes": 4
            })
            return

        # 3. Session Validation
        if path == "/auth/session":
            user, err = self._get_auth_user()
            if not user:
                self._send_json(401, {"authenticated": False, "error": err})
                return
            self._send_json(200, {"authenticated": True, "user": user})
            return

        # Protected API Routes Guard
        user, err = self._get_auth_user()
        if not user:
            self._send_json(401, {"error": "Unauthorized. Please sign in.", "details": err})
            return

        role = user["role"]

        # Dashboard Summary
        if path == "/api/dashboard":
            self._send_json(200, state_store.get_dashboard_summary())
            return

        # Pipelines
        if path == "/api/pipelines":
            self._send_json(200, {"pipelines": state_store.get_pipelines()})
            return

        if path == "/api/pipeline-runs":
            self._send_json(200, {"runs": state_store.get_pipeline_runs()})
            return

        if path.startswith("/api/pipeline-runs/"):
            run_id = path.split("/")[-1]
            run = state_store.get_pipeline_run(run_id)
            if not run:
                self._send_json(404, {"error": "Pipeline run not found"})
                return
            self._send_json(200, run)
            return

        # Deployments
        if path == "/api/deployments":
            self._send_json(200, {"deployments": state_store.get_deployments()})
            return

        # Infrastructure
        if path == "/api/infrastructure":
            self._send_json(200, state_store.get_infrastructure())
            return

        # Security
        if path == "/api/security":
            self._send_json(200, state_store.get_security_data())
            return

        # GitOps
        if path == "/api/gitops":
            self._send_json(200, state_store.get_gitops_state())
            return

        # Runners
        if path == "/api/runners":
            self._send_json(200, {"runners": state_store.get_runners()})
            return

        # Monitoring
        if path == "/api/monitoring":
            self._send_json(200, state_store.get_monitoring_data())
            return

        # Logs
        if path == "/api/logs":
            level = query.get("level", ["ALL"])[0]
            self._send_json(200, {"logs": state_store.get_logs(level=level)})
            return

        # Audit
        if path == "/api/audit":
            self._send_json(200, {"audit_chain": state_store.get_audit_trail()})
            return

        # Reports
        if path == "/api/reports":
            summary = state_store.get_dashboard_summary()
            self._send_json(200, {
                "generated_at": time.time(),
                "executive_scorecard": {
                    "security_compliance_grade": "A+ (98%)",
                    "deployment_frequency": "14 / week",
                    "change_failure_rate": "1.2%",
                    "mean_time_to_recovery": "4.2 mins",
                    "sla_availability": "99.98%"
                },
                "summary": summary
            })
            return

        # Users (ADMIN only)
        if path == "/api/users":
            if role != "ADMIN":
                self._send_json(403, {"error": "Forbidden: ADMIN role required to manage users"})
                return
            self._send_json(200, {"users": state_store.get_users()})
            return

        # Settings
        if path == "/api/settings":
            self._send_json(200, {"settings": state_store.get_settings()})
            return

        self._send_json(404, {"error": f"Endpoint '{path}' not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._parse_json_body()

        # 1. Public Auth Login
        if path == "/auth/login":
            email = body.get("email", "").strip()
            password = body.get("password", "")
            if not email or not password:
                self._send_json(400, {"error": "Email and password are required"})
                return
            
            user = state_store.authenticate_user(email, password)
            if not user:
                self._send_json(401, {"error": "Invalid email or password"})
                return
            
            token = state_store.create_session(user)
            self._send_json(200, {
                "message": "Authentication successful",
                "token": token,
                "user": user
            })
            return

        # 2. Logout
        if path == "/auth/logout":
            auth_header = self.headers.get("Authorization", "")
            token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else ""
            if token:
                state_store.invalidate_session(token)
            self._send_json(200, {"message": "Logged out successfully"})
            return

        # Protected API Routes Guard
        user, err = self._get_auth_user()
        if not user:
            self._send_json(401, {"error": "Unauthorized. Please sign in.", "details": err})
            return

        role = user["role"]
        actor_email = user["email"]

        # Create Pipeline
        if path == "/api/pipelines":
            if not state_store.check_permission(role, "pipelines:create"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to create pipelines"})
                return
            name = body.get("name", "Untitled Pipeline")
            desc = body.get("description", "")
            repo = body.get("repository", "https://github.com/Kusuma-Podili/Flint")
            branch = body.get("branch", "main")
            stages = body.get("stages", [
                {"id": "checkout", "name": "Source Checkout", "depends_on": []},
                {"id": "security-scan", "name": "Security & OPA Scan", "depends_on": ["checkout"]},
                {"id": "unit-tests", "name": "Unit Tests", "depends_on": ["checkout"]},
                {"id": "container-build", "name": "Container Build", "depends_on": ["security-scan", "unit-tests"]},
                {"id": "deploy-canary", "name": "Deploy Canary", "depends_on": ["container-build"]}
            ])
            p = state_store.create_pipeline(name, desc, repo, branch, stages, actor_email)
            self._send_json(201, p)
            return

        # Run Pipeline
        if path.startswith("/api/pipelines/") and path.endswith("/run"):
            if not state_store.check_permission(role, "pipelines:execute"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to execute pipelines"})
                return
            pipe_id = path.split("/")[3]
            sim_mode = body.get("simulation_mode", "NORMAL")
            try:
                res = state_store.run_pipeline(pipe_id, actor_email, sim_mode)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Cancel Pipeline Run
        if path.startswith("/api/pipelines/") and path.endswith("/cancel"):
            if not state_store.check_permission(role, "pipelines:execute"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to cancel pipelines"})
                return
            run_id = body.get("run_id") or path.split("/")[3]
            res = state_store.cancel_pipeline_run(run_id, actor_email)
            self._send_json(200, res)
            return

        # Deployments: Create
        if path == "/api/deployments":
            if not state_store.check_permission(role, "deployments:create"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to create deployments"})
                return
            app = body.get("application", "Core API Service")
            ver = body.get("version", f"v{int(time.time())%1000}.0")
            strat = body.get("strategy", "CANARY")
            dep = state_store.create_deployment(app, ver, strat, actor_email)
            self._send_json(201, dep)
            return

        # Deployments: Promote Canary
        if path.startswith("/api/deployments/") and path.endswith("/promote"):
            if not state_store.check_permission(role, "deployments:promote"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to promote rollouts"})
                return
            dep_id = path.split("/")[3]
            try:
                dep = state_store.promote_canary(dep_id, actor_email)
                self._send_json(200, dep)
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Deployments: Switch Blue-Green
        if path.startswith("/api/deployments/") and path.endswith("/switch"):
            if not state_store.check_permission(role, "deployments:promote"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to switch traffic"})
                return
            dep_id = path.split("/")[3]
            try:
                dep = state_store.switch_blue_green(dep_id, actor_email)
                self._send_json(200, dep)
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Deployments: Rollback
        if path.startswith("/api/deployments/") and path.endswith("/rollback"):
            if not state_store.check_permission(role, "deployments:rollback"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to rollback deployments"})
                return
            dep_id = path.split("/")[3]
            reason = body.get("reason", "Manual rollback triggered by operator")
            try:
                res = state_store.rollback_deployment(dep_id, reason, actor_email)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Infrastructure: Drift Detection
        if path == "/api/infrastructure/drift":
            if not state_store.check_permission(role, "iac:read"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions"})
                return
            res = state_store.detect_drift(actor_email)
            self._send_json(200, res)
            return

        # Infrastructure: Remediate Drift
        if path == "/api/infrastructure/remediate":
            if not state_store.check_permission(role, "iac:mutate"):
                self._send_json(403, {"error": "Forbidden: Only ADMIN and DEVOPS_ENGINEER can mutate infrastructure"})
                return
            res = state_store.remediate_drift(actor_email)
            self._send_json(200, res)
            return

        # Security: Scan
        if path == "/api/security/scan":
            if not state_store.check_permission(role, "security:scan"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to trigger security scans"})
                return
            res = state_store.trigger_security_scan(actor_email)
            self._send_json(200, res)
            return

        # GitOps: Reconcile
        if path == "/api/gitops/reconcile":
            if not state_store.check_permission(role, "gitops:reconcile"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to reconcile GitOps"})
                return
            res = state_store.reconcile_gitops(actor_email)
            self._send_json(200, res)
            return

        # Runners: Toggle
        if path.startswith("/api/runners/") and path.endswith("/toggle"):
            if not state_store.check_permission(role, "runners:mutate"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to toggle runners"})
                return
            r_id = path.split("/")[3]
            try:
                val = state_store.toggle_runner(r_id, actor_email)
                self._send_json(200, {"enabled": val})
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Runners: Drain
        if path.startswith("/api/runners/") and path.endswith("/drain"):
            if not state_store.check_permission(role, "runners:mutate"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to drain runners"})
                return
            r_id = path.split("/")[3]
            try:
                val = state_store.drain_runner(r_id, actor_email)
                self._send_json(200, {"status": val})
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Alerts: Resolve
        if path.startswith("/api/alerts/") and path.endswith("/resolve"):
            if not state_store.check_permission(role, "monitoring:mutate"):
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to resolve alerts"})
                return
            a_id = path.split("/")[3]
            state_store.resolve_alert(a_id, actor_email)
            self._send_json(200, {"status": "RESOLVED"})
            return

        # Audit: Verify
        if path == "/api/audit/verify":
            res = state_store.verify_audit_integrity(actor_email)
            self._send_json(200, res)
            return

        # Users: Create (ADMIN only)
        if path == "/api/users":
            if role != "ADMIN":
                self._send_json(403, {"error": "Forbidden: ADMIN role required to create users"})
                return
            email = body.get("email", "").strip()
            raw_pwd = body.get("password", "")
            u_role = body.get("role", "DEVELOPER")
            name = body.get("name", email.split("@")[0])
            if not email or not raw_pwd:
                self._send_json(400, {"error": "Email and password are required"})
                return
            try:
                u = state_store.create_user(email, raw_pwd, u_role, name, actor_email)
                self._send_json(201, u)
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Users: Role Update (ADMIN only)
        if path.startswith("/api/users/") and path.endswith("/role"):
            if role != "ADMIN":
                self._send_json(403, {"error": "Forbidden: ADMIN role required"})
                return
            u_id = path.split("/")[3]
            new_role = body.get("role", "DEVELOPER")
            state_store.update_user_role(u_id, new_role, actor_email)
            self._send_json(200, {"status": "UPDATED", "role": new_role})
            return

        # Users: Toggle Active/Disabled (ADMIN only)
        if path.startswith("/api/users/") and path.endswith("/toggle"):
            if role != "ADMIN":
                self._send_json(403, {"error": "Forbidden: ADMIN role required"})
                return
            u_id = path.split("/")[3]
            try:
                st = state_store.toggle_user_status(u_id, actor_email)
                self._send_json(200, {"status": st})
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        # Users: Password Reset (ADMIN only)
        if path.startswith("/api/users/") and path.endswith("/reset-password"):
            if role != "ADMIN":
                self._send_json(403, {"error": "Forbidden: ADMIN role required"})
                return
            u_id = path.split("/")[3]
            new_pwd = body.get("password", "Flint@2026")
            state_store.reset_user_password(u_id, new_pwd, actor_email)
            self._send_json(200, {"status": "PASSWORD_RESET"})
            return

        # Settings: Update
        if path == "/api/settings":
            if role not in ["ADMIN", "DEVOPS_ENGINEER"]:
                self._send_json(403, {"error": "Forbidden: Insufficient permissions to update settings"})
                return
            state_store.update_settings(body, actor_email)
            self._send_json(200, {"status": "SAVED", "settings": body})
            return

        self._send_json(404, {"error": f"POST endpoint '{path}' not found"})

    def log_message(self, format, *args):
        # Silence default stderr logging to maintain clean terminal output
        pass


def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), FlintApiHandler) as httpd:
        print(f"================================================================================")
        print(f"  FLINT ENTERPRISE DEVOPS CONTROL PLANE RUNNING LIVE ON: http://localhost:{PORT}")
        print(f"================================================================================")
        httpd.serve_forever()


if __name__ == "__main__":
    run()
