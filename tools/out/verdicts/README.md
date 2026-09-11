# tools/out/verdicts/

The raw multi-agent syntheses the numbered findings were written from. They
are not reproducible — each is the output of a workflow run — so they are kept
as provenance for the findings' claims.

## Most of this folder was never committed until 2026-09-11

`.gitignore` meant to keep this folder while ignoring the rest of `tools/out/`,
but it said `tools/out/`, which excludes the directory itself: Git never looks
inside it, so the `!tools/out/verdicts/` exception could not apply. Only three
files that were already tracked survived. The rule is now `tools/out/*`.

## three_questions_synthesis.md — recovered

Finding 10's source, cited by `STATUS.md`. It was written on 2026-09-07 at
06:42:22 UTC from workflow run `wf_abeebd4f-613`, whose dossier covers the four
experiments behind finding 10 — `q1a-nrbf-writeback`,
`q1b-crestron-to-controlscript`, `q2-missing-ethernet`,
`q3-docs-only-generation` (verdicts: 47 confirmed, 4 overstated, 2 refuted).
It was never committed, because of the rule above, and by 2026-09-11 it was no
longer on disk.

It was restored verbatim from that run's saved result
(`workflows/22114bf1/wf_abeebd4f-613.result.json`, key `result.synthesis`).
The original command's own output — it printed the Q1a analysis with
`VERDICT=YES_WITH_CAVEATS` — matches.

## workflows/

| path | what |
|---|---|
| `22114bf1/wf_*.result.json` | the saved return value of every workflow run in the project's first session (14 runs, 2026-09-06 to 09-07): dossiers, verdict counts, syntheses, completeness critiques |
| `22114bf1/*.js` | the workflow scripts from that session |
| `pkp-validator-and-ross-wf_0326d92f-35e.*` | the run behind findings 16 and 17: the validator reimplementation and the Ross review, with its adversarial verifiers' verdicts |
| `pack-up-extron-project-wf_61d1161c-2c8.js` | the run that produced `ROADMAP.md` and the C: drive sweep for the 2026-09-11 hand-off |

All were scanned for token-shaped strings before being committed; none were
found. The full conversation transcripts for these runs are not here — they are
in the git-ignored `private/claude/`, or at `Z:\.claude\projects\` for the first
session.
