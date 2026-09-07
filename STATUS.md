# Status

**Last updated: 2026-09-07, during an unattended session.**
Read this first — it says what is known, what is being built, and what is still open.

## The short version

| question | answer |
|---|---|
| Extron `.pkp` → ControlScript `.py`? | **Yes.** A Python-to-Python translation, not a format decode. |
| ControlScript `.py` → `.pkp`? | **No.** Not a practical, repeatable capability. |
| Crestron `.pkg` → Extron? | **Yes**, for JSON-engine drivers. Coverage across the catalogue is the open question. |
| Extron → Crestron `.pkg`? | **Plausible and partly demonstrated.** Blocked by Crestron's dealer/partner gate, not by code. |
| Is a shared intermediate representation justified? | **Yes** — two vendors independently encode the same device to the same bytes, including its bugs. |

## Findings (all in `findings/`)

- **01** — a `.pkp` is gzip over a .NET BinaryFormatter (NRBF) stream, and it *embeds a complete
  Python driver*. That reframed the whole project.
- **02** — verdict on `.pkp` → ControlScript. ~76% of the shipped module's lines appear verbatim
  in the package's embedded Python; ~10 AST rewrite rules and a fixed template close the gap.
- **03** — a Crestron `.pkg` is a zip whose real driver definition is plain JSON embedded in the DLL.
- **04** — Crestron interop verdict, plus the licensing position.
- **05** — the Samsung cross-vendor result: byte-identical wire traffic, *and the same undocumented
  firmware-bug workaround*, from two independent vendor teams.
- **06** — emitting a `.pkg` (demonstrated by patching a real DLL), and how far the Extron converter
  generalises to third-party hardware.

## Tools

- `tools/pkp_dump.py` — Extron `.pkp` → JSON. Parses both original samples with every byte
  accounted for.
- `tools/pkg_dump.py` — Crestron `.pkg` → JSON. Real ECMA-335 metadata parsing, no
  hardcoded offsets. 23 tests.
- `tools/wire_table.py` — the acceptance oracle. Extracts a normalised per-command
  wire table from **both** Python dialects so they can be diffed. Unresolvable
  expressions become *counted* opaque markers, never guesses. 34 tests.
- `tools/pkp2cs.py` — the `.pkp` → ControlScript translator. 25 tests.

**Translator scorecard** (validated independently, every difference traced to source):

| pair | shipped | generated | matching | differing |
|---|---|---|---|---|
| DSC 12G-HD | 29 | 29 | 28 | 1 — Extron's own `LogoAssignment` bug |
| DTP3 CP 42 | 31 | 29 | 27 | 1 + real version skew |
| Samsung serial | 9 | 9 | **9** | **0** |
| Automate VX | 18 | 18 | 17 | 1 — package omits `Scenario` params |

## Plan for this session

1. **1 Beyond DLL analysis** *(running)* — the new camera drivers are 145 KB with no
   `LegacyWrappers` and no `Crestron.RAD` reference, versus Samsung's 16 KB shells. Do they carry
   real compiled logic? This decides whether "Crestron in" generalises or covers only a subset.
2. **SIMPL `.cmc` analysis** *(running)* — finding 04 ruled the SIMPL family out on documentation.
   The Automate VX macro is plain ASCII, so that ruling is now testable against a real file.
3. **Automate VX three-way** *(running)* — Crestron-branded hardware with an Extron driver, the
   mirror of the Samsung case.
4. **Build the `.pkp` → ControlScript translator** — **done**, see the scorecard above.
5. **VISCA gap-reconstruction experiment** *(running)* — can vendor documentation close a
   precisely-known compiled-code gap? Calibrated against the 27 *declared* transformations, whose
   answers are visible in the driver JSON, before trusting it on the 6 that are IL-only.

## Open blockers, in order of how much they matter

1. **Does an outsider-built `.pkg` actually load?** Independent developers ship drivers built from
   the public NuGet DevKit, so the compile path is demonstrated. The resource-swap shortcut is not.
   Testing needs Crestron Toolbox or VC-4, both dealer-gated.
2. **Crestron's licence** limits its tools to "Developing software for Crestron Devices", bars
   reverse engineering, and requires a Dealer/AIP/Partner agreement. Extron requires only a free
   account and imposes no field-of-use limit. A lawyer's question, worth asking before building an
   emitter rather than after.
3. **Catalogue coverage** — how much of Crestron's driver library is the extractable JSON-engine
   form? `drivers.crestron.io` is login-gated, so this can only be answered by sampling. The
   1 Beyond drivers are the first data point beyond Samsung.

## Standing methodology notes

- **Acceptance is defined on the wire-string table, not on file or line similarity.** Shipped
  modules are not a pure function of their package — there is version skew, hand-edits and dropped
  throttles. Two samples now show line overlap varying from 76% to 38% while the command tables stay
  nearly identical.
- **Samples beat documentation.** Doc-only research recommended point-to-point converters and said
  Crestron's declarative layer stopped at a whitelist. Real files reversed both conclusions.
- Research runs as multi-agent workflows with an adversarial verifier per dimension. Several agents
  have submitted placeholder stubs; the verifiers caught every one. Treat any unverified claim as
  provisional.
