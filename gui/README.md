# Driver Studio -- the desktop GUI

A unified CustomTkinter application for the AV driver converter. One double-
clickable window with:

- **Convert** -- the seven `tools/convert.py` verbs (`pkp2cs`, `cs2pkp`,
  `pkg2cs`, `pkp2pkg`, `dump`, `validate`, `verify`), each with a per-verb
  form, Browse dialogs, live subprocess output, and a status bar.
- **Hand-Author** -- placeholder for the forthcoming visual editor that will
  turn an API document into any of ControlScript / `.pkp` / Crestron module /
  Crestron `.pkg` / Q-SYS Lua.
- **Directions** -- the supported-conversion matrix.
- **About** -- version, environment, repo links.

## Why this directory has a `requirements.txt`

The rest of the repo (`tools/`, `experiments/`, tests) is strictly standard
library only -- read `CLAUDE.md` for the rationale: cloud sessions, a clone
with no `pip install` step, no compiled dependency.

Driver Studio is the one exception, and it is scoped to this directory. It
needs `customtkinter` (modern-looking widgets on top of tkinter) and
`Pillow` (CustomTkinter's own dependency). Both are MIT-licensed pure Python
packages; neither reaches into any other part of the repo.

The scope rule is in CLAUDE.md:

> **Standard-library-only applies to `tools/`, `experiments/`, and tests.**
> `gui/` has its own `requirements.txt` (CustomTkinter + Pillow); the EXE
> build in `packaging/` is build-time only. No other directory may add runtime
> dependencies without the owner's word.

## Running from source

Install the deps, then launch:

```bash
pip install -r gui/requirements.txt
python gui/driver_studio.py
```

The GUI shells out to `python tools/convert.py <verb> ...` under the hood, so
anything you can do in `convert.py` or `tools/convert_gui.py` works here.

## Running the EXE

See `packaging/README.md`. In short:

```bash
cd packaging
build_exe.bat     # Windows; needs the deps above installed
```

Builds `packaging/dist/driver_studio.exe`, which runs on any Windows machine
without Python, the repo, or `pip` -- it carries its own interpreter inside.

## Headless tests

```bash
python gui/test_driver_studio.py
```

The suite probes CustomTkinter and the Tk display at startup; on a true
headless Linux CI without `xvfb` it will skip. On Windows and macOS the full
suite runs.

## Where things live

| File                            | What it holds |
| ------------------------------- | -- |
| `gui/driver_studio.py`          | Entry point + sidebar nav + every page in one file |
| `gui/requirements.txt`          | Pinned runtime deps for the GUI and build-only PyInstaller |
| `gui/test_driver_studio.py`     | Headless smoke tests (CTk-aware) |
| `packaging/driver_studio.spec`  | PyInstaller spec (onefile, `console=False`) |
| `packaging/build_exe.bat`       | Portable Windows build driver |
| `packaging/README.md`           | How to produce the EXE, sign it, cut a Release |

## Why CustomTkinter and not Qt / Pywebview?

The owner asked for a modern Windows application. The three serious contenders
were PySide6 (bigger EXE, closest to Fluent out of the box), Pywebview (web
frontend over system WebView2), and CustomTkinter (modern-flat look on top of
tkinter, no extra GUI stack). CustomTkinter was picked for the smaller
footprint and the fact that `tools/convert_gui.py` already uses tkinter, so
the subprocess runner and the per-field data model port over unchanged.

## Non-goals for v1

- Not a replacement for `tools/convert_gui.py` -- that stays as the
  stdlib-only alternate entry point for cloud sessions and anywhere pip is a
  problem.
- Not a replacement for `tools/convert.py` -- the GUI shells out to it.
- No bundled vendor material. The EXE builds from `tools/` and `gui/` source
  only; vendor packages still need to be present on disk at run time, same as
  the CLI.
