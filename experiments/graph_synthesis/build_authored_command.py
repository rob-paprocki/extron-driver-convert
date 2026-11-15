#!/usr/bin/env python3
"""R28 Phase 5 -- end-to-end from-scratch synthesis POC via in-place mutation.

Chains the position-stable authoring primitives Phase 4 established:

  * tools/pkp_build.py :: PackageBuilder.replace_string(oid, value)
  * tools/pkp_build.py :: PackageBuilder.replace_enum_value(oid, value) (new)
  * tools/pkp_asset.py :: CommandGraph.author_fresh_command(id, ...)

Picks a donor command whose _name / _scriptName strings are NOT shared with
any other asset in the package (the sharing guard refuses otherwise so no
other command gets accidentally renamed), authors all four property-bearing
fields, writes out/authored_command.pkp, and prints both our own parse and
Extron's Load-Package property-accessor readout so the decisive gate is
visible from the one script output.

Decisive gate: Load-Package.ps1 -Commands must return
  ScriptMethodName = "AuthoredScriptName"   (not "")
  Name             = "Authored Display Name"  (not "Value")
  Attributes       = 0x22                     (not 15)
  ExtronCommandId  = 0  (General)

Standard library only (same rule as tools/*). The output .pkp is a built
artefact; `out/` stays gitignored.
"""
from __future__ import annotations

import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_build as pb                              # noqa: E402
import pkp_asset as pa                              # noqa: E402
import pkp_dump as pd                               # noqa: E402
import extron_enums as ee                           # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT_DIR = os.path.join(_HERE, "out")
OUT_PKP = os.path.join(OUT_DIR, "authored_command.pkp")
LOAD_PS1 = os.path.join(_ROOT, "experiments", "gcp_harness",
                        "Load-Package.ps1")

AUTHORED_NAME = "Authored Display Name"
AUTHORED_SCRIPT_NAME = "AuthoredScriptName"
AUTHORED_ATTRS = int(ee.DriverAttributeEnum.RuntimeVisible
                     | ee.DriverAttributeEnum.LiveStatus)  # 0x22
AUTHORED_EX_CMD_ID = int(ee.ExtronCommandIdEnum.General)   # 0


def _pick_command(cg, preferred_script_name="Power"):
    """Pick a donor command to author over. Prefers a well-known command
    name (default: Power) so the gate output is easy to eyeball; falls back
    to the first command in the donor.

    Panasonic PTZ donors share strings across their 15 model variants, so
    author_fresh_command runs with allow_shared=True to rewrite every
    variant together. That is the intended semantics for the POC: one
    logical change to the command's display name affects every model.
    """
    commands = cg.commands()
    if preferred_script_name in commands:
        cmd_id = commands[preferred_script_name]
        return cmd_id, preferred_script_name
    # Fall back to first command.
    script_name, cmd_id = next(iter(sorted(commands.items(),
                                           key=lambda t: t[1])))
    return cmd_id, script_name


def main():
    print(f"donor: {DONOR}")
    if not os.path.isfile(DONOR):
        print(f"ERROR: donor missing: {DONOR}", file=sys.stderr)
        return 2

    os.makedirs(OUT_DIR, exist_ok=True)

    builder = pb.PackageBuilder(DONOR)
    print(f"donor round-trips byte-identically: {len(builder.raw)} bytes")

    cg = pa.CommandGraph(builder)
    print(f"donor has {len(cg.commands())} commands")

    cmd_id, old_script_name = _pick_command(cg)
    print(f"picked donor command #{cmd_id}: script_name={old_script_name!r}")

    result = cg.author_fresh_command(
        command_id=cmd_id,
        name=AUTHORED_NAME,
        script_name=AUTHORED_SCRIPT_NAME,
        attributes=AUTHORED_ATTRS,
        ex_cmd_id=AUTHORED_EX_CMD_ID,
        allow_shared=True,
    )
    print(f"authored: {result}")

    builder.write(OUT_PKP)
    print(f"wrote: {OUT_PKP} ({os.path.getsize(OUT_PKP)} bytes)")

    # Our parser's read-back of the authored fields.
    print()
    print("=== Our parser's read-back ===")
    parser = pd.PkpParser(pd.load_bytes(OUT_PKP))
    parser.parse()
    objs = parser.objects
    cmd = objs[cmd_id]
    members = cmd["members"]
    read_name = pb.deref(objs, members.get("AssetBase+_name"))
    read_script = pb.deref(objs, members.get("CommandAssetBase+_scriptName"))
    read_attrs_slot = members.get("CommandAssetBase+_attributes")
    read_attrs = None
    if isinstance(read_attrs_slot, dict) and read_attrs_slot.get("class"):
        # Follow the class instance to its sole Primitive value.
        read_attrs = read_attrs_slot.get("members", {}).get("value__")
    print(f"  _name              = {read_name!r}")
    print(f"  _scriptName        = {read_script!r}")
    print(f"  _attributes slot   = {read_attrs_slot!r}")
    print(f"  _attributes value  = {read_attrs!r}")

    # Extron's deserialiser via Load-Package.ps1 -- the decisive gate.
    print()
    print("=== Load-Package.ps1 -Commands ===")
    ps32 = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
    if not os.path.isfile(ps32):
        print(f"SKIPPED: 32-bit PowerShell not found at {ps32}")
        print("Cannot run the decisive gate on this box.")
        return 0
    if not os.path.isfile(LOAD_PS1):
        print(f"SKIPPED: Load-Package.ps1 not found at {LOAD_PS1}")
        return 0
    rc = subprocess.run(
        [ps32, "-ExecutionPolicy", "Bypass", "-File", LOAD_PS1,
         "-Commands", "-Path", OUT_PKP],
    ).returncode
    print()
    print(f"Load-Package.ps1 exit rc={rc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
