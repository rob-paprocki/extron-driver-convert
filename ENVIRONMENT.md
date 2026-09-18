# Environment

What a workstation needs in order to run the parts of this project that cannot
run anywhere else, and how to set one up.

**Most of this project needs none of it.** Everything in `tools/`, every test
suite, and every experiment except the final loader gates runs on any OS with
Python 3.11+ and the standard library — no packages, no `requirements.txt`, no
compiled dependency. Reach for this file only when you hit one of the
machine-bound capabilities below.

Conventions used here:

| placeholder | usual value |
|---|---|
| `<GCP_DIR>` | `C:\Program Files (x86)\Extron\GCP` |
| `<DRIVER_LIB>` | `C:\Users\Public\Documents\extron\Driver3` |
| `<PS32>` | `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe` |

Everything else is written repo-relative. Paths naming a particular checkout,
user account or drive letter do not belong in this repo.

## What needs a workstation, and what does not

| Capability | Needs | Used by |
|---|---|---|
| `tools/`, all test suites, corpus reproductions | Python 3.11+ only | most of `ROADMAP.md` §2 |
| `Load-Package.ps1` (`LoadFromFile` / `BinaryFormatter`) | Extron 15.27 DLLs + 32-bit PowerShell. **No licence needed.** | R26–R28, R30 |
| Extron's validator on new packages and mutants; IL caller scans | Extron DLLs + `csc.exe` to rebuild the C# harnesses | R9, the §5 caller scan |
| GCP render check over UI Automation | **A licensed GCP install**, and nobody else using the mouse | R23, R24, R26–R28 |
| GCP Build and Upload | A licence, plus a processor for Upload | H0, H4 |
| Crestron-side work | Crestron Toolbox | H8 |

## Required software

| component | version | why it matters |
|---|---|---|
| Windows | 10 or 11 | the Extron assemblies are Windows-only |
| Extron **Global Configurator Pro** | 3.33.0.38 or later | the loader, validator and render gates |
| **32-bit** PowerShell 5.1 | at `<PS32>` | Python cannot load the x86 Extron assemblies without a third-party bridge, which the no-dependency rule excludes. Note it lacks `Get-FileHash`. |
| Python | 3.11+ | stdlib only; verified on 3.11.9 and 3.14.7 |
| .NET | Framework 4.8 | the C# harnesses in `experiments/validator_differential/` target Framework 4.8 x86 |
| Crestron Toolbox | any recent | only for the Crestron-side items |
| `gh` CLI | any recent | convenient for auth; not required |

## The binaries the findings are measured against

These identities are **load-bearing**. Findings 15, 16 and 18 are about whether
a specific validator accepts a package, so the exact build matters. If your
hashes differ you are measuring a different program, and a differing result is
not automatically a contradiction.

`Extron.Configuration.*` are version `15.27.0.0`, x86, .NET Framework 4.8, as
shipped with GCP `3.33.0.38`:

```
05bee78d49730d6bf17cd96ee3ebe7e5d85155e7660c022e98e5171857882e35  GCP.exe
c478fc26ed21561c70df15c7c8bebb41b2254e3d2c9046489191d0905bbd5f65  Extron.Configuration.Drivers.dll
2a99217b2567b08f854a88d04e6ffe9084818d17462c51598efa3ad4b8343848  Extron.Configuration.Contracts.dll
22b34c46f7155d2e5aafd6931c993ae42aca4cc931d8d1f04bf944f4bd973b3a  Extron.Configuration.Core.dll
```

A `.pkp` stream names `Extron.Configuration.* 1.1.24.402`. Deserializing one
outside GC needs an `AssemblyResolve` handler mapping that onto the installed
`15.27.0.0`; `experiments/gcp_harness/lib/Extron.ps1` does this.

## The driver library

**Global Configurator reads `<DRIVER_LIB>`, not the packages under `<GCP_DIR>`.**
It is user-writable and needs no elevation.

**Its contents vary by install — measure, never quote.** One install has been
observed holding 6,644 `.pkp`; another 1,853. That variation is a sampling
problem, not an error. `tools/gc_catalogue.py` measures what GC actually
catalogued.

Back up `DataFile.dat` and `DriverLookup.dat` before touching the folder: GC
truncates the catalogue before rebuilding it, so an interrupted start leaves a
0-byte file. Both are raw NRBF and parse with `tools/pkp_dump.py`, so whether GC
catalogued something is directly checkable. Read finding 12 first.

A SHA-256-verified snapshot of one such library is committed under `corpus/`,
and `experiments/oracle_pairs/` reads it by default — so findings 14, 16 and 17
reproduce with no Extron install at all.

## Setting up a workstation

1. Install Global Configurator Pro and sign in.
2. Install Python 3.11 or later. No packages are needed.
3. Restore the library if a fresh install lacks packages a finding cites: copy
   `corpus/extron-driver3/*` into `<DRIVER_LIB>`, **after backing up that
   folder's `DataFile.dat` and `DriverLookup.dat`.**
4. Install Crestron Toolbox, for the Crestron-side items only.
5. Rebuild the validator harnesses, for finding-16 work:
   `C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /platform:x86 Harness.cs`
   (and `Dir.cs`, `Mutate.cs`, `Reflect2.cs`) in
   `experiments/validator_differential/`.
6. Unpack the ControlScript `.vsix` into `tools/out/vsix` if you need the
   `extronlib` stubs — see `ROADMAP.md` R13.
7. Run the test suites, below.
8. Run the acceptance check, below.

### Tests

All standard library, no pytest. Run each directly; add `python -u` if piping.

```
python -u tools/test_pkp2cs.py
python -u tools/test_wire_table.py
python -u tools/test_pkg_dump.py
python -u tools/test_pkp_build.py
python -u tools/test_pkp_validate.py
python -u tools/test_pkp_asset.py
python -u tools/test_gc_catalogue.py
python -u experiments/nrbf_writeback/test_nrbf_write.py
python -u experiments/crestron2cs/test_crestron2cs.py
python -u experiments/skeleton_i20/test_i20_wire.py
python -u experiments/skeleton_i20/test_i20_cs_wire.py
python -u experiments/oracle_pairs/test_build_index.py
python -u experiments/loopback/test_visca_listener.py
python -u experiments/loopback/test_run_loopback.py
```

**624 tests.** `test_pkp_build.py` and `test_pkp_validate.py` walk every sample
package, including a 4.4M-event one — expect roughly 13 and 5 minutes
respectively, and about 20 minutes for the whole set.

### Acceptance check

```
<PS32> -ExecutionPolicy Bypass -File experiments/gcp_harness/Load-Package.ps1
    -Path experiments/skeleton_i20/out/1bynd_19_20027_v1_0_0.pkp -Commands
```

**33 commands on each of `IV-CAM-I12` and `IV-CAM-I20`, exit 0** means the
workstation can read what this project builds.

## Troubleshooting

None of these is guaranteed to appear, and at least one is known not to appear
on every machine. Treat each as "if you see this, here is the fix."

- **Git asks for credentials, or hangs on an invisible prompt.** Git Credential
  Manager has been seen hanging on one machine and working with no prompt at all
  on another. If it hangs, push with
  `GIT_ASKPASS=experiments/gcp_harness/askpass.sh GIT_TERMINAL_PROMPT=0`, which
  answers from `gh auth token` per command without putting the secret in argv.
  If plain `git fetch` already works, you do not need any of it.
- **"dubious ownership".** Git refuses a repo on a network share until it is
  added to `safe.directory`. Applies to checkouts on a share, not local disks.
- **Commit identity.** Git needs `user.name` and `user.email` and cannot always
  auto-detect them.
- **A generated module will not parse.** Provenance paths written into generated
  output are repo-relative by design. An absolute Windows path in a docstring
  puts a backslash escape (`C:\Users` → `\U`) into a non-raw string and raises
  `SyntaxError`. See `crestron2cs.provenance_path()`.

## Related

- `notes/2026-09-pack-up.md` — the record of one workstation being retired in
  September 2026 and its files moved into this repo. History, not current state.
- `private/` is git-ignored and never pushed: application settings carrying
  licence and account data, plus session records carrying full tool output. It
  is not needed to work on anything in this repo.
