# Finding 14 — the translator measured against 312 third-party pairs

**Status: measured** 2026-09-08, against a local Global Configurator install
carrying **1,853 `.pkp`** packages and Extron's **09/06/2026 GS module
shipment** (2,235 ControlScript modules). Neither library is in this repo;
`experiments/oracle_pairs/` rebuilds the analysis on any machine that has them.
*(Since then: a snapshot of both is committed under `corpus/` (1,854 packages),
and `experiments/oracle_pairs/` reads it by default. **Re-scored 2026-09-23 —
§7**: 80.8% wire-match, and 48 of 314 generated modules (15%) would raise
`AttributeError` or `NameError` at runtime, where the first run found 25% from
`AttributeError` alone. **Then executed — §8**: counting attributes nothing
assigns and wrong argument counts too, 169 (54%) would raise, and the modules
that would raise score *lower* on the wire, not higher.)*

This closes STATUS.md's oldest methodological limitation. Finding 12 downgraded
*"only 4 oracle pairs, all Extron-authored"* from an acquisition problem to a
selection problem; this answers it outright — and the answer is not the
flattering one.

## 1. There are 352 oracle pairs, not 4

The two libraries share no identifier. Packages are named
`vendor_class_id_version.pkp`, modules `vendor_type_Model_vX_Y_Z_W.py`, and
even the vendor codes differ (`1bynd` vs `onebynd`). They join on the model
name: `DriverModelAsset`'s `AssetBase+_name`, against the module filename.

| | |
|---|---|
| packages parsed | **1,853** |
| parse errors | **0** |
| model entries | 6,820 |
| packages with a vendor-consistent module match | **314** |
| distinct pairs | **352** |

**`pkp_dump.py` parsed Extron's entire shipping library without a single
failure.** The NRBF work had only ever been exercised on 9 samples.

Two traps in the join, both hit:

- The member key is `AssetBase+_name`, not `_name`. Reading the latter returns
  `None` for every package and yields a confident zero.
- Substring matching alone is wrong. `absn` model `C110` matches **Dynascan**'s
  `DMBC110` module; `acer` `K750` matches a **Digital Projection** module whose
  normalised filename contains `k750`. Requiring vendor agreement rejected 33
  such pairs out of 347.

## 2. 80.9% wire-match on hardware nobody tuned for

Scored with `wire_table.diff_tables` — the same oracle as the 4-pair
scorecard, on 312 comparable pairs:

| | |
|---|---|
| shared commands | 4,865 |
| **wire-matching** | **3,935 (80.9%)** |
| differing | 930 |
| only in generated | 629 |
| only in shipped | **292** |
| packages with a perfect table | **138 (44%)** |

*(2026-09-23, ROADMAP R11: the two pairs that never compared — MediaPort 200
and 300, `compare-failed` with `TypeError: unhashable type: 'dict'` — were a
`wire_table` bug. A Match handler's `ValueStateValues` can be a table of
per-input state maps, which the value-map fallback inverted blindly; it is now
left unresolved and counted as opaque. Re-scored, **all 314 packages
compare**: 4,974 shared commands, **4,044 wire-matching (81.3%)**, 930
differing, 630 only in generated, 292 only in shipped, 140 perfect. Both
MediaPort pairs are perfect tables. No other row changed.)*

Where the differences fall:

| kind | packages |
|---|---|
| `set_template_slot_sources` | 67 |
| `value_map` | 62 |
| `responses` | 54 |
| `set_templates` | 52 |
| `update_templates` | 48 |
| `parameters` | 35 |
| `update_template_slot_sources` | 32 |

`set_template_slot_sources` leading is worth noting: that check was *added* by
finding 10, after the DTP3 result, to catch cases where both sides render the
same wire shape but feed the slot from different sources. It is the subtlest
category and the most common failure, which suggests the coarser checks mostly
pass.

**292 commands present in Extron's shipped module and absent from ours** is the
number to chase. Some of it is version skew — a `.pkp` and a GS module matched
by model name are not guaranteed to be the same driver revision, and finding 10
saw real skew read as translator failure — but it is not all skew, and it was
invisible until the diff keys were read correctly.

## 3. The trap, confirmed and inverted

STATUS.md's standing note says wire correctness is *necessary but not
sufficient*, after 26 dangling `self.X()` references hid behind a near-perfect
scorecard on the 4 samples. At scale it is worse than that note implies:

| | |
|---|---|
| packages that would raise `AttributeError` at runtime | **77 (25%)** |
| wire-match rate, packages **without** dangling calls | 77.1% |
| wire-match rate, packages **with** dangling calls | **86.4%** |
| **perfect wire table but still raises** | **23 packages** |

**The broken modules score better.** Not equally — measurably better, by nine
points. And 23 packages carry a flawless command table while calling a method
that does not exist.

The mechanism is presumably that a package whose driver leans on GC-only
scratch accessors produces both (a) a tidy command table, because the
composition happens in helpers the wire extractor never sees, and (b) dangling
references, because those helpers are exactly what the rewrite drops. Whatever
the cause, the correlation runs the wrong way, and any scorecard reporting wire
match alone would rank the runtime-broken modules first.

## 4. Every package has residuals

14,021 residual entries across 314 packages; **zero packages are clean**. Most
are documented, deliberate rewrites rather than faults:

| reason | entries | packages |
|---|---|---|
| `gc-dual-status-no-target` | 3,719 | 314 |
| `gc-dual-status-emulated-prewrite-dropped` | 2,695 | 293 |
| `gc-config-parsing-dropped` | 2,019 | 314 |
| `gc-scratch-timer-dropped` | 1,700 | 216 |
| `gc-sethelper-updatehelper-fixed-template` | 548 | 275 |
| `gc-dual-status-requiredtimer-dropped` | 547 | 183 |
| `extron-editorial-omission` | 544 | 272 |
| `gc-onconnected-ondisconnected-superseded` | 484 | 288 |
| `onconnected-ondisconnected-synthesized` | 314 | 314 |
| `ethernet-connection-settings-not-recoverable` | 178 | **178** |
| `dangling-self-call` | 146 | **77** |
| `dialect-transport-not-evidenced` | 115 | 115 |

`ethernet-connection-settings-not-recoverable` in 178 packages (57%)
independently corroborates finding 13 §4b: the transport lives in
`EthernetProtocolAsset`, which is package metadata, so it cannot be recovered
from the embedded script. A ControlScript module generated from a `.pkp` will
not know its own port.

## 5. Four silent, flattering harness bugs

Recorded because the pattern matters more than the bugs. Every one produced a
clean-looking number rather than a crash:

| assumed | actual | symptom |
|---|---|---|
| `translate_job` returns an object with `.source` | returns a **dict** | compared the dict's repr; every pair failed "no class definition found" while reporting **100% translated** |
| failures raise | recorded in `residuals` | 314/314 "translated successfully" — meaningless |
| `diff_tables` → `only_a`/`only_b` | `only_in_a`/`only_in_b` | **0 and 0** missing commands, i.e. apparent perfect coverage |
| `Residuals` entries keyed `kind` | keyed `reason` | **zero residuals** across 14,021 of them |

Each was an API assumed rather than read, and each wrong assumption biased the
result *upward*. That is the sharpest available argument for the repo's own
rule — a plausible guess is worse than a recorded gap, because it scores well.
Add: **a metric that cannot fail loudly is not a metric.** Three of these four
would have survived code review; what caught them was a number being too good
(0 missing commands across 312 packages, 100% success on unseen hardware).

## 6. Extron ships no i12/i20/p12/p20 driver

Across the complete 2,235-module shipment, 1 Beyond has four entries:
`onebynd_camera_AutoTracker_3`, `onebynd_camera_PTZ_IP12_IP20`,
`onebynd_sm_Automate_VX_Series`, `_1bynd_camera_automate_select_series`. No
`IV-CAM` anything, and the driver library carries exactly one `1bynd` package
(Automate VX).

Bounded negative: not found in Extron's complete 09/06/2026 GS shipment or in
this 1,853-package library. Not a claim about every Extron release ever. But it
does mean finding 13's driver is not duplicating shipped vendor work.

## 7. Re-scored, 2026-09-23

Everything above is the first run (with §2's R11 addendum). Since then the pairs,
the oracle, the translator and the metric have all changed, so the set was
scored once more with all of it (`experiments/oracle_pairs/out/scorecard.json`):

- **Pairs:** five named corrections with version or name evidence
  (`build_index.OVERRIDES`, ROADMAP R39). Still 314 packages, 352 pairs.
- **Oracle** (`wire_table`, R36): a bare `from re import compile` resolves; an
  `if`/`else` that builds a command differently per arm yields one template per
  arm; `_find_return` follows statement order.
- **Translator** (`pkp2cs`, R16/R17/R37 and after): transports read from the
  package's own protocol assets; `Read<X>`/`Write<X>` wrappers still called
  elsewhere are kept; the source's own imports are carried; and, found by the
  metric change below, its module-level definitions, the local assignments
  its match-string registrations read, its class-body attributes and Python's
  own method decorators, all of which were dropped.
- **Metric** (`score.py`): a generated module that reads a global nothing binds
  would raise `NameError`; it is now counted beside `AttributeError`.

| | first run (§2–§3, R11) | 2026-09-23 |
|---|---|---|
| shared commands | 4,974 | 5,038 |
| **wire-matching** | 4,044 (81.3%) | **4,069 (80.8%)** |
| differing | 930 | 969 |
| only in generated | 630 | 566 |
| only in shipped | 292 | **216** |
| perfect tables | 140 | 132 |
| would raise `AttributeError` | 77 (25%) | **28 (9%)** |
| would raise `NameError` | not measured | **26 (8%)** |
| would raise either | — | 48 (15%) |
| wire-match, modules that would raise / would not | 86.4% / 77.1% | 82.7% / 80.2% |
| **perfect table but still raises** | 23 | **14** |

**The wire rate barely moved; what it measures did.** The oracle now sees
commands it missed on both sides (shared commands +64, only-in-shipped −76),
and the five re-paired packages are scored against their right modules. Half a
point down on a larger, truer denominator is not a regression.

**The trap is smaller and still inverted.** Modules that would raise still
wire-match better than modules that would not, by 2.5 points rather than 9.3.
*(Superseded the same day by §8: counting every way to fail found by
executing the modules, the inversion reverses.)*
§3's presumed mechanism (scratch accessors composing payloads out of the
extractor's sight) is still unmeasured (ROADMAP R12).

**Measuring `NameError` found translator bugs, not driver bugs.** When the
check first ran, 46 packages would have raised it, and 77 of the 81 unbound
names were bound perfectly well in Extron's own script: helper classes
(`Scroller`, `Directory`), a WebSocket driver's framing constants (`FIN`,
`OPCODE`) and function (`_mask`), a regex the match-string registrations read
from an `__init__` local, and a class attribute read as a default argument.
The translator had dropped each of them. They are now carried verbatim, but
only the ones the generated module reads. Nearly every script defines
`class ExtronTime(float)` for GC's own dual-status machinery, and carrying it
everywhere would be noise. The 26 packages left, each residual now naming its
cause:

| cause | packages | names |
|---|---|---|
| bound only by a GC runtime import (`import Extron.Timer as CallBackTimer`), which has no ControlScript counterpart and no evidenced mapping | 22 | `CallBackTimer` |
| unbound in Extron's embedded script too: defects in the packages, carried faithfully (3 of the 5 are also in Extron's shipped module) | 5 | `Self`, `seld`, `matchstring`, `recorder_idindex`, `exceptions` |
| bound only inside a platform-gated `if` | 1 | `ET` |

(Two packages have two causes. For `ET`, Extron's shipped module imports
`extronlib.standard.exml.etree.ElementTree as ET`, a mapping seen once and
not generalised.)

**One bug neither check can see.** The translator stripped every decorator
from every method. 8 of these 314 packages decorate a driver method (10
methods, all but one `@staticmethod`). Without the decorator, `self` arrives
as the first argument: `ktek`'s DM8000 calls `self.__check_instance_tag(...)`
and `self.__constraint_checker(...)` from its command methods, and each such
call would raise `TypeError`. The module
compiles, every name resolves and the wire table is unaffected. Python's own
decorators are now kept; `test_pkp2cs` executes the result to prove it.
Anything that only executing the code can catch is ROADMAP R13's job.

## 8. Executed, 2026-09-23: §7 undercounted by more than half

§7's 15% counted what static checks could see: a missing method or a missing
global. ROADMAP R13 then **ran** every generated module offline
(`experiments/exec_harness/`). A stand-in extronlib recorded each `Send`, and
each generated module and Extron's shipped module for the same device got the
same inputs, taken from their own method bodies.

Running them found five translator bug classes that nothing static had
seen:
- A GC query throttle whose timer the translator dropped but whose guard it
  kept (DSC, in-sample).
- A fifth `__SetHelper` argument the fixed template refused: 1,143 calls in
  192 packages.
- Attributes set only in GC's dropped `configs[...]` parsing.
- Methods held as values in dispatch tables.
- `Send(pacing=)` (DTP3, in-sample).

The first, second, fourth and fifth are fixed. The third is reported: it
needs the package's configuration defaults (ROADMAP R41). Two new static
checks came out of it, `find_unassigned_self_attributes` and
`find_call_arity_mismatches`, and the scorecard now counts four ways to fail
at runtime:

| would raise at runtime | packages |
|---|---|
| `AttributeError`, a missing method | 28 (9%) |
| **`AttributeError`, an attribute nothing assigns** | **158 (50%)** |
| `NameError` | 26 (8%) |
| `TypeError`, a wrong argument count | 2 (1%) |
| **any of the four** | **169 (54%)** |
| perfect wire table but still raises | 53 |

The wire table is unchanged (80.8%, 132 perfect): none of these touch a
command string. The new largest class is one cause: `devicePassword` (63
packages), `DeviceID` (38) and `deviceUsername` (26) lead it, values GC reads
from its configuration and ControlScript modules must set themselves.

**§3's inversion was an artefact of what was counted.** With missing methods
alone, the modules that would raise scored nine points *higher* on the wire.
With all four checks they score ten points *lower* (76.8% against 86.8%).
§3's presumed mechanism may still be real for its 28 packages, but "broken
modules score better" does not survive a fuller definition of broken.

**Executed, the picture agrees.** Of the 314 pairs:
- 73 behave identically on every input.
- 100 differ. Those differences come from bugs in the package's own script,
  version skew or translation, and the harness cannot yet tell which.
- In 109 the generated module raises where Extron's does not, and in 94 of
  those the exception is an `AttributeError`.
- 21 generated modules cannot be constructed at all, nearly all on
  configuration values.

The execution also shows what the static checks still miss. A stripped
`@staticmethod` (§7) is invisible to all four. So is a `RecursionError` from a
carried `OnConnected` that calls `Update` (MLA VC10, ROADMAP R42).

## What this does NOT show

- **Not a clean generalisation claim.** Pairs are matched by model name, so an
  unknown fraction of the 930 differences and 292 missing commands is version
  skew between the two libraries rather than mistranslation. Separating them
  needs per-pair version comparison, which is not done here. *(2026-09-23:
  969 and 216 after the re-score, §7; still unseparated.)*
- **No module was executed.** `dangling-self-call` is a static finding; it says
  a generated module calls a method it never defines, which would raise on a
  processor. Nothing here ran on hardware. *(2026-09-23: nor since, and §7's
  stripped decorators show what static checks miss.)*
- **1,853 packages, not finding 12's 6,644.** A different (smaller) install.
  The two figures should not be compared directly.
