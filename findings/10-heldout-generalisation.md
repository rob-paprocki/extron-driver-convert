# Finding 10 — the held-out result

**Recorded before any diagnosis or tuning, because the first number is the only
honest one.**

Until the Biamp and Clock Audio samples arrived, every rewrite rule in
`tools/pkp2cs.py` was **derived from** and **validated against** the same four
device pairs. That is circular, and the ~95% scorecard the project had been
reporting was an in-sample figure.

## The numbers

**In-sample** — the four the rules were built on:

| pair | wire-matching |
|---|---|
| DSC 12G-HD | 28/29 |
| DTP3 CP 42 | 27/28 |
| Samsung serial | 9/9 |
| Automate VX | 17/18 |

Dangling `self.X()` references across all five generated modules: **5**.

**Held-out** — never seen by any rule, run with zero tuning:

| pair | shared | matching | differing | dangling |
|---|---|---|---|---|
| Clock Audio `clau_25_5940` (CDT100 MK3) | 6 | **1** | 5 | 0 |
| Clock Audio `clau_25_1777` (MK I/II/UDP) | 7 | **4** | 3 | 0 |
| Biamp Tesira `biam_25_150` | 74 | **63** | 11 | **51** |

## What this says

**Biamp generalises reasonably on wire content — 85% — and collapses on runtime
resolvability.** 51 dangling references against 5 for all four in-sample modules
*combined*. Tesira Text Protocol is structured text with instance IDs and
attributes rather than a fixed command set, so the package exercises constructs no
in-sample device had.

**Clock Audio degrades badly on wire content.** But there is a caveat that must be
resolved before calling it a translator failure: there are **two** Clock Audio
packages and only **one** shipped ControlScript module (7 commands, empty
`self.Models`). `clau_25_5940` declares one model, `CDT100 MK3`; `clau_25_1777`
declares four, `CDT 100 MK I` / `MK II` / `CDT 100` / `CDT 100-UDP`. Comparing a
MK3 package against a MK I/II module would be an unfair test, and reporting it as a
translator fault would be wrong. The correspondence is being established.

## Resolution, 2026-09-23 — the mis-pairing confirmed, and the corrected score

Source: `tools/out/verdicts/heldout_synthesis.md` §1, §5 (recovered synthesis; see
ROADMAP R6).

**The Clock Audio caveat resolves as a mis-pairing, and it is 100% of that
device's apparent failure.** The shipped `clau_dsp_CDT100_v1_0_3_0.py` belongs
to package **1777**, not 5940: it implements `LEDLightControl` on the
4-channel `ACK GCH32 0 CH1R=…CH4…` family, byte-identical to 1777's own
`AddMatchString` and entirely absent from 5940; 5940 instead hardcodes
`LOAD 0\r`/`SAVE 0\r` and a 12-channel `BSTATUS` scheme matching the
manufacturer's `MAN_CDT100_MK3.pdf`. Scoring 5940 against a MK I/II module was
an unfair test and has been dropped, exactly as Samsung's ethernet module
already was.

**Corrected held-out score: 67 of 81 shared commands wire-match a shipped
module — 82.7%, against 96.4% in-sample (81/84).** The project's "~95%" figure
is an in-sample number and does not survive out of sample. Both these numbers
are stated exactly as `heldout_synthesis.md` §1 gives them; rules were
unchanged for both.

The two metrics diverge, and both are true:
- **Fidelity to source: 81/81 held-out (100%).** No held-out difference is a
  translation error — Biamp's 11 wire differences all trace to a post-generation
  human edit in Extron's shipped module, and Clock Audio's 3 remaining
  differences on the valid (1777) pairing are byte-faithful carries of the
  `.pkp` source.
- **Agreement with a shipped module: 67/81 (83%).** The 17% gap is Extron's
  hand-editing, which no converter can predict.

**Clock Audio's own manufacturer module — not just Extron's or Crestron's —
caught a real defect in Extron's source driver.** The 5940/MK3 package emits
`'SRBG {} {} {} {}\r'`. The verb is `SRGB` — per Clock Audio's own SimplSharp
module, per Extron's own 1777 package, and per the manufacturer's manual
(`MAN_CDT100_MK3.pdf:1005,1341,1343`). Extron's MK3 driver has a
transposed-letter typo (`SRBG` for `SRGB`) that will never set an RGB LED. The
translator carries it verbatim, which is correct behaviour — but only a
manufacturer oracle could tell us the source itself was wrong rather than the
translator.

## Why this was worth doing

The two metrics separate cleanly, and neither alone would have caught this:

- Biamp looks **fine** on the wire table and is badly broken at runtime.
- Clock Audio looks **fine** at runtime (0 dangling) and is wrong on the wire.

A single-metric scorecard would have passed one of them. This is the concrete
justification for the standing rule that wire correctness is necessary but not
sufficient.

## The rule this establishes

**More samples cannot fix an overfitted rule set.** Diagnosis and generalisation
come before pulling more data — otherwise each new device gets its own special
case and the in-sample number stays flattering while the real one does not move.

Any rule change from here must be justified by what the **shipped** modules do,
and re-validated across **all six** pairs. Improving Biamp while regressing DSC is
not progress.
