#!/usr/bin/env python3
"""Driver Studio -- unified desktop app for the AV driver converter.

A modern CustomTkinter shell with a left-side navigation and swappable pages.
Mirrors the three project purposes:

  * Convert    -- the seven convert.py verbs with a per-verb form
  * Hand-Author -- (placeholder) build a command surface from an API doc
  * Directions -- the supported-conversion matrix
  * About      -- version and project info

Launch:
    python gui/driver_studio.py

Dependencies: customtkinter + Pillow (see gui/requirements.txt). This is the
one directory in the repo that is not standard-library-only; see gui/README.md
and CLAUDE.md for the rationale.

Design notes:
  * We re-use VERBS, the Field classes, and SubprocessRunner from
    tools/convert_gui.py -- the data model is already stack-agnostic. The
    rendering layer here is CustomTkinter, not ttk.
  * CustomTkinter is a tkinter subclass under the hood, so tkinter.StringVar
    and the subprocess runner's `root.after(...)` pump still work unchanged.
  * The window stays usable at 900x600 and never scrolls horizontally.
"""
from __future__ import annotations

import io
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable, Dict, List, Optional

import customtkinter as ctk

# Make tools/ importable so we can share the Field classes, VERBS, and the
# subprocess runner with the existing stdlib-only tools/convert_gui.py.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.convert_gui import (  # noqa: E402  (sys.path adjusted above)
    VERBS,
    DirOutField,
    Field,
    FileInField,
    FileOutField,
    FlagField,
    RepeatableField,
    SubprocessRunner,
    _clone_field,
    _format_cmd,
)

CONVERT_PY = REPO_ROOT / "tools" / "convert.py"

APP_NAME = "Driver Studio"
APP_VERSION = "0.1.0"
APP_TAGLINE = "Convert and author AV drivers across Extron, Crestron, and Q-SYS"

# Navigation items. Each entry is (key, label, builder) where builder takes
# the parent frame and returns a BasePage instance.
# ---------------------------------------------------------------------------


class BasePage(ctk.CTkFrame):
    """A page shown in the main content area. Subclasses override build()."""

    def __init__(self, master: "DriverStudio"):
        super().__init__(master, fg_color="transparent")
        self.app = master
        self.build()

    def build(self) -> None:
        raise NotImplementedError

    def on_shown(self) -> None:
        """Called every time the page becomes visible. Default: no-op."""


# ---------------------------------------------------------------------------
# InProcessRunner: swapped in for SubprocessRunner when the GUI is running
# from a frozen PyInstaller EXE. The windowed EXE has no reliable stdout
# handle to inherit into a child, so instead we run tools.convert.main() in
# a worker thread with sys.stdout/stderr redirected into the same queue
# SubprocessRunner uses, and keep the same (on_line, on_done, cancel)
# interface so ConvertPage doesn't care which runner is active.
# ---------------------------------------------------------------------------


class _QueueTextIO(io.TextIOBase):
    """A write-only TextIO that pushes each written chunk onto a Queue."""

    def __init__(self, q: "queue.Queue"):
        self._q = q

    def writable(self) -> bool:
        return True

    def write(self, s: str) -> int:  # type: ignore[override]
        if s:
            self._q.put(("line", s))
        return len(s)

    def flush(self) -> None:  # noqa: D401
        return None


class InProcessRunner:
    """Runs a target function in a daemon thread, pumping its stdout/stderr
    into the Tk mainloop via `root.after(50, ...)`. Mirrors the surface of
    SubprocessRunner so ConvertPage can use either interchangeably.

    cancel() is best-effort: Python threads cannot be forcibly killed, so a
    long pkp2cs/validate started here runs to completion even after cancel.
    The flag is set so later state transitions know it was cancelled.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.q: "queue.Queue" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._cancelled = False
        self.on_line: Optional[Callable[[str], None]] = None
        self.on_done: Optional[Callable[[int], None]] = None

    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def run(self, argv: List[str],
            on_line: Callable[[str], None],
            on_done: Callable[[int], None],
            *, cwd: Optional[str] = None) -> None:
        """argv matches the SubprocessRunner interface: argv[0] is the
        interpreter (ignored here), argv[1] is the verb we dispatch to
        tools.convert.main(). cwd is applied via os.chdir() for the thread's
        lifetime so convert.py sub-tools resolve relative paths against the
        user's working directory, not the bundle temp dir."""
        if self.running():
            raise RuntimeError("another operation is already running")
        if len(argv) < 2:
            on_line("[internal error: empty argv]\n")
            on_done(2)
            return
        self.on_line = on_line
        self.on_done = on_done
        self._cancelled = False

        # argv[0] is sys.executable or a convert.py path -- strip it; the
        # in-process convert.main() sees argv[1:] via sys.argv.
        shimmed_argv = ["convert.py"] + list(argv[1:])

        def worker() -> None:
            saved_argv = sys.argv
            saved_stdout = sys.stdout
            saved_stderr = sys.stderr
            saved_cwd = os.getcwd()
            writer = _QueueTextIO(self.q)
            try:
                sys.argv = shimmed_argv
                sys.stdout = writer
                sys.stderr = writer
                if cwd:
                    try:
                        os.chdir(cwd)
                    except OSError as exc:
                        self.q.put(("line", f"[chdir failed: {exc}]\n"))
                from tools import convert
                # In frozen mode, tools.convert._run subprocesses the EXE for
                # each sub-tool which would recursively launch the GUI. Patch
                # _run to dispatch sub-tools in-process instead.
                convert._run = _frozen_run_subtool  # type: ignore[attr-defined]
                try:
                    rc = convert.main()
                except SystemExit as exc:
                    rc = int(exc.code) if isinstance(exc.code, int) else (
                        0 if exc.code is None else 1)
                except Exception as exc:  # noqa: BLE001
                    writer.write(f"[error: {type(exc).__name__}: {exc}]\n")
                    rc = 1
                self.q.put(("done", int(rc) if rc is not None else 0))
            finally:
                sys.argv = saved_argv
                sys.stdout = saved_stdout
                sys.stderr = saved_stderr
                try:
                    os.chdir(saved_cwd)
                except OSError:
                    pass

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
        self.root.after(50, self._drain)

    def cancel(self) -> None:
        # Best-effort: there is no clean way to kill a Python thread. We flag
        # the cancel; the GUI appends a note; the thread runs to completion.
        self._cancelled = True

    def _drain(self) -> None:
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "line":
                    if self.on_line:
                        self.on_line(payload)
                elif kind == "done":
                    if self.on_done:
                        self.on_done(int(payload))
                    return
        except queue.Empty:
            pass
        if self.running() or not self.q.empty():
            self.root.after(50, self._drain)


def _frozen_run_subtool(argv: List[str]) -> int:
    """Replacement for tools.convert._run when the EXE calls convert.main()
    in-process. argv is like ["<path>/pkp_validate.py", "<file>.pkp"]; we
    dispatch the sub-tool as an in-process module call."""
    if not argv:
        return 2
    sub = _match_tools_script(argv[0])
    if sub is None:
        # Fall back to a real subprocess for anything unexpected (should be
        # rare -- convert.py's _run only targets known sub-tools).
        return subprocess.run([sys.executable] + argv).returncode
    import importlib
    module = importlib.import_module(f"tools.{sub}")
    saved_argv = sys.argv
    try:
        sys.argv = [argv[0]] + list(argv[1:])
        try:
            rc = module.main()
        except SystemExit as exc:
            return int(exc.code) if isinstance(exc.code, int) else (
                0 if exc.code is None else 1)
        return int(rc) if rc is not None else 0
    finally:
        sys.argv = saved_argv


# ---------------------------------------------------------------------------
# Convert page: the seven convert.py verbs with a per-verb form.
# ---------------------------------------------------------------------------


class ConvertPage(BasePage):
    def build(self) -> None:
        self.selected_verb: Optional[str] = None
        self.form_fields: List[Field] = []
        # In a frozen EXE (console=False) the usual subprocess + pipe path
        # can't be relied on for stdout capture, so run convert.main() in a
        # worker thread with sys.stdout redirected. In dev mode the proven
        # SubprocessRunner stays in play (it supports proc.terminate()
        # cancellation, which the in-process path cannot).
        if _is_frozen():
            self.runner = InProcessRunner(self.app)  # type: ignore[arg-type]
        else:
            self.runner = SubprocessRunner(self.app)  # type: ignore[arg-type]

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Verb picker on the left -----------------------------------------
        picker = ctk.CTkFrame(self, width=260, corner_radius=10)
        picker.grid(row=0, column=0, rowspan=2, sticky="nsw",
                    padx=(0, 12), pady=0)
        picker.grid_propagate(False)
        ctk.CTkLabel(picker, text="Operation",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6))

        self.verb_buttons: Dict[str, ctk.CTkButton] = {}
        for spec in VERBS:
            btn = ctk.CTkButton(
                picker, text=spec.verb,
                anchor="w", height=34, corner_radius=6,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda v=spec.verb: self._select_verb(v),
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.verb_buttons[spec.verb] = btn

        # Right side: title/description + form + run buttons -------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=1, sticky="new")
        header.grid_columnconfigure(0, weight=1)

        self.verb_title = ctk.CTkLabel(
            header, text="", anchor="w",
            font=ctk.CTkFont(size=16, weight="bold"))
        self.verb_title.grid(row=0, column=0, sticky="we")

        self.verb_desc = ctk.CTkLabel(
            header, text="", anchor="w", justify="left",
            text_color=("gray30", "gray70"),
            wraplength=700)
        self.verb_desc.grid(row=1, column=0, sticky="we", pady=(2, 10))

        # The form sits in a scrollable frame -- long verbs (cs2pkp) stay
        # usable even on small windows.
        self.form_frame = ctk.CTkScrollableFrame(
            self, corner_radius=10, label_text="")
        self.form_frame.grid(row=1, column=1, sticky="nsew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Button row at the bottom (above the console).
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=2, sticky="we", pady=(10, 6))
        buttons.grid_columnconfigure(2, weight=1)
        self.run_btn = ctk.CTkButton(
            buttons, text="Run", width=100,
            command=self._on_run)
        self.run_btn.grid(row=0, column=0, padx=(0, 8))
        self.cancel_btn = ctk.CTkButton(
            buttons, text="Cancel", width=100, state="disabled",
            fg_color=("gray80", "gray30"),
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray40"),
            command=self._on_cancel)
        self.cancel_btn.grid(row=0, column=1)
        ctk.CTkButton(
            buttons, text="Clear console", width=120,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            command=self._clear_console
        ).grid(row=0, column=3, sticky="e")

        # Console pane ----------------------------------------------------
        console_wrap = ctk.CTkFrame(self, corner_radius=10)
        console_wrap.grid(row=3, column=0, columnspan=2, sticky="nsew",
                          pady=(0, 0))
        console_wrap.grid_rowconfigure(1, weight=1)
        console_wrap.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            console_wrap, text="Output", anchor="w",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        self.console = ctk.CTkTextbox(
            console_wrap, height=200, wrap="word",
            font=ctk.CTkFont(family=_mono_family(), size=11))
        self.console.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.console.configure(state="disabled")

        self.grid_rowconfigure(3, weight=2)

        # Status label (per-page). The app also has a global status bar; this
        # one tracks the Convert operation specifically.
        self.status_label = ctk.CTkLabel(
            self, text="Ready", anchor="w",
            text_color=("gray30", "gray70"))
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="we",
                               pady=(4, 0))

        if VERBS:
            self._select_verb(VERBS[0].verb)

    # ---- verb selection ----------------------------------------------------

    def _select_verb(self, verb: str) -> None:
        spec = next((v for v in VERBS if v.verb == verb), None)
        if spec is None:
            return
        self.selected_verb = verb
        self.verb_title.configure(text=f"{spec.verb}  --  {spec.title}")
        self.verb_desc.configure(text=spec.description)

        # Highlight the active button.
        for v, btn in self.verb_buttons.items():
            if v == verb:
                btn.configure(fg_color=("gray80", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Rebuild the form for this verb.
        for child in self.form_frame.winfo_children():
            child.destroy()
        self.form_fields = []
        row = 0
        for template in spec.fields:
            clone = _clone_field(template)
            self.form_fields.append(clone)
            _render_field_ctk(clone, self.form_frame, row)
            row += 2  # help label consumes the next row

    # ---- run / cancel ------------------------------------------------------

    def _on_run(self) -> None:
        if self.selected_verb is None:
            return
        if self.runner.running():
            messagebox.showwarning(
                "Busy", "Another operation is already running. Cancel it first.")
            return
        argv_rest: List[str] = []
        for f in self.form_fields:
            argv_rest += f.argv_tokens()
        argv = _build_convert_argv(self.selected_verb, argv_rest)
        self._append_console(f"\n$ {_format_cmd(argv)}\n")
        self.status_label.configure(text=f"Running: {self.selected_verb}")
        self.app.set_status(f"Running: {self.selected_verb}")
        self.run_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        # In frozen mode we don't want the subprocess inheriting the bundle
        # temp dir as cwd -- let it inherit the user's working directory
        # instead so that relative paths and default output locations behave
        # the way the user expects.
        cwd = os.getcwd() if _is_frozen() else None
        self.runner.run(argv, on_line=self._append_console,
                        on_done=self._on_run_done, cwd=cwd)

    def _on_cancel(self) -> None:
        self.runner.cancel()
        self._append_console("[cancelled by user]\n")

    def _on_run_done(self, rc: int) -> None:
        self._append_console(f"[exit {rc}]\n")
        verb = self.selected_verb or ""
        if rc == 0:
            msg = f"OK: {verb}"
        elif rc < 0:
            msg = f"Failed to launch: {verb}"
        else:
            msg = f"Exit {rc}: {verb}"
        self.status_label.configure(text=msg)
        self.app.set_status(msg)
        self.run_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    def _append_console(self, text: str) -> None:
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self) -> None:
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")


# ---------------------------------------------------------------------------
# Hand-Author page: placeholder for Phase 3.
# ---------------------------------------------------------------------------


class HandAuthorPage(BasePage):
    def build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="Hand-Author",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, pady=(28, 6), padx=24, sticky="w")

        ctk.CTkLabel(
            card, justify="left", anchor="w", wraplength=820,
            text=(
                "A visual editor for building a driver's command surface "
                "from an API document, then emitting ControlScript (.py), "
                "an Extron .pkp (donor transplant until R28 closes), a "
                "Crestron module, a Crestron .pkg, or a Q-SYS Lua plugin."
                "\n\n"
                "The emitters already exist under tools/ and experiments/. "
                "This page will provide the editor UI on top of them: "
                "name/kind, Tx template with named parameters, reply pattern "
                "builder with live regex preview, polling, scope/qualifier, "
                "and a per-target preview pane."
                "\n\n"
                "Not yet implemented. See STATUS.md for the current "
                "roadmap; this placeholder reserves the sidebar slot."
            ),
            text_color=("gray20", "gray80")
        ).grid(row=1, column=0, padx=24, pady=(0, 16), sticky="we")

        pill = ctk.CTkLabel(
            card, text="  Planned  ",
            fg_color=("gray85", "gray25"),
            text_color=("gray10", "gray90"),
            corner_radius=8,
            padx=10, pady=4,
            font=ctk.CTkFont(size=11, weight="bold"))
        pill.grid(row=2, column=0, padx=24, pady=(0, 28), sticky="w")


# ---------------------------------------------------------------------------
# Directions page: static table of supported conversion directions.
# ---------------------------------------------------------------------------


DIRECTIONS: List[tuple] = [
    # (source, target, status, note)
    (".pkp", ".py (ControlScript)", "DONE",
     "pkp2cs. Wire-table parity measured; see STATUS.md."),
    (".py (ControlScript)", ".pkp", "Donor-only",
     "cs2pkp transplants into a round-trip-verified donor. "
     "From-scratch synthesis: ROADMAP R28 (partly done)."),
    (".pkg (Crestron)", ".py (ControlScript)", "Partial",
     "pkg2cs dumps JSON; the finish from JSON to a module is manual."),
    (".pkp", ".pkg (Crestron)", "Patch-only",
     "pkp2pkg swaps embedded resources into a Crestron donor. "
     "Schema mismatch between the two formats is manual. "
     "R35 is the schema-translation design gate on a full emitter; "
     "the licence question D2 was cleared by the owner 2026-09-29."),
    (".qplug (Q-SYS Lua)", ".py (ControlScript)", "In progress",
     "experiments/qsys: value-map lifting, __Match reply decode, "
     "~67% byte-level on the CDT100 pilot (R48)."),
    (".py (ControlScript)", ".qplug (Q-SYS Lua)", "Family plugins",
     "experiments/qsys/cs_to_qplug.py: DTP3 family plugin emitter."),
    (".pkg (Crestron)", ".qplug (Q-SYS Lua)", "Planned",
     "No direct emitter yet; today's path is pkg -> JSON -> ControlScript -> "
     "qplug. A direct emitter is a schema-translation design task, not "
     "licence-gated (D2 cleared by the owner 2026-09-29)."),
]


class DirectionsPage(BasePage):
    def build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Supported conversion directions",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="we", padx=4, pady=(0, 8))

        wrap = ctk.CTkScrollableFrame(self, corner_radius=10)
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.grid_columnconfigure(3, weight=1)

        # Header row.
        header_font = ctk.CTkFont(size=12, weight="bold")
        for col, name in enumerate(["From", "To", "Status", "Note"]):
            ctk.CTkLabel(
                wrap, text=name, anchor="w", font=header_font,
                text_color=("gray20", "gray80")
            ).grid(row=0, column=col, sticky="we", padx=6, pady=(4, 6))

        for i, (src, tgt, status, note) in enumerate(DIRECTIONS, start=1):
            fg = ("gray92", "gray18") if i % 2 else "transparent"
            frame = ctk.CTkFrame(wrap, fg_color=fg, corner_radius=6)
            frame.grid(row=i, column=0, columnspan=4, sticky="we",
                       padx=2, pady=1)
            frame.grid_columnconfigure(3, weight=1)
            ctk.CTkLabel(frame, text=src, anchor="w",
                         font=ctk.CTkFont(family=_mono_family(), size=11)).grid(
                row=0, column=0, sticky="we", padx=8, pady=4)
            ctk.CTkLabel(frame, text=tgt, anchor="w",
                         font=ctk.CTkFont(family=_mono_family(), size=11)).grid(
                row=0, column=1, sticky="we", padx=8, pady=4)
            status_colors = _status_pill_colors(status)
            ctk.CTkLabel(
                frame, text=f"  {status}  ", anchor="w",
                fg_color=status_colors[0],
                text_color=status_colors[1],
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold")
            ).grid(row=0, column=2, sticky="w", padx=8, pady=4)
            ctk.CTkLabel(frame, text=note, anchor="w", wraplength=460,
                         justify="left").grid(
                row=0, column=3, sticky="we", padx=8, pady=4)


def _status_pill_colors(status: str) -> tuple:
    """Return (fg_color, text_color) for a status pill. Uses CTk's
    (light, dark) tuple pattern."""
    s = status.lower()
    if s.startswith("done"):
        return (("#c8e6c9", "#1b5e20"), ("#1b5e20", "#c8e6c9"))
    if "progress" in s or "donor" in s or "family" in s or "partial" in s \
            or "patch" in s:
        return (("#fff8c4", "#5c4a00"), ("#5c4a00", "#fff8c4"))
    if "block" in s:
        return (("#ffcdd2", "#7a1818"), ("#7a1818", "#ffcdd2"))
    return (("gray80", "gray25"), ("gray10", "gray90"))


# ---------------------------------------------------------------------------
# About page.
# ---------------------------------------------------------------------------


class AboutPage(BasePage):
    def build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=28, pady=(28, 4), sticky="w")

        ctk.CTkLabel(
            card, text=f"version {APP_VERSION}",
            text_color=("gray30", "gray70")
        ).grid(row=1, column=0, padx=28, pady=(0, 10), sticky="w")

        ctk.CTkLabel(
            card, text=APP_TAGLINE, anchor="w", justify="left",
            wraplength=720
        ).grid(row=2, column=0, padx=28, pady=(0, 20), sticky="we")

        info_lines = [
            ("Repository", "github.com/rob-paprocki/extron-driver-convert"),
            ("Python", sys.version.split()[0]),
            ("CustomTkinter", ctk.__version__),
            ("Working dir", str(REPO_ROOT)),
        ]
        for i, (k, v) in enumerate(info_lines):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.grid(row=3 + i, column=0, padx=28, pady=2, sticky="we")
            row.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                row, text=k, anchor="w", width=140,
                text_color=("gray30", "gray70"),
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                row, text=v, anchor="w",
                font=ctk.CTkFont(family=_mono_family(), size=12)
            ).grid(row=0, column=1, sticky="we")

        ctk.CTkButton(
            card, text="Open repo folder", width=160,
            command=self._open_repo
        ).grid(row=99, column=0, padx=28, pady=(24, 28), sticky="w")

    def _open_repo(self) -> None:
        try:
            if sys.platform == "win32":
                os.startfile(str(REPO_ROOT))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(REPO_ROOT)])
            else:
                subprocess.Popen(["xdg-open", str(REPO_ROOT)])
        except OSError as exc:
            messagebox.showerror("Open folder failed", str(exc))


# ---------------------------------------------------------------------------
# CustomTkinter field renderers. The Field classes from tools/convert_gui
# describe each form field; this function builds CTk widgets for each kind,
# storing the tk.Variable on the Field so field.argv_tokens() keeps working.
# ---------------------------------------------------------------------------


def _render_field_ctk(f: Field, parent: tk.Widget, row: int) -> None:
    if isinstance(f, FileOutField):
        _render_path_field(f, parent, row, mode="file_out")
    elif isinstance(f, DirOutField):
        _render_path_field(f, parent, row, mode="dir_out")
    elif isinstance(f, FileInField):
        _render_path_field(f, parent, row, mode="file_in")
    elif isinstance(f, FlagField):
        _render_flag_field(f, parent, row)
    elif isinstance(f, RepeatableField):
        _render_repeatable_field(f, parent, row)
    else:
        raise TypeError(f"unknown field type: {type(f).__name__}")


def _render_path_field(
    f: Field, parent: tk.Widget, row: int, mode: str,
) -> None:
    str_var = tk.StringVar()
    f.var = str_var
    ctk.CTkLabel(parent, text=f.label, anchor="w", width=160).grid(
        row=row, column=0, sticky="w", padx=(4, 8), pady=4)
    entry = ctk.CTkEntry(parent, textvariable=str_var)
    entry.grid(row=row, column=1, sticky="we", padx=4, pady=4)

    def browse() -> None:
        if mode == "file_in":
            patterns = getattr(f, "patterns", [])
            path = filedialog.askopenfilename(
                title=f"Select {f.label}",
                filetypes=list(patterns) + [("All files", "*.*")],
                initialdir=str(REPO_ROOT),
            )
        elif mode == "file_out":
            patterns = getattr(f, "patterns", [])
            path = filedialog.asksaveasfilename(
                title=f"Select {f.label}",
                filetypes=list(patterns) + [("All files", "*.*")],
                initialdir=str(REPO_ROOT),
            )
        else:
            path = filedialog.askdirectory(
                title=f"Select {f.label}", initialdir=str(REPO_ROOT))
        if not path:
            return
        try:
            rel = Path(path).resolve().relative_to(REPO_ROOT)
            str_var.set(str(rel))
        except ValueError:
            str_var.set(path)

    ctk.CTkButton(parent, text="Browse", width=80, command=browse).grid(
        row=row, column=2, padx=4, pady=4)
    if f.help:
        ctk.CTkLabel(parent, text=f.help, anchor="w", justify="left",
                     wraplength=620,
                     text_color=("gray40", "gray65")).grid(
            row=row + 1, column=1, columnspan=2, sticky="we", padx=4)


def _render_flag_field(f: FlagField, parent: tk.Widget, row: int) -> None:
    bool_var = tk.BooleanVar()
    f.var = bool_var
    ctk.CTkCheckBox(parent, text=f.label, variable=bool_var).grid(
        row=row, column=1, columnspan=2, sticky="w", padx=4, pady=4)
    if f.help:
        ctk.CTkLabel(parent, text=f.help, anchor="w", justify="left",
                     wraplength=620,
                     text_color=("gray40", "gray65")).grid(
            row=row + 1, column=1, columnspan=2, sticky="we", padx=4)


def _render_repeatable_field(
    f: RepeatableField, parent: tk.Widget, row: int,
) -> None:
    ctk.CTkLabel(parent, text=f.label, anchor="nw", width=160).grid(
        row=row, column=0, sticky="nw", padx=(4, 8), pady=4)
    textbox = ctk.CTkTextbox(parent, height=90, wrap="none",
                             font=ctk.CTkFont(family=_mono_family(), size=11))
    textbox.grid(row=row, column=1, columnspan=2, sticky="we",
                 padx=4, pady=4)
    # RepeatableField.argv_tokens() reads self.text.get("1.0", "end"), and
    # CTkTextbox exposes get()/insert()/delete() with tk.Text semantics.
    f.text = textbox  # type: ignore[assignment]
    if f.help:
        ctk.CTkLabel(parent, text=f.help, anchor="w", justify="left",
                     wraplength=620,
                     text_color=("gray40", "gray65")).grid(
            row=row + 1, column=1, columnspan=2, sticky="we", padx=4)


# ---------------------------------------------------------------------------
# Main application window.
# ---------------------------------------------------------------------------


# Order drives the sidebar display.
NAV_ITEMS: List[tuple] = [
    ("convert", "Convert", ConvertPage),
    ("hand_author", "Hand-Author", HandAuthorPage),
    ("directions", "Directions", DirectionsPage),
    ("about", "About", AboutPage),
]


class DriverStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x760")
        self.minsize(900, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        self._build_statusbar()

        # Show the first page.
        self.pages: Dict[str, BasePage] = {}
        self.current_key: Optional[str] = None
        self.show_page(NAV_ITEMS[0][0])

    # ---- construction ------------------------------------------------------

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(99, weight=1)

        ctk.CTkLabel(
            self.sidebar, text=APP_NAME,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, padx=18, pady=(16, 2), sticky="we")
        ctk.CTkLabel(
            self.sidebar, text=f"v{APP_VERSION}",
            text_color=("gray40", "gray65"),
            anchor="w"
        ).grid(row=1, column=0, padx=18, pady=(0, 14), sticky="we")

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        for i, (key, label, _page_cls) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", height=38,
                corner_radius=8, fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self.show_page(k),
            )
            btn.grid(row=2 + i, column=0, padx=10, pady=2, sticky="we")
            self.nav_buttons[key] = btn

        # Appearance toggle at the bottom.
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.grid(row=100, column=0, sticky="we", padx=10, pady=14)
        bottom.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bottom, text="Appearance",
                     anchor="w",
                     text_color=("gray40", "gray65")).grid(
            row=0, column=0, sticky="we", pady=(0, 4))
        self.appearance = ctk.CTkOptionMenu(
            bottom, values=["System", "Light", "Dark"],
            command=self._on_appearance_change)
        self.appearance.set("System")
        self.appearance.grid(row=1, column=0, sticky="we")

    def _build_main(self) -> None:
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew",
                       padx=20, pady=(16, 10))
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

    def _build_statusbar(self) -> None:
        self.statusbar = ctk.CTkFrame(self, height=28, corner_radius=0)
        self.statusbar.grid(row=1, column=1, sticky="sew")
        self.statusbar.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(
            self.statusbar, text="Ready", anchor="w",
            text_color=("gray30", "gray70"),
            font=ctk.CTkFont(size=11))
        self.status_label.grid(row=0, column=0, sticky="we", padx=14, pady=4)

    # ---- navigation --------------------------------------------------------

    def show_page(self, key: str) -> None:
        # Lazy-build each page the first time it is shown.
        if key not in self.pages:
            page_cls = next((p for k, _lbl, p in NAV_ITEMS if k == key), None)
            if page_cls is None:
                return
            self.pages[key] = page_cls(self)

        # Hide current, show new.
        for k, page in self.pages.items():
            if k == self.current_key and k != key:
                page.grid_forget()
        page = self.pages[key]
        page.grid(row=0, column=0, sticky="nsew", in_=self.main)
        self.current_key = key

        # Highlight the active sidebar button.
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray80", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        page.on_shown()

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    # ---- appearance --------------------------------------------------------

    def _on_appearance_change(self, mode: str) -> None:
        # CustomTkinter accepts "System", "Light", or "Dark".
        ctk.set_appearance_mode(mode)


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _mono_family() -> str:
    if sys.platform == "win32":
        return "Consolas"
    if sys.platform == "darwin":
        return "Menlo"
    return "DejaVu Sans Mono"


def _is_frozen() -> bool:
    """True when running from a PyInstaller onefile EXE."""
    return getattr(sys, "frozen", False)


def _build_convert_argv(verb: str, verb_args: List[str]) -> List[str]:
    """Build argv for a convert.py invocation.

    In dev mode (`python gui/driver_studio.py`), sys.executable is python so
    we spell out convert.py explicitly:

        [python, tools/convert.py, verb, ...args]

    In frozen mode (the EXE), sys.executable IS the EXE. We re-invoke
    ourselves with the verb up front; main() below sees the verb and
    dispatches to convert.main() instead of launching the GUI:

        [driver_studio.exe, verb, ...args]
    """
    if _is_frozen():
        return [sys.executable, verb] + verb_args
    return [sys.executable, str(CONVERT_PY), verb] + verb_args


def _dispatch_cli() -> Optional[int]:
    """Multi-call dispatch for the frozen EXE.

    Three dispatch targets:

      * `driver_studio.exe <verb>  ...`         -> tools.convert.main()
      * `driver_studio.exe tools/<script>.py ...` -> tools.<script>.main()
      * `driver_studio.exe <script>.py ...`     -> tools.<script>.main()

    The second form matters because convert.py's `_run` helper subprocesses
    `[sys.executable, "tools/pkp_validate.py", ...]` and friends; in frozen
    mode `sys.executable` is the EXE itself, so the EXE has to recognise
    sub-tool script invocations too, not just the top-level verbs.

    Returning None means 'nothing to dispatch; fall through to the GUI'.
    """
    if not _is_frozen():
        return None
    if len(sys.argv) < 2:
        return None
    first = sys.argv[1]
    verbs = {v.verb for v in VERBS} | {"directions"}
    if first in verbs:
        from tools import convert  # lazy import keeps GUI startup slim
        # Same reason as InProcessRunner: avoid recursively launching the
        # EXE for each convert.py sub-tool call, which hangs because the
        # child inherits no stdout.
        convert._run = _frozen_run_subtool  # type: ignore[attr-defined]
        try:
            return convert.main()
        except SystemExit as exc:
            return int(exc.code) if isinstance(exc.code, int) else (
                0 if exc.code is None else 1)
    sub = _match_tools_script(first)
    if sub is not None:
        import importlib
        module = importlib.import_module(f"tools.{sub}")
        # Shift sys.argv so the sub-tool's own argparse sees its own argv:
        # argv[0] = the script path, argv[1:] = whatever followed on the EXE
        # command line.
        sys.argv = [sys.argv[1]] + sys.argv[2:]
        try:
            rc = module.main()
        except SystemExit as exc:
            return int(exc.code) if isinstance(exc.code, int) else (
                0 if exc.code is None else 1)
        return int(rc) if rc is not None else 0
    return None


# Known sub-tool scripts invoked by tools/convert.py via `_run`. These must
# match the TOOLS=... constants at the top of tools/convert.py.
_SUB_TOOLS = {
    "pkp_dump", "pkp_build", "pkp_validate", "pkp2cs",
    "pkg_dump", "pkg_patch",
}


def _match_tools_script(path: str) -> Optional[str]:
    """If `path` looks like a tools/*.py invocation, return the bare module
    name (e.g. 'pkp_validate'). Otherwise None."""
    s = path.replace("\\", "/")
    # Accept any of: "pkp_validate.py", "tools/pkp_validate.py",
    # "/abs/path/tools/pkp_validate.py".
    if not s.endswith(".py"):
        return None
    base = s.rsplit("/", 1)[-1][:-3]
    if base in _SUB_TOOLS:
        return base
    return None


def main() -> int:
    cli_rc = _dispatch_cli()
    if cli_rc is not None:
        return cli_rc
    if not CONVERT_PY.exists() and not _is_frozen():
        print(f"error: {CONVERT_PY} not found. Launch driver_studio.py "
              f"from the repo root.", file=sys.stderr)
        return 2
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = DriverStudio()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
