#!/usr/bin/env python3
"""Decode the NRBF records around byte offset 596200 in the donor."""
from __future__ import annotations
import os, sys, gzip, struct
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def main():
    with open(DONOR, "rb") as fh:
        data = fh.read()
    raw = gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data

    # Starting ~40 bytes before the diff, decode byte by byte
    start = 596170
    end = 596230
    print(f"bytes {start}..{end}:")
    for i in range(start, end):
        print(f"  {i:7d}  0x{raw[i]:02x}  ({raw[i]})")
    print()
    print("interpretations around 596201:")
    # Try interpreting various starts as int32 LE
    for off in [596190, 596192, 596193, 596195, 596197, 596201, 596205]:
        if off + 4 <= len(raw):
            v = struct.unpack("<i", raw[off:off+4])[0]
            print(f"  int32 @{off} = {v}")

if __name__ == "__main__":
    main()
