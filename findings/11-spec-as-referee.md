# Finding 11 — a protocol spec is a better referee than another implementation

Every comparison in this project until now was implementation-vs-implementation,
with Extron's shipped module treated as ground truth. Biamp publishes a **grammar**
for Tesira Text Protocol, harvested to `reference/biamp-ttp/`. Using it as referee
on Biamp's 11 wire-table differences produced two results neither the wire table
nor the runtime check could reach.

## 6 of the 11 "differences" were never differences

`Bluetooth`, `BluetoothDiscovery`, `BluetoothUSBConnectionStatus`,
`BluetoothUSBStreamingStatus`, `TILineInUse`, `VoIPLineInUse` — the `set_templates`
and their value maps are **byte-identical** between generated and shipped.

The only difference is where the mapping lives. Extron's shipped module implements
`On`/`Off` ↔ `true`/`false` inside one shared `__MatchAllSubscribe` dispatcher
(`biam_dsp_TesiraSeries_v1_18_3_0.py:135-270`), which `wire_table.py`'s
per-command static extraction cannot attribute back to individual commands. The
generated module keeps a separate `__Match<X>` per command.

**This is an oracle artifact, not a translator fault** — so Biamp's real agreement
is 69/74, not 63/74. Worth knowing that the acceptance oracle has a measurable
false-positive rate of its own.

## Extron's shipped module has a real bug the generated one does not

The `.pkp`'s own GC script quotes the preset name:

```python
'DEVICE recallPresetByName "{0}"\n'.format(name)     # .pkp, and generated
'DEVICE recallPresetByName {0}\n'.format(name)       # Extron shipped, line 1356
```

Per the TTP spec, a Value containing spaces **must** be double-quoted — the spec
demonstrates it with its own worked example, where `"my level 2" get level 1`
succeeds and `my level 2 get level 1` fails with `-ERR address not found`.

**So a preset named `Morning Setup` fails to recall on Extron's shipped module and
works on the generated one.** Same for `PresetSaveName`.

The translator is spec-correct here and the shipped module is not. That inverts
the project's working assumption, and it means a "difference from the shipped
module" is not automatically a defect — sometimes it is a *fix*.

## What the spec could not adjudicate

- **`TIHook` / `VoIPHook`** — wire strings are identical
  (`'{0} dial{1}{2} {3}\n'`, a valid Dialer verb). The difference is the Python
  qualifier contract: the `.pkp` fetches the number from GC scratch state, Extron
  requires an explicit `Number` qualifier. An API design choice, not protocol.
- **`DeviceFaultList`** — `\r\n` (`.pkp`, generated) vs `\n` (shipped). The spec's
  terminator rule does not settle which is wrong. *(Settled 2026-09-23 by a
  third implementation: `\n`. Crestron's `BiampTesiraLib3.dll`, byte-identical
  in the IP and RS232 demos, builds every attribute command from nine generic
  templates, all ending `\n`; its only `\r\n` literals are receive-side. The
  `.pkp`'s other 49 command strings end `\n`, and Extron's shipped module sends
  all 73 of its command templates with `\n`. So `DeviceFaultList`'s `\r\n` is
  a one-off in the `.pkp` that the translator faithfully carried —
  `experiments/tesira_terminator/RESULT.md`, ROADMAP R19.)*

## The conclusion: three metrics, not two

| metric | catches | blind to |
|---|---|---|
| wire-table match | wrong command strings | helper bodies; produces false positives (above) |
| runtime resolvability | dangling references | anything semantically wrong that resolves |
| **spec conformance** | malformed protocol, *and errors in the reference implementation* | anything the spec does not cover |

Each has now caught something the others structurally could not. The fabricated
SIS handshake was invisible to the wire table; the 26 dangling references were
invisible to it too; and the shipped-module quoting bug was invisible to both,
because both take the shipped module as the standard.

**Where a device's protocol is formally documented, conformance checking should be
a first-class metric** — not because documentation is authoritative (finding 09
caught Crestron's docs being wrong, and finding 08 caught them being incomplete),
but because a *third independent source* breaks ties that two sources cannot.

## Method note worth keeping

The harvest found the site's **published search manifest** (`whxdata/search_topics.js`,
273 topics with TOC paths) and filtered it, rather than guessing URLs — the lesson
from finding 08's two enumeration failures, applied. It also caught Bright Data's
markdown mode silently truncating every page mid-sentence and re-fetched as HTML.
A silent truncation would have looked exactly like a short spec.

## Addendum, 2026-09-23 — a second bug wire-diffing structurally cannot see

Source: `tools/out/verdicts/ttp_validation.md`, "The wire-diff-invisible bug
the spec caught that diffing missed" (a re-run that independently
recomputed both acceptance metrics from scratch and re-verified the 11-name
diff above; `tools/test_pkp2cs.py` reports **55 passed, 0 failed**, 52
baseline + 3 new).

While reading the quoting logic in `NewSpeedDialEntryNameCommand` /
`NewSpeedDialEntryNumberCommand` — **not** among the 11 differences above,
because `wire_table`'s diff reports these two commands as fully matching —
Extron's shipped module turned out to add a second, runtime-only quoting step
that the generated module (and the `.pkp` it comes from) does not:

```
.pkp / generated: tag = qualifier['Instance Tag']                      (no pre-quoting)
shipped:          if ' ' in tag: tag = '"' + tag + '"'                 (before the same format string)
```

Both then format into the same hardcoded-quote template,
`'"{0}" set speedDialLabel {1} {2} "{3}"\n'`. For an instance tag containing a
space ("My DSP"), simulating both gives:

```
shipped   : '""My DSP"" set speedDialLabel 1 3 "Office"\n'
generated : '"My DSP" set speedDialLabel 1 3 "Office"\n'
```

Shipped double-quotes the tag. Per the spec's own worked example of
Instance-Tag quoting (`reference/biamp-ttp/SYNTAX.md` §3, `"my level 2" get
level 1` — single-quoted, succeeds), `""My DSP""` is not that documented form
and, by the stated space-delimited tokenization rule, would parse as a
broken/empty leading token — a real regression Extron introduced, present in
both commands (`samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py:1187-1188`
and `1203-1204`).

**This is invisible to wire-diffing on principle, not by oversight.**
`wire_table.diff_tables` compares the static `.format()` template literal,
which is identical on both sides; the divergence only exists in the
runtime-substituted value fed into it, which template-level diffing never
simulates. Reading the quoting logic against the spec's literal quoting
example is what surfaced it. It is a second, independent instance of this
finding's thesis — the spec adjudicates and catches what wire-diffing
structurally cannot — beside the `PresetRecallName`/`PresetSaveName` result
above.
