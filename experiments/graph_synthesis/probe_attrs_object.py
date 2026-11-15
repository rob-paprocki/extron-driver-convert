#!/usr/bin/env python3
"""Dump what objects[-5657] looks like in both donor and mutated versions."""
from __future__ import annotations
import os, sys, gzip
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402
import pkp_dump as pd               # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT = os.path.join(_HERE, "out", "authored_command.pkp")

def main():
    print("=== DONOR ===")
    parser = pd.PkpParser(pd.load_bytes(DONOR))
    parser.parse()
    print(f"objects[-5657] = {parser.objects.get(-5657)!r}")
    print(f"objects[2498] members = {parser.objects[2498].get('members')!r}")

    print()
    print("=== OUTPUT (after mutation) ===")
    if not os.path.isfile(OUT):
        print(f"output {OUT} missing; run build_authored_command.py first")
        return
    parser2 = pd.PkpParser(pd.load_bytes(OUT))
    parser2.parse()
    print(f"objects[-5657] = {parser2.objects.get(-5657)!r}")
    print(f"objects[2498] members = {parser2.objects[2498].get('members')!r}")

if __name__ == "__main__":
    main()
