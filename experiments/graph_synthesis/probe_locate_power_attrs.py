#!/usr/bin/env python3
"""Bisect: mutate half of the DriverAttributeEnum Primitives to 42 and see
which half contains Power's effective _attributes. Repeat until the one
Primitive Extron reads for Power is identified."""
from __future__ import annotations
import os, sys, subprocess, re
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT_DIR = os.path.join(_HERE, "out")
LOAD_PS1 = os.path.join(_ROOT, "experiments", "gcp_harness",
                        "Load-Package.ps1")

MAGIC = 42

def attr_primitive_indices(trace, attr_mids):
    """Return [(trace_idx_of_classwithid, trace_idx_of_primitive), ...]"""
    out = []
    # ClassWithId chain
    for i, ev in enumerate(trace):
        if ev.get("kind") == "ClassWithId" and ev.get("metadata_id") in attr_mids:
            if i+1 < len(trace) and trace[i+1].get("kind") == "Primitive":
                out.append((i, i+1))
    # First-occurrence class defn (before any ClassWithId can reference it)
    for i, ev in enumerate(trace):
        if ev.get("kind") in ("ClassWithMembersAndTypes", "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            if "DriverAttributeEnum" in ev.get("name", ""):
                for j in range(i+1, min(i+20, len(trace))):
                    if trace[j].get("kind") == "Primitive":
                        out.append((i, j))
                        break
    return sorted(set(out), key=lambda t: t[1])

def find_power_attrs(trace, primitives, out_path):
    b = pb.PackageBuilder(DONOR)
    # Set only the indices in `primitives` to MAGIC in a fresh builder.
    attr_mids = set()
    for ev in b.trace:
        if ev.get("kind") in ("ClassWithMembersAndTypes", "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            if "DriverAttributeEnum" in ev.get("name", ""):
                attr_mids.add(ev.get("object_id"))
    all_primitives = attr_primitive_indices(b.trace, attr_mids)
    target_set = set(primitives)
    muted = 0
    for cw_idx, pr_idx in all_primitives:
        if pr_idx in target_set:
            b.trace[pr_idx]["value"] = MAGIC
            muted += 1
    b.write(out_path)
    return muted

def load_power_attrs(out_path):
    ps32 = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
    r = subprocess.run([ps32, "-ExecutionPolicy", "Bypass", "-File", LOAD_PS1,
                        "-Commands", "-Path", out_path], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if re.match(r"\s+Power\b", line):
            m = re.search(r"attrs=(\d+)", line)
            if m: return int(m.group(1))
    return None

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    b = pb.PackageBuilder(DONOR)
    attr_mids = set()
    for ev in b.trace:
        if ev.get("kind") in ("ClassWithMembersAndTypes", "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            if "DriverAttributeEnum" in ev.get("name", ""):
                attr_mids.add(ev.get("object_id"))

    all_prims = [pr for (cw, pr) in attr_primitive_indices(b.trace, attr_mids)]
    print(f"Total DriverAttributeEnum Primitives: {len(all_prims)}")

    # Binary search
    candidates = all_prims[:]
    iteration = 0
    while len(candidates) > 1:
        iteration += 1
        half = len(candidates) // 2
        left = candidates[:half]
        right = candidates[half:]
        out_path = os.path.join(OUT_DIR, f"bisect_{iteration}_left.pkp")
        muted = find_power_attrs(b.trace, left, out_path)
        attr = load_power_attrs(out_path)
        print(f"  iter {iteration}: muted {muted} left Primitives -> Power attrs={attr}")
        if attr == MAGIC:
            candidates = left
        else:
            candidates = right
    print(f"Power's effective _attributes is at trace idx {candidates[0] if candidates else None}")
    if candidates:
        pr = candidates[0]
        # Show context
        for j in range(max(0, pr-2), min(len(b.trace), pr+3)):
            print(f"  trace[{j}] = {b.trace[j]}")

if __name__ == "__main__":
    main()
