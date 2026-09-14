#!/usr/bin/env python3
"""
make_project.py - assemble a deployable ControlScript project for the loopback console.

Writes build/i20-loopback/ beside this file (git-ignored):

    project.json                                the project descriptor
    src/main.py, src/console_core.py            the console, from this folder
    src/onebynd_camera_IV_CAM_I20_v1_0_0_0.py   the module under test, from
                                                experiments/skeleton_i20/out/
    layout/ rfile/ ir/ sound/                   empty; the descriptor names them

Open build/i20-loopback/ in the ControlScript Deployment Utility, certify it if
your account requires that, and deploy. The device entry follows the snippet the
ControlScript VS Code extension ships for each model. The network block is a
first guess for a PC on the processor's AV LAN; the Deployment Utility is the
authority on it, so change it there if it objects.

Run:
    python3 experiments/loopback/controlscript/make_project.py --address 192.168.254.1
    python3 experiments/loopback/controlscript/make_project.py --model "IPCP Pro 360Q xi" --address 192.168.254.1
"""

import argparse
import json
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
MODULE = os.path.join(_ROOT, "experiments", "skeleton_i20", "out",
                      "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")

# Part numbers from the extension's snippets/device-snippets.json.
MODELS = {
    "IPCP Pro 360": "60-1432-01",
    "IPCP Pro 360Q xi": "60-1916-01",
    "IPCP Pro 360MQ xi": "60-1920-01",
}


def descriptor(model, address, network, name):
    return {
        "system": {
            "name": name,
            "code_folder_path": "src",
            "code_entry_file": "main.py",
            "layout_folder_path": "layout",
            "sound_folder_path": "sound",
            "rfile_folder_path": "rfile",
            "irfile_folder_path": "ir",
            "system_id": name,
            "author": {"name": "Your Name", "email": "user@yourdomain.com"},
            "version": "0.0.1",
            "primary_device_alias": "Processor",
        },
        "devices": [{
            "name": model,
            "part_number": MODELS[model],
            "alias": "Processor",
            "network": {
                "host_network_type": network,
                "interfaces": [{"address": address, "type": network}],
            },
        }],
        "schemaVersion": "1.0.0",
    }


def build(model, address, network="AVLAN", name="i20-loopback", out_root=None):
    root = os.path.join(out_root or os.path.join(_HERE, "build"), name)
    if os.path.isdir(root):
        shutil.rmtree(root)
    for folder in ("src", "layout", "rfile", "ir", "sound"):
        os.makedirs(os.path.join(root, folder))
    with open(os.path.join(root, "project.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(descriptor(model, address, network, name), fh, indent=4)
        fh.write("\n")
    for source in (os.path.join(_HERE, "main.py"), os.path.join(_HERE, "console_core.py"), MODULE):
        shutil.copyfile(source, os.path.join(root, "src", os.path.basename(source)))
    return root


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--address", required=True, help="the processor's address")
    ap.add_argument("--model", choices=sorted(MODELS), default="IPCP Pro 360")
    ap.add_argument("--network", choices=("LAN", "AVLAN"), default="AVLAN",
                    help="which processor port this PC reaches it through")
    ap.add_argument("--name", default="i20-loopback")
    args = ap.parse_args(argv)
    root = build(args.model, args.address, args.network, args.name)
    print("wrote %s" % os.path.relpath(root, _ROOT).replace(os.sep, "/"))
    for dirpath, _, files in sorted(os.walk(root)):
        for f in sorted(files):
            print("  %s" % os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
