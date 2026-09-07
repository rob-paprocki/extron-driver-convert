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

## Environment

**Everything here runs anywhere Python 3 does.** Standard library only, no
`requirements.txt`, no compiled dependency, no PowerShell, no Windows. There is
not a single `.ps1` in the repo. A cloud session is a first-class place to work
on this — unlike `extron-gdl-toolkit`, nothing is gated on a local machine.

Verified 2026-09-07 in a Claude Code cloud container, all passing:

| suite | tests |
|---|---|
| `tools/test_pkp2cs.py` | 56 |
| `tools/test_wire_table.py` | 34 |
| `tools/test_pkg_dump.py` | 23 |
| `experiments/nrbf_writeback/test_nrbf_write.py` | 16 |
| `experiments/crestron2cs/test_crestron2cs.py` | 14 |

Run them directly (`python3 tools/test_pkp2cs.py`); there is no pytest and they
do not need one.

### What is blocked, and by what

The open items in `STATUS.md` are **not** blocked by where the code runs. Do not
report them as "needs a local box" — the distinction matters, because a laptop
does not unblock them either:

- **Does an outsider-built `.pkg` load on a processor?** Needs Crestron Toolbox
  or VC-4. Dealer-gated: an account and an agreement, not an install.
- **Would GC accept a from-scratch `.pkp`?** Needs Windows *and* Global
  Configurator. This is the one item a Windows box actually addresses.
- **Catalogue coverage.** `drivers.crestron.io` is login-gated. Reachable from a
  cloud container, but credentials are the gate, not the network.
- **Only 4 oracle pairs.** Needs more sample files. Nothing else.
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

4. **Unresolvable means opaque, never guessed.** The translator raises rather
   than degrading, and `wire_table.py` emits *counted* opaque markers. Preserve
   that — a plausible guess is worse than a recorded gap, because it scores well.

## Provenance

`samples/` holds **vendor driver material** — Extron and Crestron both. The repo
stays private. Findings may describe formats; sample files are not
redistributed. Think before adding a remote, and note that a cloud session
clones all of it into a managed container.
