#!/usr/bin/env python3
"""
Multi-Upstream API Router Proxy (Python stdlib, zero dependencies)

Auto-detects upstream based on API key prefix:
  lv-xxx    → LapakVIP
  mk-xxx    → MarketKU
  moyra-xxx → Moyra
  ytd-xxx   → YogaTheDev
  ks-xxx    → KaoruStore
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json
from pathlib import Path

# Multiple upstream routers
UPSTREAMS = {
    "lapakvip": "https://router.lapakvip.com",
    "moyra": "https://api.moyra.my.id",
    "marketku": "https://router.marketku.id",
    "yogathedev": "https://ai.yogathedev.com",
    "kaorustore": "https://router.kaorustore.web.id",
}

def detect_upstream_from_api_key(api_key):
    """Auto-detect upstream based on API key prefix"""
    if not api_key:
        return "lapakvip"
    
    key_lower = api_key.lower()
    
    if key_lower.startswith("lv-"):
        return "lapakvip"
    elif key_lower.startswith("sk-") or key_lower.startswith("moyra-"):
        return "moyra"
    elif key_lower.startswith("mk-"):
        return "marketku"
    elif key_lower.startswith("ytd-"):
        return "yogathedev"
    elif key_lower.startswith("ks-"):
        return "kaorustore"
    
    return "lapakvip"

class ProxyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/":
            self.serve_dashboard()
        elif self.path == "/health":
            self.send_json({"status": "healthy", "upstreams": list(UPSTREAMS.keys())})
        elif self.path == "/upstreams":
            upstreams_list = [{"name": k, "url": v} for k, v in UPSTREAMS.items()]
            self.send_json({"upstreams": upstreams_list})
        elif self.path.startswith("/api/"):
            self.proxy_request()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def serve_dashboard(self):
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        try:
            with open(frontend_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Dashboard not found")
    
    def send_json(self, data):
        content = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(content))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
    
    def proxy_request(self):
        # Get Authorization header
        auth_header = self.headers.get('Authorization', '')
        api_key = ""
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        
        # Detect upstream
        upstream_name = detect_upstream_from_api_key(api_key)
        base_url = UPSTREAMS[upstream_name]
        
        # Build target URL
        path = self.path[5:]  # Remove /api/
        target_url = f"{base_url}/v1/{path}"
        
        # Get request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Forward request
        try:
            req = urllib.request.Request(
                target_url,
                data=body,
                headers=dict(self.headers),
                method=self.command
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                # Send response
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                self.send_cors_headers()
                self.end_headers()
                
                # Stream response
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(e.read())
        
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            error_data = json.dumps({"error": str(e)}).encode('utf-8')
            self.wfile.write(error_data)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=8000):
    print("=" * 70)
    print("  🚀 Multi-Upstream API Router")
    print("=" * 70)
    print(f"  Dashboard: http://0.0.0.0:{port}")
    print(f"  API Base:  http://0.0.0.0:{port}/api/v1")
    print()
    print("  Supported Upstreams:")
    for name, url in UPSTREAMS.items():
        print(f"    - {name:12} → {url}")
    print()
    print("  Auto-detection based on API key prefix:")
    print("    lv-xxx    → LapakVIP")
    print("    mk-xxx    → MarketKU")
    print("    moyra-xxx → Moyra")
    print("    ytd-xxx   → YogaTheDev")
    print("    ks-xxx    → KaoruStore")
    print("=" * 70)
    print()
    
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    
    try:
        print(f"✅ Server running on port {port}...")
        print("   Press Ctrl+C to stop")
        print()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    run_server(8000)
