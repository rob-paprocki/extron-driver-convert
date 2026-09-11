# ross_ultrix/

Finding 17 section 6: the only oracle pair in the project where **one side is
human-written.**

- `corpus/extron-driver3/ross_15_3280_v1_3_2.pkp` — Extron's package for the
  Ross Video Ultrix router. Extron ships **no** ControlScript module for it.
- `samples/Custom Module/` — the RossTalk and TSL 3.1 modules an integrator
  wrote by hand for a real project, about three years earlier.
- `ross_ultrix_generated_by_pkp2cs.py` — what `tools/pkp2cs.py` produces from
  Extron's package, generated 2026-09-09.

Regenerate with:

    python3 tools/pkp2cs.py corpus/extron-driver3/ross_15_3280_v1_3_2.pkp -o <outdir>

## What the comparison showed

| | commands |
|---|---|
| shared | `ConnectionStatus`, `MatrixTieCommand`, `OutputTieStatus` |
| only Extron's package | `RefreshMatrix`, `RequiredCommand` |
| only the human modules | `CustomControl` (`CC {}{}`), `LoadSet` (`LOADSET {}`), `SalvoRecall` (`GPI {}`) |

The translator would have saved the integrator the boilerplate and about half
the command surface, and left the capability Extron's driver never exposed.

## Not done

The generated module has **never been executed** — the comparison is wire
tables, not behaviour. Running it against a RossTalk simulator (or an Ultrix)
is an open item in `ROADMAP.md`.

## template_splice/ — finding 17 §2's evidence

Moved from `C:\Users\robp\AppData\Local\Temp\`. How "the boilerplate is
Extron's; the device is theirs" was measured:

| file | content |
|---|---|
| `gen_boiler.txt`, `tsl_boiler.txt` | the "RECOMMENDED not to modify" blocks cut from the hand-written RossTalk and TSL 3.1 modules |
| `ca.txt`, `ts.txt` | the matching template blocks from shipped modules (finding 17 §2 names ClockAudio and Tesira as the older vintage) |
| `a.txt` | a normalised diff of a generated DTP3 module against the Ross module |

`fx.py` and `wt_probe.py` run `tools/wire_table.py` over hand-written code such
as the Ross `CustomControl` command — finding 17 §4, the extractor surviving
human-written input.
