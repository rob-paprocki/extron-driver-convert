# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

Research into converting AV device drivers between vendor formats — Extron
`.pkp` (Global Configurator), Extron ControlScript `.py`, and Crestron `.pkg`.
It is a research repo with working tools, not a product.

**Read `STATUS.md` first.** It carries the verdicts, the findings index, the
translator scorecard, and the standing methodology notes. Everything in it is
measured unless marked otherwise, and it is the file to update when a verdict
moves.

**Then `ROADMAP.md`** for everything unfinished — ordered, with the blocker and
the first concrete step for each — and **`ENVIRONMENT.md`** for the Windows box,
what was moved off its C: drive, and how to rebuild it.

## Environment

**Every tool and test here runs anywhere Python 3 does.** Standard library only,
no `requirements.txt`, no compiled dependency. A cloud session is a first-class
place to work on the code.

**The one exception is `experiments/gcp_harness/`:** Windows-only PowerShell that
loads Extron's x86 assemblies and drives GCP over UI Automation. Python cannot
load those assemblies without a third-party bridge (pythonnet), which the
no-dependency rule excludes. Nothing in `tools/` or any test depends on it.

**But not every *experiment* is portable.** Finding 12 drove Global Configurator
directly, which needs the Windows box. Treat the code as cloud-first and the
acceptance experiments as machine-bound.

### The Windows box (measured 2026-09-07)

A Parallels guest sharing the Mac home directory, reachable at
`\\Mac\Home\github\rob-paprocki` (also `C:\mac\home\...`):

| | |
|---|---|
| Extron **GCP** (Global Configurator Pro) | `3.33.0-b.38` — **licence expires ~2026-10-07** |
| Extron GUI Designer, Toolbelt | installed (GUI Designer is `extron-gdl-toolkit`'s gate) |
| **Crestron Toolbox**, Simpl, Cresdb | installed |
| Python | **3.11.9** at `C:\Users\robp\AppData\Local\Programs\Python\Python311\`, on PATH in Git Bash (measured 2026-09-11; the 3.12 install recorded on 2026-09-07 is gone) |
| PowerShell, 32-bit | 5.1 at `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\` — needed by `experiments/gcp_harness/`; lacks `Get-FileHash` |
| `Extron.Configuration.Drivers.dll` | `15.27.0.0`, x86/PE32, .NET Framework 4.8 |

**GC's driver library is `C:\Users\Public\Documents\extron\Driver3`** — user-writable,
no elevation. **Its size varies by install, so measure it rather than quoting a number:**
finding 12 counted 6,644 `.pkp` + 1,745 `.eir` on one machine; this one holds
**1,853 `.pkp` + 26 `.eir`** (2026-09-09). That is what Driver Manager
reads, *not* the 54 packages under `Program Files`. Read finding 12 before
touching it, and back up `DataFile.dat` + `DriverLookup.dat` first — GC truncates
the catalogue before rebuilding it, so an interrupted start leaves 0 bytes.
**A SHA-256-verified snapshot of this library and the GS module shipment is
committed under `corpus/`** (2026-09-11), and `experiments/oracle_pairs/` reads it
by default.

Two gotchas that cost time here:

- **`git fetch` / `git push` hang.** Git Credential Manager blocks on an
  invisible prompt, and once killed it has no cached credential. `$GH_TOKEN` is
  **not** set on this box (measured 2026-09-10). Push with
  `GIT_ASKPASS=experiments/gcp_harness/askpass.sh GIT_TERMINAL_PROMPT=0`: it
  answers with `gh auth token` for the `rob-paprocki` keyring login, per command,
  without putting the token in argv or config.
- **Git refuses the share** with "dubious ownership" until the repo is added to
  `safe.directory` (already done for this repo and `extron-gdl-toolkit`).

Verified 2026-09-11 on the Windows box (Python 3.11.9), all passing — 518 tests:

| suite | tests |
|---|---|
| `tools/test_pkp2cs.py` | 56 |
| `tools/test_wire_table.py` | 34 |
| `tools/test_pkg_dump.py` | 23 |
| `tools/test_pkp_build.py` | 37 |
| `tools/test_pkp_validate.py` | 127 |
| `tools/test_pkp_asset.py` | 43 |
| `tools/test_gc_catalogue.py` | 14 |
| `experiments/nrbf_writeback/test_nrbf_write.py` | 16 |
| `experiments/crestron2cs/test_crestron2cs.py` | 14 |
| `experiments/skeleton_i20/test_i20_wire.py` | 86 |
| `experiments/skeleton_i20/test_i20_cs_wire.py` | 57 |
| `experiments/oracle_pairs/test_build_index.py` | 11 |

`test_pkp_build.py` and `test_pkp_asset.py` walk every sample package, including
the 4.4M-event Tesira one; expect minutes, not seconds. Run them with `python -u`
if you are piping the output, or it arrives only at the end.

Run them directly (`python3 tools/test_pkp2cs.py`); there is no pytest and they
do not need one.

### What is blocked, and by what

The open items in `STATUS.md` are **not** blocked by where the code runs. Do not
report them as "needs a local box" — the distinction matters, because a laptop
does not unblock them either:

- **Does an outsider-built `.pkg` load on a processor?** Toolbox is now installed
  on the Windows box, so the tool is no longer the gate — a processor or VC-4 is,
  plus the dealer agreement.
- **Does a *synthesised* `.pkp` load?** Needs Windows *and* Global Configurator.
  Finding 12 took this most of the way: GC ingests a package our writer produced,
  and one we mutated. What is left is a graph assembled from scratch rather than
  round-tripped.
- **Catalogue coverage.** `drivers.crestron.io` is login-gated. Reachable from a
  cloud container, but credentials are the gate, not the network.
- ~~**Only 4 oracle pairs.**~~ Closed by finding 12 — the GC install carries 6,644
  packages across hundreds of vendors. Selection, not acquisition, is the problem
  now.
- **Crestron's licence position.** A lawyer's question.

### Network, from a cloud container

`drivers.crestron.io`, `nuget.org` and PyPI are reachable through the agent
proxy. `www.extron.com` is not — it returns an empty reply rather than a status
code, which reads like origin-side filtering rather than proxy policy. Harvested
vendor documentation in `reference/` was collected elsewhere; assume you cannot
top it up from here without checking first.

## Things that will waste your time

1. **A negative claim needs positive evidence.** Finding 08 twice asserted an
   endpoint was undocumented when it was not. Where no published index exists,
   report a negative as *"not found by method X"*, never as *"does not exist"*.
   `STATUS.md`'s methodology notes carry the rest of these; read them before
   writing a finding.

2. **Acceptance is the wire-string table**, not file or line similarity. Line
   overlap between a package and its shipped module ranges 76% to 38% while the
   command tables stay near-identical. `tools/wire_table.py` is the oracle.

3. **Wire correctness is necessary but not sufficient.** A module can carry a
   perfect command table and still raise `AttributeError` on a processor. 26
   dangling `self.X()` references hid behind a near-perfect scorecard. Check
   runtime resolvability too.

4. **`Valid` does not mean loadable, and a local check can share your wrong model.**
   Finding 18 built a package that parsed, round-tripped, validated and passed
   39 tests — and Global Configurator would not list it at all, because .NET's
   `BinaryFormatter` refused the stream. Every one of those checks used *our*
   model of the format, so none of them could see it. **Deserialize through
   Extron's own code before believing a graph edit.** From 32-bit PowerShell:
   `LoadFromFile` (returns null on failure, swallowing the reason) or
   `BinaryFormatter.Deserialize` with an `AssemblyResolve` handler mapping the
   stream's `Extron.Configuration.* 1.1.24.402` onto the installed 15.27.0.0
   DLLs — that one gives the real exception. Both are seconds, not a trip.
   `DataFile.dat` / `DriverLookup.dat` are themselves raw NRBF and parse with
   `pkp_dump.py`, so whether GC catalogued something is directly checkable.

5. **Unresolvable means opaque, never guessed.** The translator raises rather
   than degrading, and `wire_table.py` emits *counted* opaque markers. Preserve
   that — a plausible guess is worse than a recorded gap, because it scores well.

## Provenance

`samples/` and `corpus/` hold **vendor driver material** — Extron and Crestron
both; `corpus/` alone is Extron's full 1.3 GB library from the Windows box. The
repo stays private (confirmed on GitHub 2026-09-11). Findings may describe
formats; vendor files are not redistributed. Think before adding a remote, and
note that a cloud session clones all of it into a managed container.

`private/` is **git-ignored** and stays on Z: only. `private/claude/` holds this
project's Claude Code transcripts and job records (full tool output, account
details, lab IPs); `private/app-settings/` holds the GCP, Crestron and
ControlScript tool settings, and the GCP config carries licence data.
