---
name: lessons-review
description: "Periodic (≈weekly, or when the human asks) review of the tentative-lesson archives — root and per-lab: cluster the lessons that RECUR across independent session buffers, propose promote/keep/cull with recurrence counts, and — on the human's call, never without it — graduate the keepers into best_practices.md and retire the reviewed buffers. Triggers: '/lessons-review', 'review the lessons', 'which lessons keep recurring', 'graduate lessons'."
---

# Lessons review

Mine the lesson archives for the one signal they exist to surface: **lessons
that recur across independent session buffers.** Recurrence — not in-session
conviction — is the graduation evidence. A boring lesson seen in 3 sessions
outranks a brilliant one seen once; recurrence beats eloquence.

**Announce:** "Reviewing the lesson archives — clustering recurring lessons
across N session buffers (root + M labs)."

## When

- The human asks, or roughly weekly (per AGENTS.md Memory duties).
- Worth suggesting unprompted when an archive has accumulated ~5+ unreviewed
  buffers.

## Inputs

Two scopes, reviewed in one pass but never mixed:

- **Root** (optimizer-wide lessons): `lessons_archive/*.md` → graduates into
  the root `best_practices.md`.
- **Each lab**: `games/<g>/lessons_archive/*.md` → graduates into that lab's
  `best_practices.md`. Game lessons stay in the lab; a lesson that turns out
  to be game-agnostic graduates to root instead — say so when proposing it.

For each scope:

- Unreviewed archives (`lessons_archive/*.md`) are the **candidate set**.
- `lessons_archive/reviewed/` holds already-reviewed buffers. **Exclude them
  from the candidate set, but count them toward recurrence** — a fresh lesson
  that also appeared in two reviewed buffers has recurrence 3, not 1.
- The live `TENTATIVE_LESSONS.md` counts read-only: include its lessons in
  clustering, but the buffer stays in place — this review never retires it
  (the session-start hook rotates it).
- `best_practices.md` is the graduation target — also check a candidate isn't
  already there.

## Workflow

1. **Collect** every lesson from the candidate set plus the live buffer,
   keyed by (buffer file, lesson text). Buffers are free-form — a lesson is
   one bullet (or one `###` block in older formats).
2. **Cluster semantically.** The same underlying lesson worded differently
   counts as recurrence. Count reviewed-buffer appearances too. Cite which
   session buffers (by archive filename/date) each cluster appeared in.
3. **Propose** as a table for the human, per scope:
   - **Promote** — recurred in ≥2–3 independent buffers; or a single
     occurrence that is both high-stakes and independently verified (say
     which and why).
   - **Keep waiting** — plausible, 1 occurrence. Stays discoverable in
     `reviewed/` for future recurrence counting.
   - **Cull** — contradicted by later evidence, superseded by a graduated
     practice, or noise. Every cull carries a stated reason.

   Each row: the one-line lesson, recurrence count with dates, and a
   recommendation with a reason. **The human decides — never graduate
   without their call.**
4. **Apply the decisions.**
   - Promoted lessons → the right `best_practices.md`, rewritten as durable
     practice prose (not buffer-bullet format), each marked with its
     recurrence evidence and the review date, e.g.
     *(graduated 2026-07-15; seen in 3 sessions: 06-28, 07-04, 07-11)*.
   - Culled lessons retire with their buffer, but **nothing vanishes
     silently**: the cull and its reason go in the review's closing record
     (the commit message, or a dated note the human will see). A lesson
     contradicted by later evidence is culled *with the contradiction
     recorded* — that contradiction may itself be a `closed_levers.md` entry;
     propose it when it is.
5. **Retire the reviewed buffers**: `git mv` each reviewed archive into its
   scope's `lessons_archive/reviewed/` (create if needed). They still count
   for future recurrence — retirement removes them from the candidate set,
   not from the evidence base.
6. **Close the record**: summarize per scope — N buffers reviewed,
   promoted / waiting / culled counts, with the cull reasons. If the repo's
   conventions allow, commit the review as one unit with that summary.

## Discipline

- **Recurrence beats eloquence** — graduate what keeps coming back, not what
  reads well once.
- **The human decides** — the table is a proposal; apply nothing before
  their call.
- **Check the target first** — don't re-promote something already in
  `best_practices.md`; if a recurrence refines an existing practice, propose
  amending it instead.
- **Culls leave a note** — a refutation is an asset (non-negotiable 6); a
  silent deletion destroys it.
- **Scopes stay separate** — a lab's lessons graduate into the lab's
  practices unless they are genuinely game-agnostic, and then say so.

## See also

- `TENTATIVE_LESSONS.md` (root and per-lab) and `tools/rotate_lessons.sh` —
  the buffer lifecycle this review closes.
- `best_practices.md` (root and per-lab) — where graduated practices land.
- `closed_levers.md` — where a contradiction that killed a lesson may also
  belong.
