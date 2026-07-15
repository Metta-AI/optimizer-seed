#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Manage a lab's experiment records (games/<g>/experiments/*.md).

Commands:
  record.py new <lab-dir> <slug>              create a record from the template
  record.py validate <lab-dir>                check all records' frontmatter
  record.py list <lab-dir> [--status X]       table of records

A record is Markdown with a YAML frontmatter block (see experiments/_template.md).
Refuted records are never deleted — validate warns if git shows a deleted one.
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = ["id", "policy", "baseline", "candidate", "status", "hypothesis", "decision_rule", "evals"]
STATUSES = ["proposed", "running", "confirmed", "refuted", "inconclusive"]
TERMINAL = ["confirmed", "refuted", "inconclusive"]  # these require evidence: a non-empty evals list


def experiments_dir(lab_dir: str) -> Path:
    d = Path(lab_dir) / "experiments"
    if not d.is_dir():
        sys.exit(f"error: {d} does not exist — is {lab_dir} a lab directory?")
    return d


def record_paths(exp_dir: Path) -> list[Path]:
    return sorted(p for p in exp_dir.glob("*.md") if not p.name.startswith("_"))


def parse_frontmatter(path: Path):
    """Return (frontmatter dict, error string). Exactly one may be None."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None, "no frontmatter block (expected leading '---' ... '---')"
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return None, f"frontmatter is not valid YAML: {e}"
    if not isinstance(fm, dict):
        return None, "frontmatter did not parse to a mapping"
    return fm, None


def cmd_new(lab_dir: str, slug: str) -> None:
    exp_dir = experiments_dir(lab_dir)
    template = exp_dir / "_template.md"
    if not template.is_file():
        sys.exit(f"error: {template} not found — the lab is missing its experiment template")

    slug = slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit(f"error: slug {slug!r} must be lowercase letters/digits/hyphens")

    today = datetime.date.today().isoformat()
    rec_id = f"{today}-{slug}"
    dest = exp_dir / f"{rec_id}.md"
    if dest.exists():
        sys.exit(f"error: {dest} already exists")

    text = template.read_text(encoding="utf-8")
    text = text.replace("YYYY-MM-DD-short-slug", rec_id, 1)
    dest.write_text(text, encoding="utf-8")
    print(f"created {dest}")
    print("next: fill in policy/baseline/hypothesis/decision_rule and the pre-registered predictions")


def deleted_records_in_git(exp_dir: Path) -> list[str]:
    """Names of record files git says were deleted (staged or unstaged)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(exp_dir), "status", "--porcelain", "--", "."],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []  # not a git repo, or no git — nothing to check
    deleted = []
    for line in out.splitlines():
        status, _, path = line[:2], line[2], line[3:]
        if "D" in status and path.endswith(".md") and not Path(path).name.startswith("_"):
            deleted.append(Path(path).name)
    return deleted


def cmd_validate(lab_dir: str) -> None:
    exp_dir = experiments_dir(lab_dir)
    problems: list[str] = []
    warnings: list[str] = []
    paths = record_paths(exp_dir)

    for path in paths:
        fm, err = parse_frontmatter(path)
        if err:
            problems.append(f"{path.name}: {err}")
            continue
        missing = [f for f in REQUIRED_FIELDS if f not in fm or fm[f] in (None, "")]
        if missing:
            problems.append(f"{path.name}: missing required field(s): {', '.join(missing)}")
        status = fm.get("status")
        if status not in STATUSES:
            problems.append(f"{path.name}: status {status!r} not in {STATUSES}")
        elif status in TERMINAL:
            evals = fm.get("evals")
            if not isinstance(evals, list) or len(evals) == 0:
                problems.append(
                    f"{path.name}: status '{status}' requires a non-empty evals list — "
                    "a verdict without the batches that produced it is inadmissible"
                )
        if fm.get("id") and fm["id"] != path.stem:
            warnings.append(f"{path.name}: frontmatter id {fm['id']!r} != filename stem {path.stem!r}")

    for name in deleted_records_in_git(exp_dir):
        warnings.append(
            f"{name}: git shows this record deleted — refuted records are never deleted "
            "(restore it, or confirm with the human if it was never a real record)"
        )

    for w in warnings:
        print(f"WARN  {w}")
    for p in problems:
        print(f"FAIL  {p}")
    print(f"\n{len(paths)} record(s): {len(problems)} problem(s), {len(warnings)} warning(s)")
    sys.exit(1 if problems else 0)


def cmd_list(lab_dir: str, status_filter: str | None) -> None:
    exp_dir = experiments_dir(lab_dir)
    rows = []
    for path in record_paths(exp_dir):
        fm, err = parse_frontmatter(path)
        if err:
            rows.append((path.stem, "(unparseable)", "", ""))
            continue
        status = str(fm.get("status", "?"))
        if status_filter and status != status_filter:
            continue
        hyp = " ".join(str(fm.get("hypothesis", "")).split())
        if len(hyp) > 60:
            hyp = hyp[:57] + "..."
        rows.append((str(fm.get("id", path.stem)), status, str(fm.get("policy", "?")), hyp))

    if not rows:
        print("no records" + (f" with status={status_filter}" if status_filter else ""))
        return
    widths = [max(len(r[i]) for r in rows + [("id", "status", "policy", "hypothesis")]) for i in range(4)]
    header = ("id", "status", "policy", "hypothesis")
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="create a record from the template")
    p_new.add_argument("lab_dir")
    p_new.add_argument("slug", help="short lowercase-hyphen slug, e.g. vote-timing")

    p_val = sub.add_parser("validate", help="check all records' frontmatter")
    p_val.add_argument("lab_dir")

    p_list = sub.add_parser("list", help="table of records")
    p_list.add_argument("lab_dir")
    p_list.add_argument("--status", choices=STATUSES, default=None)

    args = parser.parse_args()
    if args.command == "new":
        cmd_new(args.lab_dir, args.slug)
    elif args.command == "validate":
        cmd_validate(args.lab_dir)
    elif args.command == "list":
        cmd_list(args.lab_dir, args.status)


if __name__ == "__main__":
    main()
