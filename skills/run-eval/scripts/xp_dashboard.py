#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "pyyaml"]
# ///
"""
xp_dashboard.py — live browser dashboard for in-flight eval batches.

Serves a self-contained local page that polls one or more experience requests
and updates as episodes complete: progress, throughput/ETA, per-episode status
and scores. Read-only; game-agnostic (platform-level results only — richer
game views are lab instruments).

Usage:
    xp_dashboard.py XREQ_ID [XREQ_ID ...] [--port 8787]

Then give the human the link (http://localhost:8787) unprompted — that's the
discipline attached to this script.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx

DEFAULT_SERVER = "https://softmax.com/api/observatory"
TERMINAL = {"completed", "failed", "cancelled", "error"}
POLL_SECONDS = 15


def load_token() -> str:
    try:
        from softmax.auth import load_current_token  # type: ignore
        return load_current_token(server="https://softmax.com")
    except Exception:
        pass
    creds = Path.home() / ".softmax" / "credentials.yaml"
    if creds.exists():
        import yaml
        tokens = (yaml.safe_load(creds.read_text()) or {}).get("tokens") or {}
        for server, tok in tokens.items():
            if "softmax.com" in server and tok:
                return tok
        for tok in tokens.values():
            if tok:
                return tok
    sys.exit("No softmax credentials found — run `softmax login` first.")


class State:
    """Polled snapshot shared between the poller thread and the HTTP handler."""

    def __init__(self, xreqs: list[str], server: str):
        self.xreqs = xreqs
        self.server = server
        self.lock = threading.Lock()
        self.data: dict[str, dict] = {x: {"episodes": [], "started": time.time()} for x in xreqs}

    def poll_forever(self) -> None:
        client = httpx.Client(base_url=self.server,
                              headers={"Authorization": f"Bearer {load_token()}"},
                              timeout=60.0)
        while True:
            for xreq in self.xreqs:
                try:
                    r = client.get(f"/v2/experience-requests/{xreq}/episodes")
                    r.raise_for_status()
                    eps = r.json()
                    eps = eps if isinstance(eps, list) else eps.get("episodes", [])
                    with self.lock:
                        self.data[xreq]["episodes"] = eps
                        self.data[xreq]["polled"] = time.time()
                except Exception as e:  # keep serving stale data on poll errors
                    with self.lock:
                        self.data[xreq]["error"] = str(e)
            time.sleep(POLL_SECONDS)

    def snapshot(self) -> dict:
        with self.lock:
            out = {}
            for xreq, d in self.data.items():
                eps = d["episodes"]
                done = [e for e in eps if e.get("status") in TERMINAL]
                elapsed = max(time.time() - d["started"], 1)
                rate = len(done) / (elapsed / 60)  # episodes per minute
                remaining = len(eps) - len(done)
                out[xreq] = {
                    "total": len(eps),
                    "done": len(done),
                    "rate_per_min": round(rate, 2),
                    "eta_min": round(remaining / rate, 1) if rate > 0 and remaining else None,
                    "error": d.get("error"),
                    "episodes": [{
                        "id": e.get("id"),
                        "status": e.get("status"),
                        "scores": e.get("scores") or "",
                        "participants": [p.get("policy_name", "?") for p in (e.get("participants") or [])],
                        "error_type": e.get("error_type") or "",
                    } for e in eps],
                }
            return out


PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Eval dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@700;900&family=Merriweather+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body { margin:0; background:#fffdf4; color:#111827; font:400 0.84rem/1.55 'Merriweather Sans',sans-serif; }
.page { max-width:960px; margin:0 auto; padding:32px 24px 60px; }
h1 { font:900 1.4rem 'Merriweather',Georgia,serif; margin:0 0 4px; }
.sub { font-size:0.66rem; color:#999; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:22px; }
h2 { font:700 0.95rem 'Merriweather',Georgia,serif; margin:26px 0 6px; }
.bar { height:10px; background:#f0ebe1; border-radius:999px; overflow:hidden; margin:6px 0 4px; }
.bar > div { height:100%; background:#1a3875; transition:width 0.6s ease; }
.stats { font-size:0.74rem; color:#555; margin-bottom:8px; }
.stats b { font-feature-settings:"tnum" 1; }
table { border-collapse:collapse; width:100%; font-size:0.72rem; }
th { text-align:left; font-size:0.58rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em;
     color:#555; border-bottom:2px solid #d4c9b5; padding:4px 8px; }
td { border-bottom:1px solid #f0ebe1; padding:5px 8px; font-feature-settings:"tnum" 1; }
.st-completed { color:#6e8050; font-weight:700; }
.st-failed, .st-error { color:#b36e4e; font-weight:700; }
.st-running, .st-pending, .st-dispatched { color:#1a3875; }
.err { color:#b36e4e; font-size:0.72rem; }
</style></head><body><div class="page">
<h1>Eval dashboard</h1>
<div class="sub">polls every __POLL__s &middot; read-only &middot; close this tab freely — the batch runs server-side</div>
<div id="content">loading…</div>
<script>
async function refresh() {
  const r = await fetch('/data'); const data = await r.json();
  let html = '';
  for (const [xreq, d] of Object.entries(data)) {
    const pct = d.total ? Math.round(100 * d.done / d.total) : 0;
    html += `<h2>${xreq}</h2>`;
    if (d.error) html += `<div class="err">poll error (showing last good data): ${d.error}</div>`;
    html += `<div class="bar"><div style="width:${pct}%"></div></div>`;
    html += `<div class="stats"><b>${d.done}/${d.total}</b> terminal (${pct}%)`;
    if (d.rate_per_min) html += ` &middot; <b>${d.rate_per_min}</b> eps/min`;
    if (d.eta_min) html += ` &middot; ~<b>${d.eta_min}</b> min remaining`;
    html += `</div><table><tr><th>episode</th><th>status</th><th>players</th><th>scores</th><th>error</th></tr>`;
    for (const e of d.episodes) {
      html += `<tr><td>${(e.id||'').slice(0,26)}…</td><td class="st-${e.status}">${e.status}</td>`
            + `<td>${e.participants.join(', ')}</td><td>${JSON.stringify(e.scores)}</td><td>${e.error_type}</td></tr>`;
    }
    html += '</table>';
  }
  document.getElementById('content').innerHTML = html;
}
refresh(); setInterval(refresh, __POLL__ * 1000);
</script></div></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("xreqs", nargs="+", help="experience request id(s)")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    args = ap.parse_args()

    state = State(args.xreqs, args.server)
    threading.Thread(target=state.poll_forever, daemon=True).start()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/data":
                body = json.dumps(state.snapshot(), default=str).encode()
                ctype = "application/json"
            else:
                body = PAGE.replace("__POLL__", str(POLL_SECONDS)).encode()
                ctype = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):  # quiet
            pass

    print(f"Dashboard: http://localhost:{args.port}  (watching {len(args.xreqs)} batch(es); Ctrl-C to stop)")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
