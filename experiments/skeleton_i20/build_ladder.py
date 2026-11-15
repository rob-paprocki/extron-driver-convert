#!/usr/bin/env python3
"""
build_ladder.py - isolate WHY a script-substituted package is rejected.

The hardware result (2026-09-08)
--------------------------------
    20020  unmodified copy          loads
    20021  model strings renamed     loads
    20022  script substituted        "Invalid Driver ... Error Code: 80085"
    20023  renamed + script          same

So renaming is fine and substitution is not. The likely cause is now visible
in the object graph: a package declares its command surface as **assets**, not
in the script. The donor carries 15 `DriverCommandAsset` objects (Auto
Exposure, Auto Focus, Backlight, Connection Status, Focus, Gain, Iris, Pan
Tilt, Power, Preset, Shutter, User Defined Command, User Defined String, White
Balance, Zoom) plus 56 EnumStateAsset, 43 DecimalParamAsset and 14
EnumParamAsset hanging off them.

build_i20.py's E3 edit added ten commands to the script's `self.Commands`
dict and zero assets to the graph. GC drives its UI and its validation from
the asset tree, so the package promises commands it never declares.

That is a hypothesis, not a measurement. This ladder tests it with three
packages that differ by exactly one thing each:

    L1  header comment only          - is ANY script edit rejected?
    L2  + the E2 zoom fix            - can behaviour change?
    L3  + i20 methods, Commands dict UNTOUCHED
                                     - can code be added without declaring
                                       commands?

Reading the result:

  L1 fails            the script is hashed or signed; substitution is dead
                      in this form and the whole approach needs rethinking.
  L1 ok, L2 fails     content is validated somehow beyond a byte compare.
  L2 ok, L3 fails     added methods are themselves the problem.
  L3 ok               the script side is unconstrained and the ONLY remaining
                      work is synthesising DriverCommandAsset subtrees -
                      STATUS.md open item 4, with a concrete shape.

L3 is the informative one. If it loads, the i20 commands are already on the
processor as dead code, reachable the moment the assets exist.

Usage: python3 experiments/skeleton_i20/build_ladder.py [-o OUTDIR]
"""

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import build_i20                  # noqa: E402
import pkp_build as pb            # noqa: E402


def l1(src):
    """Header comment only. No executable change whatsoever."""
    return build_i20.patch_header(src)


def l2(src):
    """L1 plus the zoom-speed fix - one changed expression."""
    return build_i20.patch_zoom(build_i20.patch_header(src))


def l3(src):
    """L2 plus every i20 method, but the Commands dict left alone.

    The methods are unreachable: ControlScript/GC dispatch goes through the
    Commands table, and GC's own UI comes from the asset tree. This is
    deliberately dead code - the question is only whether the package still
    loads with it present.
    """
    return build_i20.patch_methods(build_i20.patch_zoom(
        build_i20.patch_header(src)))


LADDER = [
    ("1bynd_19_20030_v1_0_0.pkp", l1, "L1 header comment only"),
    ("1bynd_19_20031_v1_0_0.pkp", l2, "L2 + zoom fix"),
    ("1bynd_19_20032_v1_0_0.pkp", l3, "L3 + i20 methods, Commands dict untouched"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    probe = pb.PackageBuilder(build_i20.DONOR)
    slot = probe.scripts()[0]
    baseline = len(slot.source.encode())
    print("donor: %s (embedded script %d bytes)"
          % (os.path.basename(build_i20.DONOR), baseline))

    for filename, fn, label in LADDER:
        b = pb.PackageBuilder(build_i20.DONOR)
        s = b.scripts()[0]
        derived = fn(s.source)
        # The Commands table must be untouched in every rung - that is the
        # controlled variable. Assert it rather than trusting the patch set.
        import re
        def table(text):
            m = re.search(r"self\.Commands = \{(.*?)\n        \}", text, re.S)
            return sorted(re.findall(r"^\s+'([A-Za-z]+)':", m.group(1), re.M)) if m else None
        if table(derived) != table(s.source):
            raise SystemExit("%s changed the Commands table; the ladder is only "
                             "meaningful if it does not" % label)
        b.replace_script(s.key, derived)
        path = os.path.join(args.outdir, filename)
        b.write(path)
        print("  %-30s %8d bytes  script %+d  %s"
              % (filename, os.path.getsize(path),
                 len(derived.encode()) - baseline, label))

    print("\ncommands declared in the script (unchanged in all three): %d"
          % len(_table_names(slot.source)))
    print("DriverCommandAsset objects in the package: %d"
          % sum(1 for v in probe.objects.values()
                if isinstance(v, dict) and "DriverCommandAsset" in (v.get("class") or "")))
    return 0


def _table_names(text):
    import re
    m = re.search(r"self\.Commands = \{(.*?)\n        \}", text, re.S)
    return re.findall(r"^\s+'([A-Za-z]+)':", m.group(1), re.M) if m else []


if __name__ == "__main__":
    sys.exit(main())
