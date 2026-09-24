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
the first concrete step for each — and **`ENVIRONMENT.md`** for what a
workstation needs in order to run the machine-bound parts.

## Environment

**Every tool and test here runs anywhere Python 3 does.** Standard library only,
no `requirements.txt`, no compiled dependency. A cloud session is a first-class
place to work on the code.

**But the vendor material is not in the repository** (since 2026-09-24): the
samples, `corpus/`, harvested vendor pages, GC catalogue data and every package
built from a vendor one are untracked, listed in `vendor-files.manifest.tsv`. A
clone — including a cloud session's — has none of it, so tests that need it
**skip**, naming the file, and the suites report skips beside passes and
failures. A clean run in a clone therefore checks the code, not the findings;
reproducing a finding needs the material in place (`tools/verify_vendor_files.py`
checks it).

**The one exception is `experiments/gcp_harness/`:** Windows-only PowerShell that
loads Extron's x86 assemblies and drives Global Configurator over UI Automation.
Python cannot load those assemblies without a third-party bridge (pythonnet),
which the no-dependency rule excludes. Nothing in `tools/` or any test depends
on it.

**But not every *experiment* is portable.** Finding 12 drove Global Configurator
directly, which needs a licensed workstation. Treat the code as cloud-first and
the acceptance experiments as machine-bound.

### Where the machine-bound work runs

`ENVIRONMENT.md` is the single source of truth for what a workstation needs,
which capabilities need a GCP licence and which do not, the binary identities the
findings are measured against, and the setup and test commands. **Do not restate
its values here** — installed versions and file counts drift, and a stale copy in
two places is worse than one.

Two things worth knowing before planning work:

- **GC's driver library is not the packages under the install directory.** It is
  a separate, user-writable folder whose contents vary by install, so measure it
  rather than quoting a number. Read finding 12 before touching it, and back up
  its `DataFile.dat` and `DriverLookup.dat` first — GC truncates the catalogue
  before rebuilding it, so an interrupted start leaves 0 bytes.
- **A SHA-256-verified snapshot of one such library belongs under `corpus/`**,
  and `experiments/oracle_pairs/` reads it by default — so findings 14, 16 and 17
  reproduce with no Extron install, given the snapshot. It is vendor material and
  no longer tracked; the manifest pins every file's hash.

**Over a thousand tests, all standard library, no pytest** — the count lives in
`ENVIRONMENT.md`, not here. Run each file directly; the
commands are listed in `ENVIRONMENT.md`. `test_pkp_build.py` and
`test_pkp_validate.py` walk every sample package including a 4.4M-event one, so
budget about 20 minutes for the full set and use `python -u` if you are piping
the output.

### What is blocked, and by what

The open items in `STATUS.md` are **not** blocked by where the code runs. Do not
report them as "needs a local box" — the distinction matters, because a laptop
does not unblock them either:

- **Does an outsider-built `.pkg` load on a processor?** Crestron Toolbox is
  obtainable, so the tool is not the gate — a processor or VC-4 is, plus the
  dealer agreement.
- **Does a *synthesised* `.pkp` work on a real device?** Needs Windows, Global
  Configurator, a processor *and* the device. Finding 12 showed GC ingests a
  package our writer produced, and one we mutated; finding 18 added commands to a
  real package's object graph and took it into the GCP editor with its full
  command surface rendered; `20025` and `20026` then built, uploaded and ran on
  an IPCP Pro 360 against a PC playing the camera (`PROTOCOL.md` run log).
  **A real camera is what remains** — no socket has been opened to one. (A graph
  assembled wholly from scratch is still ROADMAP R28, partly done.)
- **Catalogue coverage.** `drivers.crestron.io` is login-gated. Reachable from a
  cloud container, but credentials are the gate, not the network.
- ~~**Only 4 oracle pairs.**~~ Closed by finding 14, which scored 352 pairs
  across 314 packages. Selection, not acquisition, is the problem now.
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
   runtime resolvability too — methods, attributes, globals and argument
   counts (`find_dangling_self_calls`, `find_unassigned_self_attributes`,
   `find_unresolved_globals`, `find_call_arity_mismatches`). The last two
   classes were found only by *executing* generated modules
   (`experiments/exec_harness/`), and a `@staticmethod` whose decorator was
   dropped is still invisible to all four. Run the module.

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

6. **Never write an absolute path into generated output.** It is meaningless in
   any other checkout, it makes the generated bytes depend on where the repo was
   cloned — which defeats byte-for-byte comparison — and on Windows it can make
   the output unparseable outright: a path under `C:\Users` puts a literal `\U`
   into a non-raw docstring, which reads as a truncated `\UXXXXXXXX` escape and
   raises `SyntaxError`. Emit repo-relative, forward-slashed paths; see
   `crestron2cs.provenance_path()`.

## Provenance

**Two repositories, and neither publishes vendor material.** The original is a
**private archive** with the complete history; a **public copy** carries the same
work with the vendor material removed from every commit (built from a rewritten
branch, so its commit hashes differ — the hashes the docs cite are the
archive's). `samples/`, `corpus/`, the pages harvested into `reference/`, GC's
catalogue captures, and every `.pkp` this project built or mutated are Extron,
Crestron or third-party material: used on disk, untracked in both, listed with
their SHA-256s in `vendor-files.manifest.tsv`. Findings may describe formats;
vendor files are not redistributed.

- **Never `git add` vendor material**, wherever it sits — the `.gitignore` rules
  cover the known shapes (`*.pkp`, `*.pkg`, `DataFile*.dat`, `*.embedded.py`,
  the sample and corpus folders), and `tools/test_verify_vendor_files.py` fails
  if a listed file becomes tracked. A *new* kind of vendor file needs a new rule
  and a manifest line, not a commit.
- **The archive's commits before 2026-09-24 hold the vendor files**, so its
  history must never reach a public remote: no pushing its branches to the
  public copy, no public forks. The public copy only ever receives commits from
  its own rewritten line of history. Do not restore vendor files into either
  index.
- Generated driver modules derived from vendor scripts are tracked; the owner
  decided (2026-09-24) that they are not a concern.

`private/` is **git-ignored** and never pushed. It holds this project's Claude
Code session records (full tool output, account details, lab IPs) and the
Extron, Crestron and ControlScript application settings, whose configs carry
licence data. Nothing in this repo requires it.
