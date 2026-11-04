#!/usr/bin/env python3
"""Shotgun: set EVERY DriverAttributeEnum Primitive in the stream to a
distinctive value. If Extron still reads 59, the mutation isn't the
problem; something else is."""
from __future__ import annotations
import os, sys, subprocess
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT_DIR = os.path.join(_HERE, "out")
OUT_PKP = os.path.join(OUT_DIR, "all_attrs_mutated.pkp")
LOAD_PS1 = os.path.join(_ROOT, "experiments", "gcp_harness",
                        "Load-Package.ps1")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    b = pb.PackageBuilder(DONOR)

    # Find the DriverAttributeEnum metadata_id
    attr_mids = set()
    for ev in b.trace:
        if ev.get("kind") in ("ClassWithMembersAndTypes", "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            if "DriverAttributeEnum" in ev.get("name", ""):
                attr_mids.add(ev.get("object_id"))

    print(f"DriverAttributeEnum metadata ids: {attr_mids}")

    # Walk the trace and mutate every Primitive following a matching ClassWithId
    muted = 0
    for i, ev in enumerate(b.trace):
        if ev.get("kind") == "ClassWithId" and ev.get("metadata_id") in attr_mids:
            if i+1 < len(b.trace) and b.trace[i+1].get("kind") == "Primitive":
                b.trace[i+1]["value"] = 42
                muted += 1
    # Also mutate the initial Primitive IF the first occurrence was a
    # ClassWithMembersAndTypes (its first instance's value is inline too).
    # Look for ClassWith*AndTypes with DriverAttributeEnum name and mutate the
    # following Primitive.
    for i, ev in enumerate(b.trace):
        if ev.get("kind") in ("ClassWithMembersAndTypes",
                              "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            if "DriverAttributeEnum" in ev.get("name", ""):
                # Members then member types then library id. Then the first
                # instance's value Primitive. But the value for the inline
                # first occurrence comes right after the class defn too.
                # Actually, ClassWithMembersAndTypes is a RECORD TYPE DEFN +
                # the first instance's values combined. The member values
                # (value__ Int32) follow immediately.
                # Find the next Primitive event and mutate it.
                for j in range(i+1, min(i+20, len(b.trace))):
                    if b.trace[j].get("kind") == "Primitive":
                        b.trace[j]["value"] = 42
                        muted += 1
                        break
    print(f"Mutated {muted} Primitives to 42 (0x2A)")

    b.write(OUT_PKP)
    print(f"Wrote {OUT_PKP}")

    # Load-Package
    ps32 = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
    if not os.path.isfile(ps32):
        print("No 32-bit PowerShell")
        return
    rc = subprocess.run([ps32, "-ExecutionPolicy", "Bypass", "-File", LOAD_PS1,
                         "-Commands", "-Path", OUT_PKP]).returncode
    print(f"rc={rc}")

if __name__ == "__main__":
    main()
