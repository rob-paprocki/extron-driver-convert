#!/usr/bin/env python3
"""
compare_semantic.py -- second, SEMANTIC comparison layer on top of
wire_table.diff_tables for experiment q1b.

wire_table.diff_tables() matches commands by exact Python identifier name.
That is meaningful when both sides happen to choose the same name (Power,
Volume: a real, tool-verified match) but understates the true correspondence
here, because the two translators group Crestron's ~60 atomic wire actions
into ControlScript commands along different lines (Extron's own shipped
script groups multiple JSON-RPC "method"s worth of button presses into one
enum-valued command, e.g. Keypad; the Crestron-derived module here mirrors
Crestron's OWN atomic granularity instead of copying Extron's grouping
choice -- see crestron2cs.py's module docstring for why).

This script establishes the ground truth for "how many match on wire
content" the honest way: group both sides' commands by the JSON-RPC
`method` they send, then diff EVERY (method, params-key-set, value-domain)
tuple that is shared. It never looks at command *names* to decide a match --
only at what is actually on the wire.
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from wire_table import extract_table  # noqa: E402

_METHOD_RE = re.compile(r"'method':\s*([A-Za-z0-9_]+)")


def method_of(canonical: str):
    m = _METHOD_RE.search(canonical)
    return m.group(1) if m else None


def _params_block(canonical: str):
    # The '{}' placeholder for a resolved-but-opaque-to-this-script slot
    # (e.g. AccessToken) is itself a brace pair NESTED inside 'params':
    # {...} -- mask it out first so a naive '[^}]*' capture of the outer
    # object doesn't stop at that inner closing brace.
    masked = canonical.replace("{}", "\x00SLOT\x00")
    m = re.search(r"'params':\s*\{([^}]*)\}", masked)
    return m.group(1).replace("\x00SLOT\x00", "{}") if m else None


def param_keys_of(canonical: str):
    block = _params_block(canonical)
    if block is None:
        return frozenset()
    keys = re.findall(r"'([A-Za-z0-9_]+)':", block)
    return frozenset(k for k in keys if k != "AccessToken")


def literal_param_values_of(canonical: str):
    """Every literal (non-slot, i.e. not rendered as the placeholder '{}')
    value bound to a non-AccessToken params key -- this is how a FIRE
    command (e.g. Crestron's Keypress5, or Extron's Keypad with an
    already-chosen enum value) bakes a single wire value directly into its
    own template, as opposed to a value_map covering many values under one
    command."""
    block = _params_block(canonical)
    if block is None:
        return frozenset()
    pairs = re.findall(r"'([A-Za-z0-9_]+)':\s*([^,{}]+)", block)
    out = set()
    for key, val in pairs:
        if key == "AccessToken":
            continue
        val = val.strip().rstrip(",").strip("'\"")
        if val and val != "{}":
            out.add(val)
    return frozenset(out)


def collect(table, side):
    """method -> list of (command_name, direction, canonical, param_keys, value_map)"""
    out = {}
    for name, rec in table.commands.items():
        for direction, templates in (("set", rec.set_templates), ("update", rec.update_templates)):
            for t in templates:
                method = method_of(t.canonical)
                if method is None:
                    continue
                out.setdefault(method, []).append(
                    (name, direction, t.canonical, param_keys_of(t.canonical), rec.value_map, side)
                )
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    gen_src = open(os.path.join(here, "out", "generated_controlscript.py")).read()
    ext_src = open(os.path.join(here, "out", "extron_ethernet_source.py")).read()
    gen = extract_table(gen_src, "generated.py")
    ext = extract_table(ext_src, "extron_ethernet.py")

    gen_by_method = collect(gen, "crestron-derived")
    ext_by_method = collect(ext, "extron-shipped")

    all_methods = sorted(set(gen_by_method) | set(ext_by_method))

    report = {"methods": {}, "summary": {}}
    only_gen = only_ext = shared = 0
    param_mismatches = []
    value_domain_notes = []

    for method in all_methods:
        g = gen_by_method.get(method, [])
        e = ext_by_method.get(method, [])
        entry = {
            "crestron_derived": [{"command": n, "direction": d, "canonical": c} for n, d, c, *_ in g],
            "extron_shipped": [{"command": n, "direction": d, "canonical": c} for n, d, c, *_ in e],
        }
        if g and e:
            shared += 1
            g_params = {pk for *_x, pk, _vm, _s in g}
            e_params = {pk for *_x, pk, _vm, _s in e}
            if g_params != e_params:
                param_mismatches.append({"method": method, "crestron_derived_params": [sorted(p) for p in g_params],
                                          "extron_shipped_params": [sorted(p) for p in e_params]})
            # compare VALUE-SIDE (wire) domains, ignoring each vendor's own
            # ControlScript-facing enum key spelling: union of (a) every
            # value_map's wire-side values and (b) every literal value a
            # fire-style command bakes directly into its own template.
            g_wire_values = set()
            for n, d, c, pk, vm, _s in g:
                if vm:
                    g_wire_values |= set(vm.values())
                g_wire_values |= literal_param_values_of(c)
            e_wire_values = set()
            for n, d, c, pk, vm, _s in e:
                if vm:
                    e_wire_values |= set(vm.values())
                e_wire_values |= literal_param_values_of(c)
            if g_wire_values or e_wire_values:
                value_domain_notes.append({
                    "method": method,
                    "crestron_derived_wire_values": sorted(g_wire_values),
                    "extron_shipped_wire_values": sorted(e_wire_values),
                    "wire_values_match": g_wire_values == e_wire_values,
                })
        elif g:
            only_gen += 1
        else:
            only_ext += 1
        report["methods"][method] = entry

    report["summary"] = {
        "total_distinct_methods": len(all_methods),
        "methods_only_in_crestron_derived": only_gen,
        "methods_only_in_extron_shipped": only_ext,
        "methods_in_both": shared,
        "param_key_set_mismatches_among_shared": param_mismatches,
        "wire_value_domain_comparison_among_shared": value_domain_notes,
    }
    print(json.dumps(report["summary"], indent=2))
    with open(os.path.join(here, "out", "semantic_comparison.json"), "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
