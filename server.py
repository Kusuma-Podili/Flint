import http.server
import socketserver
import json
import time
import os
import sys

PORT = 8080

with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html", "/dashboard"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        elif self.path == "/api/v1/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {"status": "HEALTHY", "platform": "Flint", "version": "1.0.0", "active_nodes": 6}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif self.path == "/api/v1/pipelines/trigger":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {"run_id": f"run_{int(time.time())}", "status": "RUNNING", "stages": [["checkout"], ["sast", "unit"], ["docker"], ["deploy"]]}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Flint Platform Server running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
