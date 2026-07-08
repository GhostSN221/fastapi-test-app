import os
import platform
import socket
import time
from datetime import datetime

import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

START_TIME = time.time()

app = FastAPI(
    title="SystalinkCloud Test API",
    description="App de test FastAPI pour valider le déploiement sur la plateforme Datacloud.",
    version="1.0.0",
)

HIDDEN = {"TOKEN", "SECRET", "PASSWORD", "KEY", "PWD", "PASS"}


def safe_env():
    return {
        k: v
        for k, v in os.environ.items()
        if not any(h in k.upper() for h in HIDDEN)
    }


@app.get("/health", tags=["Platform"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "uptime": int(time.time() - START_TIME)}


@app.get("/ping", tags=["Platform"])
def ping():
    """Simple ping/pong."""
    return {"pong": True, "ts": datetime.utcnow().isoformat()}


@app.get("/info", tags=["Platform"])
def info(request: Request):
    """Container and runtime information."""
    mem = psutil.virtual_memory()
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "memory": {
            "total_mb": round(mem.total / 1024 / 1024),
            "used_mb": round(mem.used / 1024 / 1024),
            "percent": mem.percent,
        },
        "cpu_count": psutil.cpu_count(),
        "uptime_s": int(time.time() - START_TIME),
        "env": safe_env(),
        "headers": dict(request.headers),
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    mem = psutil.virtual_memory()
    uptime = int(time.time() - START_TIME)
    hostname = socket.gethostname()
    env = safe_env()
    env_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in list(env.items())[:20]
    )
    mem_pct = mem.percent

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>SystalinkCloud — FastAPI Test App</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}}
    header{{background:linear-gradient(135deg,#312e81,#0f172a);padding:2rem;border-bottom:1px solid #4338ca}}
    header h1{{font-size:1.6rem;font-weight:700;color:#a5b4fc}}
    header p{{color:#94a3b8;margin-top:.25rem;font-size:.9rem}}
    .badge{{display:inline-block;background:#16a34a;color:#fff;font-size:.75rem;padding:2px 10px;border-radius:9999px;margin-left:.75rem;vertical-align:middle}}
    main{{max-width:900px;margin:2rem auto;padding:0 1rem;display:grid;grid-template-columns:1fr 1fr;gap:1.25rem}}
    .card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.25rem}}
    .card h2{{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:#64748b;margin-bottom:1rem}}
    .stat{{display:flex;justify-content:space-between;padding:.5rem 0;border-bottom:1px solid #1e3a5f}}
    .stat:last-child{{border-bottom:none}}
    .stat .label{{color:#94a3b8;font-size:.88rem}}
    .stat .value{{color:#f1f5f9;font-size:.88rem;font-family:monospace}}
    .progress-bar{{background:#1e3a5f;border-radius:4px;height:6px;margin-top:4px}}
    .progress-fill{{background:#818cf8;border-radius:4px;height:6px}}
    .full-width{{grid-column:1/-1}}
    .endpoints{{display:flex;gap:.5rem;flex-wrap:wrap}}
    .ep{{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:.35rem .75rem;font-family:monospace;font-size:.8rem;color:#a5b4fc}}
    .docs-link{{display:inline-block;margin-top:.75rem;background:#4338ca;color:#fff;padding:.5rem 1.25rem;border-radius:8px;text-decoration:none;font-size:.88rem}}
    table{{width:100%;border-collapse:collapse;font-size:.8rem}}
    th{{text-align:left;color:#64748b;padding:.4rem .5rem;border-bottom:1px solid #1e3a5f}}
    td{{padding:.4rem .5rem;border-bottom:1px solid #1e293b;font-family:monospace;word-break:break-all}}
    td:first-child{{color:#a5b4fc;white-space:nowrap}}
    .lang-tag{{background:#312e81;color:#a5b4fc;border-radius:4px;padding:2px 8px;font-size:.75rem;font-family:monospace}}
    footer{{text-align:center;padding:2rem;color:#475569;font-size:.8rem}}
  </style>
</head>
<body>
<header>
  <h1>FastAPI Test App <span class="badge">RUNNING</span></h1>
  <p><span class="lang-tag">Python {platform.python_version()}</span> · FastAPI · Container {hostname}</p>
</header>
<main>
  <div class="card">
    <h2>Runtime</h2>
    <div class="stat"><span class="label">Hostname</span><span class="value">{hostname}</span></div>
    <div class="stat"><span class="label">Platform</span><span class="value">{platform.system()}/{platform.machine()}</span></div>
    <div class="stat"><span class="label">Python</span><span class="value">{platform.python_version()}</span></div>
    <div class="stat"><span class="label">CPU cores</span><span class="value">{psutil.cpu_count()}</span></div>
    <div class="stat"><span class="label">Uptime</span><span class="value">{uptime}s</span></div>
  </div>
  <div class="card">
    <h2>Memory</h2>
    <div class="stat"><span class="label">Used</span><span class="value">{round(mem.used/1024/1024)} MB</span></div>
    <div class="stat"><span class="label">Total</span><span class="value">{round(mem.total/1024/1024)} MB</span></div>
    <div style="padding:.75rem 0">
      <div class="progress-bar"><div class="progress-fill" style="width:{mem_pct}%"></div></div>
      <div style="text-align:right;font-size:.75rem;color:#64748b;margin-top:4px">{mem_pct}%</div>
    </div>
  </div>
  <div class="card full-width">
    <h2>Endpoints</h2>
    <div class="endpoints">
      <span class="ep">GET /</span>
      <span class="ep">GET /health</span>
      <span class="ep">GET /ping</span>
      <span class="ep">GET /info</span>
      <span class="ep">GET /docs</span>
    </div>
    <a class="docs-link" href="/docs">Ouvrir Swagger UI</a>
  </div>
  <div class="card full-width">
    <h2>Environment Variables ({len(env)} vars)</h2>
    <table>
      <thead><tr><th>Variable</th><th>Value</th></tr></thead>
      <tbody>{env_rows}</tbody>
    </table>
  </div>
</main>
<footer>fastapi-test-app · SystalinkCloud Datacloud · Deployed on K8s</footer>
</body>
</html>"""
