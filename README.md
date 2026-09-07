# extron-driver-convert

Research repo. Can an Extron `.pkp` driver (Global Configurator Plus/Pro) be
converted to or from a ControlScript device module (`.py`)? And does the same
hold across vendors, with Crestron?

Read `STATUS.md` first. It carries the verdicts, the translator scorecard, the
findings index and the methodology notes, and it is the file kept current.

Not affiliated with Extron or Crestron.

## Status

All four original directions have verdicts, and the translator is built and
measured. `tools/pkp2cs.py` converts a `.pkp` into a ControlScript module and
is scored against Extron's own shipped module for the same device.

This is a research repo rather than a product. The tools exist to answer the
questions, and the open questions in `STATUS.md` matter more than the code.

## The questions, and where they landed

| Direction | Verdict |
|---|---|
| `.pkp` to `.py` | Yes. Built and measured (finding 02) |
| `.py` to `.pkp` | Format: yes. Byte-identical NRBF round-trip on all four packages. Whether Global Configurator accepts a from-scratch package is untested (finding 10 supersedes finding 02's "no") |
| Crestron `.pkg` to Extron | Yes for JSON-engine drivers (findings 03 to 05) |
| Extron to Crestron `.pkg` | Mechanically demonstrated by resource-patching a real DLL. Gated by Crestron's dealer licence, not by code (finding 06) |

Two further questions came out of the samples. A driver can be generated from
API documentation alone to about 84% of what a real driver calls, where the
danger is silent incompleteness rather than missing methods. And a shared
intermediate representation is justified, because two vendors independently
encode the same device to the same bytes.

Crestron came into scope once samples showed that same convergence: identical
wire traffic for the Samsung display, including the same undocumented
firmware-bug workaround from two vendor teams (finding 05).

## Tools

Standard library only. Run each test file directly; there is no pytest and none
is needed.

| tool | what it does |
|---|---|
| `tools/pkp_dump.py` | `.pkp` to a JSON object graph. Every byte accounted for on all four packages |
| `tools/pkg_dump.py` | Crestron `.pkg` to manifest and driver JSON. A real ECMA-335 metadata walk, no hardcoded offsets |
| `tools/wire_table.py` | the acceptance oracle. A normalised per-command wire table from both Python dialects. Unresolvable expressions become counted opaque markers, never guesses |
| `tools/pkp2cs.py` | the `.pkp` to ControlScript translator. Raises rather than degrading |

| test file | tests |
|---|---|
| `tools/test_pkp2cs.py` | 56 |
| `tools/test_wire_table.py` | 34 |
| `tools/test_pkg_dump.py` | 23 |
| `experiments/nrbf_writeback/test_nrbf_write.py` | 16 |
| `experiments/crestron2cs/test_crestron2cs.py` | 14 |

## Translator scorecard

Two metrics, because wire correctness alone is not sufficient. A module can
carry a perfect command table and still raise `AttributeError` on a processor.

| pair | shipped cmds | generated | wire-matching | differing |
|---|---|---|---|---|
| DSC 12G-HD | 29 | 29 | 28 | 1, Extron's own `LogoAssignment` bug |
| DTP3 CP 42 | 31 | 29 | 27 | 1, plus real version skew |
| Samsung serial | 9 | 9 | 9 | 0 |
| Automate VX | 18 | 18 | 17 | 1, the package omits `Scenario` params |

Runtime resolvability went from 26 dangling `self.X()` references down to 5,
with the wire baseline unchanged and all five modules compiling. The remaining
five are one honest category: GC-only scratch-command accessors called across
commands to compose another command's payload. Extron restructured these by
hand into `qualifier['Number']` and `qualifier['Name']`, which is a design
decision rather than a mechanical rewrite, so they are reported as residuals
rather than guessed.

## Layout

```
samples/<device>/pkp/            .pkp driver packages
samples/<device>/controlscript/  the shipped ControlScript module for the same device
samples/<device>/Crestron/       the Crestron package, where one exists
tools/                           the tools above, with their tests
experiments/                     NRBF writer, Crestron to ControlScript, docs-only generation
findings/                        numbered research output, 00 to 11
reference/                       harvested vendor documentation
notes/                           sample provenance
```

## Grading a conversion

Six things decide how far a direction gets:

1. Container: can the format be read at all without Extron's tooling?
2. Command table: do commands, parameters and qualifiers map 1:1?
3. Feedback and parse: do match patterns survive translation?
4. Connection model: serial params, IP ports, IR, relays, addressing.
5. Logic and events: GC's event layer against ControlScript's user code.
6. Round-trip loss: what is silently dropped, and does it matter?

A conversion that gets 1 to 4 and abandons 5 may still be worth building. That
call belongs in the writeup, so don't settle it in advance.

## What is still open

In the order it matters. `STATUS.md` has the detail.

1. Does an outsider-built `.pkg` load on a processor? Independent developers
   ship drivers built from the public NuGet DevKit, so the compile path is
   demonstrated. The resource-swap shortcut used here is not. Answering it
   needs Crestron Toolbox or VC-4, both dealer-gated. No amount of further
   research substitutes for this.
2. Crestron's licence restricts its tools to developing software for Crestron
   devices, bars reverse engineering, and requires a dealer or partner
   agreement. Extron requires a free account with no field-of-use limit. That
   is a lawyer's question, and cheaper to ask before building an emitter than
   after.
3. Catalogue coverage. How much of Crestron's library is the extractable
   JSON-engine form, against the V2 Entity Model or V1 RAD? Two data points so
   far. `drivers.crestron.io` is login-gated, so this can only be answered by
   sampling.
4. Only four oracle pairs, all Extron-authored. The translator's rules were
   derived from and validated against the same small set, so more pairs is the
   cheapest way to find where it breaks.

## Method

A negative claim needs positive evidence. Where no published index exists,
report a negative as "not found by method X", never as "does not exist".
Finding 08 got this wrong twice and carries the corrections in its header.

Acceptance is the wire-string table, not file or line similarity. Line overlap
between a package and its shipped module ranges from 76% down to 38% while the
command tables stay near-identical.

Samples beat documentation. Doc-only research recommended point-to-point
converters and claimed Crestron's declarative layer stopped at a whitelist.
Real files reversed both.

Calibrate before trusting a document. Score it against facts you can already
verify before relying on it for facts you cannot.

## Provenance and licensing

The sample drivers are Extron and Crestron vendor material, so this repo stays
private. Findings may describe the formats; the sample files are not
redistributed.
