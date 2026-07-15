# OpenAI Codex CLI wiring

Codex CLI has a full lifecycle-hooks system (stable and on by default since
the `hooks` feature stabilized — verify with `codex features list | grep
hooks`). Its hook protocol is Claude Code-compatible: `SessionStart` receives
`{"source": "startup|resume|clear|compact", ...}` on stdin and its stdout
becomes model context; `Stop` receives `{"transcript_path": ...,
"stop_hook_active": ...}` on stdin and accepts `{"decision": "block",
"reason": "..."}` on stdout. **The seed's scripts therefore work unmodified.**

Researched against learn.chatgpt.com/docs/hooks (via
developers.openai.com/codex/hooks) and the codex source
(`codex-rs/hooks/src/events/{session_start,stop}.rs`), 2026-07.

## Hooks

Copy `harness/codex/hooks.json` to `.codex/hooks.json` at the repo root:

```sh
mkdir -p .codex && cp harness/codex/hooks.json .codex/hooks.json
```

Then, inside a Codex session in this repo, run `/hooks` and **trust** the
project hooks — Codex refuses to run untrusted project-layer hooks (and the
project itself must be trusted). Restart the session afterwards.

Notes:

- `Stop` in Codex fires on **turn** completion, not process exit — the nudge
  script's once-per-session guard (keyed by transcript hash) keeps it to one
  nudge per session anyway.
- The legacy `notify` config option is fire-and-forget (spawned detached,
  output ignored) — it **cannot** deliver the nudge to the agent. Use the
  Stop hook, not `notify`.
- Config alternative: the same hooks can live as `[[hooks.SessionStart]]` /
  `[[hooks.Stop]]` tables in `.codex/config.toml`; `hooks.json` is used here
  because it matches the other harnesses byte-for-byte in shape.

## Skills

Codex discovers `SKILL.md` skills from `.agents/skills/` (searched from cwd
up to the repo root; user-level home is `~/.agents/skills`). Symlink the
seed's skills:

```sh
mkdir -p .agents/skills
for s in skills/*/; do ln -sfn "../../$s" ".agents/skills/$(basename "$s")"; done
```

Skills are invoked explicitly (`$skill-name`, `/skills`) or auto-selected by
description match. (`~/.codex/prompts/` custom prompts still work but are
deprecated in favor of skills.)

Codex also auto-loads `AGENTS.md` from the repo root — the seed's
constitution is picked up with no extra wiring.

## Record it

After wiring, record in `WORKING_CONTEXT.md` ("Harness wiring"): runtime
`codex`, `.codex/hooks.json` installed + trusted, skills symlinked into
`.agents/skills/`, date.

## Capability gaps (honest)

- No process-exit event exists; `Stop` is per-turn. Acceptable: the nudge
  fires at the first turn-end after substantive work, which is the same
  moment Claude Code's Stop fires.
- Hook support only runs `type = "command"` handlers; that is all the seed
  needs.
- If your Codex build predates the hooks feature (`codex features list`
  lacks a stable `hooks` row), update Codex; failing that, use the checklist
  fallback in `harness/README.md`.
