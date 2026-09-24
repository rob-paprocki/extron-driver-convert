# Corpus sweep (ROADMAP R15)

A sweep of **all 1,854** `.pkp` packages in `corpus/extron-driver3/` — no
sampling, nothing skipped. Six independent measurements over untested paths;
each is described below with what was actually measured, what method found
it, and what is inferred rather than directly observed.

Run with `experiments/corpus_sweep/sweep.py`; raw output in
`experiments/corpus_sweep/sweep_results.json`. Unit tests for the analyzers
against synthetic snippets are in `experiments/corpus_sweep/test_sweep.py`
(29 checks, all passing).

## Method, common to all six items

- Every `.pkp` in `corpus/extron-driver3/` is visited (`os.listdir`, filtered
  to `*.pkp`) — 1,854 files, matching the count ROADMAP.md's R15 row cites.
  Nothing is sampled; a package that fails to parse is counted and reported,
  never silently dropped.
- Item 1 uses `tools/pkp_build.PackageBuilder`, whose constructor performs
  the real round-trip gate (parse the donor, rebuild it, compare
  byte-for-byte) and raises on any mismatch.
- Items 2-6 use a **separate, lighter** parse
  (`pkp_validate.load_graph`, backed by `pkp_dump.PkpParser`) so that a
  round-trip failure in item 1 — a question about the NRBF *writer* — does
  not also blind items 2-6, which only need a *reader*. (In the event, item
  1 had zero failures, so this separation did not end up mattering for this
  run — but it means items 2-6 are not conditioned on item 1's outcome.)
- Embedded scripts are extracted with `tools/pkp_build.PackageBuilder`'s own
  `scripts()` method, called unbound against a plain object holding just the
  lightweight parse's `objects` dict (that method only touches
  `self.objects`), so extraction works even for a donor that fails item 1's
  round-trip. This is read-only use of `tools/`; nothing here mutates or
  reserializes a package, and no sample or corpus file was modified.
- Items 3-6 are `ast`-based scans over each script's source text. A script
  that does not even parse under Python 3's grammar would be counted and
  reported under `unparseable_scripts`, never silently dropped — none did
  (see §0).
- **Concurrent-edit safety.** `tools/pkp2cs.py` and `tools/pkp_validate.py`
  were being edited by other agents (R37, R38) in this worktree while this
  ran. The numbers below were produced with `CORPUS_SWEEP_SNAPSHOT_DIR`
  pointed at fixed copies of exactly those two files, taken from
  `git show HEAD:tools/pkp2cs.py` and `git show HEAD:tools/pkp_validate.py`
  at commit **`45622ef`** ("Loopback rig for 20028 / v1.6: the listener
  answers every new inquiry"). `tools/pkp_dump.py`, `tools/pkp_build.py` and
  `experiments/nrbf_writeback/nrbf_write.py` were not being touched by any
  concurrent edit, so they were read live from the tree. `sweep.py` resolves
  the snapshot directory (if set) ahead of the live `tools/` dir on
  `sys.path`, so this is reproducible against any future commit by re-running
  with a fresh snapshot — see the script's own module-resolution comment.
- Full run: 1,854/1,854 packages, 3,621 seconds (~60 minutes), 0 unexpected
  exceptions, 0 unparseable scripts, 0 light-parse failures.

## 0. What did NOT fail

Two of the six items came back clean across the whole corpus — reported here
first because "0 hits" is itself the answer to a specific open question, not
an absence of data:

- **Round-trip (item 1): 1,854/1,854 succeeded, 0 failures.** Every package
  in the corpus reproduces byte-for-byte through
  `pkp_build.PackageBuilder`'s parse/rebuild/compare gate. Not found by this
  method: any package that fails the round-trip gate.
- **No-Manifest-child (item 2): 0/1,854.** Every package has exactly one (or
  more; see below) child asset named `"Manifest"` — `pkp_validate.py` gap 4's
  "auto-created empty Manifest" branch was never exercised. Not found by this
  method: a package with no Manifest child asset. (This does not settle gap
  4 itself — gap 4 is about what `get_Manifest()`'s IL does on an *absent*
  child, which this corpus still does not contain an instance of; it settles
  only that the corpus supplies no such instance to test against.)
- **Light parse failures: 0/1,854**, and **unparseable embedded scripts:
  0/2,081** — every package's graph reads cleanly under `pkp_dump.PkpParser`,
  and every embedded script parses under Python 3's grammar. (This is itself
  informative for item 5's Python-3.5 question: nothing in the corpus uses
  syntax `ast.parse` under a modern CPython refuses outright, e.g. a bare
  Python-2 `print` statement.)

The corpus contains **2,081 embedded `.py` scripts** across the 1,854
packages (a package can carry more than one, e.g. per-transport variants).

## 1. Emulated pre-writes embedded inside a larger expression

**Pervasive — 2,416 hits across 1,685 of 1,854 packages (90.9%).**

`tools/pkp2cs.py`'s `gc-dual-status-emulated-prewrite-dropped` rule strips a
call of the shape `self.Write<X>(<args>, 'Emulated')` (GC's dual-status
pre-write bookkeeping) — but only when that call is the **entire value of a
standalone expression statement**. The rule's own comments (around the R37
`ReadMultiviewString` note) name the gap: a call carrying the same literal
`'Emulated'` context argument, sitting anywhere else in an expression —
assigned to a variable, passed as an argument, tested in a condition — is
untouched, and survives translation as a dangling reference to a wrapper
method that per-command-wrapper-deletion rules elsewhere have already
removed.

This sweep found that gap is not a corner case — it is the majority shape:

| by call target | hits |
|---|---:|
| `ReadUserDefinedString` | 1,812 |
| `ReadDelayTime` | 46 |
| `ReadDialString` | 30 |
| `ReadFadeTime` | 30 |
| `ReadInput` | 14 |
| `ReadMultiviewString` | 12 |
| `ReadMatrixIONumberSelect` | 9 |
| `ReadMatrixIONameString` | 9 |
| ...31 more names, 1-8 hits each | 254 |

| by syntactic position (AST parent of the call) | hits |
|---|---:|
| `Assign` (`x = self.Read<X>(..., 'Emulated')`) | 2,334 |
| `Call` (passed as an argument) | 29 |
| `List` / `Dict` / `Subscript` (inside a literal) | 30 |
| `Compare` / `BoolOp` / `If` (inside a condition) | 22 |
| `ListComp` | 1 |

The overwhelming shape is `Assign` — exactly the `ReadMultiviewString`
example pkp2cs.py's own comment names, just far more common than that one
citation suggested. Example: `1bynd_19_20024_v1_0_0.pkp`'s
`_1bynd_19_4743.py`, method `_cmd_SetUserDefinedCommand`:
`ReadUserDefinedString(..., 'Emulated')` assigned to a local, never a
standalone statement.

Method: `ast.parse` each script, walk for `Call` nodes matching
`pkp2cs._call_attr(node)` starting with `Write` or `Read` (excluding the
three generic dual-status accessors `WriteStatus`/`WriteStatusHelper`/
`WriteDeviceResponseStatus`/`ReadStatusHelper`, which pkp2cs.py already
drops unconditionally elsewhere) where `pkp2cs._has_emulated_context(node)`
is true, then check whether the call's immediate parent is an `Expr`
statement whose `.value` *is* that call. If not, it is embedded. This reuses
`tools/pkp2cs.py`'s own two helper predicates (from the pinned snapshot)
rather than re-implementing the shape test.

**What this does NOT show:** whether pkp2cs.py's current translator actually
emits a dangling reference for each of these 2,416 sites in its *output* —
that depends on whether the corresponding `Read<X>`/`Write<X>` wrapper
definition is *also* deleted for that specific package (which depends on
`_is_write_read_wrapper` and the R37 "referenced elsewhere" tracking this
sweep did not re-run). What this sweep measures is the precondition — how
often the shape the generic rule doesn't reach actually occurs in real
packages — not the post-translation defect count.

## 2. Runtime-injected globals beyond `ExtronTime`

**`ExtronTime` itself: 0 corpus-wide bare-global hits — every script that
uses it also defines `class ExtronTime(float): pass` itself.**

Finding 13 §5 reported (from one sample) that the embedded i20 driver "uses
`ExtronTime` 7 times as a bare name" while "importing only `BaseDriver`,
`time` and `struct.pack`," concluding the GC runtime populates module
globals beyond the driver's own imports. This sweep's flat whole-script
name-binding scan (below) never flags `ExtronTime` as unbound, in any of the
2,081 scripts. Spot-checking the packages finding 13 concerns
(`1bynd_19_20024_v1_0_0.pkp`'s `_1bynd_19_4743.py`, and the older sample
`samples/1 Beyond Cameras/AutoTracker3/pkp/1bynd_19_4741_v1_0_1.pkp`) by hand
confirms why: both, like every other `ExtronTime`-using script checked, carry

```python
class ExtronTime(float):
    pass
```

as an ordinary module-level class definition near the end of the file — not
gated by a `try`/`except ImportError` fallback, just a plain definition. So
`ExtronTime` is not, in this corpus, evidence of runtime-injected globals;
it is a locally-defined trivial `float` subclass, present in every script
that references it. **This narrows finding 13 §5's claim** — it does not
disprove that GC injects *something*, but `ExtronTime` specifically is not a
corpus-wide example of it, and the specific package finding 13 quoted from
does define the class locally when read directly. (Flagging this for the
finding, not editing it — see the parent report's doc_notes.)

One package's copy of this exact boilerplate is itself broken in a way that
directly corroborates the *general* runtime-injected-global question, just
not via `ExtronTime`:

- **`extr_31_1626_v1_0_5.pkp`**, `extr_31_1626_serial.py`, line 341: the
  standard `__StatusItems` dual-status helper reads
  `isinstance(dictionary['Live'], datetime)` — `datetime` is never imported
  (only `import time`) and no local `datetime` is defined anywhere in the
  script. Every other package carrying this same boilerplate method uses
  `ExtronTime` at this exact position and defines it locally (see above); in
  this one package the name was seemingly typo'd/mis-substituted to
  `datetime` during generation, producing a genuine bare, undefined,
  runtime-crashing name at the one place in the whole corpus this class of
  bug was measured to occur.

### The other candidates: real bugs, not runtime injection

The flat scan (below) found **7 distinct bare-name candidates, 27
occurrences total**, none of them `ExtronTime`. Every one, hand-verified
against its source, is a genuine dangling-reference bug in a shipped Extron
driver — an `AttributeError`/`NameError`-class defect of exactly the shape
CLAUDE.md's methodology notes warn about ("26 dangling `self.X()`
references hid behind a near-perfect scorecard"), except for bare globals
instead of `self.` attributes:

| name | occurrences | package(s) | what it is |
|---|---:|---|---|
| `recorder_idindex` | 12 | `pano_43_4116_v1_4_0.pkp` | typo for the in-scope `recorder_id` inside three `except (KeyError, IndexError):` handlers — the error-recovery path itself raises `NameError` |
| `Self` | 9 | `extr_15_69_v1_1_1.pkp`, `extr_17_75_v1_1_1.pkp` | typo for `self` in `Self.Discard('Invalid Command')` |
| `seld` | 2 | `extr_2_17_v1_1_1.pkp` | typo for `self` in `seld.Discard('Invalid Command')` |
| `error_code` | 1 | `extr_2_112_v1_1_0.pkp` | `self.Error(['{0}: {1}'.format(sourceCmdName, error_code)])` — no `error_code` is ever assigned in `__CheckResponseForErrors`; looks like it should have been the matched `DEVICE_ERROR_CODES` entry |
| `datetime` | 1 | `extr_31_1626_v1_0_5.pkp` | see above — the `ExtronTime`-shaped boilerplate with the name swapped |
| `matchstring` | 1 | `extr_31_247_v1_0_4.pkp` | `self.MatchStrings(matchstring)` — should be `match.group('matchstring')` (used correctly two lines earlier for the `'mode'` group) |
| `exceptions` | 1 | `senn_31_5578_v1_0_5.pkp` | `raise exceptions.DataOverflowError(...)` inside what reads as a vendored QR-code-encoding routine; no `exceptions` module is imported (and Python's real stdlib has no such attribute on any `exceptions` module in the first place — this looks like a fragment of a third-party QR library whose own `exceptions.py` never made it into the embedded script) |

Every one of these would raise at runtime **only if that code path is
actually exercised** — this sweep is static, so it does not (and cannot)
show whether any of the seven has ever fired on real hardware, only that
each is unconditionally reachable dead code waiting to happen.

**Method** (see `sweep.find_bare_globals` / `_collect_bound_names`): a
**flat, whole-script** name-binding scan, deliberately not a per-scope
(LEGB) analysis. It collects every name bound *anywhere* in the script —
assignment targets, `def`/`class` names, function parameters, import names,
`except ... as`, `global`/`nonlocal` declarations — into one set, then flags
any `Name` used in `Load` context that is in neither that set, `dir(builtins)`,
nor `{'self', 'cls'}`, nor a short list of implicit module dunders
(`__name__`, `__file__`, ...). This is a **deliberately conservative**
choice: a flat set can only ever *under*-report (a same-named local bound in
some unrelated method could mask a genuine bare-global use elsewhere in the
same script), never invent a false positive out of ordinary lexical scoping
that a precise LEGB analysis would correctly resolve. A script using
`from X import *` is excluded entirely (0 found in this corpus) rather than
guessed at, since a star import can bind anything.
**What this does NOT show:** a name bound somewhere unrelated in a script
could mask a real bare-global use elsewhere in the same script (the
under-report direction above) — so 27 is a floor, not a ceiling, for this
specific method. It also does not show whether GC's runtime actually injects
any of these names (only that the *script* never defines/imports them);
confirming that would need the same GC-side reading finding 13 §5 used.

## 3. Newest Python syntax feature per script (the "Python 3.5" question)

**Zero.** Across all 2,081 embedded scripts, not one AST node matched any of
the nine syntax markers checked, all of which require Python later than 3.5:

| feature | min. version | scripts using it |
|---|---|---:|
| f-strings (`ast.JoinedStr`) | 3.6 | 0 |
| variable annotations (`ast.AnnAssign`) | 3.6 | 0 |
| underscore numeric literals (tokenizer scan) | 3.6 | 0 |
| async comprehensions (`is_async` comprehension) | 3.6 | 0 |
| async generators (`yield` inside `async def`) | 3.6 | 0 |
| walrus (`ast.NamedExpr`) | 3.8 | 0 |
| positional-only params (`posonlyargs`) | 3.8 | 0 |
| `match` statement | 3.10 | 0 |
| `except*` | 3.11 | 0 |

This is corpus-wide **positive evidence for**, not proof of, Python-3.5
safety: ROADMAP.md's H1 row previously had only "f-string lint" behind this
question for a handful of files; this closes it to 0/2,081 across the whole
corpus for nine specific syntax shapes. Ordinary `async def`/`await`/`async
with`/`async for` (PEP 492, itself a 3.5 feature) is not flagged — flagging
it would over-count, since 3.5 already has it; only the strictly-newer
async-*comprehension*/async-*generator* shapes (3.6, PEP 525/530) are
checked for.

**What this does NOT show:** a script could still use a post-3.5 standard
library name, builtin, or method (e.g. `dict.__or__`/`|` merge, `str.
removeprefix`, an `os.PathLike` argument) that leaves no distinctive AST
node — this method is a **syntax**-shape scan only, not a name-resolution or
stdlib-surface check. "0 hits" means these nine specific markers are absent,
not that every script is provably interpretable by a genuine Python 3.5.

### A discovered, unrelated version number: `minimumVersion`

224 of 2,081 scripts (10.8%) — the `Extron2.HTTPDriver`-based ones, by
inspection — declare a module-level `minimumVersion = (…)` tuple, compared
against `version = tuple(int(i) for i in Version().split('.'))` (`Version`
imported `from Extron import Version`) with a guard like:

```python
if platform == 'Pro' and version < minimumVersion:
    initError.append('Minimum API version not met. Needs to be >= 2.8.5')
```

| declared value | scripts | example package |
|---|---:|---|
| `(3, 4, 6)` | 117 | `1bynd_42_4279_v1_0_11.pkp` |
| `(2, 8, 5)` | 95 | `atna_15_5339_v1_0_4.pkp` |
| `(1, 5, 4)` | 8 | `extr_31_17022_v1_0_1.pkp` |
| `(2, 6, 6)` | 1 | `extr_12_3042_v1_9_1.pkp` |
| `(3, 1, 8)` | 1 | `extr_31_203_v1_0_6.pkp` |
| `(2, 7, 22)` | 1 | `extr_31_3180_v1_0_2.pkp` |
| `(1, 8, 21)` | 1 | `extr_50_17089_v1_0_5.pkp` |

**This is Extron's own `Extron2` driver-API version, not the Python
interpreter version** — confirmed by the error message text above
("Minimum API version not met") and by the value set itself: `(2, 8, 5)`
has no corresponding CPython 2.x release (Python 2 never reached a 2.8), so
these cannot be read as Python version floors. Recorded because it surfaced
during the syntax scan and is a real, self-declared, per-script version
number worth not confusing with the Python-3.5 question — but it answers a
different question (minimum `Extron2` API, i.e. minimum GC/firmware
generation) than the one it was found while looking for.

## 4. `configs[...]` keys read in `__init__`, and the R22 model question

ROADMAP R22 asks: *is a `.pkp` script ever told which model it runs as?*
Measured, corpus-wide, rather than "not found in two":

**No. Across all 2,885 `__init__(self, configs, ...)` definitions in the
corpus (every class whose `__init__` takes a `configs` parameter — driver
classes and driver-model subclasses alike), zero `configs[...]` keys and
zero extra `__init__` parameters carry anything model-shaped.**

| `configs[...]` key read in `__init__` | occurrences |
|---|---:|
| `Unidirectional` | 4,173 |
| `CommandPacing` | 2,081 |
| `ResponseTimeout` | 2,081 |
| `DriverParams` | 1,125 |
| `DriverCredentials` | 553 |
| `ConnectionType` | 304 |
| `Interface` | 111 |
| `HTTPParams` | 100 |
| `Params` | 48 |
| `ssl_wrapping` | 8 |
| `Host` | 2 |
| `DriverType` | 1 |

None of these twelve keys is model-shaped, and `find_model_signals`'s
case-insensitive `"model"` search over every `configs[...]` key in the
**whole** script (not just `__init__`) found **zero** `configs["Model"]`-type
accesses anywhere in the corpus. **Extra `__init__` parameters beyond
`(self, configs)`: 0/2,885.** Not found by this method: any `configs` key or
`__init__` parameter that would tell a script its model.

**But the model is not unknown to the code — it's compiled in per subclass.**
233 `self.<attr>`-shaped "model" signals (24+ distinct attribute spellings —
`Model`, `model`, `ModelType`, `ModelNo`, `__MatchModelName`, `WriteModelName`,
...) exist across the corpus, and two hand-checked examples show the actual
mechanism:

```python
# extr_2_195.py
class extr_2_195_MLS100(extr_2_195):
    def __init__(self, configs):
        self.model = '100A'
        super().__init__(configs)

class extr_2_195_Other(extr_2_195):
    def __init__(self, configs):
        self.model = 'Other'
        super().__init__(configs)
```

```python
# shur_25_2299.py
class shur_25_2299_310(shur_25_2299):
    def __init__(self, configs):
        self.ModelNo = '310'
        ...
        super().__init__(configs)

class shur_25_2299_910(shur_25_2299):
    def __init__(self, configs):
        self.ModelNo = '910'
        ...
        super().__init__(configs)
```

i.e. **Extron ships one subclass per model**, each hardcoding its own model
tag as a literal assignment *before* calling `super().__init__(configs)` —
the base class's methods then branch on `self.model`/`self.ModelNo`. Which
subclass GC instantiates for a given catalog/asset entry is therefore how
the script "learns" its model — not data flowing through `configs`, and not
a constructor argument. (Other `self.<model-attr>` signals, e.g.
`__MatchModelName`/`WriteModelName`, are a *different* mechanism — regex-
matching a device's own identify response at runtime and pushing the
discovered name to status, i.e. the driver asking the *device*, not GC
telling the driver; not conflated with the hardcoded-subclass mechanism
above.)

**Method:** `ast.walk` each script for `def __init__` whose parameter list
contains `configs` (filtering out unrelated helper classes in the same
script that happen to define their own `__init__`, e.g. a text-scroller
utility observed early in testing); within that function, collect the
top-level string key of every `Subscript` on a bare `Name` `configs`
(`configs['DriverParams']['SSL Verify Mode']` records `'DriverParams'`, not
the nested key — a i test in `test_sweep.py` pins this). Separately,
`find_model_signals` scans the *whole* script (not just `__init__`) for any
`configs[...]` key or `self.<attr>` whose text contains `"model"`
case-insensitively. **What this does NOT show:** whether GC passes a model
identifier through some *other* channel entirely outside `configs` and the
constructor signature (e.g. environment/global state set before
`__init__` runs) — this sweep only checks what the script's own source can
see. The per-model-subclass mechanism above was confirmed by hand-reading
two example packages, not for all 233 signal occurrences.

## Reproducing

```
python3 experiments/corpus_sweep/sweep.py --out experiments/corpus_sweep/sweep_results.json
python3 experiments/corpus_sweep/test_sweep.py
```

Both are standard library only. `sweep.py` takes 50-70 minutes over the full
corpus (dominated by item 1's round-trip gate, which parses, rebuilds and
byte-compares every package); `--limit N` runs a quick subset for iteration.
Set `CORPUS_SWEEP_SNAPSHOT_DIR` to pin `pkp2cs.py`/`pkp_validate.py` to a
specific commit's copies when other agents are mid-edit on those two files;
see the "Concurrent-edit safety" note above.
