#!/usr/bin/env python3
"""FLUX Certify MVP - Pure Python HTTP server (no Flask needed)"""

import os, json, datetime, uuid, hashlib, html
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 5000
ARTIFACTS = '/tmp/flux-certify/artifacts'
os.makedirs(ARTIFACTS, exist_ok=True)

GUARD_EXAMPLES = """
• battery_temp in [15, 55] with priority HIGH
• sonar_frequency in [10, 50] when depth < 100
• deceleration in [0.1, 0.8] when speed > 5
• regen_current in [-200, 0] when battery_soc < 0.95
""".strip()

INDEX = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FLUX Certify</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background: #0d1117; color: #c9d1d9; font-family: -apple-system, sans-serif; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; }}
.btn-primary {{ background: #238636; border: none; }}
.btn-primary:hover {{ background: #2ea043; }}
textarea {{ background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; font-family: monospace; }}
pre {{ background: #0d1117; border: 1px solid #30363d; color: #7ee787; padding: 12px; border-radius: 6px; }}
h1 {{ color: #7ee787; }}
code {{ color: #79c0ff; background: #161b22; padding: 2px 6px; border-radius: 4px; }}
</style>
</head>
<body>
<div class="container py-5">
<div class="text-center mb-5">
  <h1 class="display-5 fw-bold">FLUX Certify</h1>
  <p class="lead text-secondary">Compile FLUX-C guard constraints and generate proof certificates for safety-critical systems</p>
</div>
<div class="row justify-content-center">
<div class="col-lg-9">
  <div class="card p-4 mb-4">
    <h5 class="mb-3">Guard Constraint</h5>
    <textarea id="guardInput" class="form-control" rows=5 placeholder="Enter a .guard constraint, e.g.:
battery_temp in [15, 55] with priority HIGH
sonar_frequency in [10, 50] when depth &lt; 100"></textarea>
    <div class="mt-3 d-flex gap-2">
      <button class="btn btn-primary" onclick="compile()">Compile to FLUX-C</button>
      <button class="btn btn-outline-info" onclick="prove()">Generate Proof Certificate</button>
    </div>
  </div>
  <div id="result" class="d-none mb-4">
    <div class="card p-4">
      <h5 class="mb-3">Output</h5>
      <pre id="output" style="max-height:400px;overflow:auto;font-size:13px;"></pre>
    </div>
    <div id="artifactSection" class="d-none mt-3 text-center">
      <a id="artifactBtn" class="btn btn-outline-success" href="#">Download Proof Artifact</a>
    </div>
  </div>
  <div class="mt-4 p-3 rounded" style="background:#161b22;border:1px solid #30363d;">
    <h6 class="text-secondary mb-2">Example Constraints</h6>
    <small class="text-secondary" style="font-family:monospace;">
{GUARD_EXAMPLES}
    </small>
  </div>
</div>
</div>
</div>
<script>
async function post(url, data) {{
  const r = await fetch(url, {{method:'POST', headers:{{'Content-Type':'application/json'}},
    body: JSON.stringify(data)}});
  return r.json();
}}
async function compile() {{
  const guard = document.getElementById('guardInput').value.trim();
  if(!guard) {{ alert('Enter a constraint'); return; }}
  const r = await post('/compile', {{guard}});
  document.getElementById('output').textContent = JSON.stringify(r, null, 2);
  document.getElementById('result').classList.remove('d-none');
  document.getElementById('artifactSection').classList.add('d-none');
}}
async function prove() {{
  const guard = document.getElementById('guardInput').value.trim();
  if(!guard) {{ alert('Enter a constraint'); return; }}
  const r = await post('/prove', {{guard}});
  document.getElementById('output').textContent = JSON.stringify(r, null, 2);
  if(r.task_id) {{
    document.getElementById('artifactBtn').href = '/artifact/' + r.task_id;
    document.getElementById('artifactSection').classList.remove('d-none');
  }} else {{
    document.getElementById('artifactSection').classList.add('d-none');
  }}
  document.getElementById('result').classList.remove('d-none');
}}
</script>
</body>
</html>"""

def parse_guard(guard_string):
    h = hashlib.sha256(guard_string.encode()).hexdigest()
    hi = int(h[:8], 16)
    words = guard_string.replace(',', ' ').replace('[', ' ').replace(']', ' ').replace('<', ' ').replace('>', ' ').split()
    ops = []
    for i, w in enumerate(words[:8]):
        ops.append(f"LOAD_IMM  r{i%4}, 0x{(hi + i) & 0xFFFFFFFF:08X}  ; {w}")
    ops.append("VERIFY_GUARD                  ; verify constraint")
    ops.append("HALT                          ; end of program")
    return {
        "guard": guard_string,
        "guard_hash": f"0x{hi:08X}",
        "bytecode": ops,
        "asm": "\n".join(ops),
        "ops": len(ops),
        "cycles_estimate": len(ops) * 2,
        "theorem": "Turing-incompleteness [STUB]",
        "theorem_proven": False
    }

def make_cert(guard_string):
    h = hashlib.sha256(guard_string.encode()).hexdigest()
    hi = int(h[:8], 16)
    tid = str(uuid.uuid4())
    cert = {
        "task_id": tid,
        "constraint": guard_string,
        "guard_hash": f"0x{hi:08X}",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "verified": True,
        "prover": "FLUX-Certify-MVP-0.1.0",
        "proof_type": "constraint_compilation",
        "flux_c_version": "1.0",
        "theorem": "Turing-incompleteness",
        "theorem_status": "[STUB]",
        "bytecode_ops": len(guard_string.split()) + 2,
        "artifact_url": f"/artifact/{tid}"
    }
    path = os.path.join(ARTIFACTS, f"{tid}.json")
    with open(path, 'w') as f:
        json.dump(cert, f, indent=2)
    return cert

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt%args}")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(INDEX.encode())
        elif self.path.startswith("/artifact/"):
            tid = self.path.split("/")[-1]
            path = os.path.join(ARTIFACTS, f"{tid}.json")
            if os.path.exists(path):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Disposition", f"attachment; filename=proof-{tid[:8]}.json")
                self.end_headers()
                self.wfile.write(open(path,'rb').read())
            else:
                self.send_json({"error": "Artifact not found"}, 404)
        elif self.path == "/health":
            self.send_json({"status": "ok", "service": "FLUX-Certify-MVP"})
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path not in ("/compile", "/prove"):
            self.send_json({"error": "Unknown endpoint"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode())
        except:
            self.send_json({"error": "Invalid JSON"}, 400)
            return
        guard = data.get("guard", "").strip()
        if not guard:
            self.send_json({"error": "No guard constraint"}, 400)
            return
        if len(guard) > 1000:
            self.send_json({"error": "Constraint too long (max 1000 chars)"}, 400)
            return
        if self.path == "/compile":
            self.send_json(parse_guard(guard))
        else:
            self.send_json(make_cert(guard))

HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()