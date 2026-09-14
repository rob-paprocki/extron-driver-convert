# corpus/

A snapshot of one Extron driver library, committed so that the experiments
measured against it reproduce on any machine — and so the library outlives the
Global Configurator licence it was taken from.

**Vendor material, same terms as `samples/`:** the repo stays private and these
files are not redistributed.

| folder | what it is | contents | size |
|---|---|---|---|
| `extron-driver3/` | a GC driver library (`<DRIVER_LIB>`) | 1,854 `.pkp` + 26 `.eir` + GC's catalogue (`DataFile.dat`, `DriverLookup.dat`) | 522 MB |
| `extron-gs-modules/09062026/` | the GS ControlScript module shipment | 2,235 ControlScript modules (`.py`) | 54 MB |
| `extron-features/` | install version stamps | GCP `3.33.0-b.38`, GUI Designer `1.27.0-b.9` | 2 KB |

**Integrity.** Every one of the 6,354 files copied was SHA-256 compared against
its original: 0 missing, 0 differing, 0 extra.

## Is it committed, or is it a dependency?

Not everything a vendor ships needs to live in git. The test is simple: **does
a finding's result depend on these exact bytes?** If yes it is committed, because
a re-download is not guaranteed to reproduce it. If no it is an external
dependency, recorded in a manifest and fetched on demand.

| material | verdict | why |
|---|---|---|
| `extron-driver3/` `.pkp` and `.eir` | **committed** | Findings 14, 16 and 17 are pinned to this exact set. Finding 16's "1,900 of 1,919 agreed" is a statement about these packages; a different library gives a different denominator. |
| `extron-driver3/` catalogue `.dat` | **committed** | A point-in-time capture. GC truncates both before rebuilding, so they cannot be recovered after the fact. |
| `extron-gs-modules/**/*.py` | **committed** | `experiments/oracle_pairs/` reads them directly; finding 14's 352 pairs are drawn from them. |
| `extron-gs-modules/**/*.pdf` (comm sheets) | **external dependency** | Documentation only. Verified: no tool, test or finding in this repo reads one. They were 732 MB — larger than everything else here combined. `comm-sheets.manifest.tsv` records all 2,235 (`sha256`, `size`, `path`) so a specific sheet can be re-obtained from Extron and verified. |
| ControlScript `.vsix` | **external dependency** | A pinned VS Code Marketplace download. `ROADMAP.md` R13 already treats it as external, and its unpacked form is git-ignored. |

Note the `.pdf` references in `tools/pkp_validate.py` and findings 13 and 16 are
about a comm sheet **embedded inside a `.pkp`'s own asset tree** — a different
thing entirely, and unaffected by the above.

## Things to know before using it

- **The library differs by install.** Finding 12 counted 6,644 `.pkp` + 1,745
  `.eir` on another machine; this snapshot holds 1,854 + 26. Measure, don't quote.
- **`extron-driver3/` contains one package we built:** `1bynd_19_20024_v1_0_0.pkp`,
  installed there for the finding 18 GCP test. Everything else is Extron's. Any
  future "externalize the corpus" effort must not silently treat it as vendor
  material. It is the build GC rendered; `experiments/skeleton_i20/out/` has
  since been rebuilt with two reply-parser fixes, with an identical command
  surface (`experiments/skeleton_i20/PROTOCOL.md`).
- **The catalogue files are a point-in-time capture.** They already index
  `1bynd_19_20024`. Both are raw NRBF and parse with `tools/pkp_dump.py` (see
  `tools/gc_catalogue.py`).
- **Donor packages are not all here.** `1bynd_19_4743` — the i20 donor — is in
  `samples/`, not in this library.

## What reads it

| consumer | how |
|---|---|
| `experiments/oracle_pairs/build_index.py`, `score.py` | default `--drivers`/`--modules` point here, falling back to a live GC install |
| finding 14 (third-party oracle pairs) | the pair set was built from this library |
| finding 16 (validator differential, 1,919 packages) | the 1,853 shipping packages were this library |
| finding 17 §6 (Ross Ultrix) | `extron-driver3/ross_15_3280_v1_3_2.pkp` |

## Restoring it onto a workstation

Copy `extron-driver3/*` into the GC driver library (`<DRIVER_LIB>` in
`ENVIRONMENT.md`) and `extron-gs-modules/*` alongside it. **Back up the existing
`DataFile.dat` and `DriverLookup.dat` first** — GC truncates both before it
rebuilds, so an interrupted start leaves 0 bytes (finding 12).
