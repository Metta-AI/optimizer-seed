#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "pyyaml"]
# ///
"""
lifecycle.py — monitor a league submission from placed to verdict.

Watches the membership that a submission creates, through:
placed -> qualifying -> competing (or disqualified), and reports champion
status. Read-only: SUBMITTING is done by `coworld submit` with the human's
recorded go-ahead (see the submit skill); this script only watches.

Two footguns are designed in (both verified behaviors):
  * A failed ROUND is not a disqualified POLICY — don't panic on one bad round.
  * A disqualified membership can drop out of active-only listings, so we poll
    WITHOUT an active-only filter; losing sight of a membership is not the
    same as it succeeding.

Usage:
    lifecycle.py status  --policy NAME[:vN] [--league LEAGUE_ID]
    lifecycle.py monitor --policy NAME[:vN] [--league LEAGUE_ID] [--interval 60] [--keep-watching]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

DEFAULT_SERVER = "https://softmax.com/api/observatory"
TERMINAL_STATUSES = {"competing", "disqualified", "retired", "rejected"}
FINAL_STATUSES = {"disqualified", "retired", "rejected"}


def load_token() -> str:
    """Read the softmax token for the identity the `coworld` CLI is acting as.

    `coworld player use` stores a player session under `player_sessions` in
    ~/.softmax/credentials.yaml; the plain login token under `tokens` is the
    main USER. Reading only `tokens` made these scripts act as the user while
    the CLI acted as the player: batches were created under the wrong identity
    and were then invisible to `coworld xp-request list --mine` and
    `coworld replay-open` (found 2026-10-10). So: the active player session
    first, the user token otherwise. Set OPTIMIZER_AS_USER=1 to force the user
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
                print(f"[auth] player session {active} is missing or expired; "
                      f"run `coworld player use {active}`. Falling back to the user token.", file=sys.stderr)
    tokens = data.get("tokens") or {}
    for server, tok in tokens.items():
        if "softmax.com" in server and tok:
            print("[auth] acting as the main user (no active player session)", file=sys.stderr)
            return tok
    sys.exit("No softmax.com token found — run `softmax login` first.")


def rows_of(payload, *keys: str) -> list[dict]:
    if isinstance(payload, list):
        return payload
    for k in keys:
        if isinstance(payload.get(k), list):
            return payload[k]
    return []


def _pv_name(m: dict) -> str:
    pv = m.get("policy_version") or {}
    if isinstance(pv, dict):
        pol = pv.get("policy")
        if isinstance(pol, dict):
            return pol.get("name") or ""
        return pv.get("policy_name") or pv.get("name") or ""
    return ""


def _pv_num(m: dict) -> int:
    pv = m.get("policy_version") or {}
    if isinstance(pv, dict):
        return int(str(pv.get("version") or 0).lstrip("v") or 0)
    return 0


def find_memberships(c: httpx.Client, policy: str, league: str | None) -> list[dict]:
    name, _, ver = policy.partition(":")
    params: dict = {"mine": True, "limit": 200}
    if league:
        params["league"] = league
    # deliberately NO active_only — see module docstring
    r = c.get("/v2/league-policy-memberships", params=params)
    r.raise_for_status()
    rows = rows_of(r.json(), "memberships", "league_policy_memberships", "items", "entries")
    hits = [m for m in rows if _pv_name(m) == name]
    if ver:
        want = int(ver.lstrip("v"))
        hits = [m for m in hits if _pv_num(m) == want]
    return hits


def summarize(memberships: list[dict]) -> list[dict]:
    out = []
    for m in memberships:
        league = m.get("league") or {}
        division = m.get("division") or {}
        out.append({
            "membership": m.get("id"),
            "league": league.get("name") if isinstance(league, dict) else league,
            "division": division.get("name") if isinstance(division, dict) else division,
            "policy": f"{_pv_name(m)}:v{_pv_num(m)}",
            "status": m.get("status"),
            "substatus": m.get("substatus"),
            "is_champion": m.get("is_champion"),
        })
    return out


def cmd_status(c: httpx.Client, args: argparse.Namespace) -> None:
    ms = find_memberships(c, args.policy, args.league)
    if not ms:
        print(f"No memberships found for {args.policy!r}"
              + (f" in league {args.league}" if args.league else "")
              + " — if you just submitted, placement can lag; retry shortly.")
        return
    print(json.dumps(summarize(ms), indent=2, default=str))


def cmd_monitor(c: httpx.Client, args: argparse.Namespace) -> None:
    seen: dict[str, str] = {}
    while True:
        try:
            ms = find_memberships(c, args.policy, args.league)
        except httpx.HTTPError as error:
            # A transient error must not end a background monitor.
            print(f"{time.strftime('%H:%M:%S')} poll failed ({error!r}); retrying", flush=True)
            time.sleep(args.interval)
            continue
        rows = summarize(ms)
        for row in rows:
            key = row["membership"] or "?"
            state = (f"{row['status']}/{row.get('substatus')}"
                     f"{' (champion)' if row.get('is_champion') else ''}")
            if seen.get(key) != state:
                print(f"{time.strftime('%H:%M:%S')} {row['policy']} @ {row['league']}: "
                      f"{seen.get(key, '—')} -> {state}", flush=True)
                seen[key] = state
        # "competing" is reached minutes after submitting, long before the entry's first
        # league game, and the champion flag and substatus can still move afterwards. With
        # --keep-watching the monitor only stops on a final status.
        stop_at = FINAL_STATUSES if args.keep_watching else TERMINAL_STATUSES
        if rows and all(r["status"] in stop_at for r in rows):
            print("All memberships terminal.")
            print(json.dumps(rows, indent=2, default=str))
            return
        if not rows:
            print(f"{time.strftime('%H:%M:%S')} no membership visible yet "
                  f"(placement can lag; disqualified rows may also hide — keep watching)", flush=True)
        time.sleep(args.interval)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default=DEFAULT_SERVER)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("status", cmd_status), ("monitor", cmd_monitor)):
        p = sub.add_parser(name)
        p.add_argument("--policy", required=True, help="NAME or NAME:vN")
        p.add_argument("--league", help="league id filter")
        if name == "monitor":
            p.add_argument("--interval", type=int, default=60)
            p.add_argument("--keep-watching", action="store_true",
                           help="do not stop at 'competing'; keep reporting status, substatus and "
                                "champion changes until the membership is disqualified or retired")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    with httpx.Client(base_url=args.server,
                      headers={"Authorization": f"Bearer {load_token()}"},
                      timeout=60.0) as c:
        args.fn(c, args)


if __name__ == "__main__":
    main()
