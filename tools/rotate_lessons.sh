#!/usr/bin/env bash
# Session-start hook: rotate the tentative-lesson buffers (root + every lab).
#
# Touched-only, zero churn: a buffer is archived and re-minted ONLY if it has
# content beyond its template boilerplate — something after the `---` separator
# other than blank lines and the "*(empty)*" placeholder. An untouched buffer
# is not rewritten, not re-stamped, not even touched (byte-identical, same
# mtime). Idempotent: safe to run any number of times.
#
# Dedupe (git-sync protection): before archiving, the buffer is md5-compared
# against the existing archives (including reviewed/). A git sync or merge can
# restore an already-archived buffer; re-archiving it under a new timestamp
# would mint a byte-identical duplicate and inflate the recurrence signal that
# `lessons-review` graduates lessons on. A duplicate is re-minted without
# re-archiving.
#
# Harness protocol: optionally reads hook JSON on stdin (Claude Code / Codex
# SessionStart pass {"source": "startup|resume|clear|compact", ...}); a source
# of resume or compact means the same session is continuing, so nothing is
# rotated. No stdin, or stdin without a source field, is treated as a fresh
# session start. Stdout is one line per rotation — harnesses that inject hook
# stdout as context will surface it — and silent when nothing rotated.
#
# Portable: macOS + Linux, plain bash, coreutils only.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- optional hook JSON on stdin (never block waiting on a terminal) ---
SOURCE="startup"
if [ ! -t 0 ]; then
  INPUT="$(cat 2>/dev/null || true)"
  case "$INPUT" in
    *'"source"'*)
      SOURCE="$(printf '%s' "$INPUT" \
        | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
        | head -n 1)"
      ;;
  esac
fi
case "$SOURCE" in
  resume|compact) exit 0 ;; # same session continuing — do not rotate
esac

hash_file() {
  if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | cut -d' ' -f1
  else md5 -q "$1"; fi
}

# True when the buffer has real content: any non-blank line after the first
# `---` separator that isn't the "*(empty)*" placeholder.
buffer_has_content() {
  awk '
    body && $0 !~ /^[[:space:]]*$/ && $0 !~ /^\*\(empty\)\*[[:space:]]*$/ { found = 1; exit }
    /^---[[:space:]]*$/ { body = 1 }
    END { exit !found }
  ' "$1"
}

# True when the buffer is byte-identical to an existing archive (or a reviewed
# one — those still count; duplicating them would inflate recurrence).
buffer_matches_archive() {
  local buf_md5 dir f
  buf_md5="$(hash_file "$1")"
  for dir in "$2" "$2/reviewed"; do
    [ -d "$dir" ] || continue
    for f in "$dir"/*TENTATIVE_LESSONS*.md; do
      [ -f "$f" ] || continue
      [ "$(hash_file "$f")" = "$buf_md5" ] && return 0
    done
  done
  return 1
}

# Re-mint: keep the buffer's own header (everything through the first `---`,
# which carries the lifecycle text — and, in a lab, the game name), reset the
# body to the empty placeholder.
remint_buffer() {
  local tmp
  tmp="$(mktemp)"
  awk '{ print } /^---[[:space:]]*$/ { exit }' "$1" > "$tmp"
  printf '\n*(empty)*\n' >> "$tmp"
  mv "$tmp" "$1"
}

rotate_one() {
  local buf="$1" arch="$2" label="$3" target
  [ -f "$buf" ] || return 0
  buffer_has_content "$buf" || return 0 # untouched — leave byte-identical
  mkdir -p "$arch"
  if buffer_matches_archive "$buf" "$arch"; then
    remint_buffer "$buf"
    echo "Rotated $label: buffer was a byte-identical copy of an existing archive (likely restored by a git sync) — re-minted without re-archiving."
    return 0
  fi
  target="$arch/$(date -u +%Y-%m-%dT%H%MZ)-TENTATIVE_LESSONS.md"
  # Same-minute collision with a *different* buffer: fall back to seconds.
  [ -e "$target" ] && target="$arch/$(date -u +%Y-%m-%dT%H%M%SZ)-TENTATIVE_LESSONS.md"
  cp "$buf" "$target"
  remint_buffer "$buf"
  echo "Rotated $label: previous session's lessons archived to ${target#"$REPO"/}; fresh buffer minted — write candidate lessons there as you go."
}

rotate_one "$REPO/TENTATIVE_LESSONS.md" "$REPO/lessons_archive" "root buffer"

for buf in "$REPO"/games/*/TENTATIVE_LESSONS.md; do
  [ -f "$buf" ] || continue
  lab="$(basename "$(dirname "$buf")")"
  [ "$lab" = "_template" ] && continue
  rotate_one "$buf" "$REPO/games/$lab/lessons_archive" "$lab lab buffer"
done

exit 0
