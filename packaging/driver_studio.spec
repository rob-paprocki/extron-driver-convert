# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Driver Studio.

Build with:   packaging/build_exe.bat    (Windows)
Output:       packaging/dist/driver_studio.exe   (onefile, no console)

Portable: this spec resolves REPO_ROOT at build time rather than hard-coding
a developer's local path, so the same spec builds on any workstation or in CI.
"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

REPO_ROOT = Path(SPECPATH).resolve().parent
ENTRY = REPO_ROOT / "gui" / "driver_studio.py"
TOOLS_DIR = REPO_ROOT / "tools"

# CustomTkinter loads its JSON themes and assets at runtime via importlib
# resources. collect_data_files() pulls those files into the bundle.
datas = []
datas += collect_data_files("customtkinter")

# Ship tools/ beside the EXE as a data directory so the GUI can spawn
# `python tools/convert.py <verb>` from inside the one-file bundle. The GUI
# resolves tools/ via REPO_ROOT at runtime, which PyInstaller maps to the
# bundle's temp extraction directory (sys._MEIPASS) when running from the
# single-file EXE.
tools_datas = [
    (str(p), f"tools/{p.name}") for p in TOOLS_DIR.glob("*.py")
]
datas += tools_datas

# docs/ and reference/ are intentionally NOT bundled -- they are vendor-
# derived or large, and the EXE needs neither to run its own GUI. The user
# supplies .pkp/.pkg files to the running EXE from disk, as with the CLI.

hiddenimports = [
    # tkinter can be missed by analysis in rare cases.
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.scrolledtext",
    "tkinter.ttk",
    # darkdetect is CustomTkinter's "System" appearance helper on Windows.
    "darkdetect",
    # convert.py and its sub-tools: in frozen mode driver_studio dispatches
    # to these as in-process modules rather than spawning python. The
    # dispatcher uses importlib.import_module("tools.<name>"), which
    # PyInstaller's static analysis cannot follow, so we name them here.
    "tools",
    "tools.convert",
    "tools.convert_gui",
    "tools.pkp_dump",
    "tools.pkp_build",
    "tools.pkp_validate",
    "tools.pkp2cs",
    "tools.pkg_dump",
    "tools.pkg_patch",
]

excludes = [
    "_bootlocale",
    # The rest of the stdlib we don't ship anything that uses: trim the
    # bundle a bit without risking a missing import at run time.
    "pytest",
    "sphinx",
]


a = Analysis(
    [str(ENTRY)],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="driver_studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # No terminal window: this is a real GUI app, not a TUI.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
