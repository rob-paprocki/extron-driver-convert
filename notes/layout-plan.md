# Layout plan

Which files should move so a first-time visitor finds their way, and exactly
how. Nothing here has been moved yet; this is the plan (ROADMAP R51). It was
written from a reference count of every path, on 2026-11-02.

## Move

### 1. `experiments/cip-ipid-survey/*.tsv` into `experiments/cip-ipid-survey/joins/`

The folder opens on GitHub as 47 TSV files ahead of the two documents that
explain them. After the move it shows `README.md`, `WORK-SUMMARY.md` and one
data folder. `out/` would be the wrong name, because `experiments/README.md`
says `out/` is regenerable and these were extracted by a script that is not
in the repo.

No code, test, manifest or `public_sync.py` rule names these files.

1. `git mv experiments/cip-ipid-survey/*.tsv experiments/cip-ipid-survey/joins/`
2. `experiments/cip-ipid-survey/README.md`: the line saying "27 TSVs ... under
   this directory" becomes "the TSVs, one per non-empty symbol surveyed, under
   `joins/`". The count was stale; there are 47.
3. Commit the rename on its own, so git records 100% renames.

### 2. `tools/out/verdicts/` into `evidence/verdicts/`

`tools/` is where a visitor looks for what to run, and `out/` reads as build
output; `.gitignore` says so. Yet `verdicts/` holds the one thing in `tools/`
that cannot be regenerated: the syntheses the findings were written from.
`evidence/` already exists for exactly that, raw artefacts the findings cite.

**`tools/public_sync.py` must change in the same commit.** Its `EXCLUDE` list
names `tools/out/verdicts/workflows/`. If the folder moves and that line does
not, the public build publishes the raw run records.

1. `git mv tools/out/verdicts evidence/verdicts`
2. `tools/public_sync.py`: the `EXCLUDE` entry becomes `"evidence/verdicts/workflows/",`
3. `tools/test_public_sync.py`: the four `tools/out/verdicts/...` paths in the
   exclude test become `evidence/verdicts/...`
4. `.gitignore`: delete the "EXCEPTION: tools/out/verdicts/" comment and the
   two `!tools/out/verdicts` lines. Keep `tools/out/*`.
5. In the documents that cite the folder, replace `tools/out/verdicts/` with
   `evidence/verdicts/`: `ROADMAP.md`, findings 02, 07, 10, 11 and 19, and
   `notes/2026-09-pack-up.md`. Check each line by eye; some name only the
   folder.
6. Do not rewrite the recorded run output under `evidence/verdicts/workflows/`.
   It quotes the old path as provenance.
7. `tools/README.md`: drop its `out/verdicts/` section. `evidence/README.md`:
   add a `verdicts/` section, and add `verdicts/workflows/` to its "Not in the
   public copy" paragraph. `evidence/verdicts/README.md`: retitle it and add a
   sentence saying the folder moved.

The public repo has served these files at the old path, so any outside link to
them will break. Nothing inside the repo or on the Pages site links one.

### Order and checks

Move 1, then move 2, as separate commits. Then:

```bash
python tools/test_public_sync.py
python tools/verify_vendor_files.py
git grep -n -I 'tools/out/verdicts' -- . ':!evidence/verdicts/workflows'   # expect nothing
git ls-files experiments/cip-ipid-survey/joins | wc -l                       # expect 47
git fetch https://github.com/rob-paprocki/extron-driver-convert.git main:public-main
python tools/public_sync.py build --archive HEAD --public public-main
git ls-tree -r --name-only public-next | grep -c 'evidence/verdicts/workflows'   # expect 0
python tools/public_sync.py check public-next
```

Then the rest of the suites as `ENVIRONMENT.md` lists them.

## Optional

Delete the `.gitkeep` files under `samples/`. On GitHub `samples/` opens as six
folders of empty-looking subfolders, which suggests something is missing. The
folders themselves cannot move, because `vendor-files.manifest.tsv` pins the
files inside them. The tests that walk `samples/` tolerate a missing folder,
and `tools/verify_vendor_files.py` names any missing path for someone placing
their own copies. Steps: `git rm` every `samples/**/.gitkeep`; in `.gitignore`,
update the comment about them and remove the `.gitkeep` exception; reword
`samples/README.md` to say only the README is tracked. The gain is cosmetic.

## Stays, and why

| path | why it stays |
|---|---|
| `STATUS.md` | The central document, and `CLAUDE.md` sends agents to it first. Moving it touches over fifty lines, including `convert.py`'s printed help. `docs/` is the Pages source, so a `.md` moved there would be published on the site. |
| `ROADMAP.md` | The live to-do list, and the README already tells visitors they can skip it. `notes/` would mislabel it; `docs/` would publish it. |
| `ENVIRONMENT.md` | The run-it document that the README and `tools/README.md` point to by this path. |
| `vendor-files.manifest.tsv` | `public_sync.py` reads it as the list of vendor paths the public build must not contain, and `manifest_paths()` returns an empty list when the file is missing. A checkout of the old script against the new tree would pass the vendor-leak check silently. |
| `samples/`, `corpus/` | The manifest pins every vendor file under them, and findings 14, 16 and 17 depend on those exact paths. |
| the `scratch/` folders in `experiments/` | Each is documented in its parent README. The UI Automation chain in `gcp_harness/scratch/` is due to be folded into one script (ROADMAP), and `oracle_pairs/scratch/` has code that computes the repo root from its depth. |

## Who this affects

- Any other machine with unpushed work on these paths will see rename
  conflicts on its next pull.
- Decide whether outside links to `tools/out/verdicts/*.md` in the public repo
  matter. Nothing in the repo links them.
