# oracle_pairs/scratch/

The working iterations behind finding 14, kept verbatim as provenance. They
were written between 2026-09-08 and 2026-09-09 and are
**superseded** by `../build_index.py` and `../score.py`, which is what to run.

| file | became |
|---|---|
| `pair_index.py` | `../build_index.py` |
| `score_pairs.py` → `score_pairs2.py` → `score_pairs3.py` | `../score.py` |
| `residuals.py` | the residual tally now inside `../score.py` |
| `scorecard.json`, `scorecard2.json`, `scorecard3.json` | successive outputs; `../out/scorecard.json` is the committed result |
| `pairs.json` | an empty (`[]`) result from an early pass |

Read `../score.py`'s docstring before trusting any number in here. Four harness
bugs were found and fixed across these iterations — each one produced a clean,
flattering number rather than a crash — so the earlier scorecards are records
of those bugs, not results.

`../out/pair_index.json`, `pairs_strict.json` and `residuals.json` were checked
byte-identical to the scratch copies of the same names, so those are not
duplicated here.
