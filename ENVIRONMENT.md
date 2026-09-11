# Environment

What the Windows box looked like when this project was packed up on
2026-09-11, what was moved off its C: drive, and how to rebuild it. Read with
`ROADMAP.md` — several open items can only be done on a box like this one.

**The box was reimaged after the pack-up.** Every project-related file that
lived on C: was moved here first: into git where it is safe to push, and into
the git-ignored `private/` folder where it carries account or licence data.

## The machine

A Parallels guest on a Mac, installed 2026-09-07. `Z:` is the Mac home share
(`\\Mac\Home`; `C:\Mac\Home` is a symlink to it), which is where this repo
lives: `Z:\GitHub\rob-paprocki\extron-driver-convert`.

| component | version / location | notes |
|---|---|---|
| Windows | 11 Pro 10.0.26200 | |
| Extron **Global Configurator Pro** | `3.33.0.38` (`GCP.exe` sha256 `05bee78d…882e35`) | `C:\Program Files (x86)\Extron\GCP`, 528 MB. **Licence expires early October 2026** — the status bar read "Expires in 30 Days" on 2026-09-09 and 2026-09-10 |
| `Extron.Configuration.Drivers.dll` | `15.27.0.0` (sha256 `c478fc26…bd5f65`) | x86, .NET Framework 4.8 |
| `Extron.Configuration.Contracts.dll` | `15.27.0.0` (sha256 `2a99217b…343848`) | |
| `Extron.Configuration.Core.dll` | `15.27.0.0` (sha256 `22b34c46…3b3a`) | |
| Extron GUI Designer | `1.27.0.9` | used by the separate `extron-gdl-toolkit` repo |
| Crestron Toolbox / SIMPL / Database / Device Database | `3.1390.0008.3` / `4.3200.02.01` / `228.55.001.00` / `200.465.001.00` | plus SIMPL+ Cross Compiler 1.3, MasterInstaller 4.00.11 |
| Python | **3.11.9**, `C:\Users\robp\AppData\Local\Programs\Python\Python311\`, on PATH in Git Bash | the 3.12.10 install recorded on 2026-09-07 is gone |
| PowerShell (32-bit) | 5.1, `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\` | required by `experiments/gcp_harness/`; lacks `Get-FileHash` |
| .NET | Framework 4.8; SDKs 8.0.424, 9.0.317, 10.0.400 | the C# harnesses in `experiments/validator_differential/` target Framework 4.8 x86 |
| Free space on `Z:` | ~150 GB of 466 GB | |

Full hashes for the four Extron binaries:

```
05bee78d49730d6bf17cd96ee3ebe7e5d85155e7660c022e98e5171857882e35  GCP.exe
c478fc26ed21561c70df15c7c8bebb41b2254e3d2c9046489191d0905bbd5f65  Extron.Configuration.Drivers.dll
2a99217b2567b08f854a88d04e6ffe9084818d17462c51598efa3ad4b8343848  Extron.Configuration.Contracts.dll
22b34c46f7155d2e5aafd6931c993ae42aca4cc931d8d1f04bf944f4bd973b3a  Extron.Configuration.Core.dll
```

## What moved off C:, and where it went

**Into git:**

| from (C:) | to (repo) | |
|---|---|---|
| `Users\Public\Documents\extron\Driver3\` | `corpus/extron-driver3/` | 1,854 `.pkp` + 26 `.eir` + catalogue, 522 MB |
| `Users\Public\Documents\extron\GS_Modules\09062026\` | `corpus/extron-gs-modules/09062026/` | 2,235 `.py` + 2,235 `.pdf`, 788 MB |
| `Users\Public\Documents\extron\Features\` | `corpus/extron-features/` | version stamps |
| `Users\robp\Downloads\controlscript-1x13x0-6.vsix` | `corpus/vendor-tooling/` | ControlScript VS Code extension |
| `Users\robp\extron_val\` | `experiments/validator_differential/` | finding 16's C# harnesses, mutants and results |
| `Users\robp\Pictures\Screenshots\2026-09\GCP_*.png` | `evidence/screenshots/` | the hand-taken GCP screenshots |
| Claude job dir `tmp\gcp1-4.png` | `evidence/screenshots/automation-gcp*.png` | UI Automation screenshots |
| Claude job dir `tmp\driver3_backup\` | `evidence/catalogue-snapshots/` | catalogue backups around the GCP runs |
| Claude upload `d7afbb28-Work.zip` | `evidence/uploads/2026-09-08-Work.zip` | contents already under `experiments/skeleton_i20/hardware/` |
| Claude job dir `tmp\*.log` | `evidence/test-logs/` | |
| Claude job dir `tmp\*.ps1`, `askpass.sh` | `experiments/gcp_harness/scratch/`, `experiments/gcp_harness/` | the UI Automation chain, verbatim |
| Claude job dir `tmp\probe_*`, `q_*`, `min_P*`, `compose_test.pkp`, `eirtest\` | `experiments/graph_probes/` | finding 18 s6 bisection, finding 16 s5b `.eir` pair |
| Claude job dir `tmp\score_pairs*.py`, `pair_index.py`, `residuals.py`, `scorecard*.json` | `experiments/oracle_pairs/scratch/` | finding 14 iterations |
| Claude job dir `tmp\ross_generated.py` | `experiments/ross_ultrix/` | finding 17 s6 |
| `Users\robp\AppData\Local\Temp\extval\`, `Temp\a`, `Temp\b` | `experiments/validator_differential/extval/` | finding 16's Python-side mutant differential and `.eir` test |
| `Users\robp\AppData\Local\Temp\ilres\` | `experiments/validator_differential/ilres/` | IL-resolution scripts and `ExtronDH.dat`, the GUID-table resource |
| `Temp\probe_*.ps1`, `validate*.ps1`, `refresh_hash.ps1`, `v3/v4.ps1`, `il.ps1`, `reflect.ps1`, `insp*.py`, `dis.py` | `experiments/validator_differential/scratch/` | finding 16's first probes |
| `Temp\gen_boiler.txt`, `tsl_boiler.txt`, `ca.txt`, `ts.txt`, `a.txt`, `fx.py`, `wt_probe.py` | `experiments/ross_ultrix/` | finding 17's template-splice evidence and wire-table probes |
| Claude workflow definitions and the finding 16 verifier verdicts | `tools/out/verdicts/workflows/` | how the multi-agent research runs were defined |

The corpus copy was SHA-256 verified file by file: 6,354 files, 0 mismatches.
The two `1bynd_19_20022`/`20023` builds left in the Recycle Bin (the ones tested
in GCP on 2026-09-09) are byte-identical to versions already in git history.

Found only because two independent sweeps went through `AppData\Local\Temp`,
which the first, time-based inventory had pruned as noise.

**Into `private/` (git-ignored, on Z: only):**

| from (C:) | to | why not in git |
|---|---|---|
| Claude Code transcripts and job records for this project | `private/claude/` | full tool output, account details, lab IPs; redacted of anything token-shaped |
| `AppData\Roaming\Extron\` (GCP recent hosts, GUI Designer config) | `private/app-settings/Roaming-Extron/` | processor addresses |
| `AppData\Roaming\@extron\` (ControlScript extension templates) | `private/app-settings/Roaming-@extron/` | kept with the other tool settings |
| `AppData\Local\Extron\` (GCP and GUI Designer `user.config`) | `private/app-settings/Local-Extron/` | **GCP licence blobs and the login email** |
| `AppData\Local\Crestron\` (Toolbox settings) | `private/app-settings/Local-Crestron/` | kept with the other tool settings |
| `AppData\Roaming\Code\User\settings.json` | `private/app-settings/vscode-settings.json` | editor settings; the project-relevant key is `"controlscript.version": "1.11.1xi"` — the ControlScript API level generated modules targeted |
| `Users\robp\.gitconfig` | `private/app-settings/gitconfig` | holds only the `safe.directory` entries |
| Claude verifier subagents, tool results, file-history snapshots, background-task outputs | `private/claude/` | intermediate file versions and raw run output never committed elsewhere |

The original session (`22114bf1`) lives at `Z:\.claude\projects\` regardless.

## What stayed on C:, and why that is safe

| on C: | why |
|---|---|
| `Program Files\*`, `Program Files (x86)\*` | installed applications — GCP, GUI Designer, the Crestron suite; reinstallable, versions recorded above |
| `Users\Public\Documents\Extron\GUI Designer Templates\` (2.9 GB) | GUI Designer's install payload: 0 of 6,551 files modified after installation |
| everything not related to this project — browser profile, remote-desktop and editor settings, other projects' Claude data, personal folders | out of scope for this repo |

## Rebuilding the box

1. Install Global Configurator Pro (3.33 or later) and sign in.
2. Install Python 3.11+. No packages are needed.
3. Restore the library if the new install is missing packages: copy
   `corpus/extron-driver3/*` into `C:\Users\Public\Documents\extron\Driver3\`,
   **after backing up that folder's `DataFile.dat` and `DriverLookup.dat`**.
4. Add the repo to `git config --global safe.directory` — Git refuses the
   `\\Mac\Home` share as "dubious ownership" otherwise.
5. Run the test suites (see `STATUS.md`), then
   `experiments/gcp_harness/Load-Package.ps1 -Commands` on
   `experiments/skeleton_i20/out/1bynd_19_20024_v1_0_0.pkp` — 34 commands
   means the box can read what this project builds.
6. If wanted, restore the GCP/Crestron settings from `private/app-settings/`.

## Git on this box

- **Git Credential Manager hangs** on an invisible prompt and, once killed, has
  no cached credential. `$GH_TOKEN` is not set here. Push with
  `GIT_ASKPASS=experiments/gcp_harness/askpass.sh`, which answers with
  `gh auth token` for the `rob-paprocki` login without putting the token in
  argv.
- **Commit identity** is a repo-local `user.name`/`user.email`, set by the owner
  on 2026-09-09. The folder-level `includeIf` pinning described in
  `Z:\GitHub\rob-paprocki\CLAUDE.md` is not present on this machine.
