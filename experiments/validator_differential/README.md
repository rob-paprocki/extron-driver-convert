# validator_differential/

The workspace behind **finding 16**: how Extron's own `DriverAssetValidator` was
called directly, and how `tools/pkp_validate.py` was tested against it. Kept
verbatim from the 2026-09 working session that produced it.

**Not published (since 2026-09-24):** the mutant packages (`m2/`…`m6/`, `out/`,
`b/`, `junk/`, `extval/mutants/`), `ilres/ExtronDH.dat` (a resource of Extron's
assembly), `guidtable.tsv` (extracted from it), and `b/dump.json` /
`b/new_driver.py` are Extron material or built from it, so they stay on the
owner's machine; `vendor-files.manifest.tsv` pins each one. The harness
sources, scripts, lists and every verdict file (`real_all.txt`, `oracle_*.tsv`,
`py_*.tsv`) are ours and tracked, so the differential's results remain
readable; re-running it needs the inputs.

## The harnesses (C#, .NET Framework 4.8, x86)

All four load Extron's assemblies from `C:\Program Files (x86)\Extron\GCP`
with an `AssemblyResolve` handler — the same trick as
`experiments/gcp_harness/lib/Extron.ps1`, which later replaced them for
one-off checks.

| source | built as | what it does |
|---|---|---|
| `Harness.cs` | `harness.exe` | deserializes each package and calls `DriverAssetValidator.Validate`; one line of verdict per file — produced `real_all.txt` |
| `Dir.cs` | `dir.exe` | inspects the validator's GUID table: empty on a fresh instance, 4,775 entries after `LoadDefaultFromResource()` (finding 16 §5c) |
| `Mutate.cs` | `mutate.exe` | builds the deliberate mutants in `m2/`…`m6/` and `out/` by editing the deserialized object and re-serializing it |
| `Reflect2.cs` | `reflect2.exe` | dumps fields and properties of the driver asset types — how `_resourceHashDict` was found |

Rebuild a harness with the 32-bit framework compiler, e.g.

    C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /platform:x86 Harness.cs

## Inputs and results

| file | lines | content |
|---|---|---|
| `all_pkp.txt` | 1,853 | every shipping `.pkp` on the box — now `corpus/extron-driver3/` |
| `sample_pkp.txt`, `sample_eir.txt` | 300, 26 | the sampled subsets used while developing |
| `real_all.txt` | 1,853 | **Extron's** verdict per package (`code name file`) |
| `py_all.tsv` | 1,853 | **`pkp_validate.py`'s** verdict per package, from `runpy.py` |
| `guidtable.tsv` | 4,776 | the 4,775-entry GUID table from the validator's embedded `ExtronDH.dat` |
| `b/`, `dirtest/`, `junk/`, `m2/`…`m6/`, `out/` | ~80 `.pkp` | the mutants: hash refreshed/stale, `.eir` renames, dropped manifests, null dictionaries, malformed streams |

Comparing `real_all.txt` with `py_all.tsv`, plus the mutants, is the
"1,900 exact agreements of 1,919" in finding 16. The paths inside the list
files point at `C:\Users\Public\Documents\Extron\Driver3`; to re-run anywhere,
rewrite them to `corpus/extron-driver3/`.

`b/dump.json` and `b/new_driver.py` are the i20 transplant experiment that
first showed a refreshed digest makes a replaced script `Valid`.

## extval/ — the mutant differential, Python side

Recovered from scratch space during the 2026-09 pack-up. Where `m2/`…`m6/` above
were built by `Mutate.cs` inside .NET, these were built by
`extval/make_mutants.py` from three sample packages — DSC 12G-HD, the Samsung
display and Biamp Tesira — and then scored by both validators:

| file | content |
|---|---|
| `make_mutants.py`, `mutant_list.txt`, `mutant_notes.tsv` | how each of the 53 mutants in `mutants/` was made, and why |
| `oracle.ps1` | runs Extron's validator over a list; `oracle_plain.tsv` / `oracle_guid.tsv` are without / with the GUID table loaded |
| `oracle_mut*.tsv`, `py_mut.tsv` | Extron vs `pkp_validate.py` on the mutants |
| `oracle_case.tsv`, `py_case.tsv`, `case_list.txt` | the `.eir` suffix and case-sensitivity tests (finding 16 §5b) |
| `temp_a`, `temp_b` | two byte-identical raw outputs of that `.eir` test, found loose in `Temp\` as `a` and `b` |
| `py.tsv`, `run_py.py`, `list.txt`, `all_mut.txt`, `small.*` | the Python side and its inputs |
| `probe*.ps1`, `p3.ps1`, `dbg.ps1`, `guidprobe.ps1`, `nulltest.ps1`, `smoke.ps1` | the probes that shaped `oracle.ps1` |

## ilres/ — reading the validator's IL, and the GUID table

Recovered from scratch space during the 2026-09 pack-up.

- **`ExtronDH.dat`** (534,939 bytes) is the resource embedded in
  `Extron.Configuration.Drivers.dll` 15.27.0.0 that `LoadDefaultFromResource()`
  reads: the 4,775-entry GUID table of finding 16 §5c. It can only be
  re-extracted (`dh.ps1`) while that GCP version is installed, which is why it
  is kept. Vendor material, private repo.
- `tokens.ps1`, `resolve.ps1`, `callers.ps1`, `xcallers.ps1`, `xc2.ps1`,
  `core*.ps1`, `fn*.ps1`, `more.ps1` resolve IL metadata tokens and search for
  callers — how `ComputeHash(Stream)` was found not to be on `Validate`'s path.

## scratch/

The first direct probes of the validator and the hash refresh
(`probe_*.ps1`, `validate*.ps1`, `refresh_hash.ps1`, `v3.ps1`, `v4.ps1`,
`il.ps1`, `reflect.ps1`), `insp*.py` inspecting the resource-hash dictionary
through `pkp_dump`, and `dis.py`, a hand-rolled disassembler for one validator
method body. All recovered from scratch space; superseded by
the harnesses above and by `tools/pkp_validate.py`.
