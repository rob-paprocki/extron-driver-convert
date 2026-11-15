#!/usr/bin/env python3
"""Headless smoke tests for gui/driver_studio.py.

Walks the Driver Studio shell without a visible window:

  * Imports the module without touching Tk at import time (the Field spec
    classes stay var-less until a page builds them).
  * Verifies every nav target can be instantiated.
  * Switches to each page in turn and confirms it renders.
  * End-to-end: Convert page runs `convert.py validate` on a nonexistent
    file and captures the exit code via the SubprocessRunner.

Skips the Tk-dependent suite when a display or CustomTkinter is missing.
"""
from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    ctk = None  # type: ignore[assignment]

try:
    import tkinter as tk
    _probe = tk.Tk()
    _probe.withdraw()
    _probe.destroy()
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


# Importing the module should NOT allocate any Tk vars (the Field specs stay
# bare until a page renders them). This is the regression that bit the
# stdlib convert_gui.py when VERBS was first built at module scope.
import gui.driver_studio as ds  # type: ignore[import-not-found]  # noqa: E402


class TestModuleShape(unittest.TestCase):

    def test_nav_items_are_registered(self):
        keys = [k for k, _label, _cls in ds.NAV_ITEMS]
        self.assertIn("convert", keys)
        self.assertIn("hand_author", keys)
        self.assertIn("directions", keys)
        self.assertIn("about", keys)
        self.assertEqual(len(keys), len(set(keys)),
                         "nav keys must be unique")

    def test_import_does_not_touch_tk_vars(self):
        # Each VerbSpec's Field templates must still be var-less at import.
        from tools.convert_gui import VERBS
        for v in VERBS:
            for f in v.fields:
                self.assertIsNone(f.var, f"{v.verb}/{f.label}: var set early")

    def test_directions_table_populated(self):
        self.assertGreater(len(ds.DIRECTIONS), 3)
        for row in ds.DIRECTIONS:
            self.assertEqual(len(row), 4,
                             "every direction row needs (src, tgt, status, note)")


@unittest.skipUnless(CTK_AVAILABLE and TK_AVAILABLE,
                     "CustomTkinter or Tk display not available")
class TestDriverStudioLive(unittest.TestCase):

    def setUp(self):
        assert ctk is not None
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.app = ds.DriverStudio()
        self.app.withdraw()  # don't flash a window on screen

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass

    def test_each_nav_target_builds(self):
        for key, label, _cls in ds.NAV_ITEMS:
            self.app.show_page(key)
            self.app.update_idletasks()
            self.assertIn(key, self.app.pages,
                          f"page {key} ({label}) did not instantiate")
            self.assertEqual(self.app.current_key, key)

    def test_convert_page_renders_every_verb(self):
        from tools.convert_gui import VERBS
        self.app.show_page("convert")
        self.app.update_idletasks()
        convert = self.app.pages["convert"]
        for spec in VERBS:
            convert._select_verb(spec.verb)
            self.app.update_idletasks()
            self.assertEqual(convert.selected_verb, spec.verb)
            self.assertEqual(len(convert.form_fields), len(spec.fields))
            # Each field is either a path field (StringVar), a flag field
            # (BooleanVar), or a RepeatableField (CTkTextbox stored as .text).
            for f in convert.form_fields:
                has_backing = (f.var is not None
                               or getattr(f, "text", None) is not None)
                self.assertTrue(has_backing,
                                f"{spec.verb}/{f.label} not rendered")

    def test_run_dispatches_subprocess_and_captures_exit_code(self):
        # 'validate' on a nonexistent file -> convert.py exits non-zero.
        self.app.show_page("convert")
        self.app.update_idletasks()
        convert = self.app.pages["convert"]
        convert._select_verb("validate")
        self.app.update_idletasks()
        self.assertEqual(len(convert.form_fields), 1)
        convert.form_fields[0].var.set("__definitely-not-a-file__.pkp")

        captured = []
        orig_done = convert._on_run_done

        def hook(rc):
            captured.append(rc)
            orig_done(rc)
        convert._on_run_done = hook

        convert._on_run()
        deadline = time.time() + 20
        while time.time() < deadline and not captured:
            self.app.update()
            time.sleep(0.05)
        self.assertTrue(captured, "runner never completed")
        self.assertNotEqual(captured[0], 0,
                            "validate on a nonexistent file should fail")
        console_text = convert.console.get("1.0", "end")
        self.assertIn("Unparseable", console_text,
                      "console should carry convert.py's own output")


if __name__ == "__main__":
    unittest.main(verbosity=2)
