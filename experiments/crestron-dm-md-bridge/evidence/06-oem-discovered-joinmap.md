# 06 — OEM default program discovered join map

**Date:** 2026-10-09
**Chassis:** DM-MD8X8-CPU3-RPS, firmware `v1.8001.5769.27432 (Oct 18 2024)`, serial `#8D52016F`, MAC `@E-00107fda192a`.
**IP at capture time:** `192.168.6.14` (chassis's **programmed** IP in SIMPL is still `172.16.0.104` — see `S3002`).
**Capture:** `cip_proof_of_connect.py --host 192.168.6.14 --ipid 1 --hold 10`
**Raw dump:** `05-cip-signal-cache-dump.txt`

## Headline

**The OEM default program's join numbering is NOT the Pepperdash scheme.** Pepperdash's `DmMd8x8Cpu3rps` EISC bridge put video routes on `A101..A108`, audio on `A301..A308`, USB on `A501..A508`. The OEM default program on this chassis puts information on `S900..S979` / `S1200..S1295` / `S3xxx` / `S4xxx` / `S5xxx` / `S7xxx` with digitals clustered around `D204/206`, `D690..D1020`, `D1200..D1320`, `D1800`, `D3xxx`, `D4xxx`, and only 17 analogs — none of which are `A101..A108`. The Pepperdash join reference stays in the repo as a secondary target (an EISC-peer path if a user installs the Pepperdash SIMPL template), but **the primary CIP masquerade target has to key off this discovered map**.

## Signal-cache summary

| Category | Count | Notes |
|---|---|---|
| Digitals (`D`) | 74 | All reported as `=1` (ON) in initial state |
| Analogs (`A`) | 17 | Mostly network octets + button color states |
| Serials (`S`) | 229 | Rich; carries most of the structural info |

End-of-query marker (`0x1C`) was received, confirming the chassis finished its initial cache push. Handshake sequence verified:

```
RX  0F 00 01 02                                      program-ready
TX  01 00 0B 00 00 00 00 00 01 40 FF FF F1 01       register IPID 0x01
RX  02 00 03 00 00 00 1F                             REG_SUCCESS
TX  05 00 05 00 00 02 03 00                          UPDATE_REQUEST
... stream of 0x05 / 0x12 frames ...
RX  05 00 05 00 00 02 03 1C                          end-of-query
TX  05 00 05 00 00 02 03 1D                          ACK end-of-query
TX  0D 00 02 00 00                                   heartbeat
```

## Structural clusters

### Inputs — `S900..S979`, stride 10, 8 rows (one per input)

Columns per row (offsets within the 10-join stride):

| Offset | Meaning | Example row (input 1) |
|---|---|---|
| 0 | input number | `S900 = '1'` |
| 1 | friendly name + card type | `S901 = 'Input 1 : DMC-4KZ-HD'` |
| 2–5 | reserved placeholders | `'-'` |
| 6 | HDCP state? | `'Inactive'` |
| 7 | reserved | `'-'` |
| 9 | sync state | `'Offline'` |

Discovered input cards (OEM-detected, cards 1–4 are the first set of DMC-4KZ-HD inputs; 6 & 8 are DMC-4KZ-C; 5 & 7 slots are physically empty — matches the grey color on `S5008/S5009/S5012/S5013`).

### Outputs — `S1200..S1295`, stride 12, 8 rows

Columns per row (offsets within 12-join stride):

| Offset | Meaning | Example row (output 1) |
|---|---|---|
| 0 | output number | `S1200 = '1'` |
| 1 | friendly name | `S1201 = 'Output 1'` |
| 2 | card type | `S1202 = 'DMC-4KZ-CO-HD'` |
| 3–5 | placeholders | `'-'` |
| 6 | HDCP state | `'Inactive'` |
| 7 | reserved | `'-'` |
| 9 | sync state | `'Offline'` |
| 11 | FW version of connected endpoint | `'1.3991.00099'` |

Cards 1–6 are `DMC-4KZ-CO-HD` output cards; 7–8 are `DMC-4KZ-HDO`.

### System info — `S3000..S3023`

| Join | Current value | Meaning |
|---|---|---|
| `S3000` | `'ON'` | Power state |
| `S3001` | `'DM8X8-DA192A'` | SIMPL-assigned chassis label |
| `S3002` | `'172.16.0.104'` | **programmed** IP (stale — chassis moved to 192.168.6.14) |
| `S3003` | `'255.255.0.0'` | subnet |
| `S3004` | `'0.0.0.0'` | gateway |
| `S3006` | `'00:10:7f:da:19:2a'` | MAC |
| `S3007` | `'DM8X8-DA192A'` | hostname |
| `S3022` | `'Up'` | NIC status |
| `S3023` | `'Apply Settings'` | button label |

### Endpoint firmware roll — `S4010..S4019`

Live inventory of remote endpoints (what's actually attached over the DM cables):

| Join | Content |
|---|---|
| `S4010` | `107 169.254.0.40 DMC-4KZ-HDO MICRO1 1.3991.27` |
| `S4011` | `107 169.254.0.40 DMC-4KZ-HDO MICRO2 1.3991.27` |
| `S4012` | `107 169.254.0.40 DMC-4KZ-HDO CORE 1.60` |
| `S4013` | `6.1  169.254.0.71 DM-TX-4K-100-C-1G App 1.2761.3 / 1.3209.23 (upgrade pending)` |
| `S4014` | `8.1  169.254.0.73 DM-TX-201-C App 1.2911.117` |
| `S4015` | `8.1  169.254.0.73 DM-TX-201-C FPGA 48` |
| `S4016` | `101.1 169.254.1.66 DM-RMC-4K-SCALER-C App 1.2911.103` |
| `S4017` | `101.1 169.254.1.66 DM-RMC-4K-SCALER-C CORE 3.30.1.169` |
| `S4019` | `'Command completed.'` |

### Front-panel label state — `S5000..S5015` (inputs), `S7000..S7031` (outputs)

HTML-colored labels drive the matrix picker on the physical front panel + XPanel. White = present, grey = absent/offline. Confirms **inputs 5 and 7 are empty slots**.

```
S5008 = '<FONT color="#666666">5</FONT'      ← input 5 empty
S5012 = '<FONT color="#666666">7</FONT'      ← input 7 empty
```

### Routing / command dispatch (partial)

| Join | Value | Likely meaning |
|---|---|---|
| `S4002` | `'Idle'` | command-queue state |
| `S4019` | `'Command completed.'` | last-command result |
| `S4101` | `'1'` | ??? (not yet mapped to a specific route cell) |
| `S4221` | `'6'` | ??? (same) |
| `D4001`, `D4007`, `D4009`, `D4010`, `D4122`, `D4401` | `=1` | likely action-trigger latches, needs behavioural capture |

The **actual video-route and audio-route selection joins have not been proven** from this snapshot. Analog initial-state is sparse by design: CIP initial-cache only publishes non-zero values, and if no XPanel is actively driving routes, the route-feedback analogs stay at 0 and don't appear.

**Phase 2 action:** drive one route from the chassis via a console `DMROUTE` command (we have SSH-admin), re-capture, diff. That delta is the ground-truth routing join. Keep a second long-hold capture open while routing, so we can also catch digital edge events.

## Access caveat

**IPID 1 is the only `Gway`-type slot in the live IP table.** `ADDS` adds a `CGway` (client gateway, chassis-to-chassis), which the chassis correctly refuses to accept an XPanel registration against (`REGISTER_RESULT = ff ff 02 = IPID not defined`). `ADDPEER` would add a Master-list Gway but says *"Master List set. Restart program to take effect"* — a restart would disrupt the OEM program and is not acceptable for a non-destructive probe.

**Working path:** register as IPID 1 while the real XPanel is not connected. The IP table shows IPID 1 is bound to `127.0.0.1` (loopback placeholder, no live XPanel). Our registration succeeds and the chassis treats us as the XPanel. If a human XPanel reconnects during our session, the chassis will drop one of the two — behavior to be confirmed in Phase 2.

## Impact on PLAN.md

Phase 1 (CIP baseline bring-up) is **done** for the read side: handshake, registration, initial-state dump, heartbeat, end-of-query, clean shutdown — all exercised end-to-end against the live chassis.

Phase 1 **still open for the write side:** we have not yet proven that a route command (digital press or serial command on `S4000`-cluster) actually changes a route. That is Phase 2's experiment.
