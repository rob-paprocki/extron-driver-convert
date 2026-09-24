"""
vendor_inputs.py - the vendor material tests read but the repository does not
publish, and how a test says it is missing.

Extron and Crestron packages and modules, harvested vendor documentation and
Global Configurator's catalogue data are untracked (2026-09-24);
vendor-files.manifest.tsv lists every file with its SHA-256. A test that needs
one of them and does not find it is SKIPPED with the path it wanted - never
passed, never silently dropped. The runners print skips separately and put
them in their summary line, so a clone without the material shows exactly how
much went unchecked.

  require(*paths)      raise VendorInputMissing unless every path exists
  vendor_missing(exc)  the missing vendor path behind an exception, or None
  skip_suite(*paths)   for a suite that cannot even import without them:
                       print why and exit 0 when any path is missing

Standard library only.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(_ROOT, "vendor-files.manifest.tsv")

_listed = None


class VendorInputMissing(Exception):
    """A test's vendor input is not on disk: skip the test, do not fail it."""


def _rel(path):
    try:
        rel = os.path.relpath(os.path.abspath(path), _ROOT)
    except ValueError:                                # another drive on Windows
        return None
    return rel.replace(os.sep, "/")


def _manifest_paths():
    global _listed
    if _listed is None:
        _listed = set()
        if os.path.isfile(MANIFEST):
            with open(MANIFEST, encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) == 3 and not line.startswith("#"):
                        _listed.add(parts[2])
    return _listed


def is_vendor_path(path):
    """True if the manifest lists this file, or it is a folder holding listed files."""
    rel = _rel(path)
    if rel is None:
        return False
    listed = _manifest_paths()
    return rel in listed or any(p.startswith(rel.rstrip("/") + "/") for p in listed)


def require(*paths):
    """Raise VendorInputMissing naming every path that is not on disk."""
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise VendorInputMissing("vendor input not present: %s (see vendor-files.manifest.tsv)"
                                 % ", ".join(_rel(p) or p for p in missing))


def vendor_missing(exc):
    """The reason a test should be skipped rather than failed, or None: a
    VendorInputMissing, or a FileNotFoundError on a path the manifest lists."""
    if isinstance(exc, VendorInputMissing):
        return str(exc)
    if isinstance(exc, FileNotFoundError) and exc.filename and is_vendor_path(exc.filename):
        return "vendor input not present: %s (see vendor-files.manifest.tsv)" % _rel(exc.filename)
    return None


def skip_suite(*paths):
    """For a suite that builds from vendor input at import time: if any path is
    missing, say so and exit 0 - the whole suite is skipped, visibly."""
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print("SKIPPED SUITE %s: vendor input not present: %s (see vendor-files.manifest.tsv)"
              % (os.path.basename(sys.argv[0]), ", ".join(_rel(p) or p for p in missing)))
        print("0 passed, 0 failed, all skipped")
        sys.exit(0)
