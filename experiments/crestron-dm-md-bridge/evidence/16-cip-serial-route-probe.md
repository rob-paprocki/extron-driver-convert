# 16 - CIP serial-input text-command route probe: NEGATIVE

## Hypothesis

Earlier work showed that writing to serial join `S4000` on this chassis's
OEM CIP program reliably bumps counter `S4221`. Hypothesis: the chassis's
command dispatcher accepts routing text commands (`SETVIDEOROUTE`,
`SETAVROUTE`, etc.) via CIP serial-input writes, mirroring what SSH / CTP
accepts, letting a single CIP connection carry both commands and feedback.

If true, this would collapse the unified driver's two sockets (CTP for
commands + CIP for feedback) down to one - appealing because this unit's
firmware mode **refuses `AUTHentication OFF`**, so the CTP path has to run
authenticated and holding two authenticated sockets isn't the prettiest.

## Method

With chassis quiescent (all outputs 33-40 reported "No Video / Audio / USB
connection, Hot plug is Low" via `DUMPDMROUTEINFO`):

1. Opened CIP as IPID 1, completed handshake, pumped initial cache
   (320 joins observed, including `S4221 = '43'`).
2. Wrote seven CIP serial-value payloads to candidate dispatcher joins
   (S4000, S4001, S4003, S4100) carrying text route commands.
3. After each write, polled `S4221` for a bump AND polled
   `DUMPDMROUTEINFO 33` / `101` via SSH to check actual chassis state.

## Result: NEGATIVE on all 7 probes

| # | Target | Payload | Counter bump | Route changed |
|---|---|---|---|---|
| 1 | `S4000` | `SETVIDEOROUTE 1 33\r`  | no  | **no** |
| 2 | `S4000` | `SETVIDEOROUTE 1 101\r` | +14 | **no** |
| 3 | `S4000` | `SETAVROUTE 1 33\r`     | no  | **no** |
| 4 | `S4000` | `SETAVROUTE 1 101\r`    | +7  | **no** |
| 5 | `S4001` | `SETAVROUTE 1 33\r`     | +14 | **no** |
| 6 | `S4003` | `SETAVROUTE 1 33\r`     | no  | **no** |
| 7 | `S4100` | `SETAVROUTE 1 33\r`     | +14 | **no** |

See `16-cip-serial-route-probe.log` for the raw lines.

## What the counter actually tracks

The S4221 bump pattern (0 / 14 / 0 / 7 / 14 / 0 / 14) rules out
"command-dispatch success" semantics - a dispatcher counter wouldn't bump
without a corresponding route change, and the same payload to the same
join sometimes bumps and sometimes doesn't. The counter is almost
certainly a lower-level byte / packet / parse-attempt counter inside the
OEM program's serial-input handler, published to CIP for diagnostic use -
not a command-complete signal.

## What this closes

Writing text route commands to CIP serial-input joins **does not** drive
routing on this chassis's stock OEM program. The chassis receives the
writes (counter proves it), but routes nothing because no join we tried
is wired to the chassis's command dispatcher.

## What's still open (not pursued)

Routing from CIP would require either:

1. **Smart-object events (`0x38` / `0x39` marker).** The chassis's own
   front panel and XPanel drive routing by writing SO events (SO 0x05
   input picker + SO 0x06 output picker, inferred from the initial-cache
   dump). Reverse-engineering those SO payload byte-level formats would
   unlock pure-CIP routing. Not in any OSS CIP implementation; days-to-
   weeks of work.
2. **Pepperdash-style analog joins (A101..A108).** Would require loading
   a user SIMPL program on the chassis that publishes those joins. The
   OEM default program doesn't; this is finding 10.

## Impact on the design

- **CTP for commands + CIP for feedback stands as the committed design.**
  The unified driver (`dm_md_driver_replacement.py` + .pkp) carries both
  transports in parallel, inside a single Extron package.
- CTP :41795 is reachable on this unit **only authenticated**: this
  firmware mode **refuses `AUTHentication OFF`** (previously established,
  reaffirmed here). The unified driver authenticates admin / blank at
  session open.
- Collapsing to a single CIP socket is a research project (smart-object
  RE), not a tactical rewrite. Not pursued now.

## Artifacts

- `evidence/16-cip-serial-route-probe.log` - probe lines excerpted from
  the raw task output. Original full task output was 665 lines; this file
  is the 33 probe-relevant lines.
