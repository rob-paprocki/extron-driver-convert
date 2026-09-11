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

A snapshot of both, taken 2026-09-11 from the Windows box, is committed under
corpus/extron-driver3 and corpus/extron-gs-modules (~1.3 GB, vendor material,
private repo). The defaults below prefer that snapshot so the pair set
reproduces on any machine; pass --drivers/--modules to point at a live GC
install instead. The emitted JSON is what the rest of the analysis reads.

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

_CORPUS = os.path.join(_ROOT, "corpus")
_REPO_D = os.path.join(_CORPUS, "extron-driver3")
_REPO_G = os.path.join(_CORPUS, "extron-gs-modules")
_INSTALL_D = r"C:\Users\Public\Documents\extron\Driver3"
_INSTALL_G = r"C:\Users\Public\Documents\extron\GS_Modules"

# Prefer the committed snapshot so results reproduce anywhere; fall back to a
# live Global Configurator install on the Windows box.
DEFAULT_D = _REPO_D if os.path.isdir(_REPO_D) else _INSTALL_D
DEFAULT_G = _REPO_G if os.path.isdir(_REPO_G) else _INSTALL_G

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


def match_models(names, vendor, modules, mod_vendor):
    """(vendor-consistent matches, foreign-only matches) for one package.

    For each model name: the FIRST module, in `modules` order, whose
    normalised name contains it AND whose vendor agrees. Only when no module of
    the package's own vendor contains the name is the first foreign module
    recorded - as a rejected ("loose") match.

    An earlier version broke out of the loop on the first substring hit of
    ANY vendor, so a foreign module that happened to sort first hid the right
    one. That made the pair set depend on directory order: rebuilding from
    corpus/ on 2026-09-11 gave 312, 311 or 310 packages depending on how the
    modules were ordered, and NO order reproduced the committed 314. This rule
    reproduces out/pairs_strict.json exactly (314 packages, 352 pairs) - which
    means that is the rule the committed result was actually produced with.
    test_build_index.py pins it.
    """
    tight, loose = [], []
    for n in sorted(names):
        nn = norm(n)
        if len(nn) < 4:                          # too short to join safely
            continue
        foreign = None
        for mf, mn in modules.items():
            if nn not in mn:
                continue
            if mod_vendor[mf] == vendor:
                tight.append({"model": n, "module": mf})
                break
            if foreign is None:
                foreign = mf
        else:
            if foreign is not None:
                loose.append({"model": n, "module": foreign})
    return tight, loose


def latest_gs_dir(root):
    """GS module shipments are dated directories; take the newest."""
    if not os.path.isdir(root):
        return None
    subs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    return os.path.join(root, sorted(subs)[-1]) if subs else root


def resolve_gs(root):
    """The modules folder itself, or the newest dated shipment inside it.

    Replaces a check on the folder being *named* GS_Modules, which the corpus
    snapshot (corpus/extron-gs-modules) is not.
    """
    if not root or not os.path.isdir(root):
        return None
    if any(f.lower().endswith(".py") for f in os.listdir(root)):
        return root
    return latest_gs_dir(root)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drivers", default=DEFAULT_D)
    ap.add_argument("--modules", default=DEFAULT_G)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()

    gs = resolve_gs(args.modules)
    if not (os.path.isdir(args.drivers) and gs and os.path.isdir(gs)):
        raise SystemExit("driver library or GS modules not found; pass --drivers/--modules")
    os.makedirs(args.outdir, exist_ok=True)

    # sorted(): which packages pair does not depend on order (see
    # match_models), but WHICH same-vendor module is chosen when several
    # contain the model name does. Sorting makes that choice deterministic,
    # and it is the order that reproduces out/pairs_strict.json exactly.
    modules = {f: norm(f[:-3]) for f in sorted(os.listdir(gs))
               if f.lower().endswith(".py")}
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
        tight, loose = match_models(names, vendor, modules, mod_vendor)
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
