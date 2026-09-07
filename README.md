# extron-driver-convert

Research repo. **Question:** can an Extron `.pkp` driver (Global Configurator
Plus/Pro) be converted to/from a ControlScript device module (`.py`)?

Status: **verdicts reached for all four directions — see `STATUS.md` first.**
Not yet a working converter; the translator is being built.

## The question, split

Two directions, researched separately because they are not symmetric:

| Direction | Verdict |
|---|---|
| `.pkp` → `.py` | **Yes** — a Python-to-Python translation, not a format decode (finding 02) |
| `.py` → `.pkp` | **No** — not a practical, repeatable capability (finding 02) |
| Crestron `.pkg` → Extron | **Yes** for JSON-engine drivers (findings 03–05) |
| Extron → Crestron `.pkg` | **Plausible**, gated by licence rather than by code (finding 06) |

Scope widened beyond Extron once samples showed the same device encoded by both
vendors to the same bytes.

## Working hypothesis (unverified)

A `.pkp` is a *package* holding a device's command set: command strings,
parameter/limit definitions, feedback + parse patterns, and connection
settings. A ControlScript module carries broadly the same information as
Python data structures plus `Set*` / `Update*` / parse methods. If that
holds, the **command table** is mechanically convertible in both directions
and everything around it is not.

This hypothesis is written down so the sample files can falsify it. Do not
treat any line of it as established.

## What would make conversion real

The answer is not binary. Grade each direction against these:

1. **Container** — can the format be read at all without Extron's tooling?
2. **Command table** — do commands, parameters and qualifiers map 1:1?
3. **Feedback/parse** — do match patterns survive translation?
4. **Connection model** — serial params, IP ports, IR, relays, addressing.
5. **Logic / events** — GC's event layer vs. ControlScript's user code.
6. **Round-trip loss** — what is silently dropped, and does it matter?

A conversion that gets 1–4 and abandons 5 may still be worth building; that
is a judgement call for the writeup, not an assumption made in advance.

## Layout

```
samples/pkp/            example .pkp driver files
samples/controlscript/  example ControlScript .py modules
tools/                  throwaway inspection scripts (format probing, dumps)
findings/               the actual research output
notes/                  raw observations, vendor doc references
```

## Provenance & licensing

Sample drivers are Extron vendor material. **This repo stays private.**
Findings may describe formats; sample files are not redistributed.
