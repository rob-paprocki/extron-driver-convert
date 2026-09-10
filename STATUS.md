# Status

**Last updated: 2026-09-10.** Read this first. Everything below is measured unless
marked otherwise.

## Answers

| question | answer |
|---|---|
| Extron `.pkp` → ControlScript `.py`? | **Yes — built and measured.** `tools/pkp2cs.py`. |
| ControlScript `.py` → `.pkp`? | **Format: yes. Command surface: yes.** Byte-identical NRBF round-trip on all 9 packages; GC loads and selects a transplanted package (findings 12, 16, 18); and `tools/pkp_asset.py` now **adds commands to the object graph** — 17 added to the i20 package, all 15 originals unchanged (finding 18). Whether GC *renders* added commands is the open hardware gate. |
| Crestron `.pkg` → Extron ControlScript? | **Yes — built and measured** against Extron's own driver for the same device. |
| Crestron device driven by an Extron processor? | **Built and verified offline; untested on hardware.** Both forms: 4 staged `.pkp` and a drop-in ControlScript module. Same wire table from two emitters (finding 13). |
| Extron → Crestron `.pkg`? | **Mechanically demonstrated** (resource-patched a real DLL). Gated by Crestron's dealer/partner licence, not by code. |
| Generate a driver from API docs alone? | **Mostly.** ~84% of what a real driver calls. The danger is silent incompleteness, not missing methods. |
| Is a shared intermediate representation justified? | **Yes.** Two vendors independently encode the same device to the same bytes, including its undocumented bug workarounds. |

## Findings

| # | subject |
|---|---|
| 01 | `.pkp` = gzip over .NET NRBF, **embedding a complete Python driver**. Reframed the project. |
| 02 | `.pkp` → ControlScript verdict. *Its reverse-direction "No" is superseded — see finding 10.* |
| 03 | Crestron `.pkg` = zip; the driver definition is plain JSON inside the DLL. |
| 04 | Crestron interop verdict and the licensing position. |
| 05 | Samsung cross-vendor: byte-identical wire traffic **and the same undocumented firmware-bug workaround** from two vendor teams. |
| 06 | Emitting a `.pkg`; how far the translator generalises to third-party hardware. |
| 07 | 1 Beyond cameras are SDK **V2 Entity Model**, not JSON shells. A `.cmc` is an I/O contract with a dangling pointer. |
| 08 | Docs vs implementation. **Carries two corrections — read its header.** |
| 09 | VISCA: documentation closes **protocol** gaps, not **device** gaps. |
| 10 | *(pending write-up)* the three-questions experiments — see `tools/out/verdicts/three_questions_synthesis.md`. |
| 11 | A protocol **spec** refereed what two implementations could not; the wire oracle has its own false-positive rate. |
| 12 | **GC ingests packages we generate.** The gate is an index, not the file. Locates the driver library (size varies by install; see finding 16). |
| 13 | **Crestron device -> Extron processor.** The i20's auto-switching is reserved preset numbers. Cross-vendor corroboration without a Crestron processor. |
| 14 | **312 third-party oracle pairs.** 80.9% wire-match, but 25% of generated modules would raise `AttributeError` — and the broken ones score *higher*. |
| 15 | **On hardware: `80085`.** A transplanted package is catalogued, then refused at selection. *Its proposed cause is superseded by finding 16.* |
| 16 | **`80085` is a SHA-256 mismatch.** Extron's validator reimplemented in pure Python; 1,900/1,919 exact agreement with their own code, so GC is no longer needed to check a package. |
| 18 | **The asset tree is the command surface** — GC never asks the script what it can do, so a package can be `Valid` and silently short. Object-graph synthesis built and verified **through Extron's own deserializer**; the i20 package goes 15 -> 32 commands. Carries the negative-object-id trap that no local check could see. |
| 17 | **How a human writes one.** A working integrator splices Extron's template from two vintages rather than authoring from scratch — the same instinct as our transplant. |

## Tools — all tested, all standard library only

| tool | what it does | tests |
|---|---|---|
| `tools/pkp_dump.py` | Extron `.pkp` → JSON object graph. Every byte accounted for on all 4 packages. | 23 |
| `tools/pkg_dump.py` | Crestron `.pkg` → manifest + driver JSON. Real ECMA-335 metadata walk, no hardcoded offsets. | (in above) |
| `tools/wire_table.py` | **The acceptance oracle.** Normalised per-command wire table from *both* Python dialects. Unresolvable expressions become *counted* opaque markers, never guesses. | 34 |
| `tools/pkp2cs.py` | `.pkp` → ControlScript translator. Raises rather than degrading. | 56 |
| `tools/pkp_build.py` | **`.pkp` transplant builder.** Refuses to emit unless the unmodified donor round-trips byte-for-byte first; no bypass flag. | 36 |
| `tools/pkp_validate.py` | **Extron's driver validator, in pure Python.** Same verdict as GC's own code on 1,900 of 1,919 packages, with no GC installed. | 127 |
| `tools/nrbf_graph.py` | **Structural navigation over an NRBF trace.** Every object id → its exact span of records, by replaying the reader's grammar. Verified end-to-end on all 9 packages, up to 4.4M events / 668k objects. | (with below) |
| `tools/pkp_asset.py` | **Adds commands to a `.pkp`'s object graph.** Clone/attach/detach of asset subtrees with computed ownership, so a shared string is never renamed and a donor is never damaged. Output confirmed loadable by Extron's own `LoadFromFile`. | 43 |
| `experiments/skeleton_i20/` | **i20 driver, both forms.** `.pkp` transplant + standalone ControlScript module, held to identical bytes. | 85 + 56 |

Experiments live in `experiments/` (NRBF writer, Crestron→ControlScript, missing-Ethernet
generation, docs-only generation). Harvested vendor docs in `reference/`.

### Translator scorecard

Two independent metrics, because wire correctness alone is **not sufficient** — a module
can carry a perfect command table and still raise `AttributeError` on a processor.

| pair | shipped cmds | generated | wire-matching | differing |
|---|---|---|---|---|
| DSC 12G-HD | 29 | 29 | 28 | 1 — Extron's own `LogoAssignment` bug |
| DTP3 CP 42 | 31 | 29 | 27 | 1 + real version skew |
| Samsung serial | 9 | 9 | **9** | **0** |
| Automate VX | 18 | 18 | 17 | 1 — package omits `Scenario` params |

Runtime resolvability: **26 dangling `self.X()` references → 5**, wire baseline unchanged,
all 5 modules compile. The remaining 5 are one honest category — GC-only scratch-command
accessors called cross-command to compose another command's payload. Extron restructured
these by hand into `qualifier['Number']` / `qualifier['Name']`; that is a design decision,
not a mechanical rewrite, so they are reported as residuals rather than guessed.

## Open, in order of how much they matter

1. **Does an outsider-built `.pkg` load on a processor?** Independent developers ship drivers
   built from the public NuGet DevKit, so the compile path is demonstrated; the resource-swap
   shortcut is not. **Crestron Toolbox is installed on the Windows box** (see Environment in
   `CLAUDE.md`), so the tool is no longer the gate — a processor or VC-4 instance is, plus the
   licence question below. *No amount of research substitutes for this.*
2. **Crestron's licence** restricts its tools to "Developing software for Crestron Devices",
   bars reverse engineering, and requires a Dealer/AIP/Partner agreement. Extron requires a
   free account with no field-of-use limit. A lawyer's question, cheaper to ask before building
   an emitter than after.
3. **Catalogue coverage.** How much of Crestron's library is the extractable JSON-engine form
   versus V2 Entity Model versus V1 RAD? Two data points so far: Samsung = LegacyWrappers JSON
   engine, 1 Beyond = V2 with a **bounded, named** IL residue. `drivers.crestron.io` is
   login-gated, so this can only be answered by sampling.
4. **Does GC render a command we added to the object graph?** Finding 18 closed the build
   side: `1bynd_19_20024` carries 32 command assets where the donor had 15, every original
   unchanged, and **Extron's own `DriverFileAsset.LoadFromFile` returns a live asset whose
   `DriverCommands` collection enumerates all 32** with the right names, parameters, enum
   states and attributes. What remains is whether Driver Manager lists it and the editor
   draws the parameter widgets. Note that `Valid` is NOT evidence here: the first build of
   20024 validated and was completely unloadable (finding 18 s6). GCP licence expires
   ~2026-10-07.
5. **Catalogue acceptance is not a working driver.** Finding 18 got a transplanted package
   *selected* into a GCP project — two gates past finding 12. Building, uploading, and
   controlling a device remain unproven, as does whether any of it drives an actual i20.
   Same "necessary but not sufficient" trap as the wire table.

*Closed outright by finding 14: 352 pairs across 314 packages, scored. Superseding finding 12's* The GC install carries
**6,644 `.pkp` across hundreds of vendors** in `C:\Users\Public\Documents\extron\driver3`,
96% of them third-party. The sampling problem is now a selection problem.

## Standing methodology notes

- **A negative claim needs positive evidence.** Finding 08 twice asserted an endpoint was
  undocumented when it was not — first from keyword-search enumeration, then from assuming a
  URL-naming convention was exhaustive. Where no published index exists, report a negative as
  *"not found by method X"*, never as *"does not exist"*.
- **Acceptance is the wire-string table, not file or line similarity.** Line overlap between a
  package and its shipped module ranges 76%→38% while command tables stay near-identical.
- **Wire correctness is necessary but not sufficient.** Add a runtime-resolvability check.
  26 dangling references hid behind a near-perfect scorecard.
- **Ask what the software actually reads.** "Would GC accept our `.pkp`?" looked like a
  file-format question. GC reads a 61 MB catalogue built from an index, so *discovery* and
  *parsing* are separate gates that fail differently — and the library it reads is not the one
  in `Program Files`. Separate the steps before designing the test, or a null result means
  nothing.
- **Samples beat documentation.** Doc-only research recommended point-to-point converters and
  claimed Crestron's declarative layer stopped at a whitelist. Real files reversed both.
- **Calibrate before trusting a document.** Score it against facts you can already verify
  (finding 09's declared-transformation control group) before relying on it for what you can't.
- Research runs as multi-agent workflows with an adversarial verifier per dimension. Several
  agents submitted placeholder stubs; verifiers caught every one. Treat unverified claims as
  provisional.
