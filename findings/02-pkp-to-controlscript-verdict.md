# Finding 02 — verdict: `.pkp` → ControlScript

From a 21-agent analysis with adversarial per-claim verification:
**110 claims confirmed, 15 refuted.** Full text in `tools/out/verdicts/`
(gitignored — regenerate or ask).

## Answer: yes, for Extron's own SIS drivers — and it is a Python-to-Python job

The `.pkp` does not describe a driver from which code must be invented. It
*contains* the driver as Python source, and that source shares its protocol logic
with the shipped ControlScript module almost verbatim:

- **75.9%** of the DSC 12G-HD ControlScript module's non-blank lines (779 / 1,027)
  appear word-for-word in the `.pkp`'s embedded Python.
- **65.4%** for the DTP3 CrossPoint 42 (706 / 1,080), in order.
- Of 30 `AddMatchString` registrations in the DSC, **29 are character-identical**.
  The one difference is `E(\d+)` vs `E(\d{2})`.
- The last ~170 lines of both shipped modules are identical except whitespace —
  the runtime shell is a fixed template, copied rather than derived.

The embedded Python even delimits the convertible region with literal markers:
`### BEGIN AUTO GENERATION OF COMMAND DEF` … `### END`, covering 78% / 72% of
each file.

## Architecture: hybrid, Python-primary

Translate the embedded Python; use the NRBF asset graph as the authority for
inventory, naming and validation. Neither alone suffices:

- **Metadata alone can't work** — it lacks command framing (`'w1*{}ASPR\r'`),
  response regexes and handler logic. But it holds more than first thought:
  `EnumStateAsset._tag` carries wire tokens (`'Audio'` → `'$'`), and
  `DecimalParamAsset` carries ranges (Input Gain `_min=-18 _max=24 _suffix='dB'`),
  so it is a real cross-check on values lifted from code.
- **Python alone can't work** — model names and per-model command inventories
  live only in the `DriverModelAsset` tree, and those lists are the correctly
  *pruned* ones.

Roughly ten AST rewrite rules plus a template and a comparison harness. Estimated
2–3 weeks for one engineer fluent in Python's `ast`, using the sample pairs as
oracles. The estimate is credible because the residual after mechanical rules is
small and enumerable.

**Acceptance must be defined against the wire-string table, not the file.** The
shipped modules are not a pure function of the `.pkp` — there is version skew
(DTP3 module is v1.2.0.0, package is v1.3.0), hand-edits, and a dropped throttle.
A converter that reproduces everything except the documented residuals has
succeeded.

## Reverse direction: no

ControlScript → `.pkp` is not a practical capability. NRBF is writable in
principle — it is a plain sequential record stream — but "structurally valid
bytes" and "a package Global Configurator accepts" are different bars, and
nothing has tested the second. It also requires fabricating a proprietary
metadata graph whose acceptance rules are invisible.

## Third-party: narrows rather than flips

Extraction carries over intact (the NRBF schema is device-agnostic; the script is
an opaque byte array). The command-block rules are protocol-agnostic — cmdstrings,
regexes and value maps are copied as opaque data. But the *runtime shell* is
SIS-specific in both artifacts: the `__SetHelper` handshake sends `'w0echo\r\n'` /
`'w3cv\r\n'` and waits for `Vrb3` / `Echo0`, the error path matches an Extron
error-code table, and the heartbeat rides on `ExecutiveMode`. A non-SIS device
cannot use that template.

The Samsung sample (see finding 03) is the test of this, and is under analysis.
