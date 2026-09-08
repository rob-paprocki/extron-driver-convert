# Status

**Last updated: 2026-09-08.** Read this first. Everything below is measured unless
marked otherwise.

## Answers

| question | answer |
|---|---|
| Extron `.pkp` → ControlScript `.py`? | **Yes — built and measured.** `tools/pkp2cs.py`. |
| ControlScript `.py` → `.pkp`? | **Format: yes.** Byte-identical NRBF round-trip on all 4 packages, and **GC ingests a package our writer produced — including a mutated one** (finding 12). A *synthesised* object graph is still untested. |
| Crestron `.pkg` → Extron ControlScript? | **Yes — built and measured** against Extron's own driver for the same device. |
| Crestron device driven by an Extron processor? | **Built and verified offline; untested on hardware.** `tools/pkp_build.py` + `experiments/skeleton_i20/` — 4 staged packages awaiting a GC system (finding 13). |
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
| 12 | **GC ingests packages we generate.** The gate is an index, not the file. Locates the real 6,644-package driver library. |
| 13 | **Crestron device -> Extron processor.** The i20's auto-switching is reserved preset numbers. Cross-vendor corroboration without a Crestron processor. |

## Tools — all tested, all standard library only

| tool | what it does | tests |
|---|---|---|
| `tools/pkp_dump.py` | Extron `.pkp` → JSON object graph. Every byte accounted for on all 4 packages. | 23 |
| `tools/pkg_dump.py` | Crestron `.pkg` → manifest + driver JSON. Real ECMA-335 metadata walk, no hardcoded offsets. | (in above) |
| `tools/wire_table.py` | **The acceptance oracle.** Normalised per-command wire table from *both* Python dialects. Unresolvable expressions become *counted* opaque markers, never guesses. | 34 |
| `tools/pkp2cs.py` | `.pkp` → ControlScript translator. Raises rather than degrading. | 56 |
| `tools/pkp_build.py` | **`.pkp` transplant builder.** Refuses to emit unless the unmodified donor round-trips byte-for-byte first; no bypass flag. | 36 |

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
4. **Does a *synthesised* `.pkp` load?** Finding 12 showed GC ingests a package our NRBF
   writer produced, and one we mutated — but every test descended from a real package's byte
   stream. Assembling an object graph from scratch is the untested step. The container, the
   index and the catalogue ingest are now known **not** to be the barrier.
5. **Catalogue acceptance is not a working driver.** Finding 12 got a generated package listed
   in Driver Manager. Placing it in a project, building, uploading, and controlling a device
   are each unproven. This is the same "necessary but not sufficient" trap as the wire table.

*Closed by finding 12: "only 4 oracle pairs, all Extron-authored."* The GC install carries
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
