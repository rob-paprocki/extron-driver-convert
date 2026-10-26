#!/usr/bin/env python3
"""Headless smoke tests for tools/convert_gui.py.

Walks the GUI without a visible window: imports the module (which must NOT
touch Tk at module-import time), builds a withdrawn root, instantiates the
ConvertGui, cycles through every verb, and exercises the subprocess runner
end-to-end against a safe no-op invocation. Standard library only.

Skips on headless systems where Tk can't initialise (no DISPLAY / no X11,
Linux CI without xvfb). On Windows and macOS the Tk bindings always have a
display, so the full suite runs.
"""
from __future__ import annotations

import sys
import time
import tkinter as tk
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    _root_probe = tk.Tk()
    _root_probe.withdraw()
    _root_probe.destroy()
    TK_AVAILABLE = True
except tk.TclError:
    TK_AVAILABLE = False


# Import late: the module must be importable WITHOUT a Tk root (that was the
# original bug — VERBS at module scope allocated StringVars eagerly).
import tools.convert_gui as cg  # noqa: E402


class TestFieldSpecs(unittest.TestCase):
    """Field specs must be constructible without a Tk root (they are built
    at module import time, before the GUI calls `tk.Tk()`)."""

    def test_module_import_does_not_touch_tk(self):
        for v in cg.VERBS:
            for f in v.fields:
                # The var slot should still be None — render() allocates it.
                self.assertIsNone(f.var, f"{v.verb}/{f.label}: var set at import")

    def test_clone_field_returns_same_type_and_label(self):
        for v in cg.VERBS:
            for f in v.fields:
                c = cg._clone_field(f)
                self.assertIs(type(c), type(f))
                self.assertEqual(c.label, f.label)
                self.assertIsNone(c.var)

    def test_unrendered_argv_tokens_are_empty(self):
        for v in cg.VERBS:
            for f in v.fields:
                self.assertEqual(f.argv_tokens(), [],
                                 f"{v.verb}/{f.label}: unrendered field "
                                 f"emitted argv: {f.argv_tokens()}")

    def test_every_convert_verb_is_present(self):
        expected = {"pkp2cs", "cs2pkp", "pkg2cs", "pkp2pkg",
                    "dump", "validate", "verify"}
        self.assertEqual({v.verb for v in cg.VERBS}, expected)


@unittest.skipUnless(TK_AVAILABLE, "Tk not available in this environment")
class TestGuiWiring(unittest.TestCase):
    """Build the whole GUI in a withdrawn root and exercise it headlessly."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.gui = cg.ConvertGui(self.root)

    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_each_verb_renders_its_fields(self):
        for i, spec in enumerate(cg.VERBS):
            self.gui.verb_list.selection_clear(0, "end")
            self.gui.verb_list.selection_set(i)
            self.gui._on_verb_select()
            self.root.update_idletasks()
            self.assertEqual(self.gui.selected_verb, spec.verb)
            self.assertEqual(len(self.gui.form_fields), len(spec.fields))
            # After render, each field should have *some* backing storage:
            # most carry a Tk var; RepeatableField uses a Text widget instead.
            for f in self.gui.form_fields:
                has_backing = (f.var is not None
                               or getattr(f, "text", None) is not None)
                self.assertTrue(has_backing,
                                f"{spec.verb}/{f.label} not rendered")

    def test_run_dispatches_subprocess_and_captures_exit_code(self):
        # 'validate' with a nonexistent file: convert.py reports Unparseable
        # and exits non-zero. End-to-end exercises argv assembly, Popen, the
        # pump thread, and the on_done callback.
        validate_idx = [v.verb for v in cg.VERBS].index("validate")
        self.gui.verb_list.selection_clear(0, "end")
        self.gui.verb_list.selection_set(validate_idx)
        self.gui._on_verb_select()
        self.assertEqual(len(self.gui.form_fields), 1)
        self.gui.form_fields[0].var.set("__definitely-not-a-file__.pkp")

        captured = []
        orig_done = self.gui._on_run_done

        def hook(rc):
            captured.append(rc)
            orig_done(rc)
        self.gui._on_run_done = hook

        self.gui._on_run()
        deadline = time.time() + 20
        while time.time() < deadline and not captured:
            self.root.update()
            time.sleep(0.05)
        self.assertTrue(captured, "runner never completed")
        self.assertNotEqual(captured[0], 0,
                            "validate on nonexistent file should exit nonzero")
        console_text = self.gui.console.get("1.0", "end")
        self.assertIn("Unparseable", console_text,
                      "console should carry convert.py's own output")


if __name__ == "__main__":
    unittest.main(verbosity=2)
