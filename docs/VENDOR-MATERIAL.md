# Vendor material

This repository publishes none of it.

The sample drivers, the `corpus/` library snapshot, documentation pages harvested from vendor sites, Global Configurator's catalogue data, and the packages this project built or mutated from Extron's belong to Extron, Crestron or third parties. They sit on the author's machine and are not tracked. Findings, tools and results describe the formats; they do not redistribute them.

## Getting your own copy

`vendor-files.manifest.tsv` lists every unpublished file with its SHA-256, size and the path the tools read it from. Put the files there and check them:

```bash
python tools/verify_vendor_files.py
```

## Running without it

A clone without the vendor files still runs every test that does not need them. Each suite skips what does, names the missing file, and reports the skips beside its passes and failures.

## What else stays out

Personal paths show as `<user>` and addresses come from the `192.168.100.0/24` example network.

The generated driver modules (`experiments/skeleton_i20/out/*.py`, `experiments/skeleton_p20/out/*.py`) are this project's own output and are published.
