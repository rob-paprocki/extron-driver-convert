# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-15
**Upgrading:** nothing to do. This is the first release.

### Added

- `tools/convert.py`, one command for the converters: `pkp2cs`, `cs2pkp`, `pkg2cs`, `pkp2pkg`, `author`, `dump`, `validate` and `verify`, plus `directions` to list what works today.
- A `.pkp` to ControlScript translator with a wire-table checker, scored against hundreds of third-party driver pairs.
- A transplant builder and asset editor: put a ControlScript module or new commands into a real `.pkp` and refresh its SHA-256 digests so Global Configurator loads it.
- From-scratch authoring of `.pkp` command fields from an API document.
- A Python version of Extron's driver validator, plus a reader for Global Configurator's catalogue.
- Readers and patchers for Crestron `.pkg` files.
- Q-SYS plugin bridge: read a `.qplug` as a wire table and emit ControlScript, with the DTP family plugins.
- Driver Studio, a desktop app around the converters, with a Windows `.exe` build.
- A hand-authoring guide, a status page and a landing page under `docs/`.
- Folder indexes in `experiments/`, `tools/` and `findings/`, so a first-time visitor can find the code behind each result.
- The project is licensed under Apache-2.0.

[Unreleased]: https://github.com/rob-paprocki/extron-driver-convert/commits/main
