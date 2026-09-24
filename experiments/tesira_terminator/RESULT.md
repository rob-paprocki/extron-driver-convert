# R19: Biamp Tesira `DeviceFaultList` terminator — settled

**Verdict: SETTLED. `\n` is correct; `\r\n` (in the `.pkp` and the translator's
generated module) is an anomaly, not a feature.**

Reproduce with:

```
py -3.11 -u experiments/tesira_terminator/us_heap.py
```

## The question

findings/11-spec-as-referee.md ("What the spec could not adjudicate") flagged
one unresolved disagreement out of 140+ command templates compared between
the `.pkp` / translator-generated Tesira module and Extron's own shipped
ControlScript module:

| source | `DeviceFaultList` cmdString |
|---|---|
| `.pkp` (`samples/Tesira/pkp/biam_25_150_v1_20_0.pkp`) | `'DEVICE get activeFaultList\r\n'` |
| translator-generated module | `'DEVICE get activeFaultList\r\n'` |
| Extron shipped module (`biam_dsp_TesiraSeries_v1_18_3_0.py:817`) | `'DEVICE get activeFaultList\n'` |

Biamp's published TTP grammar (`reference/biamp-ttp/`) specifies command
syntax but not a required line terminator, so it cannot referee this. Two
implementations disagree and the spec is silent — a tie that needs a third,
independent source to break.

## Method

A third independent implementation of the Tesira protocol ships inside the
Crestron demo programs under `samples/Tesira/Crestron/`:
`BiampTesiraLib3.clz` (present in both the IP and RS232 demo programs) is a
plain ZIP — a Crestron SIMPL# "certified module" — containing
`BiampTesiraLib3.dll`, a .NET assembly with its own from-scratch Tesira
Text Protocol client, built by Crestron, not Extron.

Every string literal a .NET compiler emits is stored in the assembly's
ECMA-335 `#US` ("User Strings") metadata heap. `experiments/tesira_terminator/us_heap.py`
locates it by reusing `tools/pkg_dump.py`'s existing PE/CLI-header reader
(`PEImage`, `metadata_root` — the same code that already walks Crestron
`.pkg` metadata for `ManifestResource` rows) rather than hardcoding any file
offset, then walks the `#US` heap per ECMA-335 II.24.2.4 (compressed-length
UTF-16LE blobs) — new logic, since `pkg_dump.py` never previously needed
that heap, but built on the same PE/metadata primitives, as instructed.

## What the `#US` heap shows

**Provenance: every string quoted below is a literal `ldstr` operand read
directly out of `BiampTesiraLib3.dll`'s `#US` heap** (SHA-256
`64b331042923d10b8bf284445e394f444f557b9c16ab5c2ade32b8d69ead44f1` — byte-
identical between the IP and RS232 `.clz` copies, so this is not a
transport-specific artifact).

1. **`"activeFaultList"` / `"DeviceFaultList"` is not a string literal
   anywhere in the heap**, and not found by method X = scanning the
   `#Strings` heap (type/method/field names) either. Crestron's library has
   no dedicated method for this attribute; it is built generically.

2. **The generic command-template literals** — the ones that build *every*
   attribute get/set command, including attributes with no dedicated method
   — are, verbatim from the heap:

   ```
   '"{0}" {1} {2} {3} {4} {5}\n'
   '"{0}" {1} {2} {3} {4}\n'
   '"{0}" {1} {2} {3}\n'
   '"{0}" {1} {2}\n'
   '"{0}" {1} {2} {3} {4} "{5}"\n'
   '"{0}" {1} {2} {3} "{4}"\n'
   '"{0}" {1} {2} "{3}"\n'
   '"{0}" {1}\n'
   '"{0}" {1} "{2}"\n'
   ```

   **All nine end in `\n`. Zero end in `\r\n`.** A `DEVICE get
   activeFaultList` query — instance `DEVICE`, verb+attribute `get
   activeFaultList` — is exactly the shape the 2-argument template
   `'"{0}" {1}\n'` builds. Crestron's independent implementation terminates
   it with `\n`.

3. **The only `\r\n`-related literals in the whole heap** are three bare
   terminator strings — `'\r\n'` (`US[0x0017c7]`), `'\r'` (`US[0x00212b]`),
   `'\n'` (`US[0x00212f]`) — sitting immediately next to `'login:'`
   (`US[0x00211d]`) and the session-bootstrap commands `'DEVICE get
   version\n'`, `'SESSION set verbose false\n'`, `'SESSION get alias
   "{0}"\n'`. The `#Strings` heap has `Regex`, `Split`, `DataReceived`,
   `ReceiveDataAsync`, `myStream_DataReceived` as method/type names — i.e.
   these bare terminators are **receive-side parsing tokens** (splitting or
   matching incoming lines from the device, which may arrive with either
   ending), not part of any outgoing command builder. None of the *sending*
   templates use `\r\n`.

## Cross-check: how anomalous is `\r\n` inside the `.pkp` itself

`us_heap.py` also decompresses the gzip-wrapped `.pkp` and regex-scans its
embedded GC Python source for every `cmdString = '...'` literal:

- **52** `cmdString` literals total.
- **1** ends in `\r\n` — `'DEVICE get activeFaultList\r\n'`.
- **49** end in `\n` only (e.g. `'{0} set gain {1} {2}\n'`,
  `'{0} set level {1} {2}\n'`, `'{0} set mute {1} {2}\n'`).
- 2 are empty/other.

This confirms the ROADMAP framing directly from the artifact: `\r\n` is a
**singleton** inside the `.pkp`'s own 52 command templates, not a pattern
that recurs for a reason.

## Conclusion

Three independent sources now agree against one:

- Extron's **shipped** ControlScript module: `\n`.
- Crestron's **independently written** Tesira library, both transports:
  `\n` (via the generic template family; no `\r\n`-terminated send path
  exists at all).
- The `.pkp`'s own 49 other `cmdString` templates: `\n`.
- Only the `.pkp`'s (and the derived generated module's) single
  `DeviceFaultList` template: `\r\n`.

The convergent, structural evidence (three sources, two of them completely
independent implementations, agreeing on `\n`, plus the anomaly being a
singleton among 52 templates in the very file that contains it) settles this
as a copy/template artifact in the `.pkp` — most likely a stray `\r\n` that
one command's authoring didn't get cleaned up when the rest of the driver's
templates were standardized on `\n` — rather than evidence of a real
protocol requirement for `DeviceFaultList` specifically. **`\n` is correct.**
The TTP spec's silence is not a gap that matters here: it was never going to
mandate a terminator for one command differently than for 139 others, and
it didn't need to — the tie is broken by implementation evidence, not by a
missing spec rule.

## What remains unresolved (reported as negative, not absence)

- The exact IL that concatenates a generic template with its arguments was
  not decoded (no IL disassembler was used — only the metadata tables and
  heaps `tools/pkg_dump.py`'s machinery already reaches). It is not needed
  for this question: the heap enumeration alone shows no `\r\n`-terminated
  template exists to be selected for any command, `DeviceFaultList`
  included.
- Whether the `.pkp`'s single stray `\r\n` originated from a hand-edited
  template, a different code-generator version, or a copy-paste from a
  different Biamp product line is **not found by method X** (heap/string
  comparison) and is not claimed here either way.
