#!/usr/bin/env python3
"""Desktop GUI front end for tools/convert.py.

Pure Python standard library (tkinter + subprocess + threading). Runs anywhere
Python 3.8+ is installed with the Tk bindings. No pip install, no bundled
assets.

The GUI is a thin shell around `tools/convert.py` -- it does not re-implement
any conversion semantics. Each verb maps to one subprocess call. The output
console streams the child's combined stdout/stderr live so a long-running
build or validate is visible.

Launch:
    python tools/convert_gui.py

The window is split into three panes:
  * Left:   verb picker (one row per convert.py verb)
  * Right:  per-verb form (file pickers, checkboxes, text fields)
  * Bottom: Run / Cancel buttons + scrolled text output console

If you want to see the matrix of supported conversion directions and their
status (DONE / partial / manual step / planned), click "Directions..." in the
toolbar -- it pops a modal with the same table that `convert.py directions`
prints.
"""
from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Callable, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
CONVERT_PY = REPO_ROOT / "tools" / "convert.py"


# ---------------------------------------------------------------------------
# Per-verb form specifications. Each verb has a title + description, and a
# list of fields that the user fills in. The form converts filled fields into
# argv tokens for `convert.py <verb> ...`. Keeping the specification data-
# driven means adding a new convert.py verb is a one-dict change here.
# ---------------------------------------------------------------------------


class Field:
    """One form field. Subclasses render themselves into a parent frame and
    emit the argv tokens they correspond to when the user clicks Run.

    Tk variables are allocated lazily in render() rather than __init__, so
    module-level VERBS entries can be built before `root = tk.Tk()` runs."""

    def __init__(self, label: str, help: str = ""):
        self.label = label
        self.help = help
        self.var: Optional[tk.Variable] = None
        self.widget: Optional[tk.Widget] = None

    def render(self, parent: ttk.Frame, row: int) -> None:
        raise NotImplementedError

    def argv_tokens(self) -> List[str]:
        """Return argv contribution. Empty list = field not set."""
        raise NotImplementedError


class FileInField(Field):
    """A path to an existing file. Rendered as entry + Browse button."""

    def __init__(self, label: str, patterns: List[tuple], help: str = "",
                 positional: bool = True, flag: str = ""):
        super().__init__(label, help)
        self.patterns = patterns
        self.positional = positional
        self.flag = flag  # e.g. "--donor"; ignored if positional=True

    def render(self, parent: ttk.Frame, row: int) -> None:
        str_var = tk.StringVar()
        self.var = str_var
        ttk.Label(parent, text=self.label).grid(row=row, column=0, sticky="w",
                                                padx=4, pady=4)
        entry = ttk.Entry(parent, textvariable=str_var, width=60)
        entry.grid(row=row, column=1, sticky="we", padx=4, pady=4)
        ttk.Button(parent, text="Browse...",
                   command=self._browse).grid(row=row, column=2, padx=4, pady=4)
        if self.help:
            ttk.Label(parent, text=self.help, foreground="gray40",
                      wraplength=600, justify="left").grid(
                row=row + 1, column=1, columnspan=2, sticky="w", padx=4)
        self.widget = entry

    def _browse(self) -> None:
        if self.var is None:
            return
        path = filedialog.askopenfilename(
            title=f"Select {self.label}",
            filetypes=self.patterns + [("All files", "*.*")],
            initialdir=str(REPO_ROOT),
        )
        if path:
            # Store as repo-relative when possible for cleaner commands.
            try:
                rel = Path(path).resolve().relative_to(REPO_ROOT)
                self.var.set(str(rel))
            except ValueError:
                self.var.set(path)

    def argv_tokens(self) -> List[str]:
        if self.var is None:
            return []
        val = str(self.var.get()).strip()
        if not val:
            return []
        if self.positional:
            return [val]
        return [self.flag, val]


class DirOutField(Field):
    """An output directory. Rendered as entry + Browse button."""

    def __init__(self, label: str, help: str = "", flag: str = "-o"):
        super().__init__(label, help)
        self.flag = flag

    def render(self, parent: ttk.Frame, row: int) -> None:
        str_var = tk.StringVar()
        self.var = str_var
        ttk.Label(parent, text=self.label).grid(row=row, column=0, sticky="w",
                                                padx=4, pady=4)
        entry = ttk.Entry(parent, textvariable=str_var, width=60)
        entry.grid(row=row, column=1, sticky="we", padx=4, pady=4)
        ttk.Button(parent, text="Browse...",
                   command=self._browse).grid(row=row, column=2, padx=4, pady=4)
        if self.help:
            ttk.Label(parent, text=self.help, foreground="gray40",
                      wraplength=600, justify="left").grid(
                row=row + 1, column=1, columnspan=2, sticky="w", padx=4)
        self.widget = entry

    def _browse(self) -> None:
        if self.var is None:
            return
        path = filedialog.askdirectory(title=f"Select {self.label}",
                                       initialdir=str(REPO_ROOT))
        if path:
            try:
                rel = Path(path).resolve().relative_to(REPO_ROOT)
                self.var.set(str(rel))
            except ValueError:
                self.var.set(path)

    def argv_tokens(self) -> List[str]:
        if self.var is None:
            return []
        val = str(self.var.get()).strip()
        if not val:
            return []
        return [self.flag, val]


class FileOutField(DirOutField):
    """An output FILE (not directory). Same shape as DirOutField except the
    Browse button opens a save-file dialog."""

    def __init__(self, label: str, patterns: List[tuple], help: str = "",
                 flag: str = "-o"):
        super().__init__(label, help, flag)
        self.patterns = patterns

    def _browse(self) -> None:
        if self.var is None:
            return
        path = filedialog.asksaveasfilename(
            title=f"Select {self.label}",
            filetypes=self.patterns + [("All files", "*.*")],
            initialdir=str(REPO_ROOT),
        )
        if path:
            try:
                rel = Path(path).resolve().relative_to(REPO_ROOT)
                self.var.set(str(rel))
            except ValueError:
                self.var.set(path)


class FlagField(Field):
    """A boolean --flag. Rendered as a checkbox."""

    def __init__(self, label: str, flag: str, help: str = ""):
        super().__init__(label, help)
        self.flag = flag

    def render(self, parent: ttk.Frame, row: int) -> None:
        bool_var = tk.BooleanVar()
        self.var = bool_var
        ttk.Checkbutton(parent, text=self.label, variable=bool_var).grid(
            row=row, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        if self.help:
            ttk.Label(parent, text=self.help, foreground="gray40",
                      wraplength=600, justify="left").grid(
                row=row + 1, column=1, columnspan=2, sticky="w", padx=4)

    def argv_tokens(self) -> List[str]:
        if self.var is None:
            return []
        return [self.flag] if self.var.get() else []


class RepeatableField(Field):
    """A repeatable --flag KEY=VAL input (used for cs2pkp's --script and
    --set-string). Rendered as a multi-line text box, one entry per line."""

    def __init__(self, label: str, flag: str, help: str = ""):
        super().__init__(label, help)
        self.flag = flag
        self.text: Optional[tk.Text] = None

    def render(self, parent: ttk.Frame, row: int) -> None:
        ttk.Label(parent, text=self.label).grid(row=row, column=0, sticky="nw",
                                                padx=4, pady=4)
        self.text = tk.Text(parent, width=60, height=4, wrap="none")
        self.text.grid(row=row, column=1, columnspan=2, sticky="we",
                       padx=4, pady=4)
        if self.help:
            ttk.Label(parent, text=self.help, foreground="gray40",
                      wraplength=600, justify="left").grid(
                row=row + 1, column=1, columnspan=2, sticky="w", padx=4)

    def argv_tokens(self) -> List[str]:
        if self.text is None:
            return []
        lines = [ln.strip() for ln in self.text.get("1.0", "end").splitlines()]
        out: List[str] = []
        for ln in lines:
            if ln:
                out += [self.flag, ln]
        return out


class VerbSpec:
    def __init__(self, verb: str, title: str, description: str,
                 fields: List[Field]):
        self.verb = verb
        self.title = title
        self.description = description
        self.fields = fields


# One VerbSpec per convert.py verb we expose in the GUI. Order drives the
# left-column verb list.
VERBS: List[VerbSpec] = [
    VerbSpec(
        "pkp2cs",
        "Extron .pkp -> ControlScript (.py)",
        "Translate an Extron .pkp package into one or more ControlScript "
        "Python modules. Wire-table parity has been measured against the "
        "vendor's shipped modules; see STATUS.md for the current scorecard.",
        [
            FileInField(
                "Input .pkp",
                [("Extron package", "*.pkp")],
                help="Path to an Extron package.",
            ),
            DirOutField(
                "Output directory",
                help="Directory for the generated .py module(s). Defaults to "
                     "the current directory if left blank.",
            ),
        ],
    ),
    VerbSpec(
        "cs2pkp",
        "ControlScript -> Extron .pkp (donor transplant)",
        "Transplant one or more ControlScript modules into a donor .pkp. The "
        "donor must round-trip byte-for-byte or the build is refused. KEYs "
        "are the donor's embedded script resource names (discover them with "
        "the 'dump' verb). From-scratch synthesis is tracked as ROADMAP R28.",
        [
            FileInField(
                "Donor .pkp",
                [("Extron package", "*.pkp")],
                help="A real, round-trip-verified .pkp to transplant into.",
            ),
            FileOutField(
                "Output .pkp",
                [("Extron package", "*.pkp")],
                help="Where to write the transplanted package.",
            ),
            RepeatableField(
                "Replace scripts",
                "--script",
                help="One KEY=FILE per line. Each line replaces an embedded "
                     "script resource. Example:\n"
                     "  Driver.py=experiments/skeleton_i20/out/mymodule.py",
            ),
            RepeatableField(
                "Replace strings",
                "--set-string",
                help="One ID=VAL per line. Each line replaces a .NET NRBF "
                     "string record by object id. Finding 18 warning: never "
                     "reuse an id with a flipped sign -- verify with 'verify "
                     "--load-package' before trusting the output.",
            ),
        ],
    ),
    VerbSpec(
        "pkg2cs",
        "Crestron .pkg -> ControlScript (via JSON)",
        "Dumps the Crestron driver JSON via pkg_dump.py. The finish from "
        "JSON to a ControlScript module is a manual step today; the dialect "
        "patterns are in pkp2cs.py and the Crestron-specific translator "
        "pieces live under experiments/.",
        [
            FileInField(
                "Input .pkg",
                [("Crestron package", "*.pkg")],
                help="Path to a Crestron driver package.",
            ),
            DirOutField(
                "Output directory",
                help="Directory for the extracted driver JSON.",
            ),
        ],
    ),
    VerbSpec(
        "pkp2pkg",
        "Extron .pkp -> Crestron .pkg (patch only)",
        "Patch-only cross-vendor edit: dumps the Extron package's graph and "
        "swaps embedded resources into a Crestron donor .pkg. Schema "
        "mismatch between the two formats is a manual step; this verb "
        "handles the resource swap only. See STATUS.md D2 for the Crestron "
        "licence question.",
        [
            FileInField(
                "Source .pkp",
                [("Extron package", "*.pkp")],
                help="The Extron package whose resources get dumped.",
            ),
            FileInField(
                "Donor .pkg",
                [("Crestron package", "*.pkg")],
                help="The Crestron package to patch.",
                positional=False,
                flag="--donor",
            ),
            FileOutField(
                "Output .pkg",
                [("Crestron package", "*.pkg")],
                help="Where to write the patched Crestron package.",
            ),
        ],
    ),
    VerbSpec(
        "dump",
        "Dump a .pkp or .pkg to JSON",
        "Dispatches by extension to pkp_dump.py or pkg_dump.py. Useful for "
        "inspecting a package's command graph, embedded resources, or NRBF "
        "object ids before an edit.",
        [
            FileInField(
                "Input .pkp or .pkg",
                [("Extron package", "*.pkp"),
                 ("Crestron package", "*.pkg")],
                help="Path to the package to dump.",
            ),
            FileOutField(
                "Output JSON",
                [("JSON file", "*.json")],
                help="Where to write the JSON. If left blank, the JSON is "
                     "printed to the console below.",
            ),
            FlagField(
                "Resolve references (.pkp only)",
                "--resolve",
                help="Resolve NRBF MemberReference / ClassWithId back-"
                     "references into the records they point at. Larger "
                     "output, easier to read.",
            ),
        ],
    ),
    VerbSpec(
        "validate",
        "Validate .pkp (Python model)",
        "Local validation using this project's Python reimplementation of "
        "Extron's hash validator (Finding 16). This checks the format, but "
        "a package can validate here and still fail Global Configurator -- "
        "run 'verify' for the real acceptance gate.",
        [
            FileInField(
                "Package to validate",
                [("Extron package", "*.pkp")],
                help="You can also pass several files from the command line; "
                     "this form takes one.",
            ),
        ],
    ),
    VerbSpec(
        "verify",
        "Verify .pkp (Extron's deserializer)",
        "Validates first (as above), then invokes Extron's own BinaryFormatter "
        "deserializer via experiments/gcp_harness/Load-Package.ps1 under "
        "32-bit PowerShell. This is the Finding 18 gate: a package may "
        "validate yet still refuse to load.",
        [
            FileInField(
                "Package to verify",
                [("Extron package", "*.pkp")],
                help="Path to the package to run through the full validate "
                     "+ deserialize pipeline.",
            ),
            FlagField(
                "Also run Load-Package (Windows only)",
                "--load-package",
                help="On a Windows GC workstation, invoke "
                     "experiments/gcp_harness/Load-Package.ps1 directly. "
                     "Off Windows (or without this flag) the exact command "
                     "is printed for the user to run manually.",
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Subprocess runner. Threads one `python convert.py <verb> <args>` call, pumps
# its combined stdout/stderr into a queue that the Tk mainloop drains onto
# the output console.
# ---------------------------------------------------------------------------


class SubprocessRunner:
    """One subprocess at a time. Caller supplies on_line and on_done
    callbacks; these fire on the Tk main thread via `.after`."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.proc: Optional[subprocess.Popen] = None
        self.q: queue.Queue = queue.Queue()
        self.on_line: Optional[Callable[[str], None]] = None
        self.on_done: Optional[Callable[[int], None]] = None

    def running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def run(self, argv: List[str],
            on_line: Callable[[str], None],
            on_done: Callable[[int], None]) -> None:
        if self.running():
            raise RuntimeError("another subprocess is already running")
        self.on_line = on_line
        self.on_done = on_done

        # On Windows, hide the console window the subprocess would otherwise
        # pop up when launched from a GUI parent.
        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = 0x08000000  # CREATE_NO_WINDOW

        try:
            self.proc = subprocess.Popen(
                argv,
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                bufsize=1,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
        except OSError as exc:
            on_line(f"[launch failed: {exc}]\n")
            on_done(-1)
            return

        threading.Thread(target=self._pump, daemon=True).start()
        self.root.after(50, self._drain)

    def cancel(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except OSError:
                pass

    def _pump(self) -> None:
        assert self.proc is not None
        assert self.proc.stdout is not None
        try:
            for line in self.proc.stdout:
                self.q.put(("line", line))
        except (OSError, ValueError):
            pass
        rc = self.proc.wait()
        self.q.put(("done", rc))

    def _drain(self) -> None:
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "line":
                    if self.on_line:
                        self.on_line(payload)
                elif kind == "done":
                    if self.on_done:
                        self.on_done(payload)
                    return
        except queue.Empty:
            pass
        if self.running() or not self.q.empty():
            self.root.after(50, self._drain)


# ---------------------------------------------------------------------------
# Main window.
# ---------------------------------------------------------------------------


class ConvertGui:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Extron / Crestron / Q-SYS driver converter")
        self.root.geometry("1000x720")
        self.root.minsize(800, 560)

        self.verb_specs: Dict[str, VerbSpec] = {v.verb: v for v in VERBS}
        self.selected_verb: Optional[str] = None
        self.form_fields: List[Field] = []
        self.runner = SubprocessRunner(root)

        self._build_toolbar()
        self._build_body()
        self._build_console()
        self._build_status()

        # Preselect the first verb.
        self.verb_list.selection_set(0)
        self._on_verb_select()

    # --- UI construction ---------------------------------------------------

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self.root, padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text="Convert driver files between Extron, Crestron,",
                  font=("TkDefaultFont", 10, "bold")).pack(side="left")
        ttk.Label(bar, text=" and Q-SYS formats.",
                  font=("TkDefaultFont", 10)).pack(side="left")
        ttk.Button(bar, text="Directions...",
                   command=self._show_directions).pack(side="right", padx=4)
        ttk.Button(bar, text="Open repo folder",
                   command=self._open_repo).pack(side="right", padx=4)

    def _build_body(self) -> None:
        body = ttk.Frame(self.root, padding=(8, 0, 8, 0))
        body.pack(fill="both", expand=False)

        left = ttk.Frame(body)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Operation",
                  font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.verb_list = tk.Listbox(left, width=36, height=len(VERBS),
                                    exportselection=False,
                                    activestyle="dotbox")
        for v in VERBS:
            self.verb_list.insert("end", f"{v.verb}  --  {v.title}")
        self.verb_list.pack(fill="y")
        self.verb_list.bind("<<ListboxSelect>>",
                            lambda _e: self._on_verb_select())

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.verb_title = ttk.Label(right, text="",
                                    font=("TkDefaultFont", 11, "bold"))
        self.verb_title.pack(anchor="w")
        self.verb_desc = ttk.Label(right, text="", wraplength=640,
                                   justify="left", foreground="gray30")
        self.verb_desc.pack(anchor="w", pady=(2, 8))

        self.form_frame = ttk.Frame(right)
        self.form_frame.pack(fill="x")
        self.form_frame.columnconfigure(1, weight=1)

        buttons = ttk.Frame(right)
        buttons.pack(fill="x", pady=(10, 0))
        self.run_btn = ttk.Button(buttons, text="Run", command=self._on_run)
        self.run_btn.pack(side="left")
        self.cancel_btn = ttk.Button(buttons, text="Cancel",
                                     command=self._on_cancel, state="disabled")
        self.cancel_btn.pack(side="left", padx=6)
        ttk.Button(buttons, text="Clear console",
                   command=self._clear_console).pack(side="right")

    def _build_console(self) -> None:
        wrap = ttk.LabelFrame(self.root, text="Output",
                              padding=(6, 6))
        wrap.pack(fill="both", expand=True, padx=8, pady=(10, 0))
        self.console = scrolledtext.ScrolledText(
            wrap, wrap="word", height=12, state="disabled",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
        )
        self.console.pack(fill="both", expand=True)

    def _build_status(self) -> None:
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", side="bottom")
        self.status = ttk.Label(bar, text="Ready", anchor="w",
                                padding=(8, 4), relief="sunken")
        self.status.pack(fill="x")

    # --- Verb selection ----------------------------------------------------

    def _on_verb_select(self) -> None:
        sel = self.verb_list.curselection()
        if not sel:
            return
        spec = VERBS[sel[0]]
        self.selected_verb = spec.verb
        self.verb_title.configure(text=f"{spec.verb}  --  {spec.title}")
        self.verb_desc.configure(text=spec.description)

        for child in self.form_frame.winfo_children():
            child.destroy()
        self.form_fields = []

        row = 0
        for f in spec.fields:
            # Build a fresh Field instance for each spec render so values don't
            # leak between verb switches.
            clone = _clone_field(f)
            self.form_fields.append(clone)
            clone.render(self.form_frame, row)
            row += 2  # help label consumes the next row

    # --- Run / Cancel ------------------------------------------------------

    def _on_run(self) -> None:
        if self.selected_verb is None:
            return
        if self.runner.running():
            messagebox.showwarning("Busy", "Another operation is already "
                                   "running. Cancel it first.")
            return

        argv_rest: List[str] = []
        for f in self.form_fields:
            argv_rest += f.argv_tokens()

        argv = [sys.executable, str(CONVERT_PY), self.selected_verb] + argv_rest
        self._append_console(f"\n$ {_format_cmd(argv)}\n")
        self.status.configure(text=f"Running: {self.selected_verb}")
        self.run_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")

        self.runner.run(argv, on_line=self._append_console,
                        on_done=self._on_run_done)

    def _on_cancel(self) -> None:
        self.runner.cancel()
        self._append_console("[cancelled by user]\n")

    def _on_run_done(self, rc: int) -> None:
        self._append_console(f"[exit {rc}]\n")
        if rc == 0:
            self.status.configure(text=f"OK: {self.selected_verb}")
        elif rc < 0:
            self.status.configure(text=f"Failed to launch: {self.selected_verb}")
        else:
            self.status.configure(text=f"Exit {rc}: {self.selected_verb}")
        self.run_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    # --- Console helpers ---------------------------------------------------

    def _append_console(self, text: str) -> None:
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self) -> None:
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    # --- Directions popup --------------------------------------------------

    def _show_directions(self) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Supported conversion directions")
        popup.geometry("820x320")
        popup.transient(self.root)
        text = scrolledtext.ScrolledText(
            popup, wrap="none", state="normal",
            font=("Consolas" if sys.platform == "win32" else "TkFixedFont", 9),
        )
        text.pack(fill="both", expand=True)
        try:
            out = subprocess.check_output(
                [sys.executable, str(CONVERT_PY), "directions"],
                cwd=str(REPO_ROOT), text=True, encoding="utf-8",
                errors="replace",
                stderr=subprocess.STDOUT,
            )
        except OSError as exc:
            out = f"[failed to run convert.py directions: {exc}]"
        except subprocess.CalledProcessError as exc:
            out = f"[convert.py directions exited {exc.returncode}]\n{exc.output}"
        text.insert("1.0", out)
        text.configure(state="disabled")
        ttk.Button(popup, text="Close",
                   command=popup.destroy).pack(pady=6)

    def _open_repo(self) -> None:
        path = str(REPO_ROOT)
        try:
            if sys.platform == "win32":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except OSError as exc:
            messagebox.showerror("Open folder failed", str(exc))


def _clone_field(f: Field) -> Field:
    """Return a fresh Field with the same configuration as f. Each verb
    render needs its own StringVar / BooleanVar so values stay independent."""
    if isinstance(f, FileOutField):
        return FileOutField(f.label, f.patterns, f.help, f.flag)
    if isinstance(f, DirOutField):
        return DirOutField(f.label, f.help, f.flag)
    if isinstance(f, FileInField):
        return FileInField(f.label, f.patterns, f.help, f.positional, f.flag)
    if isinstance(f, FlagField):
        return FlagField(f.label, f.flag, f.help)
    if isinstance(f, RepeatableField):
        return RepeatableField(f.label, f.flag, f.help)
    raise TypeError(f"unknown field type: {type(f).__name__}")


def _format_cmd(argv: List[str]) -> str:
    """Shell-quote-ish rendering of argv for the console header."""
    parts = []
    for a in argv:
        if any(ch in a for ch in " \t\"'()"):
            parts.append(f'"{a}"')
        else:
            parts.append(a)
    return " ".join(parts)


def main() -> int:
    if not CONVERT_PY.exists():
        print(f"error: {CONVERT_PY} not found. Launch convert_gui.py from "
              f"the repo root.", file=sys.stderr)
        return 2
    root = tk.Tk()
    # Prefer the ttk theme that looks native-ish on each platform.
    try:
        style = ttk.Style()
        if sys.platform == "win32" and "vista" in style.theme_names():
            style.theme_use("vista")
        elif sys.platform == "darwin" and "aqua" in style.theme_names():
            style.theme_use("aqua")
        else:
            style.theme_use("clam")
    except tk.TclError:
        pass
    ConvertGui(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
