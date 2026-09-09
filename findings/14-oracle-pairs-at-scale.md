# Finding 14 — the translator measured against 312 third-party pairs

**Status: measured** 2026-09-08, against a local Global Configurator install
carrying **1,853 `.pkp`** packages and Extron's **09/06/2026 GS module
shipment** (2,235 ControlScript modules). Neither library is in this repo;
`experiments/oracle_pairs/` rebuilds the analysis on any machine that has them.

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

## What this does NOT show

- **Not a clean generalisation claim.** Pairs are matched by model name, so an
  unknown fraction of the 930 differences and 292 missing commands is version
  skew between the two libraries rather than mistranslation. Separating them
  needs per-pair version comparison, which is not done here.
- **No module was executed.** `dangling-self-call` is a static finding; it says
  a generated module calls a method it never defines, which would raise on a
  processor. Nothing here ran on hardware.
- **1,853 packages, not finding 12's 6,644.** A different (smaller) install.
  The two figures should not be compared directly.
