#!/usr/bin/env python3
"""
test_load_package.py - Extron's own loader, asked about every package we build.

CLAUDE.md rule 4: `Valid` does not mean loadable, and a local check can share
our wrong model of the format. Finding 18 built a package that parsed,
round-tripped, validated and passed 39 tests, and Global Configurator would
not list it, because .NET's BinaryFormatter refused the stream. Both bugs that
only Extron's code could see were caught by running Load-Package.ps1 by hand.
This makes that run a test (ROADMAP R30).

Load-Package.ps1 runs under 32-bit PowerShell and asks Extron's
DriverFileAsset.LoadFromFile and BinaryFormatter.Deserialize about each
package, then lists the commands the loaded asset carries. The checks:

  [1] every sample package loads and deserializes - the control. If one of
      Extron's own packages fails, the harness is broken, not our package.
  [2] every package in experiments/skeleton_i20/out/ loads and deserializes.
  [3] for each of ours, the loader sees exactly the commands our own parser
      (tools/pkp_asset.py) reads out of the graph - by script name and by
      display name - and each model carries exactly the list our parser reads
      for it (from 20028 the IV-CAM-I12's is shorter than the I20's).

Skipped - exit 0, nothing counted - unless this is Windows with 32-bit
PowerShell and a Global Configurator install whose assemblies Load-Package.ps1
can load. No GCP licence is needed. Set EXTRON_GCP_DIR if GC is not installed
in its default folder.

Run: python3 experiments/gcp_harness/test_load_package.py
"""

import glob
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_asset as pa           # noqa: E402
import pkp_build as pb           # noqa: E402

PASS = []
FAIL = []

SCRIPT = os.path.join(_HERE, "Load-Package.ps1")
PS32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                    "SysWOW64", "WindowsPowerShell", "v1.0", "powershell.exe")
GCP_DIR = os.environ.get("EXTRON_GCP_DIR", r"C:\Program Files (x86)\Extron\GCP")
DRIVERS_DLL = "Extron.Configuration.Drivers.dll"

OURS = "experiments/skeleton_i20/out"

CMD_LINE = re.compile(r"^    (\S+)\s+(.*?)\s+attrs=(\d+)\s*(.*)$")
MODEL_LINE = re.compile(r"^  model (.*?)  commands=(\d+)$")


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def unavailable():
    """Why the loader cannot run here, or None if it can."""
    if os.name != "nt":
        return "not Windows"
    if not os.path.isfile(PS32):
        return "no 32-bit PowerShell"
    if not os.path.isfile(os.path.join(GCP_DIR, DRIVERS_DLL)):
        return "no %s in the GC folder (set EXTRON_GCP_DIR)" % DRIVERS_DLL
    return None


def rel(path):
    return os.path.relpath(path, _ROOT).replace(os.sep, "/")


def sample_packages():
    found = []
    for root, _dirs, files in os.walk(os.path.join(_ROOT, "samples")):
        found += [os.path.join(root, f) for f in files if f.endswith(".pkp")]
    return sorted(rel(p) for p in found)


def our_packages():
    return sorted(rel(p) for p in glob.glob(os.path.join(_ROOT, OURS, "*.pkp")))


def run_loader(paths):
    """Load-Package.ps1 -Deserialize -Commands over paths (repo-relative)."""
    args = [PS32, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SCRIPT,
            "-Path", ",".join(paths), "-Deserialize", "-Commands", "-GcpDir", GCP_DIR]
    p = subprocess.run(args, cwd=_ROOT, capture_output=True, text=True, timeout=900)
    return p.returncode, p.stdout, p.stderr


def parse(stdout):
    """{package leaf name: what the loader said about it}."""
    out = {}
    cur = None
    for line in stdout.splitlines():
        if line.startswith("=== "):
            cur = out.setdefault(line[4:].strip(), {
                "load": None, "deserialize": None, "declared": None,
                "commands": {}, "models": {}})
        elif cur is None:
            continue
        elif line.startswith("  LoadFromFile :"):
            cur["load"] = line.split(":", 1)[1].strip()
        elif line.startswith("  Deserialize  :") and cur["deserialize"] is None:
            cur["deserialize"] = line.split(":", 1)[1].strip()
        elif line.startswith("  DriverCommands:"):
            cur["declared"] = int(line.split(":", 1)[1])
        else:
            m = CMD_LINE.match(line)
            if m:
                cur["commands"][m.group(1)] = m.group(2)
                continue
            m = MODEL_LINE.match(line)
            if m:
                cur["models"][m.group(1)] = int(m.group(2))
    return out


def model_command_counts(graph):
    """{model name: commands on its own list}, from our own parse of the graph.

    A model's list is a command collection whose parent asset is the model.
    """
    out = {}
    for oid, v in graph.objects.items():
        c = pa._cls(v)
        if not c or "IDriverCommandAsset" not in c:
            continue
        if not c.startswith("Extron.Configuration.Core.Assets.AssetBase"):
            continue
        parent = pb.ref_id(v["members"].get("AssetBase+_parentAsset"))
        pv = graph.objects.get(parent) if parent is not None else None
        if isinstance(pv, dict) and pv.get("class", "").split(",")[0] \
                == "Extron.Configuration.Drivers.DriverModelAsset":
            out[graph.name_of(parent)] = len(graph.children(oid))
    return out


def loaded(entry):
    return entry is not None and entry["load"] and not entry["load"].startswith(("NULL", "threw"))


def deserialized(entry):
    return entry is not None and (entry["deserialize"] or "").startswith("OK")


def test_controls(seen, packages):
    print("\n[1] Extron's own sample packages load (the control)")
    for p in packages:
        e = seen.get(os.path.basename(p))
        check("%s loads" % os.path.basename(p), loaded(e), e and e["load"])
        check("%s deserializes" % os.path.basename(p), deserialized(e), e and e["deserialize"])


def test_ours_load(seen, packages):
    print("\n[2] every package we built loads and deserializes")
    for p in packages:
        e = seen.get(os.path.basename(p))
        check("%s loads" % os.path.basename(p), loaded(e), e and e["load"])
        check("%s deserializes" % os.path.basename(p), deserialized(e), e and e["deserialize"])


def test_ours_commands(seen, packages):
    print("\n[3] the loader sees exactly the commands our parser reads")
    for p in packages:
        leaf = os.path.basename(p)
        e = seen.get(leaf)
        if not loaded(e):
            check("%s has a command list to compare" % leaf, False, "did not load")
            continue
        graph = pa.CommandGraph(pb.PackageBuilder(os.path.join(_ROOT, p)))
        mine = graph.command_names()
        theirs = e["commands"]
        only_mine = sorted(set(mine) - set(theirs))
        only_theirs = sorted(set(theirs) - set(mine))
        check("%s: same %d script names" % (leaf, len(mine)),
              not only_mine and not only_theirs,
              "only ours %s, only the loader's %s" % (only_mine, only_theirs))
        renamed = sorted(sn for sn in set(mine) & set(theirs) if mine[sn] != theirs[sn])
        check("%s: same display names" % leaf, not renamed,
              ", ".join("%s %r vs %r" % (sn, mine[sn], theirs[sn]) for sn in renamed))
        check("%s: the loader declares %d" % (leaf, len(mine)), e["declared"] == len(mine),
              "declared %s" % e["declared"])
        # Each model has its own list into the pool (20028 gives the I12 a
        # shorter one), so compare model by model rather than assume equal.
        per_model = model_command_counts(graph)
        check("%s: each model carries what our parser reads %s" % (leaf, per_model),
              e["models"] == per_model, "the loader read %s" % e["models"])


def main():
    print("test_load_package.py - Extron's own loader on every package we build")
    why = unavailable()
    if why:
        print("\n  skip  %s: Extron's loader cannot run here. Nothing counted." % why)
        return 0
    controls = sample_packages()
    ours = our_packages()
    code, stdout, stderr = run_loader(controls + ours)
    seen = parse(stdout)
    if not seen:
        print("  FAIL Load-Package.ps1 reported nothing (exit %d)\n%s" % (code, stderr.strip()))
        return 1
    test_controls(seen, controls)
    test_ours_load(seen, ours)
    test_ours_commands(seen, ours)
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
