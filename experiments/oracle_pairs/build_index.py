#!/usr/bin/env python3
"""
build_index.py - find every .pkp <-> ControlScript oracle pair in a local
Global Configurator install.

Why
---
STATUS.md's translator scorecard has always rested on 4 pairs, all Extron-
authored for Extron hardware. That is enough to show the translator works on
its samples and not enough to show it works. This builds the pair set from
Extron's own shipping library instead.

Two directories, both created by Extron installers:

    C:\\Users\\Public\\Documents\\extron\\Driver3            .pkp packages
    C:\\Users\\Public\\Documents\\extron\\GS_Modules\\<date>  ControlScript .py

Neither is in this repo (vendor material, and ~2 GB). Run this on a machine
with GC installed; the emitted JSON is what the rest of the analysis reads.

The join
--------
There is no shared identifier. A package is named `vendor_class_id_version.pkp`
and a module `vendor_type_Model_vX_Y_Z_W.py`, and even the vendor codes differ
between the two systems (`1bynd` vs `onebynd`). What does join them is the
model name: `DriverModelAsset`'s `AssetBase+_name` inside the package, against
the model portion of the module filename.

Two traps, both hit while writing this:

  1. The member key is `AssetBase+_name`, not `_name` - reading the latter
     returns None for every package and yields a confident zero.
  2. Substring matching alone is wrong. `absn` model "C110" matches Dynascan's
     `DMBC110` module; `acer` "K750" matches a Digital Projection module whose
     normalised filename happens to contain `k750`. Requiring the vendor to
     agree rejected 33 such pairs out of 347.

So a pair is recorded only when the normalised model name appears in the
normalised module filename AND the vendor prefixes agree.
"""

import argparse
import collections
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_dump as pd            # noqa: E402

DEFAULT_D = r"C:\Users\Public\Documents\extron\Driver3"
DEFAULT_G = r"C:\Users\Public\Documents\extron\GS_Modules"

# pkp vendor prefix -> GS module vendor prefix, where the two libraries differ.
VENDOR_ALIAS = {"1bynd": "onebynd"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def model_names(parser):
    """Every DriverModelAsset._name in a parsed package.

    The concrete class is `...DriverModelAsset`; the collection wrappers carry
    `IDriverModelAsset` in a generic parameter and must not be matched, which
    is why this tests endswith rather than a substring.
    """
    out = set()
    for v in parser.objects.values():
        if not (isinstance(v, dict)
                and (v.get("class") or "").endswith("DriverModelAsset")):
            continue
        for key, raw in (v.get("members") or {}).items():
            # `AssetBase+_name`, not `_name`; skip `_defaultName`.
            if not key.endswith("_name") or key.endswith("_defaultName"):
                continue
            if isinstance(raw, dict) and "$ref" in raw:
                raw = parser.objects.get(raw["$ref"])
            if isinstance(raw, str) and raw.strip():
                out.add(raw.strip())
    return out


def latest_gs_dir(root):
    """GS module shipments are dated directories; take the newest."""
    if not os.path.isdir(root):
        return None
    subs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    return os.path.join(root, sorted(subs)[-1]) if subs else root


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drivers", default=DEFAULT_D)
    ap.add_argument("--modules", default=DEFAULT_G)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()

    gs = latest_gs_dir(args.modules) if os.path.basename(args.modules) == "GS_Modules" \
        else args.modules
    if not (os.path.isdir(args.drivers) and gs and os.path.isdir(gs)):
        raise SystemExit("driver library or GS modules not found; pass --drivers/--modules")
    os.makedirs(args.outdir, exist_ok=True)

    modules = {f: norm(f[:-3]) for f in os.listdir(gs) if f.lower().endswith(".py")}
    mod_vendor = {f: f.lstrip("_").split("_")[0].lower() for f in modules}
    pkps = sorted(f for f in os.listdir(args.drivers) if f.lower().endswith(".pkp"))
    print("driver library: %d packages" % len(pkps))
    print("GS modules:     %d  (%s)" % (len(modules), gs))

    rows, strict, errors = [], [], []
    rejected = 0
    for i, f in enumerate(pkps, 1):
        if i % 200 == 0:
            print("  ...%d/%d" % (i, len(pkps)), flush=True)
        try:
            parser = pd.PkpParser(pd.load_bytes(os.path.join(args.drivers, f)))
            parser.parse()
            names = model_names(parser)
        except Exception as e:                      # noqa: BLE001
            errors.append({"pkp": f, "error": repr(e)[:160]})
            continue

        vendor = f.split("_")[0].lower()
        vendor = VENDOR_ALIAS.get(vendor, vendor)
        loose, tight = [], []
        for n in sorted(names):
            nn = norm(n)
            if len(nn) < 4:                          # too short to join safely
                continue
            for mf, mn in modules.items():
                if nn not in mn:
                    continue
                (tight if mod_vendor[mf] == vendor else loose).append(
                    {"model": n, "module": mf})
                break
        rows.append({"pkp": f, "models": sorted(names),
                     "vendor_consistent": tight, "vendor_mismatch": loose})
        if tight:
            strict.append({"pkp": f, "matches": tight})
        elif loose:
            rejected += 1

    json.dump({"packages": rows, "errors": errors},
              open(os.path.join(args.outdir, "pair_index.json"), "w"), indent=1)
    json.dump(strict, open(os.path.join(args.outdir, "pairs_strict.json"), "w"), indent=1)

    pairs = sum(len(r["matches"]) for r in strict)
    print("\nparsed %d packages, %d parse errors" % (len(rows), len(errors)))
    print("model entries:                      %d" % sum(len(r["models"]) for r in rows))
    print("packages with a vendor-consistent match: %d" % len(strict))
    print("distinct pairs:                     %d" % pairs)
    print("packages rejected (vendor mismatch only): %d" % rejected)
    print("wrote %s" % args.outdir)


if __name__ == "__main__":
    main()
