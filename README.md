# extron-driver-convert

Research repo. **Question:** can an Extron `.pkp` driver (Global Configurator
Plus/Pro) be converted to/from a ControlScript device module (`.py`)?

Status: **investigating — no verdict yet.** Nothing here is a working converter.

## The question, split

Two directions, researched separately because they are not symmetric:

| Direction | What it would mean | Prior expectation |
|---|---|---|
| `.pkp` → `.py` | Migrate a legacy GC Plus/Pro driver onto an IP Link Pro / ControlScript system | Plausible for the command table; the GC logic layer has no direct target |
| `.py` → `.pkp` | Take a ControlScript module back into GC Plus/Pro | Harder — arbitrary Python doesn't reduce to a declarative driver package |

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
