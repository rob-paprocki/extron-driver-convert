#!/usr/bin/env python3
"""
build_mutants.py - ROADMAP R26: build three single-edit mutants of the 1
Beyond PTZ-IP12/IP20 donor, each testing an edit kind finding 12 never tried
(finding 12's own mutation was a single BinaryObjectString - a model name).

Donor: samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp
(the same donor finding 13 §4b and experiments/skeleton_i20 already used).

Mutants (one change each, written to experiments/protocol_assets/mutants/):
  a_port.pkp           EthernetProtocolAsset._port  5500 -> 5678
  b_compatibility.pkp  EthernetProtocolAsset._compatibility  16 (Ethernet_Telnet)
                        -> 32 (Ethernet_UDP) - both values the survey (part 1)
                        found in the corpus at real scale (1449 and 224 models).
  c_tag.pkp             EnumStateAsset._tag (a BinaryObjectString; see NOTE
                        below on why this substitutes for a dedicated
                        "response/match-string asset", which this donor and
                        every other samples/ package lack)

`_port` and `_compatibility` are mutated via experiments/protocol_assets/
mutate_protocol.py (new code, not an edit to tools/pkp_build.py or
experiments/nrbf_writeback/nrbf_write.py - see that module's docstring for
why the existing PackageBuilder API cannot reach an inline Int32 member).
The `_tag` edit uses PackageBuilder.replace_string(), already public.

NOTE on item (c): no "response/match-string asset" NRBF class
----------------------------------------------------------------
The task's own wording flags this as an example, with an explicit fallback:
"if the donor has none, say so and pick another sample package that does."
Measured here: none of samples/'s 9 packages carries any class whose name
contains Match, Response, Parse, Regex or Pattern (checked directly by
listing every distinct class name pkp_dump.py reads out of all 9 .pkp files -
see MUTANTS.md for the full negative result). Reply parsing in a GC package
lives entirely in the embedded Python script (`AddMatchString` calls,
GC's `__MatchAllSubscribe` dispatcher per finding 13), which is exactly what
`tools/pkp_build.PackageBuilder.replace_script` already edits and finding 12
already exercised in spirit (a script-content edit, via nrbf_write's
round-trip). So there is no *graph-level* response/match asset to mutate
instead - the closest analog this donor's own graph offers is
`EnumStateAsset._tag`, the per-state string GC's Match-All-Subscribe
dispatcher keys results against (PTZ preset numbers "1".."7" on this donor).
It is still a BinaryObjectString, so mechanically it is the same *kind* of
edit finding 12 test 3 already made (a string mutation) - the point of
including it here is only to record the negative (no dedicated asset class
exists) plainly, not to claim a new edit kind was tested by it.

Run (from repo root):
    py -3.11 -u experiments/protocol_assets/build_mutants.py
"""
import sys
import os
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "nrbf_writeback"))
sys.path.insert(0, _HERE)

import pkp_dump as pd    # noqa: E402
import pkp_build as pb   # noqa: E402
import mutate_protocol as mp  # noqa: E402

DONOR = os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20",
                      "pkp", "1bynd_19_4743_v1_0_1.pkp")
OUT_DIR = os.path.join(_HERE, "mutants")


def check_no_response_asset_class():
    """Confirms (does not assume) the negative result the module docstring
    describes: no samples/*.pkp carries a Match/Response/Parse/Regex/Pattern
    -named class. Returns {file: [matching class names]}."""
    import glob
    hits = {}
    for f in glob.glob(os.path.join(_ROOT, "samples", "**", "pkp", "*.pkp"), recursive=True):
        data = pd.load_bytes(f)
        parser = pd.PkpParser(data)
        parser.parse()
        classes = set()
        for v in parser.objects.values():
            if isinstance(v, dict) and "class" in v:
                classes.add(v["class"].rsplit(".", 1)[-1])
        matches = sorted(c for c in classes
                          if any(k in c for k in ("Match", "Response", "Parse", "Regex", "Pattern")))
        hits[os.path.relpath(f, _ROOT).replace("\\", "/")] = matches
    return hits


def build_mutant_a_port():
    b = pb.PackageBuilder(DONOR)
    oid, proto, model_name = mp.find_ethernet_protocol_asset(b)
    before_port = proto["members"]["_port"]
    before_compat = proto["members"].get("_compatibility")
    new_port = 5678
    assert before_port != new_port
    before = mp.set_inline_int_member(b, oid, "_port", new_port)
    raw_before = b.raw
    raw_after = b.raw_bytes()
    return {
        "name": "a_port",
        "description": "EthernetProtocolAsset._port: %r -> %r (object id %s, model %s)"
                        % (before, new_port, oid, model_name),
        "builder": b,
        "object_id": oid,
        "model_name": model_name,
        "before": before,
        "after": new_port,
        "byte_len_before": len(raw_before),
        "byte_len_after": len(raw_after),
        "bytes_changed": sum(1 for x, y in zip(raw_before, raw_after) if x != y),
    }


def build_mutant_b_compatibility():
    b = pb.PackageBuilder(DONOR)
    oid, proto, model_name = mp.find_ethernet_protocol_asset(b)
    # 16 (Ethernet_Telnet) is the donor's own value; 32 (Ethernet_UDP) is the
    # value the survey (part 1) found on 224 models corpus-wide - both are
    # exact-named, non-adjacent bits, so this is not a trivial +/-1 edit.
    new_compat = 32
    raw_before = b.raw
    before = mp.set_enum_ref_member(b, oid, "_compatibility", new_compat)
    raw_after = b.raw_bytes()
    return {
        "name": "b_compatibility",
        "description": "EthernetProtocolAsset._compatibility: %r (Ethernet_Telnet) -> %r "
                        "(Ethernet_UDP) (object id %s, model %s)"
                        % (before, new_compat, oid, model_name),
        "builder": b,
        "object_id": oid,
        "model_name": model_name,
        "before": before,
        "after": new_compat,
        "byte_len_before": len(raw_before),
        "byte_len_after": len(raw_after),
        "bytes_changed": sum(1 for x, y in zip(raw_before, raw_after) if x != y),
    }


def build_mutant_c_tag():
    b = pb.PackageBuilder(DONOR)
    objs = b.objects
    # Locate an EnumStateAsset whose _tag is a short numeric preset label
    # (measured: PTZ-IP12/IP20 carries presets "1".."7"; see module docstring).
    target_oid = None
    target_tag_id = None
    target_value = None
    for oid, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Core.Assets.Automation.EnumStateAsset"):
            continue
        tag_ref = v.get("members", {}).get("_tag")
        tag_id = pb.ref_id(tag_ref)
        if tag_id is None:
            continue
        val = objs.get(tag_id)
        if isinstance(val, str) and val == "3":
            target_oid, target_tag_id, target_value = oid, tag_id, val
            break
    if target_oid is None:
        raise SystemExit("no EnumStateAsset with _tag=='3' found in donor - "
                          "donor's preset tags changed; update build_mutants.py")
    new_value = "3X"
    raw_before = b.raw
    before = b.replace_string(target_tag_id, new_value)
    raw_after = b.raw_bytes()
    return {
        "name": "c_tag",
        "description": "EnumStateAsset._tag (object id %s, string object id %s): %r -> %r "
                        "(also AssetBase+_name/_defaultName on the same asset, since they "
                        "share this string object)" % (target_oid, target_tag_id, before, new_value),
        "builder": b,
        "object_id": target_oid,
        "model_name": None,
        "before": before,
        "after": new_value,
        "byte_len_before": len(raw_before),
        "byte_len_after": len(raw_after),
        "bytes_changed": None,  # length changes; a byte diff count is not meaningful
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    negative = check_no_response_asset_class()
    any_hit = any(v for v in negative.values())
    print("response/match-string asset class search across samples/: %s"
          % ("FOUND (see below)" if any_hit else "none found (negative, as expected)"))
    for f, m in negative.items():
        if m:
            print("  %s: %s" % (f, m))

    mutants = [build_mutant_a_port(), build_mutant_b_compatibility(), build_mutant_c_tag()]

    manifest = {"donor": os.path.relpath(DONOR, _ROOT).replace("\\", "/"),
                "response_asset_search": negative, "mutants": []}

    for m in mutants:
        b = m["builder"]
        out_path = os.path.join(OUT_DIR, m["name"] + ".pkp")
        b.write(out_path)
        print("wrote %s" % os.path.relpath(out_path, _ROOT).replace("\\", "/"))
        print("  %s" % m["description"])
        print("  edits: %s" % b.edits)
        print("  bytes: %d -> %d (changed: %s)"
              % (m["byte_len_before"], m["byte_len_after"], m["bytes_changed"]))
        manifest["mutants"].append({
            "name": m["name"], "description": m["description"],
            "object_id": m["object_id"], "model_name": m["model_name"],
            "before": m["before"], "after": m["after"],
            "byte_len_before": m["byte_len_before"], "byte_len_after": m["byte_len_after"],
            "bytes_changed": m["bytes_changed"], "edits": b.edits,
            "output": os.path.relpath(out_path, _ROOT).replace("\\", "/"),
        })

    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("wrote %s" % os.path.relpath(manifest_path, _ROOT).replace("\\", "/"))


if __name__ == "__main__":
    main()
