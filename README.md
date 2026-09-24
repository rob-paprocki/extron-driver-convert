# extron-driver-convert

Research repo. Can an Extron `.pkp` driver (Global Configurator Plus/Pro) be
converted to or from a ControlScript device module (`.py`)? Does the same hold
across vendors, with Crestron? And, in practice: can an Extron processor drive
Crestron-owned hardware — the 1 Beyond IV-CAM-I20 — from a driver built here?

**Read `STATUS.md` first.** It carries the verdicts, the findings index, the
translator scorecard and the methodology notes, and it is the file kept
current. **`ROADMAP.md`** lists everything unfinished, in order, with the
blocker and first step for each. **`ENVIRONMENT.md`** describes what a workstation
the machine-bound work runs on.

Not affiliated with Extron or Crestron.

## Where it stands

| Direction | Verdict |
|---|---|
| `.pkp` → ControlScript `.py` | **Yes, built and measured.** `tools/pkp2cs.py`; 80.8% wire-match across 314 third-party oracle packages, but 54% of generated modules would still raise at runtime, mostly on configuration values GC supplies and ControlScript does not (finding 14 §8) |
| ControlScript `.py` → `.pkp` | **Yes, including new commands.** Transplant into a real package, refresh its SHA-256 digests, and synthesise `DriverCommandAsset` subtrees into the object graph. Global Configurator loads, catalogues and renders the result (findings 16, 18) |
| Crestron `.pkg` → Extron | **Yes** for JSON-engine drivers (findings 03 to 05, 13) |
| Extron → Crestron `.pkg` | Mechanically demonstrated by resource-patching a real DLL. Gated by Crestron's dealer licence, not by code (finding 06) |
| Crestron IV-CAM-I20 on an Extron processor | **Built both ways; the `.pkp` runs on a processor.** A 45-command `.pkp` (v1.6, parity with Crestron's own I20 driver) and a drop-in ControlScript module, byte-identical on the wire. The `.pkp` builds, uploads and is controlled from a touch panel on an IPCP Pro 360, against a PC playing the camera. **Not yet run against a real camera**, and the ControlScript form not yet on a processor |

Two further results came out of the samples: a driver can be generated from API
documentation alone for 29 of the 32 endpoints a real driver calls (~91%,
re-measured from saved files; `experiments/docs_only/REMEASURE.md`), where the danger
is silent incompleteness; and a shared intermediate representation is
justified, because two vendors independently encode the same device to the same
bytes — including the same undocumented firmware-bug workaround (finding 05).

## Tools

Standard library Python only. Run each test file directly; there is no pytest
and none is needed.

| tool | what it does |
|---|---|
| `tools/pkp_dump.py` | `.pkp` to a JSON object graph |
| `tools/pkg_dump.py` | Crestron `.pkg` to manifest and driver JSON, via a real ECMA-335 metadata walk |
| `tools/wire_table.py` | **the acceptance oracle** — a normalised per-command wire table from both Python dialects |
| `tools/pkp2cs.py` | `.pkp` → ControlScript translator. Raises rather than degrading |
| `tools/pkp_build.py` | `.pkp` transplant builder; refuses to emit unless the donor round-trips byte-for-byte |
| `tools/pkp_validate.py` | Extron's driver validator reimplemented; agrees with GC on all 1,853 shipping packages given Extron's Guid table |
| `tools/nrbf_graph.py` | maps every NRBF object to its exact span of records |
| `tools/pkp_asset.py` | adds commands to a `.pkp`'s object graph by clone / attach / detach |
| `tools/gc_catalogue.py` | reads GC's `DriverLookup.dat`: what it actually catalogued |

The one non-Python component is `experiments/gcp_harness/` — Windows-only
PowerShell that asks Extron's own DLLs whether a package loads, and the UI
Automation chain that drove GCP. See its README for why.

Test counts are in `STATUS.md`.

## Layout

```
STATUS.md  ROADMAP.md  ENVIRONMENT.md
findings/                    numbered research output, 01 to 18
tools/                       the tools above, with their tests
experiments/
  skeleton_i20/              the IV-CAM-I20 driver, .pkp and ControlScript forms
  oracle_pairs/              the 312-pair translator scorecard (finding 14)
  gcp_harness/               Windows-only: Extron DLL probes + GCP UI Automation
  graph_probes/              packages that located finding 18's deserializer bug
  ross_ultrix/               the one oracle pair with a human-written side (finding 17)
  nrbf_writeback/ crestron2cs/ docs_only/ missing_ethernet/
samples/<device>/            .pkp, shipped ControlScript module, Crestron package
corpus/                      1.3 GB snapshot of an Extron driver library
evidence/                    screenshots and GC catalogue captures the findings cite
reference/                   harvested vendor documentation
notes/                       sample provenance
private/                     session records + tool settings (licence data) — git-ignored, on disk only
```

## Grading a conversion

Six things decide how far a direction gets:

1. Container: can the format be read at all without Extron's tooling?
2. Command table: do commands, parameters and qualifiers map 1:1?
3. Feedback and parse: do match patterns survive translation?
4. Connection model: serial params, IP ports, IR, relays, addressing.
5. Logic and events: GC's event layer against ControlScript's user code.
6. Round-trip loss: what is silently dropped, and does it matter?

## Method

A negative claim needs positive evidence: report *"not found by method X"*,
never *"does not exist"*. Acceptance is the wire-string table, not file
similarity — and wire correctness is necessary but not sufficient. `Valid` does
not mean loadable: finding 18 built a package that passed every local check and
that GC would not list, because every local check shared one wrong model of the
format. Deserialize through the vendor's own code before believing an edit.

## Provenance and licensing

The sample drivers and `corpus/` are Extron and Crestron vendor material, so
this repo stays private. Findings may describe the formats; vendor files are
not redistributed.
