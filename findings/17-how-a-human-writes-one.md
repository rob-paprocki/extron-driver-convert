# Finding 17 — how an integrator actually writes a driver for an unsupported device

**Status: measured** 2026-09-09, from `samples/Custom Module/` — a three-tier
ControlScript stack a working programmer built for **Ross Ultrix**, a router
Extron ships no driver for.

Every other ControlScript module in this repo was emitted by Extron's own
tooling. This is the first evidence of what a human does when the vendor has not
done it for them — which is exactly the i20 problem finding 13 set out to solve.

The headline: **they do not write from scratch. They splice Extron's template.**

## 1. The stack has three tiers, and the repo had only ever seen one

| file | lines | role |
|---|---|---|
| `mod_ross_matrix_RossTalk_v1_1_0_0.py` | ~300 | device module, RossTalk protocol — the wire |
| `mod_ross_matrix_tsl_3_1_v1_1_0_0.py` | ~330 | device module, TSL 3.1 — a second protocol to the same box |
| `plugin_ross_ultrix.py` | ~90 | translation layer between program and modules |
| `tools.py` | **7,644** | general framework (Valley Communications, v1.6.0.0, 2023) |

`plugin_ross_ultrix.py` states its own job in its docstring: *"providing a
translation layer between the main program and hardware module."* That is the
**plugin tier the repo has never had a sample of** — and it is the same
architectural idea STATUS.md asks about under "is a shared intermediate
representation justified". A practitioner independently arrived at it.

Note the shape: **one plugin over two protocol modules for one device.** The
plugin is where "which protocol answers this question" is decided. That is
precisely the problem a cross-vendor IR would have to solve.

## 2. The device modules are spliced Extron templates, from two vintages

This is the finding that matters for our method.

Normalising whitespace and `except BaseException:` → `except:`, then diffing the
`# RECOMMENDED not to modify` block against shipped Extron modules:

- **Lines 78–174** (`Set`, `Update`, `SubscribeStatus`, `NewStatus`,
  `WriteStatus`, `ReadStatus`) are byte-equivalent to the **older** Extron
  template — the `getattr(self, 'Set%s' % command)` / `print(command, 'does not
  support Set.')` vintage that ships in ClockAudio and Tesira. Normalised diff
  across 95 lines: **one dropped comment**.
- **Lines 176–204** (`__ReceiveData`, `AddMatchString`) are the **newer**
  template — `self.__receiveBuffer` / `self.__matchStringDict` with an inline
  regex loop — not ClockAudio's `_ReceiveBuffer` + separate
  `CheckMatchedString()`.

**The author copied boilerplate out of two different shipped modules and joined
them.** A generator does not do that. The whole file has also been through
autopep8 (bare `except:` → `except BaseException:`, dict-literal spacing,
trailing whitespace) — and not one Extron-generated sample in `samples/` shows
those marks.

Two of the divergences are semantic rather than cosmetic, e.g. `WriteStatus`
drops Extron's `if not self.connectionFlag and command != 'ConnectionStatus'`
guard. Deliberate, not sloppy.

## 3. Why that matters for finding 13

`build_i20.py` derives the i20 driver by transplanting into Extron's own 1
Beyond package and applying named patches, rather than authoring a module from
first principles. That was chosen to keep the work on the measured side of the
line — and it turns out to be **what a competent integrator does anyway**, for
the same reason: the ~130-line status/mutex/dispatch block is host contract, not
device knowledge, and rewriting it only adds risk.

The difference is which artifact gets spliced. Ross's author spliced from two
shipped `.py` modules and hand-merged. We splice the `.pkp` and patch by anchor.
Same instinct; ours is reproducible and theirs is not.

## 4. The wire-table oracle survives hand-written input

`tools/wire_table.py` had only ever been run on machine-generated modules.
Against these:

| module | commands extracted |
|---|---|
| `mod_ross_matrix_RossTalk_v1_1_0_0.py` | 5 — `ConnectionStatus`, `CustomControl`, `LoadSet`, `MatrixTieCommand`, `SalvoRecall` |
| `mod_ross_matrix_tsl_3_1_v1_1_0_0.py` | 2 — `ConnectionStatus`, `OutputTieStatus` |

It extracts cleanly. That is a real generalisation datapoint for finding 14's
oracle: the extractor keys on the template's structure, and hand-written code
that keeps the template is still readable to it.

## 5. `tools.py` is a runtime, not a driver

7,644 lines, 30 top-level classes, a hand-maintained 90-line changelog running
v1.0 → v1.6.0.0. Authored by Jean-Luc Rioux at Valley Communications, targeting
Pro controller firmware 3.10+.

| lines | provides |
|---|---|
| 161–590 | JSON persistence to `/NVRAM/`, log rotation with a 90%-storage cap |
| 644–1000 | a **telnet debug server on TCP 1988**, one synthetic listening port per wrapped object |
| 1002–1669 | `__InterfaceWrapper` + 6 transport subclasses |
| 1670–4435 | 12 port wrappers — Relay, IR, FlexIO, Volume, PoE, SWAC, Tally, Contact, DigitalIO, CircuitBreaker, SWPower |
| 4436–6266 | processor / SP / UI device wrappers |

None of it is a `.pkp`, and none of it needs Global Configurator. It is evidence
that the ControlScript side of Extron's platform is a general programming target
that practitioners build real infrastructure on — which strengthens the case,
already made in finding 13, that the ControlScript module is the shorter path to
a working i20 driver than the `.pkp`.

## What this does NOT show

- **One integrator, one device.** Conventions here may be Valley
  Communications' house style rather than industry practice. Nothing else in the
  repo corroborates it.
- **Nothing was executed.** The splice claim is from normalised diffs against
  shipped modules; no module was run.
- **The plugin tier is unmeasured as an abstraction.** It is one example over
  two protocols for one device, not evidence that the pattern generalises to a
  cross-vendor IR.
- **`tools.py` was mapped, not read.** 30 classes were enumerated by AST and the
  transport section read; most of the 7,644 lines were not.
