#!/usr/bin/env python3
"""
generate.py - Q2 experiment: drive the Samsung QNxxLS03DAFXZA .pkp's embedded
ETHERNET script (which Extron never shipped as a ControlScript module)
through pkp2cs to a complete ControlScript .py, then validate it against
the embedded script itself with wire_table.py.

Writes only inside this experiment's own directory
(experiments/missing_ethernet/). Does not modify tools/.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)

import pkp2cs  # noqa: E402
import wire_table  # noqa: E402

PKP = os.path.join(
    ROOT, "samples", "Samsung QNxxLS03DAFXZA", "pkp", "smsg_10_6738_v1_0_0.pkp")

OUT_MODULE = os.path.join(HERE, "smsg_10_6738_ethernet.generated.py")
OUT_EMBEDDED = os.path.join(HERE, "smsg_10_6738_ethernet.embedded.py")
OUT_DIFF = os.path.join(HERE, "wire_diff.json")
OUT_TABLE_GEN = os.path.join(HERE, "wire_table.generated.json")
OUT_TABLE_EMB = os.path.join(HERE, "wire_table.embedded.json")


def main():
    jobs = pkp2cs.discover_jobs(PKP)
    print("discover_jobs(%r) -> %d jobs" % (os.path.relpath(PKP, ROOT), len(jobs)))
    for j in jobs:
        print("  job: %s  models=%d" % (j.script_file_name, len(j.models)))

    eth_jobs = [j for j in jobs if "ethernet" in j.script_file_name]
    ser_jobs = [j for j in jobs if "serial" in j.script_file_name]
    assert len(jobs) == 2, "expected exactly 2 jobs (serial + ethernet), got %d" % len(jobs)
    assert len(eth_jobs) == 1, "expected exactly 1 ethernet job"
    assert len(ser_jobs) == 1, "expected exactly 1 serial job"
    eth_job = eth_jobs[0]

    # Save the raw embedded ethernet script verbatim, for the wire_table oracle run.
    # newline="" on every write here: the embedded script already carries the
    # package's CRLF, and text-mode translation on Windows turned it into CRLF
    # CR LF - every regeneration silently corrupted the file (found 2026-09-23).
    with open(OUT_EMBEDDED, "w", encoding="utf-8", newline="") as f:
        f.write(eth_job.source)
    print("wrote embedded ethernet script -> %s (%d bytes)"
          % (OUT_EMBEDDED, len(eth_job.source)))

    result = pkp2cs.translate_job(eth_job)
    if result["source"] is None:
        print("FAILED: translate_job returned no source. Residuals:")
        for r in result["residuals"]:
            print("  - [%s] %s" % (r["reason"], r["detail"]))
        sys.exit(1)

    print("dialect detected: %s" % result["dialect"])
    with open(OUT_MODULE, "w", encoding="utf-8", newline="") as f:
        f.write(result["source"])
    print("wrote generated ControlScript module -> %s (%d bytes)"
          % (OUT_MODULE, len(result["source"])))

    print("\nresiduals (%d):" % len(result["residuals"]))
    for r in result["residuals"]:
        print("  - [%s] %s" % (r["reason"], r["detail"]))

    # Compile check
    import py_compile
    py_compile.compile(OUT_MODULE, doraise=True)
    print("\npy_compile: OK -- %s compiles cleanly" % OUT_MODULE)

    # wire_table validation: generated module vs embedded ethernet script
    with open(OUT_MODULE, encoding="utf-8") as f:
        gen_src = f.read()
    with open(OUT_EMBEDDED, encoding="utf-8") as f:
        emb_src = f.read()

    table_gen = wire_table.extract_table(gen_src, OUT_MODULE)
    table_emb = wire_table.extract_table(emb_src, OUT_EMBEDDED)

    with open(OUT_TABLE_GEN, "w", encoding="utf-8", newline="") as f:
        json.dump(table_gen.to_dict(), f, indent=2, default=str)
    with open(OUT_TABLE_EMB, "w", encoding="utf-8", newline="") as f:
        json.dump(table_emb.to_dict(), f, indent=2, default=str)

    diff = wire_table.diff_tables(table_emb, table_gen)
    with open(OUT_DIFF, "w", encoding="utf-8", newline="") as f:
        json.dump(diff, f, indent=2, default=str)

    print("\n=== SCORECARD ===")
    print("embedded (A) commands found: %d  stats=%s" % (len(table_emb.commands), table_emb.stats))
    print("generated (B) commands found: %d  stats=%s" % (len(table_gen.commands), table_gen.stats))
    print("shared commands: %d" % len(diff["shared"]))
    print("only in embedded (A), missing from generated: %s" % diff["only_in_a"])
    print("only in generated (B), not in embedded: %s" % diff["only_in_b"])
    print("shared commands WITH differences: %d" % len(diff["differences"]))
    for name, d in diff["differences"].items():
        print("  %s: %s" % (name, list(d.keys())))

    matching = len(diff["shared"]) - len(diff["differences"])
    print("\nMATCHING (shared, zero-diff) commands: %d / %d shared (%d total in embedded)"
          % (matching, len(diff["shared"]), len(table_emb.commands)))


if __name__ == "__main__":
    main()
