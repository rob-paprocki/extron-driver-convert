#!/usr/bin/env python3
"""
test_pkp_validate.py - offline gate for tools/pkp_validate.py.

pkp_validate.py claims to answer, without Global Configurator installed, the
question GC answers with a modal box: "would this package be refused with
Error Code: 80085?". That claim is only worth anything if the reimplementation
is pinned to real files, so this suite checks it four ways:

  1. AGREEMENT WITH REALITY. Every shipping package in samples/ must come back
     Valid. Nine packages, twenty resources - if the reimplementation were
     wrong about the digest, the manifest, or the dictionary shape, this fails.
  2. IT ACTUALLY DETECTS THE FAILURE. A script substituted without refreshing
     the stored digest must come back MismatchHash (80085) - the exact
     condition finding 15 hit on hardware. The comm-sheet PDF too: it is
     embedded, it is hashed, and a stale PDF digest is the same failure.
  3. THE FIX IS THE FIX. The same substitution, with
     pkp_build.refresh_resource_hash, must come back Valid. This is the
     property the transplant builder depends on.
  4. IT FAILS LOUDLY. Truncated, garbage, empty and wrong-format inputs must
     never return Valid. A validator that says "fine" to a file it could not
     read is worse than no validator.

Plus the branches no shipping package exercises - an empty _resourceHashDict,
a populated Guid table, the "eir" bypass - driven through validate_graph so
they are covered without synthesising an NRBF stream for each.

Run: python3 tools/test_pkp_validate.py
"""

import gzip
import hashlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import pkp_build as pb            # noqa: E402
import pkp_validate as pv         # noqa: E402


PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def all_packages():
    out = []
    for root, _dirs, files in os.walk(os.path.join(_ROOT, "samples")):
        for f in files:
            if f.endswith(".pkp"):
                out.append(os.path.join(root, f))
    return sorted(out)


def donor():
    """One mid-sized package to carry the per-branch tests."""
    for p in all_packages():
        if os.path.basename(p).startswith("extr_17_17677"):
            return p
    return all_packages()[0]


def pdf_content_id(builder):
    """(key, content object id) of the comm-sheet PDF resource.

    pkp_build exposes script slots only; the PDF is the same kind of
    StreamResourceAsset, so find it the same way.
    """
    objs = builder.objects
    for oid, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") == pb.STREAM_ASSET_CLASS):
            continue
        m = v.get("members", {})
        key = pb.deref(objs, m.get("ResourceAssetBase+_key"))
        if isinstance(key, str) and key.lower().endswith(".pdf"):
            return key, pb.ref_id(m.get("ResourceAssetBase+_content"))
    return None, None


# ---------------------------------------------------------------------------

def test_enum_mirrors_extron():
    print("\n[1] the enum mirrors Extron's ErrorCode exactly")
    check("Valid == 0", pv.VALID == 0)
    check("MismatchHash == 80085", pv.MISMATCH_HASH == 80085)
    check("NoHash_NoGuid == 80086", pv.NO_HASH_NO_GUID == 80086)
    check("names match the CLR enum",
          pv.CODE_NAMES[0] == "Valid"
          and pv.CODE_NAMES[80085] == "MismatchHash"
          and pv.CODE_NAMES[80086] == "NoHash_NoGuid")
    check("repo-local sentinels are negative, so they cannot collide",
          pv.UNVERIFIABLE < 0 and pv.UNPARSEABLE < 0)


def test_every_sample_validates():
    print("\n[2] every shipping package in samples/ validates Valid")
    pkgs = all_packages()
    check("found sample packages", len(pkgs) > 0, "%d" % len(pkgs))
    for p in pkgs:
        r = pv.validate(p)
        ok = check("Valid: %s" % os.path.basename(p),
                   r.code == pv.VALID and r.name == "Valid",
                   "%s %s | %s" % (r.name, r.code, "; ".join(r.details[:2])))
        if ok:
            check("  fully verified, no gaps: %s" % os.path.basename(p),
                  r.ok and r.verified and not r.warnings,
                  "warnings=%s" % r.warnings)


def test_pdf_is_embedded_and_checked():
    print("\n[3] the comm-sheet PDF is embedded, and it IS hash-checked")
    pdfs = 0
    for p in all_packages():
        r = pv.validate(p)
        for res in r.resources:
            if res.key and res.key.lower().endswith(".pdf"):
                pdfs += 1
                check("%s: pdf hashed from embedded bytes" % os.path.basename(p),
                      res.computed is not None and res.size and res.size > 0
                      and res.code == pv.VALID and res.source == "key",
                      "size=%s code=%s source=%s" % (res.size, res.code, res.source))
    check("every sample carried a checkable PDF", pdfs == len(all_packages()),
          "%d pdfs across %d packages" % (pdfs, len(all_packages())))


def test_mutated_script_without_refresh_is_80085():
    print("\n[4] a script mutated WITHOUT a hash refresh returns MismatchHash")
    for p in all_packages():
        b = pb.PackageBuilder(p)
        slot = b.scripts()[0]
        b.replace_script(slot.key, slot.source + "\n# transplant marker\n",
                         refresh_hash=False)
        r = pv.validate(b.build(compress=True))
        name = os.path.basename(p)
        ok = check("MismatchHash: %s" % name,
                   r.code == pv.MISMATCH_HASH and r.name == "MismatchHash",
                   "got %s %s" % (r.name, r.code))
        if ok:
            failing = [x for x in r.resources if x.code == pv.MISMATCH_HASH]
            check("  blamed the script we changed: %s" % name,
                  len(failing) == 1 and failing[0].key == slot.key,
                  "blamed %s" % [x.key for x in failing])


def test_mutated_script_with_refresh_is_valid():
    print("\n[5] the same mutation WITH refresh_resource_hash returns Valid")
    for p in all_packages():
        b = pb.PackageBuilder(p)
        slot = b.scripts()[0]
        new_source = slot.source + "\n# transplant marker\n"
        # Refresh explicitly rather than via replace_script's default, so this
        # test exercises pkp_build.refresh_resource_hash by name.
        b.replace_script(slot.key, new_source, refresh_hash=False)
        changed = b.refresh_resource_hash(slot.key, source=new_source)
        r = pv.validate(b.build(compress=True))
        name = os.path.basename(p)
        check("refresh reported the change: %s" % name, changed == [slot.key],
              "%s" % (changed,))
        check("Valid after refresh: %s" % name,
              r.code == pv.VALID and r.ok,
              "got %s %s warnings=%s" % (r.name, r.code, r.warnings))


def test_mutated_pdf_is_also_caught():
    print("\n[6] a stale PDF digest fails exactly like a stale script digest")
    b = pb.PackageBuilder(donor())
    key, cid = pdf_content_id(b)
    check("found the PDF resource", key is not None and cid is not None, str(key))
    if cid is None:
        return
    original = bytes(pb.deref(b.objects, {"$ref": cid})["items"])
    pb.mutate_primitive_array_by_object_id(b.trace, cid, original + b"\n%% edited\n")
    r = pv.validate(b.build(compress=True))
    check("MismatchHash on the PDF", r.code == pv.MISMATCH_HASH,
          "got %s %s" % (r.name, r.code))
    blamed = [x.key for x in r.resources if x.code == pv.MISMATCH_HASH]
    check("the PDF is the resource blamed", blamed == [key], "%s" % blamed)
    check("the script beside it still passes",
          any(x.code == pv.VALID and x.key.endswith(".py") for x in r.resources))


def test_first_failure_wins():
    print("\n[7] the reported code comes from the FIRST failing resource")
    b = pb.PackageBuilder(donor())
    slot = b.scripts()[0]
    b.replace_script(slot.key, slot.source + "\n#x\n", refresh_hash=False)
    key, cid = pdf_content_id(b)
    original = bytes(pb.deref(b.objects, {"$ref": cid})["items"])
    pb.mutate_primitive_array_by_object_id(b.trace, cid, original + b"\n%% edited\n")
    r = pv.validate(b.build(compress=True))
    check("still one code, MismatchHash", r.code == pv.MISMATCH_HASH)
    check("both resources reported as failing",
          sum(1 for x in r.resources if x.code == pv.MISMATCH_HASH) == 2,
          "%s" % [(x.key, x.code) for x in r.resources])
    check("details name the first failure",
          r.details and r.details[0].startswith("first failing resource:"),
          "%s" % (r.details[:1],))


def test_no_hash_no_guid_branch():
    print("\n[8] a resource in neither table returns NoHash_NoGuid (80086)")
    objects, root = pv.load_graph(donor())
    # Drop the package's own dict. Per every decode, get_ResourceHashDict()
    # lazily creates an EMPTY dictionary when the field is null, so this is a
    # real package shape, not an impossible one: every resource then falls
    # through to the validator's Guid table.
    root["members"]["_resourceHashDict"] = None
    r = pv.validate_graph(objects, root, path=donor())
    check("code is NoHash_NoGuid", r.code == pv.NO_HASH_NO_GUID,
          "got %s %s" % (r.name, r.code))
    check("every resource missed both tables",
          all(x.code == pv.NO_HASH_NO_GUID for x in r.resources) and r.resources)
    check("warns that no ExtronDH.dat table was available (gap 1)",
          any("Guid table was supplied" in w for w in r.warnings),
          "%s" % r.warnings)
    check("not ok, because a prediction is not a measurement", not r.ok)


def test_guid_fallback_paths():
    print("\n[9] the Guid fallback resolves both ways when a table is supplied")
    objects, root = pv.load_graph(donor())
    root["members"]["_resourceHashDict"] = None
    probe = pv.validate_graph(objects, root, path=donor())
    table = {x.guid: x.computed for x in probe.resources if x.guid}
    check("resources carry parseable GUIDs", len(table) == len(probe.resources),
          "%d of %d" % (len(table), len(probe.resources)))

    good = pv.validate_graph(objects, root, guid_hash_table=table, path=donor())
    check("correct Guid-table digests -> Valid", good.code == pv.VALID,
          "got %s %s" % (good.name, good.code))
    check("the Guid table is recorded as the answering source",
          all(x.source == "guid" for x in good.resources))
    check("no gap-1 warning once a table was supplied", not good.warnings,
          "%s" % good.warnings)

    bad_key = sorted(table)[0]
    bad = dict(table)
    bad[bad_key] = b"\x00" * 32
    r = pv.validate_graph(objects, root, guid_hash_table=bad, path=donor())
    check("wrong Guid-table digest -> MismatchHash", r.code == pv.MISMATCH_HASH,
          "got %s %s" % (r.name, r.code))


def test_unhashable_content_is_not_a_pass():
    print("\n[10] a resource with no embedded bytes is Unverifiable, never Valid")
    objects, root = pv.load_graph(donor())
    resources, _w = pv.manifest_resources(objects, root)
    check("manifest resources found", len(resources) >= 2, "%d" % len(resources))
    resources[0]["members"]["ResourceAssetBase+_content"] = None
    r = pv.validate_graph(objects, root, path=donor())
    check("code is the repo-local Unverifiable sentinel", r.code == pv.UNVERIFIABLE,
          "got %s %s" % (r.name, r.code))
    check("it is not Valid", r.code != pv.VALID and not r.ok)
    check("the note says GC would throw rather than return a code",
          any("ArgumentNullException" in (x.note or "") for x in r.resources))


def test_eir_bypass_is_reported_never_silent():
    print("\n[11] the eir bypass follows the ON-DISK name only (gap 2, measured)")
    objects, root = pv.load_graph(donor())
    stored = pv.member(objects, root, "DriverDescriptorAsset+_filename", "_filename")
    check("sample stored filename ends in pkp, so the bypass is moot",
          isinstance(stored, str) and not pv._ends_with_eir(stored), repr(stored))

    # Measured against Extron 15.27.0.0 on 2026-09-09: LoadFromFile overwrites
    # Filename with Path.GetFileName(), so ONLY the on-disk name is tested. An
    # earlier revision required both names to agree; that was wrong in both
    # directions, and this test asserted the wrong behaviour along with it.
    r = pv.validate_graph(objects, root, on_disk_name="some_driver.eir")
    check("on-disk name ends in eir -> Valid by bypass",
          r.code == pv.VALID and r.bypassed)
    check("bypass verified nothing", not r.verified and not r.resources)
    check("bypass is a warning, so the CLI still exits non-zero",
          r.warnings and not r.ok, "%s" % r.warnings)
    check("case-insensitive, per InvariantCultureIgnoreCase",
          pv.validate_graph(objects, root, on_disk_name="X.EIR").bypassed)

    # The serialized _filename must NOT trigger it: a .pkp whose _filename was
    # rewritten to end in .eir still returns MismatchHash from Extron when its
    # digest is corrupt - measured, and this reimplementation agrees.
    fid = pb.ref_id(root["members"]["DriverDescriptorAsset+_filename"])
    objects[fid] = "tampered.eir"
    r2 = pv.validate_graph(objects, root, on_disk_name="some_driver.pkp")
    check("serialized _filename ending in eir does NOT bypass",
          not r2.bypassed and len(r2.resources) >= 2)
    check("and the reimplementation says why",
          any("does NOT bypass" in d for d in r2.details), "%s" % r2.details)

def test_bad_input_fails_loudly():
    print("\n[12] truncated / garbage input fails loudly, never Valid")
    raw = open(donor(), "rb").read()
    plain = gzip.decompress(raw)
    cases = [
        ("empty bytes", b""),
        ("ascii garbage", b"this is not a driver package at all\n" * 40),
        ("random binary", bytes(range(256)) * 8),
        ("gzip magic, garbage body", b"\x1f\x8b" + b"\x00" * 512),
        ("truncated gzip container", raw[:len(raw) // 2]),
        ("truncated NRBF stream", plain[:len(plain) // 2]),
        ("NRBF with MessageEnd chopped off", plain[:-1]),
        ("header only", plain[:17]),
        ("a python source file", open(os.path.join(_HERE, "pkp_validate.py"), "rb").read()),
    ]
    for name, data in cases:
        r = pv.validate(data)
        check("not Valid: %s" % name, r.code != pv.VALID and not r.ok,
              "got %s %s" % (r.name, r.code))
        check("  says why: %s" % name, bool(r.warnings) and bool(r.details),
              "%s" % (r.warnings[:1],))

    r = pv.validate(os.path.join(_ROOT, "no", "such", "file.pkp"))
    check("a missing file is Unparseable, not a crash", r.code == pv.UNPARSEABLE)

    # A wrong-but-parseable NRBF root must be refused too: parsing is not
    # validation, and "it deserialized" is not "it is a driver package".
    check("load_graph raises PackageError on garbage",
          _raises(pv.PackageError, pv.load_graph, b"garbage" * 100))


def _raises(exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except exc:
        return True
    except Exception:
        return False
    return False


def test_accepts_bytes_and_gzip():
    print("\n[13] the API takes a path, raw bytes, or gzipped bytes alike")
    p = donor()
    raw = open(p, "rb").read()
    plain = gzip.decompress(raw)
    a, b_, c = pv.validate(p), pv.validate(raw), pv.validate(plain)
    check("path -> Valid", a.code == pv.VALID)
    check("gzipped bytes -> Valid", b_.code == pv.VALID)
    check("decompressed bytes -> Valid", c.code == pv.VALID)
    check("all three agree on the resources",
          [x.key for x in a.resources] == [x.key for x in b_.resources]
          == [x.key for x in c.resources])
    check("byte input has no path", b_.path is None and a.path == p)


def test_digest_is_plain_sha256():
    print("\n[14] the stored digest really is plain SHA-256 over the raw bytes")
    b = pb.PackageBuilder(donor())
    stored = b.resource_hashes()
    r = pv.validate(donor())
    for res in r.resources:
        oid_digest = stored[res.key][1]
        check("stored == sha256(content): %s" % res.key,
              res.computed == oid_digest and len(oid_digest) == 32)
    slot = b.scripts()[0]
    check("and it is sha256 of the utf-8 script text, unsalted",
          hashlib.sha256(slot.source.encode("utf-8")).digest() == stored[slot.key][1])


def test_cli():
    print("\n[15] the CLI exits 0 on good packages and non-zero on bad ones")
    check("CLI returns 0 for the samples", pv.main(all_packages()) == 0)
    bad = os.path.join(_HERE, "pkp_validate.py")
    check("CLI returns non-zero when any input is invalid",
          pv.main([donor(), bad]) != 0)


def main():
    print("test_pkp_validate.py - offline gate for the .pkp validator")
    for fn in (test_enum_mirrors_extron,
               test_every_sample_validates,
               test_pdf_is_embedded_and_checked,
               test_mutated_script_without_refresh_is_80085,
               test_mutated_script_with_refresh_is_valid,
               test_mutated_pdf_is_also_caught,
               test_first_failure_wins,
               test_no_hash_no_guid_branch,
               test_guid_fallback_paths,
               test_unhashable_content_is_not_a_pass,
               test_eir_bypass_is_reported_never_silent,
               test_bad_input_fails_loudly,
               test_accepts_bytes_and_gzip,
               test_digest_is_plain_sha256,
               test_cli):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
