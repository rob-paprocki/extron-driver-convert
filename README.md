# extron-driver-convert

Research and working converters between Extron `.pkp` drivers (Global Configurator), ControlScript modules, Crestron `.pkg` packages and Q-SYS plugins, with measured results.

[![Release](https://img.shields.io/github/v/release/rob-paprocki/extron-driver-convert)](https://github.com/rob-paprocki/extron-driver-convert/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/rob-paprocki/extron-driver-convert/ci.yml?branch=main&label=CI)](https://github.com/rob-paprocki/extron-driver-convert/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/rob-paprocki/extron-driver-convert)](LICENSE)
![Python 3](https://img.shields.io/badge/python-3-blue)
![Dependencies: standard library only](https://img.shields.io/badge/dependencies-standard%20library%20only-brightgreen)

This repository works out how far an Extron `.pkp` driver can be turned into a ControlScript `.py` module and back, and whether the same holds across vendors. It also tests whether an Extron processor can drive Crestron-owned hardware from a driver built here. The answers come as code, tests and numbered findings.

Not affiliated with Extron or Crestron.

## What you get

- A `.pkp` to ControlScript translator that raises instead of guessing.
- A transplant builder that puts new or edited commands into a real `.pkp`, so Global Configurator loads it.
- Readers for Crestron `.pkg` files and Q-SYS plugins, scored against a wire-string table.
- A Python re-implementation of Extron's driver validator.
- Driver Studio, a desktop window around the same tools (Windows `.exe` build in `packaging/`).

**Does not:** redistribute vendor drivers, documentation or installers. Those are listed by SHA-256 in `vendor-files.manifest.tsv`; see [docs/VENDOR-MATERIAL.md](docs/VENDOR-MATERIAL.md).

## Where it stands

| Direction | Verdict |
|---|---|
| `.pkp` to ControlScript `.py` | **Built and measured.** 80.8% wire-match across 314 third-party packages; 54% of generated modules would still raise at runtime, mostly on configuration values GC supplies and ControlScript does not (finding 14 §8). |
| ControlScript `.py` to `.pkp` | **Yes, including new commands.** Transplant into a real package, refresh its SHA-256 digests, add `DriverCommandAsset` subtrees. Global Configurator loads and renders the result (findings 16, 18). |
| Crestron `.pkg` to Extron | **Yes** for JSON-engine drivers (findings 03 to 05, 13). |
| Extron to Crestron `.pkg` | Demonstrated by patching a real DLL's resources. Gated by Crestron's dealer licence, not by code (finding 06). |
| Crestron IV-CAM-I20 on an Extron processor | **Built both ways.** A 45-command `.pkp` runs on a processor against a simulated camera, with a byte-identical ControlScript module. Not yet tried on a real camera. |

Two more results came out of the samples. A driver can be generated from API documentation alone for 29 of the 32 endpoints a real driver calls. The risk is incompleteness that nobody notices. A shared intermediate representation is justified, because two vendors independently encode the same device to the same bytes (finding 05).

## Requirements

| Item | Needed |
|---|---|
| Python | 3, standard library only (CI runs 3.12) |
| Driver Studio (optional) | `pip install -r gui/requirements.txt` (CustomTkinter, Pillow) |
| Real acceptance checks (optional) | Windows with Global Configurator, for `verify --load-package` |

## Install

```bash
git clone https://github.com/rob-paprocki/extron-driver-convert.git
cd extron-driver-convert
python tools/convert.py directions   # prints the conversion matrix if everything works
```

## Quick start

Translate a `.pkp` to a ControlScript module, then check a package with the local validator:

```bash
python tools/convert.py pkp2cs <PACKAGE>.pkp -o out/
python tools/convert.py validate <PACKAGE>.pkp
```

Every verb has `--help`. `validate` uses this project's model of the format; `verify` runs Extron's own deserializer and is the one to trust before loading a package into Global Configurator.

Run a test file directly. There is no pytest, and suites skip what needs vendor files, naming each missing one:

```bash
python tools/test_pkp2cs.py
```

## Tools

| Tool | What it does |
|---|---|
| `tools/convert.py` | One front door for the verbs below |
| `tools/pkp_dump.py` | `.pkp` to a JSON object graph |
| `tools/pkg_dump.py` | Crestron `.pkg` to manifest and driver JSON |
| `tools/wire_table.py` | The acceptance oracle: a normalised per-command wire table from both Python dialects |
| `tools/pkp2cs.py` | `.pkp` to ControlScript translator |
| `tools/pkp_build.py` | `.pkp` transplant builder; refuses unless the donor round-trips byte for byte |
| `tools/pkp_asset.py` | Adds commands to a `.pkp` by clone, attach and detach |
| `tools/pkp_validate.py` | Extron's driver validator in Python |
| `tools/gc_catalogue.py` | Reads what Global Configurator actually catalogued |
| `tools/pkg_patch.py` | Replaces the driver definition inside a Crestron `.pkg` |
| `tools/verify_vendor_files.py` | Checks a local copy of the unpublished vendor material against the manifest |

The one non-Python part is `experiments/gcp_harness/`: Windows-only PowerShell that asks Extron's DLLs whether a package loads.

## Docs

| Read | For |
|---|---|
| [STATUS.md](STATUS.md) | Verdicts, findings index, translator scorecard. Kept current. |
| [ROADMAP.md](ROADMAP.md) | Everything unfinished, with the blocker and first step |
| [docs/LAYOUT.md](docs/LAYOUT.md) | Folder map, how conversions are graded, method |
| [docs/VENDOR-MATERIAL.md](docs/VENDOR-MATERIAL.md) | What is and is not published |
| [docs/HAND_AUTHORING_PKP.md](docs/HAND_AUTHORING_PKP.md) | Writing a `.pkp` by hand |
| [findings/](findings/README.md) | Numbered research output, 01 to 20 |

## Help and contributing

Questions and bug reports go in [Issues](https://github.com/rob-paprocki/extron-driver-convert/issues). Development happens in a separate repository, so a fix sent here is folded into the next release.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

[Apache-2.0](LICENSE) (c) 2026 Rob Paprocki. Vendor files are theirs, not covered by this license, and not included.
