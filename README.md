# extron-driver-convert

Can a device driver written for one AV control system become a driver for
another? This repo tests that for Extron Global Configurator packages (`.pkp`),
Extron ControlScript modules (`.py`), Crestron driver packages (`.pkg`) and
Q-SYS plugins, with working converters and measured results. It is a research
project, not a product.

Not affiliated with Extron, Crestron or QSC. No vendor files are published
here, which is why the folders under `samples/` and `corpus/` hold no files.

## Start here

| if you want to | go to |
|---|---|
| see what it found | the [status page](https://rob-paprocki.github.io/extron-driver-convert/status.html), or the table below |
| convert a driver | `python tools/convert.py pkp2cs path/to/driver.pkp -o out/`, with your own `.pkp`. [`tools/README.md`](tools/README.md) has the other verbs. |
| build a `.pkp` by hand | the [hand-authoring guide](docs/HAND_AUTHORING_PKP.md) |
| check a result | [`findings/`](findings/) for the write-ups, [`experiments/README.md`](experiments/README.md) for the code and data behind each |

## Where it stands

| question | answer |
|---|---|
| Extron `.pkp` to ControlScript? | **Works.** Across 314 third-party drivers, 80.8% of commands send the same bytes as the shipped module, but 54% of the generated modules would still fail at runtime, mostly on settings GC supplies and ControlScript does not (finding 14). |
| ControlScript to `.pkp`? | **Works, including new commands.** The IV-CAM-I20 package goes from 15 to 45 commands, and GC loads, lists and renders them (findings 12, 16, 18). |
| Crestron `.pkg` to ControlScript? | **Works** for Crestron's JSON-engine drivers, measured against Extron's own driver for the same device (findings 03 to 05, 13, 19). `convert.py` stops at the JSON; the module step is in `experiments/crestron2cs/`. |
| Extron to Crestron `.pkg`? | **Patch only.** Swapping the driver inside a real package works mechanically; going further needs Crestron's dealer licence (findings 04, 06). |
| A Crestron camera on an Extron processor? | **Runs against a stand-in.** Earlier builds of the 1 Beyond IV-CAM-I20 `.pkp` uploaded to an IPCP Pro 360 and were driven from a touch panel, with a PC playing the camera. The current 45-command build passes Extron's loader. No real camera yet, and the ControlScript form has not run on a processor. |
| A Crestron DM-MD switcher on an Extron processor? | **Routing and serial pass-through work on the chassis.** A DM-MD8X8-CPU3-RPS takes both over one socket from a Python stand-in for the control system. A `.pkp` that sends the same bytes is built but has not run on an Extron processor. IR and relay are stubbed. See [`experiments/crestron-dm-md-bridge/`](experiments/crestron-dm-md-bridge/), whose numbered notes 24, 28 and 29 are what the status page calls findings 24, 28 and 29. |
| Q-SYS to and from Extron? | **Both directions built.** Q-SYS plugins translate to ControlScript (two pilots, exact on the wire), and Extron CrossPoint switchers get Q-SYS plugins (`experiments/qsys/`). |

GC is Extron Global Configurator. The [status page](https://rob-paprocki.github.io/extron-driver-convert/status.html)
has the full answers and what is left to do.

## What is in each folder

| folder | contents | need it? |
|---|---|---|
| `tools/` | the converters and checkers, with their tests | to run anything |
| `findings/` | numbered write-ups, 00 to 20 | to read the results |
| `experiments/` | one folder per question, with the scripts and data behind each finding | to check or extend a result |
| `docs/` | the GitHub Pages site and the hand-authoring guide | |
| `evidence/` | screenshots and logs the findings cite | when checking a citation |
| `reference/` | our notes on vendor documentation | rarely |
| `samples/`, `corpus/` | placeholder folders with no files in them; vendor drivers sit here on the owner's machine | no |
| `notes/` | early desk research, sample provenance, and the plan for which files to move (`layout-plan.md`) | no |

And the files at the top:

| file | what it is |
|---|---|
| `STATUS.md` | every verdict, the findings index and the translator scorecard, in full. Last fully revised 2026-10-05; the status page covers later work. |
| `ROADMAP.md` | the owner's to-do list, with hardware steps. Not needed to use anything. |
| `ENVIRONMENT.md` | setting up Windows for the few experiments that need Extron or Crestron software installed |
| `CLAUDE.md` | instructions for AI coding agents working in this repo |
| `vendor-files.manifest.tsv` | path, size and SHA-256 of every vendor file the tests can use but the repo does not publish |

## Running it

Everything needs only Python 3.11 or later; there is nothing to install and no
pytest. Run a test file directly, for example `python tools/test_wire_table.py`. Tests
that need a vendor file skip and name it, so a clean clone checks the code but
not the findings. `ENVIRONMENT.md` lists every suite.

## Vendor material and the two repositories

There are two repositories. Work happens in a private archive,
`rob-paprocki/extron-driver-convert-archive`, whose commits before 2026-09-24
still hold vendor files. The public one, `rob-paprocki/extron-driver-convert`,
is built from it by `tools/public_sync.py` with a history rewritten without
them, so the commit hashes the docs cite are the archive's. The public copy
also holds back the `experiments/dm_md/` design work and anything showing the
owner's account or lab network; the `EXCLUDE` list in `public_sync.py` names
every path.

The sample drivers, the corpus, harvested vendor pages and every package built
from a vendor one are Extron, Crestron or third-party material. Neither
repository tracks them, except the two DM-MD driver builds in
`experiments/crestron-dm-md-bridge/pkp-out/`, which were reviewed and listed
for publication in `public_sync.py`'s `BINARY_OK`. If you have your own copies, put them at the paths in
`vendor-files.manifest.tsv` and check them with
`python tools/verify_vendor_files.py`. The findings and tools describe the
formats; they do not redistribute them.

Driver modules this project generated, such as
`experiments/skeleton_i20/out/*.py`, are its own output and are tracked.
