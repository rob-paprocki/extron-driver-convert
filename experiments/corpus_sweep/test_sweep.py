#!/usr/bin/env python3
"""
experiments/corpus_sweep/test_sweep.py - unit tests for sweep.py's per-script
analyzers, against small synthetic snippets rather than the corpus itself.

These exist so the corpus-wide numbers in SWEEP.md rest on analyzers whose
behaviour is pinned on known-shape inputs, not just eyeballed against a
handful of real packages. Standard library only; run directly.
"""

import ast
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import sweep  # noqa: E402

PASS = 0
FAIL = 0


def check(label, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
    else:
        FAIL += 1
        print("FAIL: %s\n  got:  %r\n  want: %r" % (label, got, want))


def parse(src):
    tree = ast.parse(src)
    sweep._add_parents(tree)
    return tree


# =========================================================================
# 1. item 3: Emulated pre-writes embedded inside a larger expression
# =========================================================================
print("-- item 3: Emulated pre-write embedded in a larger expression --")

SRC_STANDALONE = """
class D:
    def Set(self, value):
        self.WriteThing(value, 'Emulated')
"""
tree = parse(SRC_STANDALONE)
check("standalone Expr statement -> no hit (pkp2cs's own rule already strips this)",
      sweep.find_embedded_emulated_calls(tree), [])

SRC_ASSIGNED = """
class D:
    def Set(self, qualifier):
        mode = self.ReadMultiviewString(qualifier, 'Emulated')
        return mode
"""
tree = parse(SRC_ASSIGNED)
hits = sweep.find_embedded_emulated_calls(tree)
check("assigned to a variable -> 1 hit", len(hits), 1)
check("hit names the right attr", hits[0]["attr"] if hits else None, "ReadMultiviewString")
check("hit names the right parent kind", hits[0]["parent_kind"] if hits else None, "Assign")

SRC_ARG = """
class D:
    def Set(self, value):
        foo(self.WriteThing(value, 'Emulated'))
"""
tree = parse(SRC_ARG)
check("used as a call argument -> 1 hit", len(sweep.find_embedded_emulated_calls(tree)), 1)

SRC_LIVE_NOT_EMULATED = """
class D:
    def Set(self, value):
        x = self.WriteThing(value, 'Live')
"""
tree = parse(SRC_LIVE_NOT_EMULATED)
check("'Live' context (not 'Emulated') -> no hit",
      sweep.find_embedded_emulated_calls(tree), [])

SRC_EXCLUDED_GENERIC = """
class D:
    def Set(self, value):
        x = self.WriteStatus(value, 'Emulated')
"""
tree = parse(SRC_EXCLUDED_GENERIC)
check("generic WriteStatus accessor is excluded even when embedded",
      sweep.find_embedded_emulated_calls(tree), [])


# =========================================================================
# 2. item 4: bare/runtime-injected globals
# =========================================================================
print("-- item 4: bare globals --")

SRC_TRUE_BARE_GLOBAL = """
import time

class D:
    def Set(self):
        return ExtronTime(time.monotonic())
"""
tree = parse(SRC_TRUE_BARE_GLOBAL)
check("ExtronTime used, never bound in-script -> flagged once",
      sweep.find_bare_globals(tree), ["ExtronTime"])

SRC_LOCALLY_DEFINED = """
import time

class D:
    def Set(self):
        return ExtronTime(time.monotonic())

class ExtronTime(float):
    pass
"""
tree = parse(SRC_LOCALLY_DEFINED)
check("ExtronTime used AND locally defined -> not flagged (this is the "
      "actual shape most corpus scripts turned out to use)",
      sweep.find_bare_globals(tree), [])

SRC_STAR_IMPORT = """
from os import *

class D:
    def Set(self):
        return getcwd()
"""
tree = parse(SRC_STAR_IMPORT)
check("star import -> None sentinel (excluded, not guessed at)",
      sweep.find_bare_globals(tree), None)

SRC_BUILTIN_ONLY = """
class D:
    def Set(self, items):
        return len(items) + int('1')
"""
tree = parse(SRC_BUILTIN_ONLY)
check("only builtins used -> nothing flagged", sweep.find_bare_globals(tree), [])

SRC_SELF_NOT_FLAGGED = """
class D:
    def Set(self):
        return self.Value
"""
tree = parse(SRC_SELF_NOT_FLAGGED)
check("bare 'self' is never flagged", sweep.find_bare_globals(tree), [])


# =========================================================================
# 3. item 5: newest Python syntax feature
# =========================================================================
print("-- item 5: python feature detection --")

check("f-string detected", "f-string" in sweep.find_python_features(parse("x = f'{1}'"), "x = f'{1}'"), True)
check("plain script has no post-3.5 markers",
      sweep.find_python_features(parse("x = 1\ny = x + 1\n"), "x = 1\ny = x + 1\n"), set())
check("walrus detected", "walrus" in sweep.find_python_features(
      parse("if (n := 1): pass"), "if (n := 1): pass"), True)
check("variable annotation detected", "variable-annotation" in sweep.find_python_features(
      parse("x: int = 1"), "x: int = 1"), True)
check("underscore numeric literal detected", "underscore-numeric-literal" in sweep.find_python_features(
      parse("x = 1_000_000"), "x = 1_000_000"), True)
check("plain 'async def'/'await' (baseline 3.5, PEP 492) is NOT flagged as a newer feature",
      sweep.find_python_features(
          parse("async def f():\n    await g()\n"), "async def f():\n    await g()\n"),
      set())
check("async comprehension IS flagged (3.6, PEP 530)", "async-comprehension" in sweep.find_python_features(
      parse("async def f(y):\n    return [x async for x in y]\n"),
      "async def f(y):\n    return [x async for x in y]\n"), True)

check("declared minimumVersion tuple is read back exactly",
      sweep.find_declared_minimum_version(parse("minimumVersion = (3, 4, 6)\n")), (3, 4, 6))
check("no minimumVersion assignment -> None",
      sweep.find_declared_minimum_version(parse("x = 1\n")), None)


# =========================================================================
# 4. item 6: configs[...] keys in __init__, and model signals
# =========================================================================
print("-- item 6: configs keys / model signals --")

SRC_INIT = """
class D(BaseDriver):
    def __init__(self, configs):
        self.Unidirectional = configs['Unidirectional']
        self.SSL = configs['DriverParams']['SSL Verify Mode']

class Scroller:
    def __init__(self, items, window):
        self.items = items
"""
tree = parse(SRC_INIT)
entries = sweep.find_init_configs_keys(tree)
check("only the configs-taking __init__ is reported (helper class __init__ excluded)",
      len(entries), 1)
check("class name recorded", entries[0]["class"] if entries else None, "D")
check("top-level configs keys captured, nested nesting not expanded past its own key",
      sorted(entries[0]["keys"]) if entries else None,
      ["DriverParams", "Unidirectional"])
check("no extra __init__ params beyond (self, configs)",
      entries[0]["extra_params"] if entries else None, [])

SRC_EXTRA_PARAM = """
class D(BaseDriver):
    def __init__(self, configs, model):
        self.Model = model
"""
tree = parse(SRC_EXTRA_PARAM)
entries = sweep.find_init_configs_keys(tree)
check("an extra __init__ param is captured", entries[0]["extra_params"], ["model"])

SRC_MODEL_SIGNAL = """
class D(BaseDriver):
    def __init__(self, configs):
        self.Model = configs['Model']
        self.other = configs['Unidirectional']
"""
tree = parse(SRC_MODEL_SIGNAL)
signals = sorted(sweep.find_model_signals(tree))
check("both a configs['Model']-shaped key and a self.Model attr are caught",
      signals, [("configs-key", "Model"), ("self-attr", "Model")])

SRC_NO_MODEL_SIGNAL = """
class D(BaseDriver):
    def __init__(self, configs):
        self.Unidirectional = configs['Unidirectional']
"""
tree = parse(SRC_NO_MODEL_SIGNAL)
check("no model-shaped signal -> empty (report as 'not found by method X', never a guess)",
      sweep.find_model_signals(tree), [])


# =========================================================================
# 5. item 1: round-trip failure message classing (no corpus needed)
# =========================================================================
print("-- item 1: message-class normalization --")

check("digits collapse and the leading '<path>.pkp: ' prefix is stripped",
      sweep._message_class("some/where/donor_1_2.pkp: donor does not round-trip "
                            "(in=123 out=456, first difference at byte 789) - refusing"),
      "donor does not round-trip (in=N out=N, first difference at byte N) - refusing")


print("\n%d passed, %d failed, %d total" % (PASS, FAIL, PASS + FAIL))
sys.exit(1 if FAIL else 0)
