# POSTFIX — the validator differential, re-run against the post-fix `pkp_validate.py`

**R9.** STATUS.md and finding 16 quote "1,900 of 1,919 exact agreement" between
`tools/pkp_validate.py` and Extron's own `DriverAssetValidator`. That number was
measured with an earlier, pre-fix revision of the tool; after the fixes finding
16 §5a/§5b describe, only the individual disagreeing cases were spot-checked
against the fix, never a full re-run. This re-runs the whole differential
against the **committed HEAD validator**
(`1edbb2382e023b806526a21ff56afcba070eca0`, saved to a private tmp file via
`git show HEAD:tools/pkp_validate.py` because `tools/pkp_validate.py` has
uncommitted, concurrent edits in this working tree — the run never touched
that copy) and reports what changed.

## Method

- **Snapshot.** `git show HEAD:tools/pkp_validate.py` → a tmp-dir file, run
  with `tools/` (pkp_dump.py, nrbf_graph.py — unmodified at HEAD, confirmed via
  `git status`) added to `sys.path` *after* the tmp dir, so `import pkp_dump`
  resolves to the real module while `import pkp_validate` resolves to the
  snapshot. The loaded module's `__file__` was asserted against the tmp path
  on every run.
- **Corpus.** `experiments/validator_differential/all_pkp.txt` (1,853 paths,
  `C:\Users\Public\Documents\Extron\Driver3\...`) rewritten to
  `corpus/extron-driver3/...` in a tmp copy; all 1,853 rewritten paths verified
  to exist before running. Extron's verdicts: `real_all.txt` (all 1,853 are
  `0 Valid`, confirmed).
- **Mutants.** `experiments/validator_differential/extval/mutant_list.txt` (47
  paths) and `case_list.txt` (6 paths) rewritten from
  the workstation's temp folder (`...\Temp\extval\mutants\...`) to
  `experiments/validator_differential/extval/mutants/...`; all 53 files
  verified to exist. Extron's verdicts: `oracle_mut.tsv` (47) and
  `oracle_case.tsv` (6) — these two lists together are the "53 deliberate
  mutants" in finding 16's 1,919 total.
- No `guid_hash_table` was passed for the headline runs (same as the original
  `runpy.py` / `extval/run_py.py` methodology, for an apples-to-apples
  comparison with `py_all.tsv` / `py_mut.tsv` / `py_case.tsv`). A separate,
  targeted run *with*
  `experiments/validator_differential/guidtable.tsv` (4,775 entries) was made
  for the 3 packages known to need it, to confirm the classification below —
  see "gap 1" under Disagreements.
- "Exact agreement" = the numeric code (`0`/`80085`/`80086`) this tool
  returned equals Extron's. Where Extron's own loader (`LoadFromFile`) never
  reaches `Validate` at all (`oracle_*.tsv` status `loadnull`, no code), there
  is no numeric code to match against — those rows are counted separately as
  "representation-only" mismatches, explained below, and are **not** counted
  as agreements or scored as failures of the code fix.

## Results

### 1,853-package shipping corpus

**Post-fix: 1,850 / 1,853 exact agreement (99.84%).**
Pre-fix (`py_all.tsv`, same corpus, same code-column comparison): 1,853 / 1,853
— see "why the pre-fix number is misleading," below.

3 disagreements, all the same cause:

| package | Extron | post-fix `pkp_validate.py` |
|---|---|---|
| `extr_10_397_v1_0_4.pkp` | `0 Valid` | `80086 NoHash_NoGuid` |
| `extr_1_789_v1_0_2.pkp` | `0 Valid` | `80086 NoHash_NoGuid` |
| `extr_8_89_v1_0_0.pkp` | `0 Valid` | `80086 NoHash_NoGuid` |

**Classified: gap 1 (finding 16 §5c), confirmed resolvable, not a bug.** These
are the three pre-13.x packages whose `_resourceHashDict` is empty; Extron's
validator vouches for them entirely through the Guid fallback table
(`ExtronDH.dat`, committed as `guidtable.tsv`). `pkp_validate.py`'s
`guid_hash_table` parameter defaults to empty by design (finding 16's gap 1),
so without it every resource falls through to `NoHash_NoGuid` — an honest
"cannot verify," not a guess. Confirmed measured, not assumed: running these
same 3 packages through the identical snapshot **with** `guidtable.tsv` passed
as `guid_hash_table` returns `0 Valid, verified=True` for all three, and
nothing else in the run changes (matches finding 16 §5c: "changes nothing else
across the corpus," re-confirmed here for this triple specifically, not
re-measured across the full 1,853 in this pass).

**Why the pre-fix "1,853/1,853" is misleading, not better.** Finding 16 §5a
documents that an earlier revision of `pkp_validate.py` looked for the
`Manifest` **child asset** these 3 packages don't have, found nothing, and
returned `Valid` — "having verified zero resources." That bug is what made
`py_all.tsv` show 1,853/1,853 raw code-matches: the false `Valid` happened to
equal Extron's real `Valid`, by accident, not by the tool having actually
checked anything. The post-fix code no longer does that; it correctly reads
the pre-13.x layout (per finding 16 §5a, "the serialized `_manifest` field
**holds** the manifest" for these), finds no hash for each resource, and
reports `NoHash_NoGuid` honestly instead of a silent `Valid`. The raw
agreement count on this subset went **down** (1,853 → 1,850) because a bug
that was hiding a real, always-existing gap (gap 1) was fixed, not because the
tool regressed.

### Mutants — `extval/mutant_list.txt` (47) + `extval/case_list.txt` (6) = 53

(This is finding 16's "53 deliberate mutants" bucket exactly: 47 + 6 = 53.)

**Post-fix: 45 / 53 exact agreement.** Pre-fix (`py_mut.tsv` + `py_case.tsv`,
same comparison): 37 / 53. **+8 net.**

By list:

| list | post-fix | pre-fix | oracle N |
|---|---|---|---|
| `mutant_list.txt` (47) | 42/47 | 36/47 | 47 |
| `case_list.txt` (6) | 3/6 | 1/6 | 6 |

#### Verdicts that changed between pre-fix and post-fix (10 rows)

All 10 are the on-disk-`.eir`-name bypass, finding 16 §5b / the module's "gap
2." The pre-fix code required **both** the on-disk filename and the
serialized `_filename` field to end in `eir` before taking the bypass; the
post-fix code (already in the HEAD snapshot) keys the bypass **solely** on the
on-disk name, matching Extron's measured behavior (`LoadFromFile` overwrites
`Filename` with the on-disk name before `Validate` ever runs, so the
serialized field cannot matter).

| package | Extron | pre-fix | post-fix | now matches Extron? |
|---|---|---|---|---|
| `dsc_01_stale_script_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `dsc_03_bad_py_digest_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `smsg_01_stale_script_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `smsg_03_bad_py_digest_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `tesira_01_stale_script_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `tesira_03_bad_py_digest_ondisk.eir` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `case_UPPER.EIR` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `case_mixed.EiR` | `0 Valid` | `80085 MismatchHash` | `0 Valid` | yes |
| `case_bare_noDOT_xxxeir` | `loadnull` (no code) | `80085 MismatchHash` | `0 Valid` | **no** — still wrong, differently (see below) |
| `case_weir.weir` | `loadnull` (no code) | `80085 MismatchHash` | `0 Valid` | **no** — still wrong, differently (see below) |

The 6 `_ondisk.eir` mutants and 2 of the 6 `case_*` files went from a real
disagreement to a real agreement. `case_UPPER.EIR` and `case_mixed.EiR` are
the same fix. `case_bare_noDOT_xxxeir` and `case_weir.weir` also flipped their
*wrong* answer (`MismatchHash` → `Valid`) but remain disagreements, for the
reason below.

#### Remaining disagreements, all one cause (8 rows: 5 mutant + 3 case)

`empty.pkp`, `gzip_garbage.pkp`, `notgzip.pkp`, `trunc_16.pkp`,
`trunc_half.pkp` (mutant set), and `case_bare_noDOT_xxxeir`, `case_not.eirx`,
`case_weir.weir` (case set) — Extron's status for all 8 is `loadnull`:
`DriverFileAsset.LoadFromFile` returned **null** and `Validate` was never
called, so there is no Extron code to agree or disagree with.

**Classified: out of scope for this tool by design, unchanged pre- to
post-fix.** `pkp_validate.py` reimplements `Validate`, not `LoadFromFile` —
its own docstring says so verbatim (finding 16's gap 2 discussion: "`LoadFromFile`
accepts only `.pkp` and `.eir`... and returns null otherwise"). It has no
model of that extension allow-list and always attempts to parse+validate the
bytes it is given, regardless of the path's extension. Two different reasons
land in this same bucket:

- **`empty.pkp`, `gzip_garbage.pkp`, `notgzip.pkp`, `trunc_16.pkp`,
  `trunc_half.pkp`**: these DO have a `.pkp` extension (Extron's loader would
  accept the extension), but the bytes themselves are corrupt/truncated/not a
  readable stream. Extron's `LoadFromFile` (per the module's own gap-1 note,
  "returns null on failure, swallowing the reason") and `pkp_validate.py`'s
  `load_graph()` (which raises `PackageError` with a specific reason —
  `EOFError`, "empty input," "not a readable NRBF stream," etc., preserved in
  `Result.warnings`) reach the **same conclusion** — this file cannot be
  validated — by two different code paths that don't share a code number.
  `pkp_validate.py` reports its own sentinel, `UNVERIFIABLE`/`UNPARSEABLE`
  (`-2`, a repo-local value that can never collide with Extron's enum, by
  design), rather than inventing a fake `0`/`80085`/`80086`.
- **`case_bare_noDOT_xxxeir`** (no extension at all) and **`case_weir.weir`**
  (extension `.weir`) and **`case_not.eirx`** (extension `.eirx`): none of
  these three end in a bare `.pkp` or `.eir` extension, so Extron's loader
  refuses them before `Validate` runs (finding 16 §5b, "the reach is
  bounded"). `pkp_validate.py` has no extension gate and evaluates the graph
  regardless of the path's extension, so it reports whatever the eir-bypass +
  hash logic computes for a `.pkp`-shaped file at that path — `Valid` for the
  two whose on-disk name still ends in the literal 3 characters "eir"
  (`bare_noDOT_xxxeir`, `weir.weir`), `MismatchHash` for `case_not.eirx`
  (which doesn't).

None of the 8 is a code defect; all 8 are the same, already-documented scope
boundary (the module validates a parsed graph — it does not simulate
`LoadFromFile`'s file-extension gate), present identically before and after
the fixes under test here.

### m2/m3/m4/m5/m6, out/, b/, dirtest/, junk/ (C# `Mutate.cs` output, top level of `experiments/validator_differential/`)

**Not found by method X.** Searched: `README.md` (only prose-describes `b/` as
"the i20 transplant experiment that first showed a refreshed digest makes a
replaced script Valid" — no per-file verdict recorded there), every
`findings/*.md` (`grep` for `m2`, `m3`, `m4`, `m5`, `m6`, `dirtest`, `junk`
matches only `README.md`), and the directory tree itself (`ls` for
`*.tsv`/`*.txt`/`*.log`/`*.csv`/`*.json` at the top level and inside each of
these 9 directories — none exists; `b/dump.json` is a structural NRBF dump of
the *source* package before mutation, not a validator verdict). `Harness.cs`
(the tool that calls Extron's `Validate` and could have produced such a file)
takes no visible flag to write one, and `Mutate.cs` only prints `"wrote
<mutation>"` per file — neither leaves a verdict on disk for these 9
directories' ~80 files. **Excluded from this re-score**, per the task's own
"if their Extron verdicts are recorded anywhere" condition — none are.

### The "13 built" packages (finding 16's 1,853 + 13 + 53 = 1,919)

Not addressed here. This task named `all_pkp.txt`/`real_all.txt` (the 1,853)
and `extval/`'s mutant sets (the 53) as the sources to re-run; it did not name
where the 13 built packages (i20 deliverables, most likely, per finding 16 §4 —
"The i20 deliverables `20020`–`20023` all return `Valid`") or their recorded
Extron verdicts live, and a search of `experiments/validator_differential/`
turned up no third list/oracle file distinct from the two already covered.
**Re-running this bucket is unaddressed, not ruled out** — whoever owns
STATUS.md/finding 16 should confirm where those 13 verdicts are recorded
before folding a combined total back into the "1,919" figure.

## Combined total (1,853 + 53 = 1,906 — the part of finding 16's 1,919 this pass covers)

| | post-fix | pre-fix (same method) |
|---|---|---|
| shipping (1,853) | 1,850 | 1,853 |
| mutants (53) | 45 | 37 |
| **total** | **1,895 / 1,906 (99.4%)** | **1,890 / 1,906 (99.2%)** |

Net **+5** exact agreements overall, from two offsetting changes: **+8** from
the gap-2 (on-disk-`.eir`-name) fix landing correctly, **-3** from a masking
bug's fix in the shipping corpus turning 3 accidental raw matches into honest,
correctly-classified, guid-table-resolvable gaps (gap 1). All 11 remaining
post-fix disagreements (3 shipping + 5 mutant + 3 case) are classified above;
none is an unexplained gap, and none is a content bug in `Validate`'s
reimplementation.

## Where the data is

- `experiments/validator_differential/py_all_postfix.tsv` — this run's
  1,853-row result, same 5-column shape as `py_all.tsv`
  (`code\tname\tverified\tnwarnings\tfilename`), **filename only** in the last
  column (not the full path `py_all.tsv` used — no absolute path is written
  into committed output, per CLAUDE.md).
- The 53-mutant re-score (`py_mut_postfix` / `py_case_postfix` equivalents) is
  not saved as a separate committed file — this task's scope was the two files
  above plus this one — but every row that changed or still disagrees is
  tabulated in full above, by filename, with both verdicts.

## Addendum — 2026-09-23 (R38): the 8 `loadnull` rows now agree, 53/53

**R38.** The 8 remaining mutant disagreements above (`empty.pkp`,
`gzip_garbage.pkp`, `notgzip.pkp`, `trunc_16.pkp`, `trunc_half.pkp`,
`case_bare_noDOT_xxxeir`, `case_not.eirx`, `case_weir.weir`) were all the same
shape: Extron's `DriverFileAsset.LoadFromFile` returns null and `Validate` is
never called (`loadnull`, no code), while `pkp_validate.py` scored them as
`UNPARSEABLE` (-2) or a real hash verdict instead of representing "Extron
never looked" at all.

### What changed in `tools/pkp_validate.py`

A new, distinct, repo-local sentinel, `REFUSED_BEFORE_VALIDATE = -3`
(negative, consistent with `UNVERIFIABLE = -1` / `UNPARSEABLE = -2` — never
collides with the real `0`/`80085`/`80086` enum), returned by `validate()` in
exactly the two shapes the oracle files measured, and *only* those two — see
`pkp_validate.py`'s new docstring gap (9) for the full reasoning:

- **Extension gate (gap 9a).** The on-disk name's extension must be exactly
  `.pkp` or `.eir`, case-insensitively (`os.path.splitext`, not a bare
  3-character suffix test — that is Validate's separate `EndsWith("eir")`
  bypass, gap 2, applied *after* this gate, not the same check). Checked
  against the on-disk name before `load_graph()` is ever called. Pinned by the
  3 refused / 3 accepted `case_*` siblings, which are otherwise
  content-identical in shape (`case_bare_noDOT_xxxeir` / `case_not.eirx` /
  `case_weir.weir` all `loadnull`; `case_UPPER.EIR` / `case_mixed.EiR` /
  `case_clean.eir` all load and take the eir bypass).
- **Content gate (gap 9b).** A new `PackageError` subclass, `ContentUnreadable`
  (so existing `except PackageError` callers, and `load_graph()`'s own
  docstring promise, are unaffected), raised for exactly the parse failures
  already being detected — empty input, a corrupt gzip container, a stream
  that is not readable NRBF, one that never reaches a `MessageEnd` record —
  and reported as `REFUSED_BEFORE_VALIDATE` instead of `UNPARSEABLE` when
  `validate()` catches it. A file that cannot even be *opened* (missing,
  permission denied) is unaffected: it stays plain `PackageError` /
  `UNPARSEABLE`, since that is a filesystem-level failure, not one of the 5
  measured `loadnull` content shapes, and the existing test asserting this
  (`test_bad_input_fails_loudly`, "a missing file is Unparseable, not a
  crash") was kept passing unchanged.

**Left unimplemented, as open questions (not pinned by any oracle mutant):**
whether a well-formed NRBF stream that deserializes to something other than
`DriverFileAsset` is also swallowed to null by `LoadFromFile` (plausible, by
the same "returns null on failure" pattern CLAUDE.md's methodology notes
describe, but untested — `load_graph()` still raises plain `PackageError` for
"no root object" / "root is not DriverFileAsset", not `ContentUnreadable`);
and whether the extension gate is exactly `Path.GetExtension()` equality
(what is implemented, and what the 6 case-mutants pin) or something looser at
the edges (e.g. trailing whitespace in the name) that no mutant probes.

### Method

Same corpus as the original run: `experiments/validator_differential/extval/`
`oracle_mut.tsv` (47 rows) + `oracle_case.tsv` (6 rows) = 53, read directly
(these two files were already re-scored in the main run above) against the
actual committed mutant files under `extval/mutants/` — no oracle re-capture
needed, Extron's verdicts don't change; only the Python side changed. Unlike
the wire_table.py / pkp2cs.py callers this task's harness warned about,
`pkp_validate.py` has no cross-module import onto files other sessions were
concurrently editing (it imports only `tools/pkp_dump.py`), so this run reads
the worktree's own edited copy directly — no snapshot needed. Runner:
`rerun_mutants.py` (private tmp dir, not committed) reads both oracle TSVs,
maps `path`'s basename onto `extval/mutants/<name>`, calls
`pkp_validate.validate()`, and classifies a `loadnull` oracle row as agreement
when the Python code is `REFUSED_BEFORE_VALIDATE` — the sentinel exists
exactly to represent "Extron never called Validate," so that correspondence
*is* the agreement, not a coincidental numeric match (there is no numeric
match to have; `loadnull` carries no code).

### Result

**53 / 53 exact agreement, 0 disagreements** (up from 45/53; the fix landed
exactly the 8 rows it targeted, nothing else moved):

| list | agreement |
|---|---|
| `mutant_list.txt` (47) | 47/47 |
| `case_list.txt` (6) | 6/6 |
| **total** | **53/53** |

The 1,853-package shipping corpus was not re-run here — none of those files
exercise either gate (all are valid gzip streams named `*.pkp`), so R9's
1,850/1,853 (gap 1, unrelated to R38) stands unchanged. Combined with R9's
unaffected shipping figure, the 1,906-row total this doc tracks moves from
1,895/1,906 (99.4%) to **1,903/1,906 (99.9%)** — the only 3 remaining
disagreements anywhere in this doc's scope are the pre-13.x, Guid-only
shipping packages (gap 1), which are resolvable by passing `guidtable.tsv`
(finding 16 §5c) and were never counted as a code defect.

### Tests

`tools/test_pkp_validate.py` gained test `[12b]` (33 checks: both gates
against the real committed mutant files, the accept-side siblings, synthetic
edge cases for `_loadable_extension`, the "gate is the name not the content"
cross-check, the no-filename-known case, and the missing-file regression
check) plus two additions to `[1]`. Full suite, run after the fix:
**182 passed, 0 failed, 182 total** (`py -3.11 -u tools/test_pkp_validate.py`)
— every pre-existing test still passes; default behavior for ordinary
packages (all 9 samples in `samples/`, all Valid) is unchanged.
