# corpus/

A snapshot of the Extron library that lives on the Windows box, copied here on
2026-09-11 so the experiments that measured against it reproduce on any
machine — and so the library survives the Global Configurator licence, which
expires in early October 2026.

**Vendor material, same terms as `samples/`:** the repo stays private and these
files are not redistributed.

| folder | source on the Windows box | contents | size |
|---|---|---|---|
| `extron-driver3/` | `C:\Users\Public\Documents\extron\Driver3` | 1,854 `.pkp` + 26 `.eir` + GC's catalogue (`DataFile.dat`, `DriverLookup.dat`) | 522 MB |
| `extron-gs-modules/09062026/` | `C:\Users\Public\Documents\extron\GS_Modules\09062026` | 2,235 ControlScript modules (`.py`) + 2,235 comm sheets (`.pdf`) | 788 MB |
| `extron-features/` | `C:\Users\Public\Documents\extron\Features` | install version stamps: GCP `3.33.0-b.38`, GUI Designer `1.27.0-b.9` | 2 KB |
| `vendor-tooling/` | `C:\Users\robp\Downloads` | `controlscript-1x13x0-6.vsix` — Extron's ControlScript VS Code extension | 15 MB |

**Integrity.** Every one of the 6,354 files was SHA-256 compared against its C:
original after copying: 0 missing, 0 differing, 0 extra.

## Things to know before using it

- **The library differs by install.** Finding 12 counted 6,644 `.pkp` + 1,745
  `.eir` on another machine; this box held 1,854 + 26. Measure, don't quote.
- **`extron-driver3/` contains one package we built:** `1bynd_19_20024_v1_0_0.pkp`,
  installed there for the finding 18 GCP test. Everything else is Extron's.
- **The catalogue files are a point-in-time capture.** `DataFile.dat` and
  `DriverLookup.dat` are what GC wrote after its last rebuild on 2026-09-10,
  i.e. they already index `1bynd_19_20024`. Both are raw NRBF and parse with
  `tools/pkp_dump.py` (see `tools/gc_catalogue.py`).
- **Donor packages are not all here.** `1bynd_19_4743` — the i20 donor — is in
  `samples/`, not in this install's library.

## What reads it

| consumer | how |
|---|---|
| `experiments/oracle_pairs/build_index.py`, `score.py` | default `--drivers`/`--modules` now point here, falling back to a live GC install |
| finding 14 (312 third-party oracle pairs) | the pair set was built from this library |
| finding 16 (validator differential, 1,919 packages) | the 1,853 shipping packages were this library |
| finding 17 §6 (Ross Ultrix) | `extron-driver3/ross_15_3280_v1_3_2.pkp` |

## Restoring it onto a GC machine

Copy `extron-driver3/*` back to `C:\Users\Public\Documents\extron\Driver3\` and
`extron-gs-modules/*` to `...\GS_Modules\`. **Back up the existing
`DataFile.dat` and `DriverLookup.dat` first** — GC truncates both before it
rebuilds, so an interrupted start leaves 0 bytes (finding 12).
