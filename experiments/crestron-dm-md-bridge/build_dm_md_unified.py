#!/usr/bin/env python3
"""build_dm_md_unified.py - build a SINGLE Extron .pkp for Crestron DM-MD CPU3/CPU4
chassis that does routing (CTP :41795) AND real-time feedback (CIP :41794 as IPID 1).

Replaces the earlier two-package design (dm_md_ctp + dm_md_cip_feedback) with a
single unified driver per Rob's push for a sensible UX and a matrix-shaped donor.

Donor: Extron DTP3 CP 42 (`extr_15_17578`) - a real matrix switcher whose asset
graph already has routing-shaped commands (`MatrixTieCommand` with Input, Output,
Tie Type parameters, `OutputTieStatus`, `InputTieStatus`, `ConnectionStatus`,
`RefreshMatrix`, `InputSignalStatus`, HDCP statuses, Firmware/MAC/Serial).

Pattern:
  1. REPLACE the donor's embedded Python with a from-scratch module that keeps
     the SAME class name and Commands-table shape, so the asset graph's
     references to it remain valid, but internally speaks Crestron CTP + CIP.
  2. ADD 4 new DM-specific feedback commands to the asset graph:
         InputOnlineStatus, OutputOnlineStatus,
         SystemPowerStatus, ChassisProgrammedIP
  3. Rename the model string to make it clear this is DM-MD, not DTP3.
  4. Validate the result via pkp_validate.py.

NO camera cruft: the matrix donor has none to begin with.

Run:  python build_dm_md_unified.py [-o OUTDIR]
"""
from __future__ import annotations

import argparse
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = r"<repo>"
sys.path.insert(0, os.path.join(_ROOT, "tools"))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "nrbf_writeback"))

import pkp_build as pb       # noqa: E402
import pkp_asset as pa       # noqa: E402
import pkp_validate as pv    # noqa: E402


DONOR = os.path.join(_ROOT, "samples", "DTP3 CP 42", "pkp",
                     "extr_15_17578_v1_3_0.pkp")

NEW_SCRIPT = os.path.join(_HERE, "dm_md_driver_replacement.py")


ATTR_UPDATE_ONLY = 35   # from finding 18


def _clone_io_param(g, name):
    """Clone the Input or Output parameter from the donor's MatrixTieCommand.
    These are enum assets on this donor (not decimal), so set_range doesn't
    apply - the Python driver enforces the 1-8 range at runtime instead."""
    donor_cmd = g.commands().get("MatrixTieCommand")
    if donor_cmd is None:
        raise SystemExit("donor missing MatrixTieCommand - unexpected shape")
    for k in g.children(donor_cmd):
        if g.name_of(k) in ("Input", "Output"):
            new_id, _ = g.clone_asset(k, name=name)
            return new_id
    raise SystemExit("could not find an I/O param to clone")


def add_simple_feedback(g, name, script, description):
    cid = g.clone_command("ConnectionStatus", name, script,
                          description=description,
                          attributes=ATTR_UPDATE_ONLY)
    print("   + %-22s %s" % (script, name))


def add_feedback_with_io_param(g, name, script, description, param_name):
    """Feedback command with an Input or Output qualifier (enum-shaped on this donor)."""
    cid = g.clone_command("ConnectionStatus", name, script,
                          description=description,
                          attributes=ATTR_UPDATE_ONLY)
    p = _clone_io_param(g, param_name)
    g.attach(cid, p)
    print("   + %-22s %s  (%s)" % (script, name, param_name))


def build(outdir):
    print("donor: %s" % os.path.basename(DONOR))
    b = pb.PackageBuilder(DONOR)
    print("  round-trip OK, %d bytes NRBF" % len(b.raw))

    # ---- Phase 1: replace the embedded script ----
    slot = b.scripts()[0]
    print("  script slot: %s (%d bytes original)" % (slot.key, len(slot.source)))
    with open(NEW_SCRIPT, "r", encoding="utf-8", newline="") as f:
        new_src = f.read()
    # Match the donor's line endings
    nl = "\r\n" if "\r\n" in slot.source else "\n"
    new_src = new_src.replace("\r\n", "\n").replace("\n", nl)
    b.replace_script(slot.key, new_src)
    print("  replaced with DM-MD driver (%d bytes)" % len(new_src))

    # ---- Phase 2: add DM-specific feedback commands to the asset graph ----
    g = pa.CommandGraph(b)
    print("  donor commands: %d" % len(g.commands()))
    print("  adding DM-specific feedback commands:")
    add_feedback_with_io_param(g, "Input Online Status", "InputOnlineStatus",
                                "Online state of a chassis input slot", "Input")
    add_feedback_with_io_param(g, "Output Online Status", "OutputOnlineStatus",
                                "Online state of a chassis output endpoint", "Output")
    add_simple_feedback(g, "System Power Status", "SystemPowerStatus",
                         "Overall chassis power state")
    add_simple_feedback(g, "Chassis Programmed IP", "ChassisProgrammedIP",
                         "IP address programmed into the chassis SIMPL")
    print("  total commands after rebuild: %d" % len(g.commands()))

    # ---- Phase 3: rename the model string ----
    renamed = 0
    for s_oid, s_val in list(b.find_strings(r"DTP3 CP 42|DTP3.CP42|DTP3-CP")):
        b.replace_string(s_oid, "Crestron DM-MD CPU3 (CTP + CIP)")
        renamed += 1
        print("  renamed string oid %d: %r -> 'Crestron DM-MD CPU3 (CTP + CIP)'" % (s_oid, s_val[:60]))
        if renamed >= 3: break   # don't rename too many

    # ---- Phase 4: write ----
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "dm_md_unified_v0_0_1.pkp")
    b.write(out_path, compress=True)
    print("  wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))

    # ---- Phase 5: validate ----
    print("  validating...")
    verdict = pv.validate(out_path)
    print("  verdict: %r" % (verdict,))
    return out_path, verdict


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--outdir",
                    default=os.path.join(_ROOT, "experiments",
                                         "crestron-dm-md-bridge", "pkp-out"))
    args = ap.parse_args()
    build(args.outdir)
