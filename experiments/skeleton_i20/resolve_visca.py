#!/usr/bin/env python3
"""
resolve_visca.py - flatten the Crestron 1 Beyond driver's Template command
chain into concrete VISCA byte templates.

Crestron's SchemaVersion 2.0 encodes a command as a Template that names
another command and supplies values for its placeholders (SetPower ->
ViscaCommand -> ViscaPacket). Reading any single command therefore tells you
almost nothing about the bytes on the wire. This walks the chain to a literal.

It is deliberately read-only and prints what it cannot resolve rather than
guessing - finding 07's rule: partial extraction that looks complete is the
failure mode to design against.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import pkg_dump


def load(pkg):
    return pkg_dump.process_pkg(pkg)["driver_definition"]


def resolve(dd, name, seen=None, depth=0):
    """Expand command `name` to a flat template string plus unresolved slots."""
    seen = seen or set()
    if name in seen or depth > 8:
        return "<cycle:%s>" % name
    seen = seen | {name}
    cmd = next((c for c in dd["Commands"] if c.get("Name") == name), None)
    if cmd is None:
        return "<undefined:%s>" % name
    info = cmd.get("Info", {})
    if cmd.get("Type") == "Text" or "Content" in info:
        return info.get("Content", "")
    inner = info.get("CommandName")
    if not inner:
        return "<no-chain:%s>" % name
    template = resolve(dd, inner, seen, depth + 1)
    for k, v in (info.get("Values") or {}).items():
        template = template.replace("{%s}" % k, str(v))
    return template


def normalise(t):
    """Drop the {:hex} mode marker and squeeze whitespace. It selects hex
    literal interpretation for the tokens that follow; it emits no byte of
    its own, which is why SetPower resolves to 81 01 04 00 {OnOff} FF and
    matches Extron's pack('>6B', DeviceID, 0x01, 0x04, 0x00, v, 0xFF)."""
    return re.sub(r"\s+", " ", t.replace("{:hex}", "")).strip()


def normalise(t):
    """Drop the {:hex} mode marker and squeeze whitespace.

    {:hex} selects hex interpretation for the tokens that follow; it emits no
    byte of its own. That is why SetPower resolves to `{Header} 01 04 00 {OnOff}
    FF` and matches Extron's pack('>6B', DeviceID, 0x01, 0x04, 0x00, v, 0xFF)
    exactly. Reading it as a byte would put the two vendors permanently out of
    agreement, so it is worth being explicit about.
    """
    return re.sub(r"\s+", " ", t.replace("{:hex}", "")).strip()


def main():
    pkg = sys.argv[1] if len(sys.argv) > 1 else (
        "samples/Crestron 1 Beyond IV-CAM-i12_i20/Crestron/"
        "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg")
    dd = load(pkg)
    rows, broken = [], []
    for c in dd["Commands"]:
        n = c["Name"]
        t = normalise(resolve(dd, n))
        # {Header}/{OnOff}/{Preset} are runtime parameters, not failures. Only
        # the <...> markers mean the chain could not be followed.
        params = sorted(set(re.findall(r"\{([A-Za-z][^}]*)\}", t)))
        rows.append((n, t, params))
        if "<" in t:
            broken.append((n, t))
    for n, t, params in rows:
        print("%-28s %-56s %s" % (n, t, ",".join(params)))
    literal = sum(1 for _n, _t, p in rows if not p)
    print("\n%d commands: %d literal, %d parameterised, %d UNRESOLVED"
          % (len(rows), literal, len(rows) - literal - len(broken), len(broken)))
    for n, t in broken:
        print("  UNRESOLVED %s -> %s" % (n, t))


if __name__ == "__main__":
    main()
