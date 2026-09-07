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
