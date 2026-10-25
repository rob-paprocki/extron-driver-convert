#!/usr/bin/env python3
# convert.py - a thin, honest front door to the per-format tools that already
# exist in this repo. Each verb is a wrapper around one of the real tools
# (pkp_dump.py, pkp_build.py, pkp_validate.py, pkp2cs.py, pkg_dump.py,
# pkg_patch.py) plus, for `verify`, experiments/gcp_harness/Load-Package.ps1.
# No conversion semantics live here; this file is a discoverable CLI over
# tools that already carry them.
#
# Why `validate` and `verify` are separate verbs: `validate` runs the project's
# Python reimplementation of Extron's hash check (Finding 16). `verify` runs
# Extron's own deserializer. A package can pass validate and still fail
# `verify` because the Python model shares the author's assumptions
# (Finding 18 - a cloned subtree with freshly-minted negative object ids
# round-trips, validates, passes 39 tests, and still crashes BinaryFormatter).
# Prefer `verify` for real acceptance.
#
# Standard library only.

import argparse
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# convert.py is expected to live at <repo>/tools/convert.py. If this file is
# relocated or symlinked elsewhere, LOAD_PACKAGE_PS1 will not resolve and
# `verify --load-package` reports it. No upward search; the layout is pinned.
REPO = os.path.dirname(HERE)

PKP_DUMP = os.path.join(HERE, "pkp_dump.py")
PKP_BUILD = os.path.join(HERE, "pkp_build.py")
PKP_VALIDATE = os.path.join(HERE, "pkp_validate.py")
PKP2CS = os.path.join(HERE, "pkp2cs.py")
PKG_DUMP = os.path.join(HERE, "pkg_dump.py")
PKG_PATCH = os.path.join(HERE, "pkg_patch.py")
LOAD_PACKAGE_PS1 = os.path.join(REPO, "experiments", "gcp_harness", "Load-Package.ps1")

# verb, direction, status, gating finding/roadmap note
DIRECTIONS = [
    ("pkp2cs",
     "Extron .pkp  ->  Extron ControlScript (.py)",
     "DONE, measured",
     "pkp2cs.py; wire-table parity measured in experiments/"),
    ("cs2pkp",
     "ControlScript (.py)  ->  Extron .pkp",
     "DONE via donor transplant; from-scratch synthesis partial",
     "Finding 12 / Finding 18; ROADMAP R28 for from-scratch graph"),
    ("pkg2cs",
     "Crestron .pkg  ->  Extron ControlScript (.py)",
     "pkg_dump measured; .pkg -> ControlScript emit is a manual step",
     "No single-command .pkg->CS translator ships yet"),
    ("pkp2pkg",
     "Extron .pkp  ->  Crestron .pkg (resource-swap patch only)",
     "patch-only; schema mismatch between formats is a manual step",
     "STATUS.md D2 - Crestron licence question; Finding 04"),
]


def _run(argv):
    """Run a child Python tool and return its exit code unmodified."""
    return subprocess.run([sys.executable] + argv).returncode


def _rel(path, base=None):
    """Repo-relative, forward-slashed path for printing. Falls back to the
    absolute path (forward-slashed) if the two live on different Windows
    drives (os.path.relpath raises ValueError in that case)."""
    base = base or os.getcwd()
    try:
        return os.path.relpath(path, base).replace("\\", "/")
    except ValueError:
        return os.path.abspath(path).replace("\\", "/")


def _list_directions():
    verb_w = max(len(v) for v, _, _, _ in DIRECTIONS)
    dir_w = max(len(d) for _, d, _, _ in DIRECTIONS)
    stat_w = max(len(s) for _, _, s, _ in DIRECTIONS)
    header = ("verb".ljust(verb_w) + "  " + "direction".ljust(dir_w) +
              "  " + "status".ljust(stat_w) + "  " + "gating")
    print(header)
    print("-" * len(header))
    for v, d, s, g in DIRECTIONS:
        print(v.ljust(verb_w) + "  " + d.ljust(dir_w) + "  " +
              s.ljust(stat_w) + "  " + g)


def _powershell_32bit():
    """Resolve the 32-bit powershell.exe path. On a healthy Windows install
    this is C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe;
    the AssemblyResolve shim in Load-Package.ps1 needs the 32-bit host to
    load Extron's x86 Configuration DLLs. Returns None if not found."""
    sysroot = os.environ.get("SystemRoot", r"C:\Windows")
    candidate = os.path.join(sysroot, "SysWOW64", "WindowsPowerShell",
                             "v1.0", "powershell.exe")
    if os.path.isfile(candidate):
        return candidate
    # Fallback: whatever PATH gives us. Not 32-bit on an ARM64/Nano SKU,
    # but better than a cryptic WinError 2.
    return shutil.which("powershell.exe")


def _printable_ps_command(file_path):
    """Render the exact PowerShell line a user should paste. Uses
    $env:SystemRoot (PowerShell syntax, not cmd's %SystemRoot%) and double-
    quotes both paths so spaces survive. Prints repo-relative paths when
    they share a drive with the cwd; absolute paths otherwise."""
    ps1 = _rel(LOAD_PACKAGE_PS1)
    pkp = _rel(file_path)
    return ('& "$env:SystemRoot\\SysWOW64\\WindowsPowerShell\\v1.0'
            '\\powershell.exe" -ExecutionPolicy Bypass '
            '-File "%s" "%s"' % (ps1, pkp))


# ---- verbs --------------------------------------------------------------

def cmd_dump(args):
    """Dispatch to pkp_dump.py or pkg_dump.py by extension. Forwards -o
    and (for pkp inputs) --resolve so the single front door exposes both
    tools' main options."""
    ext = os.path.splitext(args.input)[1].lower()
    if ext == ".pkp":
        tool = PKP_DUMP
        argv = [tool]
        if args.resolve:
            argv.append("--resolve")
    elif ext == ".pkg":
        tool = PKG_DUMP
        argv = [tool]
    else:
        print("convert.py dump: %s: unknown extension %r (expected .pkp or .pkg)" %
              (args.input, ext), file=sys.stderr)
        return 2
    if args.output:
        argv += ["-o", args.output]
    argv += [args.input]
    return _run(argv)


def cmd_validate(args):
    """Pass through to pkp_validate.py. Always print the gate note to
    stderr afterward, success or failure: a failing validate still benefits
    from being pointed at verify."""
    rc = _run([PKP_VALIDATE] + args.files)
    print("note: valid != loadable (Finding 18). "
          "Run `convert.py verify --load-package` for the full gate.",
          file=sys.stderr)
    return rc


def cmd_verify(args):
    """Run the Python validator; if --load-package and we are on Windows,
    also run Load-Package.ps1 under 32-bit PowerShell. Otherwise print the
    exact PowerShell command for the user to run on a Windows box."""
    if not os.path.isfile(args.file):
        print("convert.py verify: no such file: %s" % args.file, file=sys.stderr)
        return 2
    rc = _run([PKP_VALIDATE, args.file])
    if rc != 0:
        return rc
    if not args.load_package:
        print("")
        print("note: validator passed. For Extron's own deserializer check, run on "
              "Windows (32-bit PowerShell, Extron Configuration DLLs installed):")
        print("  " + _printable_ps_command(args.file))
        print("  (Finding 18: valid != loadable; only Extron's own deserializer")
        print("  catches negative-object-id and signature mismatches.)")
        return 0
    if platform.system() != "Windows":
        print("convert.py verify --load-package: can only run on Windows. On a "
              "Windows workstation with Extron GC installed, run:", file=sys.stderr)
        print("  " + _printable_ps_command(args.file), file=sys.stderr)
        return 2
    if not os.path.isfile(LOAD_PACKAGE_PS1):
        print("convert.py verify: Load-Package.ps1 not found at %s" %
              LOAD_PACKAGE_PS1, file=sys.stderr)
        print("  (expected layout: <repo>/experiments/gcp_harness/Load-Package.ps1)",
              file=sys.stderr)
        return 2
    ps = _powershell_32bit()
    if ps is None:
        print("convert.py verify: 32-bit powershell.exe not found. Expected at "
              "%%SystemRoot%%\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe.",
              file=sys.stderr)
        return 2
    return subprocess.run(
        [ps, "-ExecutionPolicy", "Bypass", "-File", LOAD_PACKAGE_PS1, args.file]
    ).returncode


def cmd_pkp2cs(args):
    argv = [PKP2CS]
    if args.output:
        argv += ["-o", args.output]
    argv += [args.input]
    return _run(argv)


def cmd_cs2pkp(args):
    """Donor-transplant: pkp_build.py refuses the donor if it does not
    round-trip byte-for-byte first (RoundTripError at open), so this verb
    inherits that safety property. Script resource KEYs come from
    `convert.py dump <donor>`; a wrong KEY silently leaves the donor's
    script in place."""
    if not args.script and not args.set_string:
        print("convert.py cs2pkp: pass at least one --script KEY=FILE or "
              "--set-string ID=VAL. Discover KEY/ID from `convert.py dump "
              "<donor>`.", file=sys.stderr)
        return 2
    argv = [PKP_BUILD, args.donor]
    for pair in args.script or []:
        argv += ["--replace-script", pair]
    for pair in args.set_string or []:
        argv += ["--set-string", pair]
    argv += ["-o", args.output]
    return _run(argv)


def cmd_pkg2cs(args):
    """.pkg -> ControlScript: no single invoked translator for this
    direction yet. Extract the driver JSON via pkg_dump.py and stop with
    the exact next step for the user. Honest about where the automation
    ends; writes JSON to a user-visible path (never a leaked temp file)."""
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        json_path = os.path.join(args.output,
            os.path.splitext(os.path.basename(args.input))[0] + ".json")
    else:
        # Default to CWD, not a temp path. Visible, named, and the user
        # knows where to find it.
        json_path = os.path.splitext(os.path.basename(args.input))[0] + ".json"
    rc = _run([PKG_DUMP, "-o", json_path, args.input])
    if rc != 0:
        return rc
    print("")
    print("convert.py pkg2cs: driver JSON extracted to %s" % _rel(json_path))
    print("No single-command .pkg -> ControlScript translator ships yet.")
    print("The ControlScript dialect patterns live in tools/pkp2cs.py; the")
    print("translator pieces for Crestron-flavoured driver JSON are under")
    print("experiments/. Finishing a module from this JSON is a manual step.")
    return 0


def cmd_pkp2pkg(args):
    """Patch-only Extron -> Crestron: refuses to chain the raw Extron
    object graph into pkg_patch.py (different schemas - that would hand
    the user a broken .pkg with a confusing error from the wrong layer).
    Dumps the Extron graph for inspection and prints the pkg_patch.py
    command the user would run once they have a conforming Crestron
    driver JSON. Gate: STATUS.md D2."""
    print("convert.py pkp2pkg: resource-swap only. Full Extron -> Crestron")
    print("emit is gated by the Crestron licence question (STATUS.md D2).")
    print("The Extron object graph and the Crestron driver JSON do not share")
    print("a schema, so this verb will not auto-chain pkp_dump into pkg_patch.")
    print("")
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".",
                    exist_ok=True)
        extron_json = os.path.splitext(args.output)[0] + ".extron.json"
    else:
        extron_json = (os.path.splitext(os.path.basename(args.input))[0]
                       + ".extron.json")
    rc = _run([PKP_DUMP, "-o", extron_json, args.input])
    if rc != 0:
        return rc
    print("")
    print("Extron object graph dumped to: %s" % _rel(extron_json))
    print("")
    print("Next step (manual): convert that graph to a Crestron driver JSON")
    print("that matches your donor's schema, then run pkg_patch.py directly:")
    print("")
    print("  %s tools/pkg_patch.py %s \\" % (
        _rel(sys.executable),
        _rel(args.donor),
    ))
    print("    --json-file <YOUR CRESTRON JSON> \\")
    print("    -o %s" % _rel(args.output) if args.output else "    -o <OUT.pkg>")
    print("")
    print("See `tools/pkg_patch.py --help` for the strip-signature option.")
    return 0


# ---- argparse plumbing --------------------------------------------------

def build_parser():
    description = (
        "A single front door to the per-format tools in this repo. Each verb "
        "wraps an existing tool; this file adds no new conversion semantics.")
    epilog = (
        "VALIDATE vs VERIFY (Finding 18): `validate` uses this project's "
        "Python model of the .pkp format. `verify` runs Extron's own "
        "deserializer. A package can validate and still fail GC load. Prefer "
        "`verify --load-package` on a Windows GC workstation for real "
        "acceptance.")
    p = argparse.ArgumentParser(
        prog="convert.py",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="verb")

    s = sub.add_parser("directions",
                       help="print the matrix of conversion directions and their status")
    s.set_defaults(func=lambda a: (_list_directions() or 0))

    s = sub.add_parser("dump",
                       help="dump a .pkp or .pkg to JSON (dispatches by extension)")
    s.add_argument("input")
    s.add_argument("-o", "--output", help="write JSON to file instead of stdout")
    s.add_argument("-r", "--resolve", action="store_true",
                   help="(.pkp only) resolve MemberReference / ClassWithId back-references")
    s.set_defaults(func=cmd_dump)

    s = sub.add_parser(
        "validate",
        help="validate one or more .pkp packages (pkp_validate.py)",
        description="Local Python check (Finding 16's reimplementation of "
                    "Extron's hash validator). See `verify` for Extron's "
                    "own deserializer.",
    )
    s.add_argument("files", nargs="+")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser(
        "verify",
        help="validate, and (with --load-package on Windows) run Load-Package.ps1",
        description="Validate first, then invoke Extron's deserializer via "
                    "experiments/gcp_harness/Load-Package.ps1 under 32-bit "
                    "PowerShell. Off Windows, or without --load-package, "
                    "prints the exact command for a user to run manually.",
    )
    s.add_argument("file")
    s.add_argument("--load-package", action="store_true",
                   help="on Windows, also invoke experiments/gcp_harness/Load-Package.ps1 "
                        "under 32-bit PowerShell (Finding 18 gate)")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("pkp2cs",
                       help="translate Extron .pkp -> ControlScript (pkp2cs.py)")
    s.add_argument("input")
    s.add_argument("-o", "--output", help="output directory for the generated module(s)")
    s.set_defaults(func=cmd_pkp2cs)

    s = sub.add_parser(
        "cs2pkp",
        help="transplant ControlScript into a donor .pkp (pkp_build.py)",
        description="Donor-transplant. The donor must round-trip byte-for-byte "
                    "(pkp_build.py enforces this in PackageBuilder.__init__; "
                    "failure raises RoundTripError before any edit is allowed). "
                    "KEYs are the donor's embedded script resource names; "
                    "discover them with `convert.py dump <donor>`. IDs are "
                    "NRBF object ids; reusing an id with a flipped sign fails "
                    "GC load (Finding 18) - verify with `convert.py verify "
                    "--load-package` before trusting the output.",
    )
    s.add_argument("donor", help="a real .pkp to transplant into (round-trip-verified first)")
    s.add_argument("--script", action="append", metavar="KEY=FILE",
                   help="replace an embedded script by key (repeatable)")
    s.add_argument("--set-string", action="append", metavar="ID=VAL",
                   help="replace a string record by object id (repeatable)")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_cs2pkp)

    s = sub.add_parser(
        "pkg2cs",
        help="Crestron .pkg -> JSON then (manual) ControlScript",
        description="Dumps the Crestron driver JSON via pkg_dump.py. The "
                    "finish from JSON to a ControlScript module is a manual "
                    "step - the dialect patterns are in pkp2cs.py and the "
                    "Crestron-specific translator pieces are under experiments/.",
    )
    s.add_argument("input")
    s.add_argument("-o", "--output", help="output directory for the extracted driver JSON")
    s.set_defaults(func=cmd_pkg2cs)

    s = sub.add_parser(
        "pkp2pkg",
        help="patch-only Extron .pkp -> Crestron .pkg (dump + print pkg_patch command)",
        description="Dumps the Extron object graph for inspection and prints "
                    "the exact pkg_patch.py command to run once a conforming "
                    "Crestron driver JSON is produced. Does NOT chain the raw "
                    "Extron graph into pkg_patch.py - the schemas differ and "
                    "doing so would produce a broken artifact. STATUS.md D2 is "
                    "the licence gate behind a full emit.",
    )
    s.add_argument("input", help="source Extron .pkp (its graph is dumped to JSON)")
    s.add_argument("--donor", required=True,
                   help="Crestron .pkg whose resource JSON gets swapped (passed through to pkg_patch.py)")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_pkp2pkg)

    return p


def main():
    p = build_parser()
    args = p.parse_args()
    if not getattr(args, "verb", None):
        # First-run surface: show the directions matrix, then point at --help.
        _list_directions()
        print("")
        print("Run `convert.py <verb> --help` for details, or "
              "`convert.py --help` for the verb list.")
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
