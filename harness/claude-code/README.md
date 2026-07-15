# Claude Code wiring

Complete wiring for Claude Code: both lifecycle hooks plus native skill
discovery. Install with one command from the repo root:

```sh
harness/claude-code/install.sh
```

What it does:

1. **Hooks** — merges `harness/claude-code/settings.json` into the repo's
   `.claude/settings.json`: creates it if absent, appends to existing hook
   lists if present (never overwrites them), and if a safe merge isn't
   possible (invalid JSON, no python3) it stops and tells you what to merge
   by hand:
   - `SessionStart` → `tools/rotate_lessons.sh`. Claude Code passes
     `{"source": "startup|resume|clear|compact"}` on stdin; the script
     rotates only on fresh starts (`startup`/`clear`) and only rotates
     buffers that have content — untouched labs generate zero churn.
   - `Stop` → `tools/lessons_stop_nudge.sh`. Reads the transcript path from
     the hook's stdin JSON, and emits `{"decision":"block","reason":...}`
     once per session if a worked-in lab's buffer is untouched. The nudge
     says to write nothing if there are genuinely no lessons.
2. **Skills** — symlinks each `skills/*` directory into `.claude/skills/`.
   Claude Code auto-discovers skills there; each lab's mixin skills live in
   the lab and are resolved through the lab's `MIXIN.md`, not symlinked.

After installing, record the wiring in `WORKING_CONTEXT.md` ("Harness
wiring"): runtime `claude-code`, hooks installed, date. Restart the Claude
Code session so the hooks load.

## Verifying

- Start a session: with an empty buffer nothing happens (silence is
  correct); with a buffer that has content you'll see a rotation line and a
  new file in the right `lessons_archive/`.
- `/hooks` inside Claude Code lists the active hooks.

## Notes

- Hook stdout from `SessionStart` is injected as context, so the rotation
  summary (when there is one) reaches the agent.
- The stop nudge keeps a once-per-session guard file in `$TMPDIR`, keyed by
  transcript hash, and honors `stop_hook_active` — it can't loop.
- `settings.json` here is the canonical hook config; `install.sh` copies it
  rather than duplicating it inline.
