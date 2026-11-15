#!/usr/bin/env python3
"""Diff the donor and our output at the byte level in the region of
Power's _attributes slot. Our trace says the Primitive at slot_idx 503483
holds value=34 after set_attributes; this script confirms whether the
output bytes actually encode 34 at the corresponding file offset."""
from __future__ import annotations
import os, sys, gzip, struct
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "nrbf_writeback"))

import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402
import nrbf_write as nw             # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def main():
    # Build both donor and mutated versions
    donor_bytes = gzip.decompress(open(DONOR, "rb").read()) if open(DONOR, "rb").read()[:2] == b"" else None
    with open(DONOR, "rb") as fh:
        data = fh.read()
    donor_raw = gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data
    print(f"donor raw bytes: {len(donor_raw)}")

    b = pb.PackageBuilder(DONOR)
    cg = pa.CommandGraph(b)
    cmd_id = cg.commands()["Power"]
    cg.set_attributes(cmd_id, 0x22)
    out_raw = b.build(compress=False)
    print(f"output raw bytes: {len(out_raw)}")

    # The donor and output differ only in the mutated Primitive's bytes.
    # Find the first differing byte.
    n = min(len(donor_raw), len(out_raw))
    first_diff = next((i for i in range(n) if donor_raw[i] != out_raw[i]), -1)
    print(f"first byte diff: {first_diff}")
    if first_diff >= 0:
        print(f"  donor  bytes @{first_diff}: {donor_raw[first_diff:first_diff+16].hex()}")
        print(f"  output bytes @{first_diff}: {out_raw[first_diff:first_diff+16].hex()}")

    # Count byte differences
    total_diff = sum(1 for i in range(n) if donor_raw[i] != out_raw[i])
    print(f"total differing bytes: {total_diff}")

    # Decode nearby - a PT_Int32 primitive is 4 bytes little-endian.
    if first_diff >= 0 and first_diff + 4 <= len(out_raw):
        donor_val = struct.unpack("<i", donor_raw[first_diff:first_diff+4])[0]
        output_val = struct.unpack("<i", out_raw[first_diff:first_diff+4])[0]
        print(f"interpreted as little-endian int32: donor={donor_val} output={output_val}")

if __name__ == "__main__":
    main()
