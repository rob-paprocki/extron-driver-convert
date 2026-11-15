# Automate VX: three-way verification

Extron's Automate VX Pro driver (GC package `1bynd_42_4279` v1.0.11 and ControlScript module
v1.0.11.0), Crestron's SIMPL module (`1Beyond Automate_VX` v1.2) and native IP ID control, and
the live Automate VX API documentation, compared call by call. Finding 20 summarises it.

| file | what |
|---|---|
| `REPORT.md` | the verification: summary, one row per API call across all sources, request and response comparison, 37 discrepancies, details |
| `discrepancies.json` | the 37, each with category, severity, evidence and the verifier's verdict |
| `LIVE_TESTS.md` | the calls that settle what only a live unit can (extends ROADMAP H6) |
| `surfaces.py` | `extract`, `params`, `toc`, `probe`: every measurement the report rests on |
| `crestron_module.py` | `list`, `extract`, `interface`, `library`: Crestron's module read from an installed device database (§8) |
| `test_surfaces.py` | pins the offline facts: one 33-URI set in both Extron drivers, the GC parameter types, the Crestron wrapper building no requests |
| `probe_names.txt`, `probe_results.txt` | the page names probed on the documentation site (2026-09-24) and their HTTP status in both URL shapes |
| `BUILD.md` | the improved ControlScript module (v1.1): ten fixes and six documented additions to Extron's v1.0.11.0, what each changes, what is not proven |
| `build_avx_cs.py` | derives it from Extron's module by named edits (needs Extron's module, untracked) |
| `out/onebynd_sm_Automate_VX_Series_v1_1_0_0.py` | the derived module (tracked, as generated modules are) |
| `test_avx_cs.py` | runs it against a stand-in unit on 127.0.0.1: every fix and addition, and the same requests as Extron's module for valid calls |

The samples, the extracted GC script (`1bynd_42_4279.embedded.py`) and the documentation pages
are vendor material and are not tracked. Without them the vendor-dependent tests skip.

The Crestron module's `.csp` (in the installed device database's `crssplus.dat`) is a SIMPL+
wrapper over a compiled SIMPL# library (REPORT.md §8). `crestron_module.py extract` writes the
readable parts to `crestron/`, git-ignored. The library's requests come from decompiling it
(REPORT.md §10); `experiments/crestron_decompile/decompile.py` repeats that, given ILSpy's
`ilspycmd`, into a git-ignored folder.
