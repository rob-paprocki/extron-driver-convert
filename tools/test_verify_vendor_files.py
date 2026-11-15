#!/usr/bin/env python3
"""
test_verify_vendor_files.py - tests for verify_vendor_files.py and for the
policy the manifest records: the repository publishes no vendor material.

  [1] the committed manifest is well formed: repo-relative paths, 64-hex
      digests, no duplicates
  [2] verify() tells present-and-matching from missing from different
  [3] the CLI's exit status says whether everything matched
  [4] every listed file is untracked and ignored, so a vendor file added by
      mistake fails here (needs git; skipped without it)

Run: python3 tools/test_verify_vendor_files.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import verify_vendor_files as vvf  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def test_manifest_is_well_formed():
    print("\n[1] the committed manifest is well formed")
    entries = vvf.load_manifest(vvf.DEFAULT_MANIFEST)
    paths = [e[2] for e in entries]
    check("it lists the vendor files", len(entries) > 1000, "%d" % len(entries))
    check("paths are unique", len(paths) == len(set(paths)))
    check("paths are repo-relative with forward slashes",
          all(not p.startswith("/") and ":" not in p and "\\" not in p and ".." not in p.split("/")
              for p in paths))
    check("digests are 64 lowercase hex characters",
          all(len(e[0]) == 64 and all(c in "0123456789abcdef" for c in e[0]) for e in entries))
    check("sizes are non-negative integers", all(e[1] >= 0 for e in entries))


def test_verify_classifies_each_file():
    print("\n[2] verify() tells matching, missing and different apart")
    tmp = tempfile.mkdtemp(prefix="vvf_")
    try:
        os.makedirs(os.path.join(tmp, "a", "b"))
        good, bad = b"vendor bytes", b"changed bytes"
        with open(os.path.join(tmp, "a", "b", "good.pkp"), "wb") as f:
            f.write(good)
        with open(os.path.join(tmp, "a", "bad.pkp"), "wb") as f:
            f.write(bad)
        entries = [(hashlib.sha256(good).hexdigest(), len(good), "a/b/good.pkp"),
                   (hashlib.sha256(good).hexdigest(), len(bad), "a/bad.pkp"),
                   (hashlib.sha256(good).hexdigest(), len(good), "a/missing.pkp")]
        r = vvf.verify(tmp, entries)
        check("a matching file is ok", r["ok"] == ["a/b/good.pkp"], str(r))
        check("a file with other content is different", r["different"] == ["a/bad.pkp"], str(r))
        check("an absent file is missing", r["missing"] == ["a/missing.pkp"], str(r))

        manifest = os.path.join(tmp, "m.tsv")
        with open(manifest, "w", encoding="utf-8") as f:
            f.write("# comment\n%s\t%d\ta/b/good.pkp\n" % entries[0][:2])
        check("[3] the CLI exits 0 when everything matches",
              vvf.main(["--manifest", manifest, "--root", tmp]) == 0)
        with open(manifest, "a", encoding="utf-8") as f:
            f.write("%s\t%d\ta/missing.pkp\n" % entries[2][:2])
        check("[3] and 1 when anything is missing",
              vvf.main(["--manifest", manifest, "--root", tmp]) == 1)
        check("[3] --only narrows the check to a prefix",
              vvf.main(["--manifest", manifest, "--root", tmp, "--only", "a/b/"]) == 0)
        with open(manifest, "a", encoding="utf-8") as f:
            f.write("not a manifest line\n")
        try:
            vvf.load_manifest(manifest)
            check("[3] a malformed line is refused, not skipped", False)
        except ValueError:
            check("[3] a malformed line is refused, not skipped", True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _git(*args, stdin=None):
    return subprocess.run(["git", "-C", _ROOT] + list(args), input=stdin,
                          capture_output=True)


def test_listed_files_are_not_published():
    print("\n[4] every listed file is untracked and ignored")
    try:
        inside = _git("rev-parse", "--is-inside-work-tree").stdout.strip() == b"true"
    except OSError:
        inside = False
    if not inside:
        print("  skip: not a git checkout, or git not available")
        return
    paths = [e[2] for e in vvf.load_manifest(vvf.DEFAULT_MANIFEST)]
    tracked = set(_git("ls-files", "-z").stdout.decode("utf-8").split("\0"))
    published = sorted(set(paths) & tracked)
    check("no listed file is tracked", not published,
          "%d tracked, e.g. %s" % (len(published), published[:3]))
    out = _git("check-ignore", "--no-index", "--stdin", "-z",
               stdin="\0".join(paths).encode("utf-8")).stdout.decode("utf-8")
    ignored = set(x for x in out.split("\0") if x)
    unignored = sorted(set(paths) - ignored)
    check("every listed file is ignored, so it cannot be added by accident", not unignored,
          "%d not ignored, e.g. %s" % (len(unignored), unignored[:3]))


def main():
    print("test_verify_vendor_files.py - the vendor manifest and its checker")
    for fn in (test_manifest_is_well_formed,
               test_verify_classifies_each_file,
               test_listed_files_are_not_published):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
