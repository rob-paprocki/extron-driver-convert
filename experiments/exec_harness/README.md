# exec_harness/ — running generated modules offline (ROADMAP R13)

Every other check in this repo reads code. `wire_table` extracts command
templates; `find_dangling_self_calls`, `find_unassigned_self_attributes` and
`find_unresolved_globals` look for names nothing defines. None of them sees a
call made the wrong way. Finding 14 §7's stripped `@staticmethod` compiled,
resolved every name and scored a perfect wire table, and raised `TypeError`
on every use. This harness **runs** the modules.

| file | what |
|---|---|
| `extronlib_stub.py` | A stand-in `extronlib`, written from the public names in Extron's ControlScript extension stubs; no vendor code, and the extension is not needed. Interfaces record every `Send`/`SendAndWait` instead of opening a port; `Wait` and `Timer` never fire; any unmodelled name is an inert placeholder. |
| `drive.py` | Loads a generated module and Extron's shipped module for the same device, constructs both through the same transport class and model, and calls every `Set` and `Update` both define with the same inputs. Also `--module` for one module on its own. |
| `differential.py` | Runs `drive.py` over finding 14's pairs, one process per pair with a timeout; writes `out/exec_results.json`. |
| `test_exec_harness.py` | The stub, input derivation, synthetic pairs that must be caught (a stripped `@staticmethod`, different bytes, an import failure), and the DSC pair end to end. |

## What a comparison means

The shipped module is the reference. For each input, each side's outcome is
the bytes it sent, whether it discarded the input, and the type of any
exception that escaped. Per command method:

| bucket | meaning |
|---|---|
| `same` | identical outcome |
| `both_reject` | neither sent anything and both refused, differently (one discards, the other lets a `ValueError` escape). Counted, not scored as a difference |
| `gen_raises` | the generated module raised where the shipped one did not refuse: **the bucket to read first** |
| `ship_raises` | the reverse |
| `differ` | different bytes, or one refused what the other accepted |

**Inputs are never invented.** They come from both modules' own method
bodies: the keys of the value maps they look values up in, the literals they
compare with, and the numeric bounds they check (each bound and one either
side), for the value and every qualifier key they read. Both methods of a
command (Set and Update) feed the qualifier candidates. Every Set also gets a
few adversarial values: empty, a space, a quote, `None`, out of range. A
command whose bodies offer nothing gets a small default set.

**Two fairness choices.** Extron's SIS template starts with `EchoDisabled` set
and swallows commands until the device answers its echo handshake. The harness
clears that flag, and `VerboseDisabled`, on both sides, as a device that has
answered would. `SendAndWait` returns `None` to both.

**Not modelled, so not compared:** device replies (nothing is fed to
`ReceiveData`, so match handlers never run) and anything a `Wait` or `Timer`
would do later.

## Reading a difference: source, skew or translation

A difference against the shipped module has three possible causes, and only
one is a translator bug:

- **The package's own script does it.** DSC's generated module sends
  `wANoneLOGO` where the shipped one sends `wA1LOGO`. The `.pkp`'s script has
  the bug, and Extron fixed it by hand in the shipped module (STATUS's
  scorecard). Likewise the `.pkp`'s own qualifier validation raising
  `ValueError` on `''` where the shipped module has no validation at all.
- **Version skew.** `ktek`'s shipped DM8000 module speaks a different protocol
  generation from its package (`1 set gain 1 0` against `set 1 Input_Gain 1 0;`),
  so nearly every command differs. Finding 14's pairing cannot tell them apart;
  that is ROADMAP R12.
- **The translation.** Running it found five classes, none of which any
  static check covered, each now fixed or reported by `pkp2cs`:
  - DSC: `UpdateLogoAvailability` read the GC throttle timer
    `self.lastLogoAvailabilityUpdate`, whose every write the translator drops,
    so each call raised `AttributeError`. The throttle guard is now dropped
    whole, as in Extron's shipped DSC.
  - ktek: GC's `__SetHelper` takes a fifth argument, `queryDisallowTime`, that
    the fixed template did not; 1,143 call sites in 192 of the 314 packages
    would raise `TypeError`. The parameter is carried where calls pass it.
  - ktek: `self.deviceUsername`, set only in GC's dropped `configs[...]`
    parsing, read at login. Reported (`unassigned-self-attribute`); the fix
    needs the package's configuration defaults (ROADMAP R41).
  - nec, yama: methods held as values in a dispatch table built in `__init__`
    (a renamed `_cmd_` method, a deleted `Write<X>` wrapper), so the class
    could not be constructed. References are renamed, and such wrappers kept.
  - DTP3 (in-sample): `self.Send(query, pacing=0.1)`, a GC `BaseDriver`
    option extronlib's `Send` does not take. Dropped, with a residual.

  Two static checks came out of it and now run on every translation:
  `find_unassigned_self_attributes` and `find_call_arity_mismatches`.

## Across finding 14's 314 pairs (2026-09-23)

| | pairs |
|---|---|
| identical outcome on every input | 73 |
| behaviour differs (source bug, version skew or translation, not yet split) | 100 |
| the generated module raises where Extron's does not | 109 |
| the generated module cannot be constructed | 21 |
| Extron's module cannot be driven (non-standard transport class names; one imports GC's `Extron2`) | 8 |
| only Extron's module raises | 3 |

(The rows sum to 314. Two more shipped modules cannot be driven either, but
their generated modules also fail to construct, so they are counted in that
row.) 44,555 inputs ran on both sides; 71.5% gave the
same outcome. In 94 of the 109 pairs the generated module's exception is an
`AttributeError`, and 603 of the 783 command methods failing that way read a
config-sourced attribute: `DeviceID` alone in 444 methods of 36 packages. The
21 unconstructable modules fail the same way, mostly on counts GC reads from
its configuration (`NumberofPlaylists`, `NumberOfAllUsers`). One cause,
ROADMAP R41, accounts for most of what is left.

To separate "the source does it" from "the translation does it" without a
shipped module, the embedded GC script itself would have to run, under a
stand-in for GC's `Extron2.BaseDriver`. That is the natural next step and is
not done.

## Running

```
python -u experiments/exec_harness/test_exec_harness.py
python -u experiments/exec_harness/differential.py                 # all 314 pairs
python -u experiments/exec_harness/differential.py --only extr_17_17677_v1_0_0.pkp
python -u experiments/exec_harness/drive.py --module path/to/module.py
```

Standard library only. `drive.py` patches `time.sleep` and `urllib.request` in
the process it runs in, which is why `differential.py` and the tests give it a
process of its own.
