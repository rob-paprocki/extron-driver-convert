# Packaging -- Driver Studio EXE build

Turn `gui/driver_studio.py` into a single `.exe` that runs on any Windows box
with no Python, no `pip`, no cloned repo.

## Prereqs (one-time)

Build-time deps live in `gui/requirements.txt`, which includes PyInstaller:

```bash
pip install -r gui/requirements.txt
```

The requirements file pins exact versions so successive builds produce the
same artifact.

## Build

From the repo root OR from inside this directory:

```bat
packaging\build_exe.bat
```

That script:

1. Changes into `packaging/`.
2. Runs `pyinstaller --clean --noconfirm driver_studio.spec`.
3. Leaves `dist/driver_studio.exe` (and intermediate `build/`) beside the
   spec. Nothing from the build is tracked.

Typical artifact: ~45-70 MB single file, launches in a couple of seconds the
first time (PyInstaller unpacks the bundle to `%TEMP%` on each run).

## What the spec bundles

- `gui/driver_studio.py` -- the entry point.
- `tools/*.py` -- every module under `tools/` so `convert.py` and its
  siblings run from inside the one-file bundle at `sys._MEIPASS/tools/`.
- CustomTkinter's own JSON themes and assets (via
  `collect_data_files("customtkinter")`).
- `darkdetect` as a hidden import (CustomTkinter's "System" appearance mode
  reads it on Windows).

What is NOT bundled:

- `samples/`, `corpus/`, `reference/` -- vendor material, never in the EXE.
- `docs/`, `evidence/`, `experiments/`, `findings/`, `notes/` -- not needed
  to run the GUI.
- A Python interpreter the user already has: the EXE carries its own.

## Testing the EXE

Launch:

```bat
packaging\dist\driver_studio.exe
```

Smoke checklist:

1. Window opens, no terminal window appears alongside it (that's the
   `console=False` in the spec).
2. Four sidebar entries (Convert, Hand-Author, Directions, About).
3. Convert page: click `pkp2cs`, Browse into `samples/` (if present on
   disk) and point at a `.pkp`. Run. The console pane should fill with the
   conversion output and the status line should turn green on `exit 0`.
4. Appearance toggle in the sidebar footer flips Light / Dark / System.
5. Appears in the Windows taskbar and Alt-Tab list as "Driver Studio".

## SmartScreen

Unsigned EXEs show a "Windows protected your PC" prompt on first launch. The
user clicks "More info -> Run anyway". If you want to skip that:

1. Buy a code signing certificate (DigiCert / Sectigo / etc.).
2. Sign with `signtool sign /fd SHA256 /tr http://... /td SHA256
   /f cert.pfx /p <pwd> driver_studio.exe`.
3. Verify with `signtool verify /pa /v driver_studio.exe`.

Not required for internal use; worth it if the EXE goes to end users.

## Cutting a Release

Builds are **not** committed to the repo (unlike jlrioux/Extron-Debug-Tool,
which ships ZIPs inside its `release/` folder). The EXE is a release
artifact:

1. Tag the commit:  `git tag v0.1.0 && git push --tags`
2. Build:           `packaging\build_exe.bat`
3. Open the GitHub Releases UI, create a Release against the tag, drag
   `packaging\dist\driver_studio.exe` into the assets box.
4. Paste release notes (what changed, link to the compare view).

A future PR can add a GitHub Actions Windows job to automate this: build on
tag push, attach the EXE to the Release automatically. Not in scope for the
skeleton PR.

## Troubleshooting

**ImportError at runtime for `_tkinter`:** CPython for Windows ships Tk with
the installer, but some stripped-down distributions do not. Build on a stock
`python.org` installer, not a minimized/portable Python.

**EXE launches but window flashes and closes:** turn on PyInstaller's debug
console temporarily by editing the spec: `console=True`, rebuild, run from
`cmd.exe` to see the traceback.

**Antivirus flags the EXE:** common for unsigned PyInstaller output.
Submit the hash to the vendor as a false positive, or sign the EXE.
