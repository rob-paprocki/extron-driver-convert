# experiments/

One folder per question. Each holds the scripts, data and write-up behind a
result; the numbered findings in [`../findings/`](../findings/) summarise
them. Most folders need vendor files to re-run (see `../samples/README.md`),
but every write-up reads fine without them.

Terms: GC is Extron Global Configurator, CS is an Extron ControlScript module
(Python), `.pkp` is a GC driver package, `.pkg` is a Crestron driver package.

## The translator: `.pkp` to ControlScript

| folder | question | result | open first |
|---|---|---|---|
| `oracle_pairs/` | How close is the translator to the CS modules Extron ships? | 314 packages, 352 pairs: 80.8% of commands wire-match, but 54% of generated modules would raise at runtime (finding 14). | [finding 14](../findings/14-oracle-pairs-at-scale.md) |
| `exec_harness/` | Do generated modules actually run, and send what Extron's module sends? | Runs both offline against a stand-in `extronlib` and compares every send. Found bug classes no static check saw. First step only; device replies are not modelled. | [`README.md`](exec_harness/README.md) |
| `corpus_sweep/` | Do the translator's assumptions hold across all 1,854 packages, not just the samples? | Yes for byte-exact rebuild and Manifests. Corrected finding 13 on `ExtronTime`. | [`SWEEP.md`](corpus_sweep/SWEEP.md) |
| `missing_ethernet/` | Can the translator write the Samsung Ethernet module Extron never shipped? | Yes. 10 of 11 shared commands send identical bytes; the 11th differs by a declared substitution (finding 19). | [finding 19](../findings/19-three-questions.md) |
| `ross_ultrix/` | How does generated output compare with an integrator's hand-written module? | 3 commands shared, 2 only in Extron's package, 3 only hand-written (finding 17). | [`README.md`](ross_ultrix/README.md) |

## Building and checking `.pkp` files

| folder | question | result | open first |
|---|---|---|---|
| `nrbf_writeback/` | Can we write the .NET format inside a `.pkp`, not just read it? | Yes, byte for byte on real packages, and GC loads the result (finding 12). Building one from nothing is still open. | [`nrbf_write.py`](nrbf_writeback/nrbf_write.py) |
| `graph_synthesis/` | Can a command move between packages, and can a package be built from scratch? | Moving a command works. From scratch is unfinished. | [`RESULTS.md`](graph_synthesis/RESULTS.md) |
| `graph_probes/` | Why did a package our validator passed fail Extron's loader? | Cloned objects got negative ids; positive ids fix it (finding 18). | [`README.md`](graph_probes/README.md) |
| `protocol_assets/` | How is the connection type (ports, Telnet, UDP, HTTP, SSH) stored, and can it be edited? | Every flag value named across the corpus. Single-field edits load in Extron's loader. | [`SURVEY.md`](protocol_assets/SURVEY.md) |
| `validator_differential/` | Does our Python validator agree with Extron's? | Yes on all 1,853 shipping packages (with Extron's Guid table) and all 53 deliberate mutants (finding 16). | [`README.md`](validator_differential/README.md) |
| `gcp_harness/` | Can Extron's own code tell us whether a package loads, without hardware? | Yes. `Load-Package.ps1` calls Extron's loader. Windows only, needs GC installed. | [`README.md`](gcp_harness/README.md) |

## Crestron devices on Extron processors

| folder | question | result | open first |
|---|---|---|---|
| `skeleton_i20/` | Can a Crestron-supported camera (1 Beyond IV-CAM-I20) get an Extron driver, as both a `.pkp` and a CS module? | Earlier builds ran on an IPCP Pro 360 against a PC playing the camera. The current 45-command build passes Extron's loader but is not uploaded. No real camera yet. | [`QUICKSTART.md`](skeleton_i20/QUICKSTART.md) |
| `skeleton_p20/` | Can the P12/P20 camera reuse the i20 work? | A 38-command `.pkp` and a CS module, 69 of 69 wire tests pass. Offline only. | [`README.md`](skeleton_p20/README.md) |
| `loopback/` | Does a processor running the i20 driver send the expected bytes to a PC playing the camera? | The GC path ran on hardware: 30 of 30 panel frames, 802 clean poll cycles. The CS path is not started. | [`README.md`](loopback/README.md) |
| `crestron2cs/` | Can a Crestron `.pkg` be translated to a CS module? | Yes for building requests: 62 commands, none opaque. The output is for measurement and has not run on a processor (finding 19). | [finding 19](../findings/19-three-questions.md) |
| `crestron_decompile/` | How do Crestron's compiled libraries build their requests? | Extracted and decompiled with ILSpy for finding 20. Output is vendor-derived and not tracked. | [`README.md`](crestron_decompile/README.md) |
| `crestron-dm-md-bridge/` | Can a non-Crestron controller run a Crestron DM-MD8X8-CPU3-RPS switcher with no Crestron processor? | Routing and serial pass-through work on the chassis, driven by a Python stand-in for the master. A `.pkp` that sends the same bytes is built but has not run on an Extron processor. IR and relay are stubbed. | [`README.md`](crestron-dm-md-bridge/README.md) |
| `cip-ipid-survey/` | What signals do Crestron's IP devices (VX2, NVX, Connected displays) expose? | Join maps read from Crestron's device database. Reference only; no driver built from it. | [`README.md`](cip-ipid-survey/README.md) |

`dm_md/`, an earlier design for the same switcher built around its text
console, is held back from the public copy.

## Other vendors and documentation

| folder | question | result | open first |
|---|---|---|---|
| `automate_vx_threeway/` | Do Extron's drivers, Crestron's module and the docs agree on the 1 Beyond Automate VX? | 40 discrepancies found offline, plus a v1.1 CS module with 10 fixes (finding 20). No live unit tested. | [`README.md`](automate_vx_threeway/README.md) |
| `docs_only/` | Can a driver be written from the API docs alone? | Mostly: 29 of the 32 calls a real driver makes are documented. | [`REMEASURE.md`](docs_only/REMEASURE.md) |
| `qsys/` | Can Q-SYS plugins and Extron modules convert into each other? | Both directions built as pilots. The Extron-to-Q-SYS plugin ran in Q-SYS Designer's emulator against a mock device. Nothing on a real Core yet. | [`SCOPE.md`](qsys/SCOPE.md) |
| `tesira_in1804/` | Can a Biamp Tesira control an Extron IN1804 with its own blocks? | On paper, yes: 21 ready-to-paste strings. Never run on either device. | [`MAP.md`](tesira_in1804/MAP.md) |
| `tesira_terminator/` | Does a Tesira command end in LF or CR LF? | LF. The one CR LF in Extron's package is a stray. | [`RESULT.md`](tesira_terminator/RESULT.md) |

## Safe to skip

Inside these folders, `scratch/` holds superseded drafts, `out/` holds
regenerable build output, and `captures/` and most of `evidence/` are raw
logs. The write-ups above cite the parts that matter.
