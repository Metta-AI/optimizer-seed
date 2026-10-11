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
    """Read the softmax token for the identity the `coworld` CLI is acting as.

    `coworld player use` stores a player session under `player_sessions` in
    ~/.softmax/credentials.yaml; the plain login token under `tokens` is the
    main USER. Reading only `tokens` made these scripts act as the user while
    the CLI acted as the player: batches were created under the wrong identity
    and were then invisible to `coworld xp-request list --mine` and
    `coworld replay-open` (found 2026-10-10). So: the active player session
    first; the user token only when no player is active (an expired player
    session is an error, not a fallback). Set OPTIMIZER_AS_USER=1 to force the user
    token (for batches that were created as the user). The identity chosen is
    printed to stderr.
    """
    import os
    from datetime import datetime, timezone

    creds = Path.home() / ".softmax" / "credentials.yaml"
    if not creds.exists():
        sys.exit("No softmax credentials found — run `softmax login` first.")
    import yaml
    data = yaml.safe_load(creds.read_text()) or {}
    if not os.environ.get("OPTIMIZER_AS_USER"):
        for server, session in (data.get("player_sessions") or {}).items():
            if "softmax.com" not in server:
                continue
            active = (session or {}).get("active")
            entry = ((session or {}).get("cache") or {}).get(active) or {}
            expires = str(entry.get("expires_at") or "")
            if entry.get("token") and expires > datetime.now(timezone.utc).isoformat():
                print(f"[auth] acting as player {active}", file=sys.stderr)
                return entry["token"]
            if active:
                # Do not fall back to the user token here: that is the wrong-identity bug again,
                # only quieter.
                sys.exit(f"[auth] player session {active} is missing or expired; run "
                         f"`coworld player use {active}`, or set OPTIMIZER_AS_USER=1 to act as the main user.")
    tokens = data.get("tokens") or {}
    for server, tok in tokens.items():
        if "softmax.com" in server and tok:
            print("[auth] acting as the main user", file=sys.stderr)
            return tok
    sys.exit("No softmax.com token found — run `softmax login` first.")


def seat_scores(e: dict) -> list[dict]:
    """One {label, score} per seat, in position order.

    `participant_scores` is by position. The older `scores` list is keyed by
    policy-version id and collapses a policy seated twice, so it is only a
    fallback.
    """
    by_pos = {p.get("position"): p.get("score") for p in (e.get("participant_scores") or [])}
    by_pvid = {s.get("policy_version_id"): s.get("score")
               for s in (e.get("scores") or []) if isinstance(s, dict)}
    seats = []
    for p in sorted(e.get("participants") or [], key=lambda p: p.get("position", 0)):
        label = p.get("label") or p.get("policy_name") or "?"
        score = by_pos.get(p.get("position"), by_pvid.get(p.get("policy_version_id")))
        seats.append({"label": label, "score": score})
    return seats


def policy_means(eps: list[dict]) -> list[dict]:
    """Mean platform score per policy label over completed episodes (seats, not games)."""
    acc: dict[str, list[float]] = {}
    for e in eps:
        if e.get("status") != "completed":
            continue
        for seat in seat_scores(e):
            if seat["score"] is not None:
                acc.setdefault(seat["label"], []).append(seat["score"])
    rows = [{"label": k, "n": len(v), "mean": round(sum(v) / len(v), 4)} for k, v in acc.items()]
    return sorted(rows, key=lambda r: -r["mean"])


class State:
    """Polled snapshot shared between the poller thread and the HTTP handler."""

    def __init__(self, xreqs: list[str], server: str):
        self.xreqs = xreqs
        self.server = server
        self.lock = threading.Lock()
        self.data: dict[str, dict] = {x: {"episodes": [], "started": time.time(), "done_at_start": None}
                                      for x in xreqs}

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
                        if self.data[xreq]["done_at_start"] is None:
                            self.data[xreq]["done_at_start"] = sum(e.get("status") in TERMINAL for e in eps)
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
                # Rate counts only episodes that finished while this dashboard watched;
                # a batch that was already done would otherwise show an absurd rate.
                rate = (len(done) - (d["done_at_start"] or 0)) / (elapsed / 60)  # episodes per minute
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
                        "seats": seat_scores(e),
                        "error_type": e.get("error_type") or "",
                    } for e in eps],
                    "by_policy": policy_means(eps),
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
table.means { width:auto; min-width:340px; margin:4px 0 4px; }
.note { font-size:0.66rem; color:#777; margin:0 0 12px; max-width:640px; }
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
    html += `</div>`;
    if (d.by_policy.length) {
      html += `<table class="means"><tr><th>policy</th><th>seats</th><th>mean score</th></tr>`;
      for (const p of d.by_policy) html += `<tr><td>${p.label}</td><td>${p.n}</td><td>${p.mean.toFixed(3)}</td></tr>`;
      html += `</table><div class="note">Raw platform means over completed seats, not adjusted for which role or position each seat drew. Directional only; read the batch with the lab's analysis tools.</div>`;
    }
    html += `<table><tr><th>episode</th><th>status</th><th>seats (score)</th><th>error</th></tr>`;
    for (const e of d.episodes) {
      const seats = e.seats.map(s => s.score == null ? s.label : `${s.label} <b>${s.score.toFixed(2)}</b>`).join(' &middot; ');
      html += `<tr><td>${(e.id||'').slice(0,13)}…</td><td class="st-${e.status}">${e.status}</td>`
            + `<td>${seats}</td><td>${e.error_type}</td></tr>`;
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
