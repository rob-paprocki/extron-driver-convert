# Status

**Last updated: 2026-09-23.** Read this first. Everything below is measured unless
marked otherwise. **What is left to do lives in `ROADMAP.md`; the machine it runs on is
described in `ENVIRONMENT.md`.**

## Answers

| question | answer |
|---|---|
| Extron `.pkp` → ControlScript `.py`? | **Yes — built and measured.** `tools/pkp2cs.py`. |
| ControlScript `.py` → `.pkp`? | **Format: yes. Command surface: yes.** Byte-identical NRBF round-trip on all 9 packages; GC loads and selects a transplanted package (findings 12, 16, 18); and `tools/pkp_asset.py` now **adds commands to the object graph** — 19 added to the i20 package in `20024` (34 commands), 30 in today's `20028` (45; two were merged into one in `20027`), all 15 originals unchanged (finding 18). `20028` also gives each model its own command list, so the IV-CAM-I12 does not offer the three I20-only commands. GC renders every one, with the exact ranges and enum states written into the graph (finding 18 §8), and a processor runs them (next row but one). |
| Crestron `.pkg` → Extron ControlScript? | **Yes — built and measured** against Extron's own driver for the same device. |
| Crestron device driven by an Extron processor? | **The `.pkp` runs on a processor; no real camera yet.** `20025` and `20026` built and uploaded from GC Pro to an IPCP Pro 360 and were controlled from a TLP Pro 725M against a PC playing the camera, with feedback following it both ways (`experiments/skeleton_i20/PROTOCOL.md`). `20028` (v1.6, parity with Crestron's own driver; 2026-09-23) is the current package, verified through Extron's loader but not yet uploaded. The drop-in ControlScript module has not run on a processor. Same wire table from both emitters (finding 13). |
| Extron → Crestron `.pkg`? | **Mechanically demonstrated** (resource-patched a real DLL). Gated by Crestron's dealer/partner licence, not by code. |
| Generate a driver from API docs alone? | **Mostly.** 29 of the 32 endpoints a real driver calls have their own documentation page (~91%), re-measured from saved files on 2026-09-23 (`experiments/docs_only/REMEASURE.md`); the earlier ~84% predated finding 08's correction. The other 3 are the ISO-record family: `ISORecordStatus` appears only inside another page's example, and `StartISORecord`/`StopISORecord` appear nowhere. The danger is silent incompleteness, not missing methods. |
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
| 10 | **The held-out result.** Rules built on four pairs, run untuned on three unseen: Biamp 63 of 74 on the wire but 51 dangling references; Clock Audio drops on the wire, and one of its two pairs set a MK3 package against the only shipped module, a MK I/II one. A resolution section (2026-09-23) confirms the Clock Audio mis-pairing: **67 of 81 held-out commands wire-match (82.7%) against 96.4% in-sample**, while fidelity to the source is 81 of 81. |
| 11 | A protocol **spec** refereed what two implementations could not; the wire oracle has its own false-positive rate. |
| 12 | **GC ingests packages we generate.** The gate is an index, not the file. Locates the driver library (size varies by install; see finding 16). |
| 13 | **Crestron device -> Extron processor.** The i20's auto-switching is reserved preset numbers. Cross-vendor corroboration without a Crestron processor. |
| 14 | **314 third-party oracle packages.** First run: 81.3% wire-match, but 25% of generated modules would raise `AttributeError` — and the broken ones score *higher*. **Re-scored and then executed, 2026-09-23 (§7, §8):** 80.8% wire-match, but **54% of generated modules would raise at runtime** once attributes nothing assigns and wrong argument counts are counted too, mostly on configuration values GC supplies and ControlScript does not. Counted fully, the broken modules score *lower* on the wire; the first run's inversion was an artefact of counting only missing methods. Running the modules found five translator bug classes no static check had seen. |
| 15 | **On hardware: `80085`.** A transplanted package is catalogued, then refused at selection. *Its proposed cause is superseded by finding 16.* |
| 16 | **`80085` is a SHA-256 mismatch.** Extron's validator reimplemented in pure Python; 1,900/1,919 exact agreement with their own code before its fixes, 1,853/1,853 shipping packages after them with the Guid table, so GC is no longer needed to check a package. |
| 17 | **How a human writes one.** A working integrator splices Extron's template from two vintages rather than authoring from scratch — the same instinct as our transplant. |
| 18 | **The asset tree is the command surface** — GC never asks the script what it can do, so a package can be `Valid` and silently short. Object-graph synthesis built and verified **through Extron's own deserializer** and in GCP itself; the i20 package goes 15 -> 34 commands. Carries the negative-object-id trap that no local check could see. |
| 19 | **The three-questions experiments** (written up 2026-09-23). Crestron `.pkg` → ControlScript works: 62 commands, 0 opaque. The `.pkp`'s never-shipped Ethernet script translates with 11 of 11 shared commands present and one wire difference, plus a dangling `ReadMultiviewString` that would raise at runtime with no residual reported (fixed 2026-09-23, R37). Docs-only generation covers 22 of 22 endpoints Extron implements, but 15 of its 33 commands wrote the raw response dict as a status (fixed, R32); 4 of its 6 "doc gaps" were gaps in our harvest. |

## Tools — all tested, all standard library only

| tool | what it does | tests |
|---|---|---|
| `tools/pkp_dump.py` | Extron `.pkp` → JSON object graph. Every byte accounted for on all 9 sample packages (each round-trips byte-for-byte in `test_pkp_build.py`). | 23 |
| `tools/pkg_dump.py` | Crestron `.pkg` → manifest + driver JSON. Real ECMA-335 metadata walk, no hardcoded offsets. | (in above) |
| `tools/wire_table.py` | **The acceptance oracle.** Normalised per-command wire table from *both* Python dialects. Unresolvable expressions become *counted* opaque markers, never guesses. | 47 |
| `tools/pkp2cs.py` | `.pkp` → ControlScript translator. Raises rather than degrading; reports what would fail at runtime as residuals: a missing method, an attribute nothing assigns, an unbound global, a call with an argument count nothing accepts. | 90 |
| `tools/pkp_build.py` | **`.pkp` transplant builder.** Refuses to emit unless the unmodified donor round-trips byte-for-byte first; no bypass flag. | 37 |
| `tools/pkp_validate.py` | **Extron's driver validator, in pure Python.** Same verdict as GC's own code on all 1,853 shipping packages when given Extron's Guid table (`--guid-table`), 1,850 without it; all 53 deliberate mutants, including the 8 that Extron refuses to load before validating (`REFUSED_BEFORE_VALIDATE`; re-run 2026-09-23, `experiments/validator_differential/POSTFIX.md`). No GC installed. | 182 |
| `tools/nrbf_graph.py` | **Structural navigation over an NRBF trace.** Every object id → its exact span of records, by replaying the reader's grammar. Verified end-to-end on all 9 packages, up to 4.4M events / 668k objects. | (with below) |
| `tools/pkp_asset.py` | **Adds commands to a `.pkp`'s object graph.** Clone/attach/detach of asset subtrees with computed ownership, so a shared string is never renamed and a donor is never damaged. Output confirmed loadable by Extron's own `LoadFromFile`. Per-model command lists can be trimmed (`CommandGraph.detach`). | 48 |
| `tools/pkg_patch.py` | **Replaces the driver definition inside a Crestron `.pkg`'s DLL.** In place, or grown within the section's slack with every RVA fixed up; refuses to grow beyond it. Authenticode detected and optionally stripped, never re-signed. | 11 |
| `tools/verify_vendor_files.py` | **Checks a local copy of the unpublished vendor material** against `vendor-files.manifest.tsv` (SHA-256 and size per file). Its test also fails if a listed file becomes tracked or stops being ignored. `tools/vendor_inputs.py` is how every suite skips, visibly, what needs a missing file. | 14 |
| `tools/gc_catalogue.py` | **What Global Configurator catalogued.** Reads `DriverLookup.dat` (raw NRBF); `--against` compares it with a driver folder. Failing the catalogue-parse gate shows only as absence — this measures it. | 14 |
| `experiments/skeleton_i20/` | **i20 driver, both forms.** `.pkp` transplant + standalone ControlScript module, held to identical bytes, every added frame matched against Crestron's resolved template. | 179 + 103 |
| `experiments/skeleton_p20/` | **P12/P20 driver, both forms**, from the i20 builders: `1bynd_19_20102` (38 commands), loads through Extron's loader. Not uploaded. | 69 |
| `experiments/oracle_pairs/` | **Finding 14's pair index and scorecard.** `build_index.py` reproduces the pair set exactly (314 packages, 352 pairs) from `corpus/`, with five named, evidenced corrections (`OVERRIDES`); `score.py` counts `AttributeError` and `NameError` beside the wire table. | 26 |
| `experiments/loopback/` | **A processor drives the i20 module at a PC.** A command console on the processor, a VISCA listener playing the camera, and an orchestrator checking every step's frames and reads against the module run locally. Rehearsed end to end offline. Path A (ControlScript) needs the Deployment Utility and a certified project; Path B drives the synthesised 20028 from a Global Configurator macro. Found two reply-parser bugs before any hardware. | 116 + 19 |
| `experiments/exec_harness/` | **Runs generated modules offline.** A stand-in extronlib records every `Send`; each generated module and Extron's shipped module for the same device get the same inputs, taken from their own method bodies, and the outcomes are compared. Found the bug classes no static check could see (ROADMAP R13). | 8 |
| `experiments/gcp_harness/` | **Windows-only.** `Load-Package.ps1` asks Extron's own `LoadFromFile`/`BinaryFormatter` about a package; `scratch/` is the verified UI Automation chain that drove GCP. PowerShell because Python cannot load the x86 Extron assemblies without a third-party bridge. | manual |

Experiments live in `experiments/` (NRBF writer, Crestron→ControlScript, missing-Ethernet
generation, docs-only generation, oracle pairs, graph probes and cross-package cloning,
a sweep of all 1,854 corpus packages, Ross Ultrix, GCP harness).
Our indexes and analyses of vendor docs in `reference/`. **`corpus/` holds a snapshot of
an Extron library** (1,854 `.pkp`, 2,235 ControlScript modules), so findings 14, 16 and 17
reproduce off that machine — given the snapshot. `evidence/` holds the screenshots and
logs the findings cite.

**The repository is public and publishes no vendor material** (since 2026-09-24): the
samples, the corpus, harvested vendor pages, GC catalogue captures and the packages built
from vendor ones are untracked, pinned by SHA-256 in `vendor-files.manifest.tsv`
(`tools/verify_vendor_files.py` checks a copy). In a clone without them, every suite runs
what it can and skips the rest, naming the missing file. Earlier commits still contain them.

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
   shortcut is not. **Crestron Toolbox is obtainable** (see `ENVIRONMENT.md`), so
   the tool is no longer the gate — a processor or VC-4 instance is, plus the
   licence question below. *No amount of research substitutes for this.*
2. **Crestron's licence** restricts its tools to "Developing software for Crestron Devices",
   bars reverse engineering, and requires a Dealer/AIP/Partner agreement. Extron requires a
   free account with no field-of-use limit. A lawyer's question, cheaper to ask before building
   an emitter than after.
3. **Catalogue coverage.** How much of Crestron's library is the extractable JSON-engine form
   versus V2 Entity Model versus V1 RAD? Two data points so far: Samsung = LegacyWrappers JSON
   engine, 1 Beyond = V2 with a **bounded, named** IL residue. `drivers.crestron.io` is
   login-gated, so this can only be answered by sampling.
4. ~~**Does GC render a command we added to the object graph?**~~ **Closed by finding 18.**
   `1bynd_19_20024` carries 34 command assets where the donor had 15; Driver Manager lists
   it, it assigns to an Ethernet port, and the editor renders every command with the exact
   decimal ranges and enum states written into the graph — verified by driving GCP over UI
   Automation. Since closed further: `20025` **built and uploaded** to an IPCP Pro 360 and
   drove a PC playing the camera, and `20026` closed the feedback half — a panel's readouts
   follow statuses the synthesised assets added (2026-09-18). **What remains is a real i20:**
   no socket has been opened to a camera, so every reply parsed came from the documentation.
   GCP's licence is a rolling 30 days, renewed whenever it starts online (`ROADMAP.md` D7).
5. **A rendered command is not a polled one.** A package can render, build, upload and send
   correctly and still never be *asked* anything, because polling is gated twice: the
   command's `PollingInterval` must carry `Enabled` (`1bynd_19_20026`), **and** the project
   must contain an instance of it — GC compiles its poll list from panel feedback, monitors
   and macros, not from the driver's command list. Both gates were hit in turn, each looking
   like the package was wrong. Same "necessary but not sufficient" trap as the wire table,
   two gates further along.

6. **Emulated feedback where the device publishes nothing — now down to one.** In `20024`
   7 of the 19 added commands polled a VISCA inquiry and 12 were emulated, because the
   documented 47-inquiry set had nothing to read for them. Crestron's own driver did:
   `CRESTRON_PARITY.md` read its 18 reply rules, and `20028` (v1.6) polls through them. Of
   the 30 commands it adds, **21 report live status**, 8 are momentary actions with nothing
   to report, and **only the lightbar is emulated** — neither vendor's driver nor the
   documentation has an inquiry for it. One reply rule is still unsourced: Crestron
   declares none for `GetFreezeFrame`, so that parse follows VISCA's convention.

*The "only 4 oracle pairs" item was closed by finding 14: 352 pairs across 314 packages,
scored.* Finding 12 counted **6,644 `.pkp`** in one GC install; the snapshotted library held
1,854, and that library is kept under `corpus/` (untracked, hash-pinned). The sampling
problem is a selection problem.

## Standing methodology notes

- **A negative claim needs positive evidence.** Finding 08 twice asserted an endpoint was
  undocumented when it was not — first from keyword-search enumeration, then from assuming a
  URL-naming convention was exhaustive. Where no published index exists, report a negative as
  *"not found by method X"*, never as *"does not exist"*.
- **Acceptance is the wire-string table, not file or line similarity.** Line overlap between a
  package and its shipped module ranges 76%→38% while command tables stay near-identical.
- **Wire correctness is necessary but not sufficient.** Add a runtime-resolvability check.
  26 dangling references hid behind a near-perfect scorecard. It has more than one shape:
  a missing method, a missing global, an attribute nothing assigns, a wrong argument count
  — four static checks now — and some no static check sees (a stripped `@staticmethod`, a
  re-entrant `OnConnected`). **Run the code.** The last two checks exist because executing
  the generated modules (R13) found them; counted fully, 54% of finding 14's modules would
  raise, not the 15% the first two checks showed.
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
