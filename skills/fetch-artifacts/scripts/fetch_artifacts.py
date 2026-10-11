#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "pyyaml"]
# ///
"""
fetch_artifacts.py — download episode artifacts for a hosted eval batch.

Pulls, per episode: results (from the episode row), the replay, the game log,
per-agent policy logs, and player artifact zips — into a per-episode directory
layout that downstream analysis can rely on:

    <out>/<xreq_id>/<episode_request_id>/
        episode.json        # the episode row (status, participants, scores)
        replay.*            # the replay bytes, extension from content-type
        game.log
        policy-logs/<policy_version_id>.<agent_idx>.log
        artifacts/<policy_version_id>.<agent_idx>.zip

Modes:
  one-shot (default): fetch everything terminal right now and exit
  --watch:            poll; download each episode as it turns terminal; exit
                      when all episodes are terminal

Resume-safe: completeness is judged from disk (episode dir + a .done marker),
so re-running the same command skips finished episodes and resumes the rest.

Routes (verified live 2026-07-15, base https://softmax.com/api/observatory):
  GET /v2/experience-requests/{xreq}/episodes         -> episode rows
  GET /v2/episode-requests/{ereq}/artifacts/{type}    -> type in {replay, results, logs}
      (a 404 here means "this episode has no such artifact", not a bad route;
       "debug" also exists but is permission-gated)
  GET /v2/episode-requests/{ereq}/{pvid}/policy-logs/{idx}
  GET /v2/episode-requests/{ereq}/{pvid}/policy-artifact/{idx}
When a route 4xxs unexpectedly, re-derive from <server>/openapi.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

DEFAULT_SERVER = "https://softmax.com/api/observatory"
TERMINAL = {"completed", "failed", "cancelled", "error"}


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


def episodes_for(c: httpx.Client, xreq: str) -> list[dict]:
    r = c.get(f"/v2/experience-requests/{xreq}/episodes")
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else data.get("episodes", [])


def save_stream(c: httpx.Client, url: str, dest: Path) -> bool:
    """Stream a GET to dest.

    Returns False on 404 (artifact doesn't exist) and 403 (not ours — rival
    policies' logs/artifacts are private; only your own are readable).
    """
    with c.stream("GET", url) as r:
        if r.status_code in (403, 404):
            return False
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return True


def ext_for(content_type: str) -> str:
    if "json" in content_type:
        return ".json"
    if "zip" in content_type:
        return ".zip"
    return ".bin"


def fetch_episode(c: httpx.Client, ep: dict, out: Path, skip: frozenset[str] = frozenset()) -> None:
    ereq = ep.get("id") or ep.get("episode_request_id")
    epdir = out / ereq
    done = epdir / ".done"
    if done.exists():
        return
    epdir.mkdir(parents=True, exist_ok=True)

    (epdir / "episode.json").write_text(json.dumps(ep, indent=2, default=str))

    # replay + results + game logs via the generic artifact route
    # (valid types verified live: replay, results, logs; 404 = absent, not a bad route)
    for artifact_type, fname in (("replay", "replay"), ("results", "results"), ("logs", "game.log")):
        if artifact_type in skip:
            continue
        url = f"/v2/episode-requests/{ereq}/artifacts/{artifact_type}"
        with c.stream("GET", url) as r:
            if r.status_code == 404:
                continue
            r.raise_for_status()
            suffix = "" if fname.endswith(".log") else ext_for(r.headers.get("content-type", ""))
            dest = epdir / (fname + suffix)
            with open(dest, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)

    # per-agent policy logs + artifacts, from the participant list
    # (participant rows carry `position` as the agent index — verified live)
    for part in ep.get("participants", []) or []:
        pvid = part.get("policy_version_id")
        idx = part.get("position", part.get("agent_idx"))
        if pvid is None or idx is None:
            continue
        save_stream(c, f"/v2/episode-requests/{ereq}/{pvid}/policy-logs/{idx}",
                    epdir / "policy-logs" / f"{pvid}.{idx}.log")
        save_stream(c, f"/v2/episode-requests/{ereq}/{pvid}/policy-artifact/{idx}",
                    epdir / "artifacts" / f"{pvid}.{idx}.zip")

    done.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(f"  fetched {ereq} ({ep.get('status')})", flush=True)


def fetch_pass(c: httpx.Client, xreq: str, args: argparse.Namespace, skip: frozenset[str]) -> bool:
    """One poll of one batch: fetch what is terminal. Returns True when everything is fetched."""
    out = Path(args.out) / xreq
    eps = episodes_for(c, xreq)
    terminal = [e for e in eps if e.get("status") in TERMINAL]
    pending = [e for e in terminal if not (out / (e.get("id") or "?") / ".done").exists()]

    def fetch_one(ep: dict) -> None:
        # One failed episode (rate limit, transient 5xx) must not kill the watch or the
        # other downloads; it has no .done marker, so the next poll or re-run retries it.
        try:
            fetch_episode(c, ep, out, skip)
        except httpx.HTTPError as error:
            print(f"  FAILED {ep.get('id')}: {error!r} (will retry)", flush=True)

    # Episodes of one batch often finish together and replays can be large, so download
    # several at once (httpx.Client is thread-safe).
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(fetch_one, pending))
    done_count = sum(1 for e in eps if (out / (e.get("id") or "?") / ".done").exists())
    print(f"{time.strftime('%H:%M:%S')} {xreq}: {len(terminal)}/{len(eps)} terminal, "
          f"{done_count} fetched -> {out}", flush=True)
    return bool(eps) and done_count == len(eps)


def run(c: httpx.Client, args: argparse.Namespace) -> None:
    skip = frozenset(args.skip)
    remaining = list(args.xreq)
    while True:
        remaining = [x for x in remaining if not fetch_pass(c, x, args, skip)]
        if not args.watch or not remaining:
            break
        time.sleep(args.interval)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xreq", nargs="+", help="one or more experience request ids (xreq_…)")
    ap.add_argument("--out", default=".runtime/artifacts", help="output root (default .runtime/artifacts)")
    ap.add_argument("--watch", action="store_true", help="stream: poll and fetch episodes as they finish")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--workers", type=int, default=6, help="episodes downloaded at once (default 6)")
    ap.add_argument("--skip", action="append", default=[], choices=["replay", "results", "logs"],
                    help="artifact type to leave out (repeatable); e.g. --skip replay when replays are bulky")
    ap.add_argument("--server", default=DEFAULT_SERVER)
    args = ap.parse_args()

    with httpx.Client(base_url=args.server,
                      headers={"Authorization": f"Bearer {load_token()}"},
                      timeout=120.0, follow_redirects=True) as c:
        run(c, args)


if __name__ == "__main__":
    main()
