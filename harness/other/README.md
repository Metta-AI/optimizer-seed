# Generic self-wiring — any other runtime

No prebuilt wiring exists for your runtime. Wire it yourself from the three
needs in `harness/README.md`, in this order of preference.

## 1. Find the runtime's own hook mechanism

Read your runtime's documentation for lifecycle hooks, automation events, or
startup/shutdown commands. You are looking for:

- **Session start** (or first-prompt) event → run `tools/rotate_lessons.sh`.
  The script is safe under any trigger discipline: it only rotates buffers
  that have content, is idempotent, silent when there's nothing to do, and
  understands Claude Code-style `{"source": ...}` stdin if your runtime
  sends it (rotating only on `startup`/`clear`, never `resume`/`compact`).
- **Session end / agent-stop** event → run `tools/lessons_stop_nudge.sh`.
  It expects Claude Code-style stdin JSON with a `transcript_path` to a
  JSONL transcript and emits `{"decision": "block", "reason": ...}` when the
  agent should be nudged. If your runtime's stop event has a different
  contract, write a thin adapter in this directory that maps between them
  (see `harness/auggie/auggie_stop_nudge.sh` for a worked example of
  adapting when no transcript is available — it uses git status as the
  activity signal).

## 2. Load the skills

Best: your runtime's native skills/commands directory — symlink `skills/*`
into it. Minimum: add one instruction to the runtime's context file (its
AGENTS.md / rules equivalent — most runtimes auto-load the seed's own
`AGENTS.md`, which already covers this): consult `skills/` for the core
skills and resolve game bindings through each lab's `MIXIN.md`.

## 3. No hooks at all? Use the checklist fallback

Per AGENTS.md Memory duties, the automation's duties fall to you:

- **Session start:** run `tools/rotate_lessons.sh` yourself.
- **Session end:** for each lab you worked in (and the root, for
  optimizer-wide work), check its `TENTATIVE_LESSONS.md`. If the session
  produced candidate lessons, buffer them. If it genuinely produced none,
  write nothing — no filler.

A documented fallback IS an acceptable wiring.

## 4. Record what you did

In the root `WORKING_CONTEXT.md`, under "Harness wiring": the runtime, what
was installed (or "checklist fallback in effect"), and the date. If you built
an adapter, keep it in `harness/<runtime>/` with a README so the next agent
on this runtime doesn't rebuild it.
