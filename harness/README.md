# Harness wiring — making any runtime run the seed

The seed is runtime-agnostic: its memory lifecycle is implemented by plain
scripts in `tools/` and plain `SKILL.md` docs in `skills/`. What varies by
runtime (Claude Code, Codex, Auggie, anything else) is only how those get
*invoked*. This directory holds the per-runtime wirings.

## What the seed needs from a runtime

Three things, in order of value:

1. **A session-start event** that runs `tools/rotate_lessons.sh` — archives
   any lesson buffer with content and re-mints it fresh. Touched-only: an
   untouched buffer generates zero churn, so running it is always safe.
2. **A session-end event** that runs `tools/lessons_stop_nudge.sh` — nudges
   once, for labs with substantive session activity whose buffers are
   untouched, to buffer candidate lessons *if there are any* (and to write
   nothing if there are none).
3. **A way to load `skills/`** — a directory of `SKILL.md` docs. Native skill
   discovery is best; at minimum, an instruction in the runtime's context
   file (its AGENTS.md / rules equivalent) to consult `skills/` and resolve
   game bindings through each lab's `MIXIN.md`.

## The self-wiring step (onboarding)

During onboarding, the agent wires its own runtime:

1. **Identify the runtime you are running in.**
2. **If `harness/<runtime>/` exists here** (claude-code, codex, auggie),
   follow its README — it has a tested wiring.
3. **Otherwise**, read your own runtime's documentation for lifecycle
   hooks / automation and wire the closest equivalents of the three needs
   above. `harness/other/README.md` has the generic recipe.
4. **Record what you did** in the root `WORKING_CONTEXT.md` under
   "Harness wiring": which runtime, which hooks were installed (or that the
   checklist fallback is in effect), and the date. A fresh agent must be able
   to tell from disk whether the hooks are running.

## The checklist fallback (hookless runtimes)

A runtime with no hook mechanism still runs the seed — the duties move from
automation to doctrine (AGENTS.md, Memory duties):

- **At session start:** run `tools/rotate_lessons.sh` yourself (or perform
  its check by hand: any buffer with content after its `---` separator gets
  archived to its `lessons_archive/` with a UTC timestamp and re-minted).
- **At session end:** check the buffers for the labs you actually worked in.
  If a worked-in lab's buffer is untouched, consider whether the session
  produced candidate lessons and buffer them. If it genuinely produced none,
  write nothing.

A documented fallback IS an acceptable wiring — record it in
`WORKING_CONTEXT.md` like any other.

## Contents

| Path | Runtime |
|---|---|
| `claude-code/` | Claude Code — full hook wiring (tested) + skills symlink installer |
| `codex/` | OpenAI Codex CLI — full hook wiring via its hooks system |
| `auggie/` | Augment Auggie CLI — full hook wiring via its hooks system |
| `other/` | Generic self-wiring instructions for anything else |
