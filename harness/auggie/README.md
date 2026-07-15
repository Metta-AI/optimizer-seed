# Augment Auggie CLI wiring

Auggie has a first-class lifecycle-hooks system modeled on Claude Code's:
`SessionStart`, `SessionEnd`, `Stop`, `PreToolUse`, `PostToolUse`, configured
under a `hooks` key in `settings.json`. `SessionStart` stdout (exit 0) is
injected as agent context; `Stop` can block completion and hand the agent a
reason. Researched against docs.augmentcode.com (`/cli/hooks`,
`/cli/hooks-examples`, `/cli/rules`, `/cli/skills`, `/cli/config`), 2026-07.

## Hooks

Copy `harness/auggie/settings.json` into the workspace settings (or merge the
`hooks` key if `.augment/settings.json` already exists — note Auggie's
documented merge semantics: settings files layer, they don't deep-merge
everything):

```sh
mkdir -p .augment && cp harness/auggie/settings.json .augment/settings.json
```

- `SessionStart` → `tools/rotate_lessons.sh`, unmodified. Auggie's stdin
  JSON has no `source` field; the script treats that as a fresh session
  start, which is correct here — Auggie fires SessionStart on new sessions.
  Rotation output (only when something rotated) is injected as context.
- `Stop` → `harness/auggie/auggie_stop_nudge.sh`, an **adapter**, because
  Auggie's Stop hook input has no `transcript_path` (a documented gap:
  hooks cannot read conversation history). The adapter detects substantive
  activity from the git working tree instead — uncommitted changes under
  `games/<lab>/` mean the lab was worked on; changes outside `games/` mean
  root work — and emits Auggie's documented block shape
  (`hookSpecificOutput.decision: "block"`). Same no-filler contract: one
  nudge per conversation (guard file keyed by `conversation_id`), and it
  says to write nothing if there are genuinely no lessons.

Timeouts in Auggie's settings are **milliseconds** (Claude Code's are
seconds) — the shipped `settings.json` already uses ms.

## Skills and the constitution

- Auggie discovers `SKILL.md` skills from `.augment/skills/` and — Claude
  Code-compatibly — from `.claude/skills/` and `.agents/skills/`. If you ran
  the claude-code installer, its `.claude/skills/` symlinks already work.
  Otherwise:

  ```sh
  mkdir -p .augment/skills
  for s in skills/*/; do ln -sfn "../../$s" ".augment/skills/$(basename "$s")"; done
  ```

- Auggie auto-loads `AGENTS.md` (and `CLAUDE.md`) from the workspace — the
  seed's constitution needs no extra wiring.

## Record it

After wiring, record in `WORKING_CONTEXT.md` ("Harness wiring"): runtime
`auggie`, `.augment/settings.json` hooks installed, skills path used, date.

## Capability gaps (honest)

- **No transcript access for hooks.** The seed's transcript-based nudge
  (`tools/lessons_stop_nudge.sh`) cannot run; the git-status adapter is the
  honest substitute. Its known blind spots: a read/analysis-only session
  (no file changes) won't trigger a nudge even if it produced lessons, and a
  session that committed all its work before stopping looks clean. For those
  sessions the AGENTS.md Memory duties (buffer eagerly as you go) are the
  backstop.
- `SessionEnd` exists but cannot block or reach the agent — cleanup only;
  the nudge must be a `Stop` hook.
- Hook scripts must be executable with a shebang (they are).
