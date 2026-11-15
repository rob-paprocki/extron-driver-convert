#!/usr/bin/env python3
"""
build_inplace_string.py - R28 Phase 4 POC follow-on.

build_fresh_root.py showed that `author_command_values` writes our
authored strings into new BinaryObjectString records and repoints the
command's _name / _scriptName MemberReferences to them. Our Python
parser reads the authored values; Extron's property accessors still
return the donor's originals.

This script tests the alternative primitive: mutate the EXISTING
BinaryObjectString record's bytes in place at its original oid
(pkp_build.replace_string), rather than adding a new record.
Hypothesis: Extron's ISerializable bridging depends on WHERE in the
stream the string lives (ordering/position), not just the reference
value. In-place byte mutation preserves position.

Risk: a string that's shared across commands/models would change the
value everywhere. We measure whether the string we touch is uniquely
referenced first.

Run from the repo root:
    python experiments/graph_synthesis/build_inplace_string.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb        # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT_DIR = os.path.join(_HERE, "out")
OUT_PATH = os.path.join(OUT_DIR, "inplace_string_poc.pkp")

# AutoTracking's _name string (oid 294) and _scriptName string (oid 296)
# measured directly off the donor by build_fresh_root.py's trailing
# probe. Replace in place.
NAME_STRING_OID = 294       # was 'Auto Tracking'
SCRIPT_NAME_STRING_OID = 296  # was 'AutoTracking'
AUTHORED_NAME = "POC Authored Display Name"
AUTHORED_SCRIPT_NAME = "POCAuthoredScriptName"


def refcount_of(builder, oid):
    """Count how many MemberReference-style $refs in the trace point at
    this oid. Reused to check that we're not stepping on a string shared
    across commands."""
    count = 0
    for ev in builder.trace:
        if ev.get("kind") == "MemberReference" and ev.get("idref") == oid:
            count += 1
    return count


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    b = pb.PackageBuilder(DONOR)
    print("donor:", DONOR)

    before_name = b.strings().get(NAME_STRING_OID)
    before_script = b.strings().get(SCRIPT_NAME_STRING_OID)
    print("oid %d  before: %r  refs: %d"
          % (NAME_STRING_OID, before_name, refcount_of(b, NAME_STRING_OID)))
    print("oid %d  before: %r  refs: %d"
          % (SCRIPT_NAME_STRING_OID, before_script,
             refcount_of(b, SCRIPT_NAME_STRING_OID)))

    b.replace_string(NAME_STRING_OID, AUTHORED_NAME)
    b.replace_string(SCRIPT_NAME_STRING_OID, AUTHORED_SCRIPT_NAME)

    print("edits:", b.edits)
    b.write(OUT_PATH)
    size = os.path.getsize(OUT_PATH)
    print("wrote %s  (%d bytes)" % (OUT_PATH, size))


if __name__ == "__main__":
    main()
