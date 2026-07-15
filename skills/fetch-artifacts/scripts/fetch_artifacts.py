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
from pathlib import Path

import httpx

DEFAULT_SERVER = "https://softmax.com/api/observatory"
TERMINAL = {"completed", "failed", "cancelled", "error"}


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


def fetch_episode(c: httpx.Client, ep: dict, out: Path) -> None:
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


def run(c: httpx.Client, args: argparse.Namespace) -> None:
    out = Path(args.out) / args.xreq
    while True:
        eps = episodes_for(c, args.xreq)
        terminal = [e for e in eps if e.get("status") in TERMINAL]
        for ep in terminal:
            fetch_episode(c, ep, out)
        done_count = sum(1 for e in eps if (out / (e.get("id") or "?") / ".done").exists())
        print(f"{time.strftime('%H:%M:%S')} {args.xreq}: {len(terminal)}/{len(eps)} terminal, "
              f"{done_count} fetched -> {out}", flush=True)
        if not args.watch or (eps and len(terminal) == len(eps)):
            break
        time.sleep(args.interval)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xreq", help="experience request id (xreq_…)")
    ap.add_argument("--out", default=".runtime/artifacts", help="output root (default .runtime/artifacts)")
    ap.add_argument("--watch", action="store_true", help="stream: poll and fetch episodes as they finish")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    args = ap.parse_args()

    with httpx.Client(base_url=args.server,
                      headers={"Authorization": f"Bearer {load_token()}"},
                      timeout=120.0, follow_redirects=True) as c:
        run(c, args)


if __name__ == "__main__":
    main()
