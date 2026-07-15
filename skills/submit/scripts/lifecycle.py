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
    lifecycle.py monitor --policy NAME[:vN] [--league LEAGUE_ID] [--interval 60]
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
        ms = find_memberships(c, args.policy, args.league)
        rows = summarize(ms)
        for row in rows:
            key = row["membership"] or "?"
            state = f"{row['status']}{' (champion)' if row.get('is_champion') else ''}"
            if seen.get(key) != state:
                print(f"{time.strftime('%H:%M:%S')} {row['policy']} @ {row['league']}: "
                      f"{seen.get(key, '—')} -> {state}", flush=True)
                seen[key] = state
        if rows and all(r["status"] in TERMINAL_STATUSES for r in rows):
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
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    with httpx.Client(base_url=args.server,
                      headers={"Authorization": f"Bearer {load_token()}"},
                      timeout=60.0) as c:
        args.fn(c, args)


if __name__ == "__main__":
    main()
