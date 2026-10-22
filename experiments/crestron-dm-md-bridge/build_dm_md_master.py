#!/usr/bin/env python3
"""build_dm_md_master.py - build an Extron .pkp for Crestron DM-MD CPU3 chassis
that runs the full MASTER-OF-RECORD design proven by finding 24.

Everything over ONE TCP socket to chassis:41794:
  - Chassis dials OUT to the master (us); we accept the TCP server-side
  - Server-side CGway handshake per evidence/19
  - Nested-container Cresnet payloads for all slot-addressed operations

Supported operations (per output slot 1..8):
  - MatrixTieCommand(Input, Output, Tie Type)   - routing
  - OutputTieStatus / InputTieStatus            - routing feedback
  - ComPortSendString(Output, Value)            - RMC ComPort TX (new)
  - ComPortReceivedString(Output, Value)        - RMC ComPort RX feedback (new)
  - IRPulse(Output, Code)                       - RMC IR port (new)
  - RelayClose(Output), RelayOpen(Output)       - RMC Relay (new)
  - RelayStatus(Output, Value)                  - Relay feedback (new)
  - HDCPOutputStatus / HDCPInputStatus          - HDCP state (keep from donor)
  - OutputResolution                            - resolution feedback
  - InputSignalStatus                           - input signal present
  - InputOnlineStatus / OutputOnlineStatus      - endpoint online state
  - SystemPowerStatus / ChassisProgrammedIP     - chassis-level
  - ConnectionStatus                            - our session connected?
  - Firmware / MACAddress / SerialNumber        - device metadata

Build strategy:
  1. Load DTP3 CP 42 donor (shape-right matrix with full routing + HDCP)
  2. REPLACE embedded Python with dm_md_master_driver.py (ControlScript port
     of cip_master_server_v2.py)
  3. ADD new DM-master-specific commands via clone-and-rename:
       - clone MatrixIONameString for string-shaped commands (ComPort I/O)
       - clone MatrixTieCommand for Output+Value shaped (IR, Relay)
       - clone ConnectionStatus for simple status feedback (Relay state, etc.)
  4. Rename model string to "Crestron DM-MD CPU3 (master-of-record)"
  5. Validate via pkp_validate.py

Run:  python build_dm_md_master.py [-o OUTDIR]
"""
from __future__ import annotations

import argparse
import os
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

NEW_SCRIPT = os.path.join(_ROOT, "experiments", "crestron-dm-md-bridge",
                          "dm_md_master_driver.py")

ATTR_UPDATE_ONLY = 35
ATTR_SET_AND_UPDATE = 51


def _get_child(g, cmd_id, child_name):
    for k in g.children(cmd_id):
        if g.name_of(k) == child_name:
            return k
    return None


def _clone_param(g, donor_cmd_name, child_name, new_name=None):
    donor_cmd = g.commands().get(donor_cmd_name)
    if donor_cmd is None:
        raise SystemExit("donor missing %s" % donor_cmd_name)
    child = _get_child(g, donor_cmd, child_name)
    if child is None:
        raise SystemExit("%s missing child %s" % (donor_cmd_name, child_name))
    new_id, _ = g.clone_asset(child, name=new_name or child_name)
    return new_id


def add_cmd(g, name, script_name, description,
            donor_script_name="ConnectionStatus",
            attributes=ATTR_UPDATE_ONLY,
            params=()):
    cid = g.clone_command(donor_script_name, name, script_name,
                          description=description, attributes=attributes)
    for donor_cmd, child_name, new_name in params:
        pid = _clone_param(g, donor_cmd, child_name, new_name)
        g.attach(cid, pid)
    marker = "[FB]" if attributes == ATTR_UPDATE_ONLY else "[SET+FB]"
    pnames = [p[2] or p[1] for p in params]
    print("   + %-28s %-8s %s  params=%s" % (script_name, marker, name, pnames))


def build(outdir):
    print("donor: %s" % os.path.basename(DONOR))
    b = pb.PackageBuilder(DONOR)
    print("  round-trip OK, %d bytes NRBF" % len(b.raw))

    slot = b.scripts()[0]
    print("  script slot: %s (%d bytes original)" % (slot.key, len(slot.source)))
    with open(NEW_SCRIPT, "r", encoding="utf-8", newline="") as f:
        new_src = f.read()
    nl = "\r\n" if "\r\n" in slot.source else "\n"
    new_src = new_src.replace("\r\n", "\n").replace("\n", nl)
    b.replace_script(slot.key, new_src)
    print("  replaced with master-of-record driver (%d bytes)" % len(new_src))

    g = pa.CommandGraph(b)
    print("  donor commands: %d" % len(g.commands()))
    print("  adding master-of-record command surface:")

    # ComPort passthrough
    add_cmd(g, "ComPort Send String", "ComPortSendString",
            "Send ASCII to an RMC endpoint's ComPort TX",
            donor_script_name="MatrixIONameString",
            attributes=ATTR_SET_AND_UPDATE,
            params=[("MatrixTieCommand", "Output", "Output")])
    add_cmd(g, "ComPort Received String", "ComPortReceivedString",
            "ASCII received from an RMC endpoint's ComPort RX",
            donor_script_name="MatrixIONameString",
            attributes=ATTR_UPDATE_ONLY,
            params=[("MatrixTieCommand", "Output", "Output")])

    # IR port
    add_cmd(g, "IR Pulse", "IRPulse",
            "Trigger IR pulse on an RMC endpoint's IR port",
            donor_script_name="MatrixTieCommand",
            attributes=ATTR_SET_AND_UPDATE,
            params=[("MatrixTieCommand", "Output", "Output"),
                    ("MatrixTieCommand", "Tie Type", "IR Code")])

    # Relay
    add_cmd(g, "Relay Close", "RelayClose",
            "Close relay on an RMC endpoint",
            donor_script_name="ConnectionStatus",
            attributes=ATTR_SET_AND_UPDATE,
            params=[("MatrixTieCommand", "Output", "Output")])
    add_cmd(g, "Relay Open", "RelayOpen",
            "Open relay on an RMC endpoint",
            donor_script_name="ConnectionStatus",
            attributes=ATTR_SET_AND_UPDATE,
            params=[("MatrixTieCommand", "Output", "Output")])
    add_cmd(g, "Relay Status", "RelayStatus",
            "Current state of an RMC endpoint's relay",
            donor_script_name="ConnectionStatus",
            attributes=ATTR_UPDATE_ONLY,
            params=[("MatrixTieCommand", "Output", "Output")])

    # Endpoint-level feedback
    add_cmd(g, "Input Online Status", "InputOnlineStatus",
            "Online state of a chassis input slot (0/1)",
            params=[("MatrixTieCommand", "Input", "Input")])
    add_cmd(g, "Output Online Status", "OutputOnlineStatus",
            "Online state of a chassis output endpoint (0/1)",
            params=[("MatrixTieCommand", "Output", "Output")])

    # Chassis-level feedback
    add_cmd(g, "System Power Status", "SystemPowerStatus",
            "Overall chassis power state (0/1)")
    add_cmd(g, "Chassis Programmed IP", "ChassisProgrammedIP",
            "IP address of the chassis programmed on us")

    print("  total commands after rebuild: %d" % len(g.commands()))

    renamed = 0
    for s_oid, s_val in list(b.find_strings(r"DTP3 CP 42|DTP3.CP42|DTP3-CP")):
        b.replace_string(s_oid, "Crestron DM-MD CPU3 (master-of-record)")
        renamed += 1
        print("  renamed string oid %d" % s_oid)
        if renamed >= 3:
            break

    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "dm_md_master_v0_0_1.pkp")
    b.write(out_path, compress=True)
    print("  wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))
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
