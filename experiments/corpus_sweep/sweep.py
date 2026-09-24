#!/usr/bin/env python3
"""
experiments/corpus_sweep/sweep.py - ROADMAP R15: a corpus-wide sweep of the
untested paths, over every .pkp in corpus/extron-driver3/, no sampling.

Six independent measurements, each described in detail in SWEEP.md:

  1. Round-trip every package through tools/pkp_build.PackageBuilder's
     byte-for-byte gate; bucket failures by (exception type, message class).
  2. Does any package have no "Manifest" child asset (pkp_validate.py gap 4)?
  3. Emulated pre-writes (or reads) embedded inside a larger expression,
     rather than sitting as a standalone statement (the shape
     tools/pkp2cs.py's gc-dual-status-emulated-prewrite-dropped rule does
     not reach - see its own comments around the ReadMultiviewString case).
  4. AST-scan every embedded script for bare names used (Load context) that
     are neither bound anywhere in the script, imported, nor a builtin -
     candidate runtime-injected globals beyond ExtronTime (finding 13 sec.5).
  5. The newest Python syntax feature each embedded script's AST exhibits,
     for the "is this Python-3.5-safe" question - plus, where present, the
     script's own self-declared `minimumVersion` tuple.
  6. Every `configs[...]` key read inside `__init__` (and, more broadly, any
     "model"-shaped configs key or self attribute anywhere in the script, or
     an __init__ parameter beyond (self, configs)) - ROADMAP R22's question:
     is a .pkp script ever told which model it runs as?

Method notes common to all six
-------------------------------
* Every package in corpus/extron-driver3/*.pkp is visited; nothing is
  sampled. A package that cannot even be parsed is counted and reported,
  never silently skipped.
* Item 1 uses tools/pkp_build.PackageBuilder, which performs the real
  round-trip gate in its constructor (parse -> rebuild -> byte compare).
* Items 2-6 use a SEPARATE, lighter parse (pkp_validate.load_graph, backed
  by pkp_dump.PkpParser) so that a round-trip failure in item 1 - a
  question about the NRBF *writer* - does not also blind items 2-6, which
  are questions about the object graph and the embedded scripts and need
  only a *reader*.
* Embedded scripts are extracted with tools/pkp_build's own
  PackageBuilder.scripts() logic (called unbound against a plain object
  holding the lightweight parse's `objects` dict, so it works even for a
  donor that fails item 1's round-trip). This is read-only use of tools/;
  nothing here mutates or reserializes a package.
* Items 3-6 are AST scans (Python's own `ast` module) over each script's
  source text. A script that does not even parse under Python 3's grammar
  is counted and reported (see 'unparseable_py3' in the results), never
  silently dropped from the denominator.
* Concurrent-edit safety: tools/pkp2cs.py and tools/pkp_validate.py were
  being edited by other agents while this ran. Set
  CORPUS_SWEEP_SNAPSHOT_DIR to a directory holding fixed copies of those two
  files (and only those two - pkp_dump.py, pkp_build.py and nrbf_write.py
  are read from the live tree, since nothing else was touching them) to pin
  the version measured. SWEEP.md records which commit was snapshotted for
  the numbers it reports.

Usage
-----
    python3 experiments/corpus_sweep/sweep.py [--corpus DIR] [--out FILE]
                                               [--limit N] [--checkpoint-every N]

Standard library only.
"""

import argparse
import ast
import io
import json
import os
import re
import sys
import time
import tokenize
import traceback
import types

# -- module resolution -------------------------------------------------
#
# tools/wire_table.py, tools/pkp2cs.py and tools/pkp_validate.py were each
# being edited by another agent in this worktree while R15 ran.
# CORPUS_SWEEP_SNAPSHOT_DIR, if set, is searched BEFORE the live tools/ dir,
# so pkp2cs.py and pkp_validate.py resolve to pinned copies while pkp_dump.py,
# pkp_build.py and nrbf_write.py (untouched by any concurrent edit) still
# resolve from the live tree.

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
_NRBF_WRITEBACK = os.path.join(_ROOT, "experiments", "nrbf_writeback")
_SNAP = os.environ.get("CORPUS_SWEEP_SNAPSHOT_DIR")

_prefix = [_TOOLS, _NRBF_WRITEBACK]
if _SNAP:
    _prefix.insert(0, _SNAP)
for _p in reversed(_prefix):
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd            # noqa: E402
import pkp_build as pb           # noqa: E402
import pkp_validate as pv        # noqa: E402
import pkp2cs as p2c             # noqa: E402
import nrbf_write as nw          # noqa: E402  (imported for parity; pb uses it internally)

DEFAULT_CORPUS = os.path.join(_ROOT, "corpus", "extron-driver3")

_DIGITS = re.compile(r"\d+")


# =========================================================================
# item 1: round-trip
# =========================================================================

def _message_class(msg):
    """Normalize an error message into a bucketable class: strip a leading
    '<path>.pkp: ' prefix (which varies per package) and collapse digit runs
    (byte offsets, lengths) so 'first difference at byte 4821' and 'at byte
    19' land in the same bucket."""
    msg = re.sub(r"^\S+\.pkp:\s*", "", msg)
    msg = _DIGITS.sub("N", msg)
    return msg.strip()[:220]


def check_round_trip(path):
    """(ok, exc_type_name, message_class). exc_type_name/message_class are
    None on success."""
    try:
        pb.PackageBuilder(path)
        return True, None, None
    except pb.RoundTripError as e:
        return False, "RoundTripError", _message_class(str(e))
    except Exception as e:
        return False, type(e).__name__, _message_class(str(e))


# =========================================================================
# items 2-6 shared plumbing: a lightweight read-only parse, script extraction
# =========================================================================

def load_light(path):
    """(objects, root) via pkp_validate's own reader. Raises pv.PackageError
    on anything unreadable - never silently returns a partial graph."""
    return pv.load_graph(path)


def check_gap4(objects, root):
    """(no_manifest_child, warnings) - True when pkp_validate's own gap-4
    warning ('no manifest found: ...') fired for this package."""
    result = pv.validate_graph(objects, root)
    no_manifest = any("no manifest found" in w for w in result.warnings)
    return no_manifest, list(result.warnings)


def extract_scripts(objects):
    """Every embedded .py script, via pkp_build.PackageBuilder.scripts()
    called unbound against a stand-in holding just `.objects` - the method
    only touches self.objects, so this works on a graph read without going
    through (or requiring) the round-trip gate."""
    fake = types.SimpleNamespace(objects=objects)
    return pb.PackageBuilder.scripts(fake)


# =========================================================================
# AST plumbing shared by items 3, 4, 5, 6
# =========================================================================

def _add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._sweep_parent = node
    tree._sweep_parent = None


def _enclosing_function_node(node):
    n = getattr(node, "_sweep_parent", None)
    while n is not None:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return n
        n = getattr(n, "_sweep_parent", None)
    return None


def _enclosing_function_name(node):
    fn = _enclosing_function_node(node)
    return fn.name if fn is not None else "<module>"


def _enclosing_class_name(node):
    n = getattr(node, "_sweep_parent", None)
    while n is not None:
        if isinstance(n, ast.ClassDef):
            return n.name
        n = getattr(n, "_sweep_parent", None)
    return None


# =========================================================================
# item 3: Emulated pre-writes embedded inside a larger expression
# =========================================================================

# The three names pkp2cs.py's generic Write<X>(..., 'Emulated') rule itself
# excludes, because they are the generic dual-status accessors (handled by
# their own separate rules), not per-command wrappers - see the long comment
# above gc-dual-status-emulated-prewrite-dropped in tools/pkp2cs.py.
_GENERIC_ACCESSORS = {"WriteStatus", "WriteStatusHelper", "WriteDeviceResponseStatus",
                       "ReadStatusHelper"}


def find_embedded_emulated_calls(tree):
    """Calls carrying GC's literal 'Emulated' status-context argument (the
    same test pkp2cs.py's own _has_emulated_context makes) to a per-command
    Write<X>/Read<X> wrapper, that are NOT the entire value of a standalone
    expression-statement - i.e. embedded inside a larger expression: assigned
    ('mode = self.ReadMultiviewString(qualifier, "Emulated")', the exact
    shape named in pkp2cs.py's own R37 comment), passed as an argument,
    tested in a condition, etc. pkp2cs.py's generic rule only strips the
    standalone-statement shape; this measures what is left over."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        attr = p2c._call_attr(node)
        if not attr or attr in _GENERIC_ACCESSORS:
            continue
        if not (attr.startswith("Write") or attr.startswith("Read")):
            continue
        if not p2c._has_emulated_context(node):
            continue
        parent = getattr(node, "_sweep_parent", None)
        standalone = isinstance(parent, ast.Expr) and parent.value is node
        if standalone:
            continue
        hits.append({
            "attr": attr,
            "method": _enclosing_function_name(node),
            "parent_kind": type(parent).__name__ if parent is not None else "<none>",
        })
    return hits


# =========================================================================
# item 4: runtime-injected globals beyond ExtronTime
# =========================================================================

_IMPLICIT_MODULE_GLOBALS = {
    "__name__", "__file__", "__doc__", "__package__", "__spec__",
    "__loader__", "__builtins__", "__class__", "__annotations__",
    "__dict__", "__module__", "__qualname__",
}


def _collect_bound_names(tree):
    """A FLAT, whole-script set of every name bound anywhere - deliberately
    not a per-scope (LEGB) analysis. See SWEEP.md 'Method' for why: a flat
    set can only ever UNDER-report (a same-named local bound in some other
    method could mask a genuine bare-global use elsewhere), never invent a
    false positive out of ordinary lexical scoping. That is the conservative
    direction for a claim of the shape 'the runtime injects this name'.

    Returns (bound_names, uses_star_import). A star import can bind anything,
    so a script using one is excluded from item 4 entirely rather than
    guessed at.
    """
    bound = set()
    uses_star_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bound.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    uses_star_import = True
                else:
                    bound.add(alias.asname or alias.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
    return bound, uses_star_import


def find_bare_globals(tree):
    """List of candidate runtime-injected global names (with duplicates, one
    per use, so a caller can count occurrences), or None if the script uses a
    star import and is therefore excluded (see _collect_bound_names)."""
    bound, uses_star_import = _collect_bound_names(tree)
    if uses_star_import:
        return None
    import builtins as _b
    excluded = set(dir(_b)) | {"self", "cls"} | _IMPLICIT_MODULE_GLOBALS
    return [n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
            and n.id not in bound and n.id not in excluded]


# =========================================================================
# item 5: newest Python syntax feature per script
# =========================================================================

_FEATURE_MIN_VERSION = {
    "f-string": (3, 6),
    "variable-annotation": (3, 6),
    "underscore-numeric-literal": (3, 6),
    "async-comprehension": (3, 6),
    "async-generator": (3, 6),
    "walrus": (3, 8),
    "positional-only-params": (3, 8),
    "match-statement": (3, 10),
    "except-star": (3, 11),
    "generic-type-params": (3, 12),
}


def find_python_features(tree, source):
    """Set of feature names (keys of _FEATURE_MIN_VERSION) this script's AST
    exhibits. Absence of a marker is evidence of absence for THESE specific
    syntax shapes only - not a general proof of Python-3.5 compatibility
    (a script could still use a post-3.5 stdlib name or builtin undetectable
    by node type alone; see SWEEP.md)."""
    features = set()
    for node in ast.walk(tree):
        t = type(node).__name__
        if t == "JoinedStr":
            features.add("f-string")
        elif t == "NamedExpr":
            features.add("walrus")
        elif t == "AnnAssign":
            features.add("variable-annotation")
        elif t == "Match":
            features.add("match-statement")
        elif t == "TryStar":
            features.add("except-star")
        elif t in ("FunctionDef", "AsyncFunctionDef"):
            if getattr(node.args, "posonlyargs", None):
                features.add("positional-only-params")
            if getattr(node, "type_params", None):
                features.add("generic-type-params")
        elif t == "ClassDef" and getattr(node, "type_params", None):
            features.add("generic-type-params")
        elif t == "comprehension" and getattr(node, "is_async", 0):
            features.add("async-comprehension")
        elif t in ("Yield", "YieldFrom"):
            fn = _enclosing_function_node(node)
            if isinstance(fn, ast.AsyncFunctionDef):
                features.add("async-generator")
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.NUMBER and "_" in tok.string:
                features.add("underscore-numeric-literal")
                break
    except (tokenize.TokenizeError, SyntaxError, IndentationError, ValueError):
        pass  # tokenize is stricter than ast.parse on some inputs; not fatal
    return features


def find_declared_minimum_version(tree):
    """The script's own `minimumVersion = (3, 4, 6)`-shaped module-level
    assignment, if present - direct, self-declared evidence (not inferred
    from syntax) of what Extron's generator believes the floor is."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt = node.targets[0]
        if not (isinstance(tgt, ast.Name) and tgt.id == "minimumVersion"):
            continue
        val = node.value
        if isinstance(val, ast.Tuple) and all(isinstance(e, ast.Constant) for e in val.elts):
            return tuple(e.value for e in val.elts)
        if isinstance(val, ast.Constant):
            return val.value
    return None


# =========================================================================
# item 6: configs[...] keys read in __init__, and any other model signal
# =========================================================================

def _subscript_key(node):
    s = node.slice
    if isinstance(s, ast.Index):     # py < 3.9
        s = s.value
    if isinstance(s, ast.Constant) and isinstance(s.value, str):
        return s.value
    return None


def find_init_configs_keys(tree):
    """One entry per `def __init__` found, however many classes the script
    defines: {class, keys (top-level configs[...] string keys, with
    duplicates), extra_params (params beyond self/configs)}."""
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "__init__"):
            continue
        args = node.args
        all_params = ([a.arg for a in getattr(args, "posonlyargs", [])]
                      + [a.arg for a in args.args]
                      + ([args.vararg.arg] if args.vararg else [])
                      + [a.arg for a in args.kwonlyargs]
                      + ([args.kwarg.arg] if args.kwarg else []))
        if "configs" not in all_params:
            # not a driver __init__(self, configs[, ...]) - some other
            # helper class defined alongside the driver in the same script
            # (e.g. a text-scroller utility); out of scope for R22.
            continue
        keys = []
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name)
                    and sub.value.id == "configs"):
                key = _subscript_key(sub)
                if key is not None:
                    keys.append(key)
        extra_params = [p for p in all_params if p not in ("self", "configs")]
        out.append({"class": _enclosing_class_name(node), "keys": keys,
                     "extra_params": extra_params})
    return out


_MODEL_PATTERN = re.compile(r"model", re.I)


def find_model_signals(tree):
    """[(kind, name)] for every configs[...] key or self.<attr> whose text
    contains 'model' (case-insensitive), ANYWHERE in the script (not just
    __init__) - the broader ROADMAP R22 sweep for any way a script might
    learn which model it is."""
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and node.value.id == "configs"):
            key = _subscript_key(node)
            if key and _MODEL_PATTERN.search(key):
                out.append(("configs-key", key))
        elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
              and node.value.id == "self" and _MODEL_PATTERN.search(node.attr)):
            out.append(("self-attr", node.attr))
    return out


# =========================================================================
# per-package driver
# =========================================================================

class Aggregate(object):
    def __init__(self):
        self.n_packages = 0
        self.round_trip_ok = 0
        self.round_trip_fail = 0
        self.round_trip_causes = {}          # "ExcType: message class" -> count
        self.round_trip_fail_examples = {}    # cause -> [package,...] (first 3)

        self.light_parse_fail = 0
        self.light_parse_fail_examples = []

        self.gap4_hits = []                   # [package,...]

        self.n_scripts = 0
        self.n_scripts_unparseable = 0
        self.unparseable_examples = []        # [(package, script_key, msg)]

        self.emulated_embedded_hits = []      # [(package, script_key, attr, method, parent_kind)]

        self.star_import_scripts = []         # [(package, script_key)]
        self.bare_global_counts = {}          # name -> count (occurrences)
        self.bare_global_examples = {}        # name -> [(package, script_key), ...] (first 3)

        self.feature_counts = {}              # feature -> count (scripts)
        self.feature_examples = {}            # feature -> [(package, script_key), ...]
        self.max_feature_overall = (0, 0)
        self.declared_min_version_counts = {}  # str(value) -> count
        self.declared_min_version_examples = {}

        self.init_key_counts = {}             # key -> count (occurrences)
        self.init_key_examples = {}           # key -> [(package, class), ...]
        self.n_inits = 0
        self.extra_param_hits = []            # [(package, class, params)]

        self.model_signal_counts = {}         # (kind, name) -> count
        self.model_signal_examples = {}

        self.unexpected_errors = []           # [(package, type, msg)]

    def to_json(self):
        def top(d, n=None):
            items = sorted(d.items(), key=lambda kv: -kv[1])
            return items if n is None else items[:n]

        return {
            "n_packages": self.n_packages,
            "item1_round_trip": {
                "ok": self.round_trip_ok,
                "fail": self.round_trip_fail,
                "causes": top(self.round_trip_causes),
                "examples": self.round_trip_fail_examples,
            },
            "item2_no_manifest_child": {
                "light_parse_fail": self.light_parse_fail,
                "light_parse_fail_examples": self.light_parse_fail_examples[:10],
                "packages_with_no_manifest_child": self.gap4_hits,
            },
            "item3_emulated_embedded": {
                "n_scripts": self.n_scripts,
                "n_hits": len(self.emulated_embedded_hits),
                "hits": self.emulated_embedded_hits,
            },
            "item4_bare_globals": {
                "star_import_scripts": self.star_import_scripts,
                "counts": top(self.bare_global_counts),
                "examples": self.bare_global_examples,
            },
            "item5_python_features": {
                "feature_script_counts": top(self.feature_counts),
                "examples": self.feature_examples,
                "max_feature_overall": list(self.max_feature_overall),
                "declared_minimum_version_counts": top(self.declared_min_version_counts),
                "declared_minimum_version_examples": self.declared_min_version_examples,
            },
            "item6_configs_model": {
                "n_inits": self.n_inits,
                "init_key_counts": top(self.init_key_counts),
                "init_key_examples": self.init_key_examples,
                "extra_param_hits": self.extra_param_hits,
                "model_signal_counts": {str(k): v for k, v in top(self.model_signal_counts)},
                "model_signal_examples": {str(k): v for k, v in self.model_signal_examples.items()},
            },
            "unparseable_scripts": {
                "count": self.n_scripts_unparseable,
                "examples": self.unparseable_examples[:20],
            },
            "unexpected_errors": self.unexpected_errors,
        }


def _add_example(bucket, key, value, cap=3):
    lst = bucket.setdefault(key, [])
    if len(lst) < cap:
        lst.append(value)


def process_package(name, path, agg):
    agg.n_packages += 1

    # -- item 1: round trip (independent of everything below) --
    ok, exc_type, msg_class = check_round_trip(path)
    if ok:
        agg.round_trip_ok += 1
    else:
        agg.round_trip_fail += 1
        cause = "%s: %s" % (exc_type, msg_class)
        agg.round_trip_causes[cause] = agg.round_trip_causes.get(cause, 0) + 1
        _add_example(agg.round_trip_fail_examples, cause, name)

    # -- items 2-6: a separate, lighter read-only parse --
    try:
        objects, root = load_light(path)
    except pv.PackageError as e:
        agg.light_parse_fail += 1
        agg.light_parse_fail_examples.append((name, str(e)))
        return

    no_manifest, warnings = check_gap4(objects, root)
    if no_manifest:
        agg.gap4_hits.append(name)

    scripts = extract_scripts(objects)
    for slot in scripts:
        agg.n_scripts += 1
        script_key = slot.key
        try:
            tree = ast.parse(slot.source, filename=script_key)
        except (SyntaxError, ValueError) as e:
            agg.n_scripts_unparseable += 1
            agg.unparseable_examples.append((name, script_key, "%s: %s" % (type(e).__name__, e)))
            continue

        _add_parents(tree)

        # item 3
        for hit in find_embedded_emulated_calls(tree):
            agg.emulated_embedded_hits.append(
                (name, script_key, hit["attr"], hit["method"], hit["parent_kind"]))

        # item 4
        bare = find_bare_globals(tree)
        if bare is None:
            agg.star_import_scripts.append((name, script_key))
        else:
            for gname in bare:
                agg.bare_global_counts[gname] = agg.bare_global_counts.get(gname, 0) + 1
                _add_example(agg.bare_global_examples, gname, (name, script_key))

        # item 5
        features = find_python_features(tree, slot.source)
        for feat in features:
            agg.feature_counts[feat] = agg.feature_counts.get(feat, 0) + 1
            _add_example(agg.feature_examples, feat, (name, script_key))
            v = _FEATURE_MIN_VERSION[feat]
            if v > tuple(agg.max_feature_overall):
                agg.max_feature_overall = v
        declared = find_declared_minimum_version(tree)
        if declared is not None:
            key = str(declared)
            agg.declared_min_version_counts[key] = agg.declared_min_version_counts.get(key, 0) + 1
            _add_example(agg.declared_min_version_examples, key, (name, script_key))

        # item 6
        for entry in find_init_configs_keys(tree):
            agg.n_inits += 1
            for k in entry["keys"]:
                agg.init_key_counts[k] = agg.init_key_counts.get(k, 0) + 1
                _add_example(agg.init_key_examples, k, (name, entry["class"]))
            if entry["extra_params"]:
                agg.extra_param_hits.append((name, entry["class"], entry["extra_params"]))
        for kind, mname in find_model_signals(tree):
            key = (kind, mname)
            agg.model_signal_counts[key] = agg.model_signal_counts.get(key, 0) + 1
            _add_example(agg.model_signal_examples, key, (name, script_key))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--out", default=os.path.join(_HERE, "sweep_results.json"))
    ap.add_argument("--limit", type=int, default=None,
                     help="process only the first N packages (sorted by name) - for a quick smoke test")
    ap.add_argument("--checkpoint-every", type=int, default=200)
    ap.add_argument("--progress-every", type=int, default=25)
    args = ap.parse_args()

    names = sorted(f for f in os.listdir(args.corpus) if f.lower().endswith(".pkp"))
    if args.limit:
        names = names[:args.limit]

    agg = Aggregate()
    t0 = time.time()
    for i, name in enumerate(names, 1):
        path = os.path.join(args.corpus, name)
        try:
            process_package(name, path, agg)
        except Exception:
            agg.unexpected_errors.append((name, "UNEXPECTED", traceback.format_exc(limit=4)))
        if i % args.progress_every == 0 or i == len(names):
            elapsed = time.time() - t0
            print("[%d/%d] %s  (%.1fs elapsed, %.2fs/pkg avg)"
                  % (i, len(names), name, elapsed, elapsed / i), flush=True)
        if args.checkpoint_every and i % args.checkpoint_every == 0:
            _write_out(args.out, agg, names, i, time.time() - t0, partial=True)

    _write_out(args.out, agg, names, len(names), time.time() - t0, partial=False)
    print("done: %d packages, %.1fs total" % (len(names), time.time() - t0))


def _write_out(out_path, agg, names, n_done, elapsed, partial):
    payload = {
        "meta": {
            "corpus_total": len(names),
            "n_done": n_done,
            "partial": partial,
            "elapsed_seconds": round(elapsed, 1),
            # Whether pinned copies stood in for the live tools/ files, and
            # what they were - never the directory, which is machine-local.
            "snapshot_used": bool(_SNAP),
            "snapshot_label": os.environ.get("CORPUS_SWEEP_SNAPSHOT_LABEL"),
        },
        "results": agg.to_json(),
    }
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, sort_keys=False)
    os.replace(tmp, out_path)


if __name__ == "__main__":
    main()
