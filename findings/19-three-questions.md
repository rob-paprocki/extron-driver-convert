# Finding 19 — three questions: generating from a Crestron package, filling a `.pkp`'s gap, and generating from docs alone

Three small, targeted experiments, each answering one narrow question the
rest of the project's findings don't: can the translator run **into**
ControlScript from Crestron (`experiments/crestron2cs/`), can it fill in a
`.pkp` script Extron never shipped as a standalone module
(`experiments/missing_ethernet/`), and can a module be generated from
documentation with the implementation withheld (`experiments/docs_only/`)?
Their write-up existed only as `tools/out/verdicts/three_questions_synthesis.md`
(recovered 2026-09-11, per ROADMAP R4/D9) until now; this finding records it,
independently re-checks its headline numbers against the experiments' own
output files, and traces the one residual the synthesis left unexplained.

None of the three experiment directories contains a README or report file of
its own — the synthesis and the raw output artifacts are the only record.

## 1. Crestron `.pkg` → ControlScript `.py`: works end-to-end (`experiments/crestron2cs/`)

`experiments/crestron2cs/crestron2cs.py` resolves the Samsung IP `.pkg`'s
LegacyWrappers Template/Transformation/Rule graph and emits
`experiments/crestron2cs/out/generated_controlscript.py`. Re-run today:
`wire_table.extract_table` on it returns **62 commands, 0 opaque markers** —
independently reproduced against the committed output file, matching
`tools/out/verdicts/three_questions_synthesis.md` exactly.

The synthesis's "14/14 unit tests pass" matches the test file as it stood when
this was written up (14 `def test_` methods; later work adds more).

Name-keyed diffing is the wrong oracle here — only `Power` and `Volume` share
identifiers, because the generator mirrors Crestron's atomic command
granularity rather than Extron's editorial grouping. Method-keyed comparison
(`experiments/crestron2cs/out/semantic_comparison.json`) is the real picture:
**17 distinct JSON-RPC methods, 8 in both, 8 Crestron-only, 1 Extron-only.**
Of the 8 shared, `powerControl`, `muteControl`, `inputSourceControl` and
`channelUpDnControl` report identical value domains; `directVolumeControl`
matches on the Set direction; `remoteKeyControl`'s 19 Extron values are a
proper subset of Crestron's 30. The remaining two diverge for reasons that
are not translation errors: `createAccessToken` differs only in id policy
(Crestron's manifest declares `MonotonicIntegerId` 1–127; Extron hardcodes
`'id': 1`), and `multiviewControl` reflects two commissioning models
(Crestron hardcodes `My Multi View 1/2/3`; Extron reads an installer-set
free-text status).

The one Extron capability with no Crestron counterpart —
`pictureSizeControl`/AspectRatio — is blocked by a bug in **Crestron's own
manifest**: exactly 1 of 77 `Commands[]` entries (`SetVideoConfiguration`)
spells the key lowercase `info`, so `GetVideoConfiguration` is silently
orphaned. That is a dead command as authored, not a protocol gap.

**Remaining work, per the synthesis:** the emitted module is a measurement
artifact, not a driver. Crestron's Rule engine is not executed —
`CommandSequence` chains, `NeedsPowerOn`/`RequireAccessToken` blocking rules,
and response-routing/`WriteStatus` plumbing are unimplemented (only the 6×
WakeOnLan-before-power-on rule was folded in explicitly), and nothing
measures whether the runtime behaviour is right, since `wire_table` only
inspects request construction.

## 2. The `.pkp`'s missing Ethernet module: 11/11 commands, one dangling reference (`experiments/missing_ethernet/`)

`pkp2cs.discover_jobs()` on the Samsung `.pkp` returns exactly two jobs
(serial, 6 models; ethernet, 6 models — Extron never shipped this ethernet
script as a standalone ControlScript module). `translate_job()` needed **zero
changes to `tools/`**: the HTTP dialect path built for Automate VX detected
`Extron2.HTTPDriver` and emitted the module directly, and it compiles under
`py_compile`.

Diffing the generated module against the `.pkp`'s own embedded script —
independently re-run today with `wire_table.extract_table`/`diff_tables`,
reproducing `experiments/missing_ethernet/wire_diff.json` exactly —
gives `only_in_a: []`, `only_in_b: ['ConnectionStatus']` (boilerplate Extron
itself injects), **11 shared, 1 difference (`MultiviewCommand`)**.
AspectRatio, AudioMute, ChannelStep, Input, Keypad, MenuNavigation,
MultiviewString, Power, RefreshToken and Volume are wire-identical including
the `createAccessToken` handshake.

**The one defect is real and reproducible.** `experiments/missing_ethernet/smsg_10_6738_ethernet.generated.py:135`
calls `self.ReadMultiviewString(qualifier, 'Emulated')`, deleted by
`pkp2cs`'s write/read-wrapper pruning rule (`_is_write_read_wrapper`,
`tools/pkp2cs.py:714-726`) because it looks like a pure status accessor —
except this driver calls it cross-command from another command's Set body
(the case the rule's own docstring at `tools/pkp2cs.py:1775-1782`,
`find_dangling_self_calls`, names directly). Grepping the generated file
confirms no definition of `ReadMultiviewString`, `WriteMultiviewString`,
`ReadStatusHelper` or `WriteStatusHelper` survives anywhere in it — only the
one call site. Instantiating the class and calling the method would raise
`AttributeError: 'DeviceClass' object has no attribute 'ReadMultiviewString'`,
**with no residual warning at all.**

There is a second dangling reference from the same root cause: the generated
`OnDisconnected` at `smsg_10_6738_ethernet.generated.py:258-259` calls the
deleted `self.__ResetLiveStatus()`. It is harmless only by accident — the
generated class contains **duplicate** `OnConnected`/`OnDisconnected`
definitions (`generated.py:255,258` — the real, now-broken pair;
`generated.py:261,266` — a synthesized pair), confirmed by grep, and Python's
later definition wins,
so the synthesized one runs. That also means the synthesis's own aside that
"the synthesized handlers match the original no-op design" does not hold: the
live (winning) handler sets `connectionFlag`, calls
`WriteStatus('ConnectionStatus','Connected')` and resets a counter, where the
original `OnConnected` was `pass`.

### The `MultiviewCommand` wire-diff residual, traced

`wire_diff.json`'s one recorded difference is a literal-value mismatch inside
the `multiviewMode` field: the embedded script's template resolves to
`'multiviewMode': None`, the generated module's to `'multiviewMode': {}`.
Tracing this (executed, not just read, against `tools/wire_table.py`):

- **The generated side's `{}` is `wire_table`'s standard placeholder for an
  unresolvable value.** `ReadMultiviewString` doesn't exist in the generated
  module, so `Resolver._find_method` (`tools/wire_table.py:330-334`) can't
  find it to inline, and the call resolves as `(OPAQUE, fname)`
  (`tools/wire_table.py:321-325`), which `render()` prints as `{}`
  (`tools/wire_table.py:426-427`). Confirmed: re-extracting both tables today
  reports `opaque_markers: 1` for the generated module and `0` for the
  embedded one.
- **The embedded side's `None` is not a "correct resolution" in the sense
  that matters.** `ReadStatusHelper` *is* defined in the embedded script
  (`embedded.py:865-887`), so the resolver inlines it — but
  `Resolver._find_return` (`tools/wire_table.py:369-383`) does a depth-first
  walk of the method body that descends into a `Try`'s `except` handlers
  before checking a later sibling statement in the same block. Executing it
  directly confirms it returns the `return None` at `embedded.py:880` (the
  `except KeyError: return None` inside the Parameters-loop) rather than the
  `try: return Status[context]` / `except: return None` at `embedded.py:881-884`
  that is the statement actually reached at runtime for a command with no
  `'Parameters'` entry.

  For `MultiviewString` specifically the two happen to coincide — both paths
  return `None`, since `Command['Status']` starts as an empty dict and
  `'Emulated'` is not yet a key in it — so this is not misreporting the wire
  content here. But it is a genuine statement-order bug in `_find_return`
  that would misreport the resolved value on any command where the two
  `return`s actually differ, and it is not recorded anywhere else in this
  repo's findings.

So the residual has two separate causes bundled into one diff entry: a real,
already-named translator bug (the dangling `ReadMultiviewString` reference,
which `pkp2cs.find_dangling_self_calls` is built to catch and which the
synthesis's Q2 section documents), and a `wire_table` analysis quirk (the
`_find_return` traversal order) that happens not to distort this particular
value.

**Remaining work, per the synthesis:** fix the pruning rule to keep a
`Read<X>`/`Write<X>` wrapper referenced from any other command body; fix
duplicate handler emission. Both are still open — nothing in `tools/pkp2cs.py`
has changed to address either as of this write-up. The duplicate-definition
pattern reproduces on the Automate VX `.pkp` too, so it is pre-existing
translator behaviour, not specific to this device.

*(2026-09-23, ROADMAP R36/R37: all three fixed. The wrapper is kept, backed
by a private scratch store, with a residual; GC's own `OnConnected`/
`OnDisconnected` are never carried as methods, so each handler is emitted
once; `_find_return` follows statement order. Regenerated, the module has no
dangling call, and `MultiviewCommand` is still the one difference, but now of
kind `set_template_slot_sources`: both sides leave the multiview mode opaque,
the embedded script reading GC's own status table (`OPAQUE:Status[context]`)
and the generated module its scratch store
(`OPAQUE:self._emulated_status.get`). That is the substitution the residual
declares, not a mistranslation.)*

## 3. Docs-only generation: 22/22 and 5/5, and a payload problem (`experiments/docs_only/`)

From `reference/automate-vx-api/` alone, `experiments/docs_only/generator.py`
produced a module reproducing **22 of 22** documented endpoints Extron
actually implements, plus **5 of 5** example-only sub-APIs. Re-read today
directly from `experiments/docs_only/endpoint_crossref.txt`:

```
official endpoint coverage: both=22, extron-only=0, generated-only(unimplemented-by-extron)=10, total-official=32
sub-api (example-only) coverage: both=5, generated-only=4, total-listed=9
```

The 10 "generated-only" official endpoints are documented endpoints Extron
chose not to build (CopyFiles, GetAllStatus, Macro, Restart, …) — a product
decision, not a generator gap.

**The experiment marked 6 endpoints as doc gaps** (`endpoint_crossref.txt`'s
`DOC_GAP` lines): `StartAutoSwitch`, `StopAutoSwitch`, `StartISORecord`,
`StopISORecord`, `Wake`, and `api/ChangeRoomConfiguration` — the last called
at `samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py:282`
and appearing only once in the harvest, inside an unrelated malformed cURL
example at `reference/automate-vx-api/API-Reference/Macro-API.md:57`.

**Four of those six are not documentation gaps; they are harvest gaps.**
Finding 08's correction header, written after this experiment, found
`StartAutoSwitch`, `StopAutoSwitch`, `Wake` and `ChangeRoomConfiguration`
documented on pages the harvest never fetched (`Wake-API.htm`, the
unsuffixed `StopAutoSwitch.htm`, the shortened `ChangeRoomConfig-API.htm`).
Only `StartISORecord` and `StopISORecord` remain without a page. So the
generator's blindness to four commands measures this project's copy of the
docs, not the docs; re-measuring from a complete harvest is ROADMAP R32.

**The generator's own limits are separate and larger.** Range validation is
applied inconsistently (some parameters guarded, others not), and
`GetAllStatus-API.md` states that each nested `response_body` "must be
deserialized by the client," which the generated module never does. The big
one, independently reproduced today —
`grep -c "self.WriteStatus(.*res, qualifier)" experiments/docs_only/automate_vx_docs_only.py`
returns **15** — matching the synthesis's count exactly: **15 of the
module's 33 commands** pass the raw HTTP response dict straight to
`WriteStatus` with no field extraction, nearly half the module. Two confirmed
type mismatches against Extron's shipped module (`ptDir`/`zDir` as int vs.
Extron's `'0'..'7'`) came from trusting quoted-but-labelled-Integer values in
the docs' own example blocks.

**One integrity caveat the synthesis records against itself:** an early
over-broad file read exposed Extron's `Commands` dict and the bodies of
`SetCameraPresetRecall`/`SetCameraPresetSave` while identifying scaffold
boilerplate. The doc-gap set stayed clean — none of the 6 endpoints invisible to it
appear anywhere in the generated module — but those two commands' specific
parameter/qualifier design is compromised corroboration, not independent
evidence, and is disclosed as such at `experiments/docs_only/generator.py:11-33`.

**Would it control the device? Partly, and asymmetrically**, per the
synthesis: the Set direction is mostly sound; the Update/feedback direction
is broadly broken — 15 commands hand a dict where the status system expects a
scalar, while returning HTTP 200 with valid JSON on the documented success
path. A reviewer without hardware can see the missing commands for free
(`analyze_endpoints.py` produces the coverage table mechanically); nothing
about the 15 broken ones looks wrong without comparing the `WriteStatus`
argument against what a downstream GUI tag expects, which requires knowing
the device — the thing docs-only generation exists to avoid needing.

### `REPORT.md`: not found by method git log --all

`experiments/docs_only/generator.py:23` cites "the 'protocol integrity' note
in REPORT.md written alongside this file" as the source for its disclosure
practice. No such file exists in this repository. Checked by:

- `ls experiments/docs_only/` — no `.md` file of any kind is present, and
  none of the three three-questions experiment directories
  (`crestron2cs/`, `missing_ethernet/`, `docs_only/`) contains a README or
  report file.
- `git log --all --full-history -- experiments/docs_only/REPORT.md` — empty.
  No commit, on any branch, has ever touched this path.
- `git log --all --diff-filter=A --name-only | grep -i REPORT.md` — no
  match anywhere in the repository's entire commit history, under any path.

So this is not a file that was written and later removed or renamed; by
git's own record it was never committed at all. The disclosure the comment
promises is recoverable only from the comment itself
(`experiments/docs_only/generator.py:11-33`), which does carry the
substance of the caveat inline — reported above — even though the file it
points to does not exist.

## What this does NOT show

- **Nothing here ran on a processor.** `py_compile` and `wire_table` are
  static checks; the crestron2cs module's Rule/state engine, the missing
  Ethernet module's `AttributeError`, and the docs-only module's payload
  handling are all argued from reading code, not from execution against
  `extronlib` or real hardware.
- **The `ReadMultiviewString` pruning bug and the duplicate-handler bug are
  still open.** Nothing in `tools/pkp2cs.py` has changed to fix either as of
  this write-up; this finding records them, it does not close them.
- **The `_find_return` traversal-order issue in `tools/wire_table.py` is
  reported, not fixed**, and this finding does not establish how many other
  wire-table comparisons it affects — only that it does not distort this one.
- **This finding does not cover Q1a** (`experiments/nrbf_writeback/`, whether
  a `.pkp` can be generated from nothing rather than mutated or transplanted).
  That remains open per findings 12, 14 and 18: the NRBF byte format is
  proven writable, package *validity* is not, and finding 18's synthesised
  command surface is a donor transplant, not a from-scratch build.
- **The docs-only int-vs-string question** (`ptDir`/`zDir`) is unresolved
  without a real Automate VX unit; the docs and Extron's shipped module
  simply disagree, and only hardware settles which is right.
