#!/usr/bin/env python3
"""Generate a corpus of deliberately-broken .pkp packages to hunt for
disagreements between tools/pkp_validate.py and Extron's real validator."""
import os, sys, hashlib, gzip, shutil

REPO = r"Z:\GitHub\rob-paprocki\extron-driver-convert"
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "experiments", "nrbf_writeback"))
import pkp_build as pb
import nrbf_write as nw
import pkp_dump as pd

OUT = r"C:\Users\robp\AppData\Local\Temp\extval\mutants"
os.makedirs(OUT, exist_ok=True)

STREAM = pb.STREAM_ASSET_CLASS


def resources(b):
    """[(asset_oid, key, key_oid, content_oid, content_bytes)] for every
    StreamResourceAsset with an embedded primitive-array content."""
    out = []
    for oid, v in b.objects.items():
        if not (isinstance(v, dict) and v.get("class") == STREAM):
            continue
        m = v.get("members", {})
        kref = m.get("ResourceAssetBase+_key")
        key = pb.deref(b.objects, kref)
        cref = m.get("ResourceAssetBase+_content")
        content = pb.deref(b.objects, cref)
        if not isinstance(key, str):
            continue
        if isinstance(content, dict) and content.get("$type") == "ArraySinglePrimitive":
            data = bytes(content["items"])
            cid = pb.ref_id(cref)
        else:
            data, cid = None, None
        out.append((oid, key, pb.ref_id(kref), cid, data))
    out.sort(key=lambda r: (r[1], r[0]))
    return out


def hash_kv(b):
    """{key: (key_object_id, hash_object_id, digest)} from _resourceHashDict."""
    root = b.objects.get(1)
    d = pb.deref(b.objects, root["members"]["_resourceHashDict"])
    kvps = pb.deref(b.objects, (d.get("members") or {}).get("KeyValuePairs"))
    out = {}
    for item in (kvps or {}).get("items") or []:
        e = pb.deref(b.objects, item)
        if not isinstance(e, dict):
            continue
        m = e.get("members") or {}
        kref, vref = m.get("key"), m.get("value")
        k = pb.deref(b.objects, kref)
        v = pb.deref(b.objects, vref)
        if isinstance(k, str) and isinstance(v, dict):
            out[k] = (pb.ref_id(kref), pb.ref_id(vref), bytes(v.get("items") or []))
    return out


def filename_string(b):
    """(object_id, value) of DriverDescriptorAsset+_filename, if present."""
    for oid, v in b.objects.items():
        if not isinstance(v, dict) or "members" not in v:
            continue
        for mname, mref in (v.get("members") or {}).items():
            if mname.endswith("_filename"):
                val = pb.deref(b.objects, mref)
                if isinstance(val, str):
                    return pb.ref_id(mref), val, oid
    return None, None, None


def emit(b, name):
    p = os.path.join(OUT, name)
    b.write(p)
    return p


made = []


def mutant(donor, name, fn):
    """fn(builder) -> None|'skip'.  Writes OUT/name."""
    try:
        b = pb.PackageBuilder(donor)
        r = fn(b)
        if r == "skip":
            print("  skip %s" % name)
            return
        p = emit(b, name)
        made.append((name, p, r or ""))
        print("  made %s  (%s)" % (name, r or ""))
    except Exception as e:
        print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))


DONORS = [
    (r"Z:\GitHub\rob-paprocki\extron-driver-convert\samples\DSC_12G-HD\pkp\extr_17_17677_v1_0_0.pkp", "dsc"),
    (r"Z:\GitHub\rob-paprocki\extron-driver-convert\samples\Samsung QNxxLS03DAFXZA\pkp\smsg_10_6738_v1_0_0.pkp", "smsg"),
    (r"Z:\GitHub\rob-paprocki\extron-driver-convert\samples\Tesira\pkp\biam_25_150_v1_20_0.pkp", "tesira"),
]

for donor, tag in DONORS:
    print("== donor %s (%s)" % (tag, os.path.basename(donor)))
    b0 = pb.PackageBuilder(donor)
    res = resources(b0)
    hk = hash_kv(b0)
    print("   resources: %s" % [(r[1], (len(r[4]) if r[4] is not None else None)) for r in res])
    print("   hashdict keys: %s" % sorted(hk))
    fid, fval, fowner = filename_string(b0)
    print("   _filename: id=%s %r" % (fid, fval))
    pykey = next((r for r in res if r[1].lower().endswith(".py")), None)
    pdfkey = next((r for r in res if r[1].lower().endswith(".pdf")), None)
    print("   dict-key oid vs resource-key oid: %s" %
          [(r[1], r[2], hk.get(r[1], (None,))[0]) for r in res])

    # --- control: rebuild untouched -------------------------------------
    mutant(donor, "%s_00_control.pkp" % tag, lambda b: "untouched rebuild")

    # --- 1. script bytes changed, hash NOT refreshed  -> expect 80085 ---
    if pykey:
        def f(b, k=pykey[1]):
            slot = next(s for s in b.scripts() if s.key == k)
            b.replace_script(k, slot.source + "\n# tampered\n", refresh_hash=False)
            return "stale script hash"
        mutant(donor, "%s_01_stale_script.pkp" % tag, f)

        # --- 2. script changed AND hash refreshed -> expect Valid -------
        def f(b, k=pykey[1]):
            slot = next(s for s in b.scripts() if s.key == k)
            b.replace_script(k, slot.source + "\n# tampered\n", refresh_hash=True)
            return "script + refreshed hash"
        mutant(donor, "%s_02_refreshed_script.pkp" % tag, f)

        # --- 3. stored digest corrupted (last byte flipped) -> 80085 ---
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            hid, dig = h[k][1], h[k][2]
            bad = dig[:-1] + bytes([dig[-1] ^ 0xFF])
            pb.mutate_primitive_array_by_object_id(b.trace, hid, bad)
            return "py digest last byte flipped"
        mutant(donor, "%s_03_bad_py_digest.pkp" % tag, f)

        # --- 4. stored digest truncated to 16 bytes -> 80085 (length) --
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            hid, dig = h[k][1], h[k][2]
            pb.mutate_primitive_array_by_object_id(b.trace, hid, dig[:16])
            return "py digest truncated to 16 bytes"
        mutant(donor, "%s_04_short_py_digest.pkp" % tag, f)

        # --- 5. stored digest emptied -> ? -----------------------------
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            pb.mutate_primitive_array_by_object_id(b.trace, h[k][1], b"")
            return "py digest zero-length"
        mutant(donor, "%s_05_empty_py_digest.pkp" % tag, f)

        # --- 6. dict KEY renamed -> lookup miss -> 80086 or NRE --------
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            koid = h[k][0]
            rkoid = next(r[2] for r in resources(b) if r[1] == k)
            if koid == rkoid:
                return "skip"     # shared string; renaming would rename both
            nw.mutate_string_by_object_id(b.trace, koid, "ZZ_" + k)
            return "dict key renamed -> %r (resource key unchanged)" % ("ZZ_" + k)
        mutant(donor, "%s_06_dictkey_renamed.pkp" % tag, f)

        # --- 7. RESOURCE key renamed -> lookup miss --------------------
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            koid = h[k][0]
            rkoid = next(r[2] for r in resources(b) if r[1] == k)
            if koid == rkoid:
                return "skip"
            nw.mutate_string_by_object_id(b.trace, rkoid, "ZZ_" + k)
            return "resource key renamed -> %r (dict key unchanged)" % ("ZZ_" + k)
        mutant(donor, "%s_07_reskey_renamed.pkp" % tag, f)

        # --- 8. both renamed together (shared or not) -> still matches -
        def f(b, k=pykey[1]):
            h = hash_kv(b)
            koid = h[k][0]
            rkoid = next(r[2] for r in resources(b) if r[1] == k)
            nw.mutate_string_by_object_id(b.trace, koid, "ZZ_" + k)
            if rkoid != koid:
                nw.mutate_string_by_object_id(b.trace, rkoid, "ZZ_" + k)
            return "both keys renamed to ZZ_%s" % k
        mutant(donor, "%s_08_bothkeys_renamed.pkp" % tag, f)

    # --- 9/10. PDF: bytes tampered, digest tampered ---------------------
    if pdfkey and pdfkey[4] is not None:
        def f(b, k=pdfkey[1]):
            r = next(x for x in resources(b) if x[1] == k)
            pb.mutate_primitive_array_by_object_id(b.trace, r[3], r[4] + b"\x00TAMPER")
            return "pdf bytes appended, digest untouched"
        mutant(donor, "%s_09_stale_pdf.pkp" % tag, f)

        def f(b, k=pdfkey[1]):
            h = hash_kv(b)
            hid, dig = h[k][1], h[k][2]
            pb.mutate_primitive_array_by_object_id(b.trace, hid, dig[:-1] + bytes([dig[-1] ^ 0xFF]))
            return "pdf digest last byte flipped"
        mutant(donor, "%s_10_bad_pdf_digest.pkp" % tag, f)

        # both wrong at once - which resource does GC report first?
        def f(b, kp=pykey[1] if pykey else None, kd=pdfkey[1]):
            h = hash_kv(b)
            for k in ([kp] if kp else []) + [kd]:
                hid, dig = h[k][1], h[k][2]
                pb.mutate_primitive_array_by_object_id(
                    b.trace, hid, dig[:-1] + bytes([dig[-1] ^ 0xFF]))
            return "BOTH digests corrupted"
        mutant(donor, "%s_11_both_digests_bad.pkp" % tag, f)

    # --- 12. serialized _filename ends in 'eir' -------------------------
    if fid is not None and pykey:
        def f(b, k=pykey[1]):
            fi, fv, _ = filename_string(b)
            nw.mutate_string_by_object_id(b.trace, fi, "C:\\tmp\\tampered.eir")
            h = hash_kv(b)
            hid, dig = h[k][1], h[k][2]
            pb.mutate_primitive_array_by_object_id(b.trace, hid, dig[:-1] + bytes([dig[-1] ^ 0xFF]))
            return "_filename -> *.eir AND py digest corrupted"
        mutant(donor, "%s_12_filename_eir_baddigest.pkp" % tag, f)

        def f(b):
            fi, fv, _ = filename_string(b)
            nw.mutate_string_by_object_id(b.trace, fi, "C:\\tmp\\tampered.eir")
            return "_filename -> *.eir, everything else intact"
        mutant(donor, "%s_13_filename_eir_clean.pkp" % tag, f)

print()
print("== on-disk .eir copies (gap 2, the other side) ==")
for name, p, note in list(made):
    if "_01_stale_script" in name or "_03_bad_py_digest" in name:
        q = p[:-4] + ".eir_ondisk.pkp"
        # a real on-disk .eir name
        q = os.path.join(OUT, name.replace(".pkp", "") + "_ondisk.eir")
        shutil.copyfile(p, q)
        made.append((os.path.basename(q), q, note + " + on-disk name ends .eir"))
        print("  made %s" % os.path.basename(q))

print()
print("== structurally broken inputs ==")
src = os.path.join(OUT, "dsc_00_control.pkp")
if os.path.exists(src):
    raw = open(src, "rb").read()
    cases = {
        "trunc_half.pkp": raw[:len(raw) // 2],
        "trunc_16.pkp": raw[:16],
        "empty.pkp": b"",
        "notgzip.pkp": b"this is not a pkp at all" * 10,
        "gzip_garbage.pkp": gzip.compress(b"\x00\x01\x02not nrbf" * 50, mtime=0),
    }
    for n, data in cases.items():
        p = os.path.join(OUT, n)
        open(p, "wb").write(data)
        made.append((n, p, "structurally broken"))
        print("  made %s" % n)

with open(os.path.join(OUT, "..", "mutant_list.txt"), "w", encoding="utf-8") as fh:
    for name, p, note in made:
        fh.write(p + "\n")
with open(os.path.join(OUT, "..", "mutant_notes.tsv"), "w", encoding="utf-8") as fh:
    for name, p, note in made:
        fh.write("%s\t%s\n" % (p, note))
print("\n%d mutants" % len(made))
