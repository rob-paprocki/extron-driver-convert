# crestron-dm-md-bridge/

Can a non-Crestron control system run a Crestron DM-MD8X8-CPU3-RPS matrix
switcher and its DM-RMC endpoints, with no Crestron processor in the rack?

The chassis speaks Crestron's CIP peer protocol on TCP 41794, and it dials out
to its control system rather than waiting to be polled. Answer that call as
the control system and routing and endpoint serial ride one socket.

## Where it stands

On the chassis, with a Python master (`cip_master_server_v2.py`) on a PC in
the control system's place:

- routing works, byte for byte (note 28)
- RS-232 out of a DM-RMC works, proven with a TX-to-RX loopback jumper (notes 24, 29)
- IR and relay are stubbed: the chassis gave no feedback on any probe, so
  whether the pins fire needs a meter and an IR scope

`pkp-out/dm_md_master_v0_0_1.pkp` is the Extron driver for this design and
sends the same bytes. It has not yet been loaded on an Extron processor (note
29, "Phase 4").

## Read in this order

1. [`../cip-ipid-survey/WORK-SUMMARY.md`](../cip-ipid-survey/WORK-SUMMARY.md), the whole effort in plain prose
2. [`evidence/24-spike-complete-END-TO-END-WIN.md`](evidence/24-spike-complete-END-TO-END-WIN.md), the handshake and first endpoint serial
3. [`evidence/28-routing-WORKS-at-output-card-slot.md`](evidence/28-routing-WORKS-at-output-card-slot.md), routing
4. [`evidence/29-slot-architecture-resolved.md`](evidence/29-slot-architecture-resolved.md), how the chassis numbers its slots, and what is left

`evidence/` is the lab notebook, notes 01 to 29 with their logs. The status
page calls these findings 24, 28 and 29; they are not the files in
`findings/`. Several early notes are negative results or were corrected by
later ones, so read the four above first.

## Files

| file | what it is |
|---|---|
| `cip_master_server_v2.py` | the working master: listens on 41794, answers the chassis, sends routing and serial |
| `cresnet_cip.py` | builds the nested slot payloads |
| `dm_md_master_driver.py` | the same master as a ControlScript module |
| `build_dm_md_master.py` | builds `pkp-out/dm_md_master_v0_0_1.pkp` |
| `build_dm_md_unified.py`, `dm_md_driver_replacement.py` | the other design: routing over CTP (TCP 41795) plus CIP feedback, built as `pkp-out/dm_md_unified_v0_0_1.pkp` |
| `drivers/` | standalone CTP drivers for ControlScript and Q-SYS. They predate note 24, so their README's claim that endpoint RS-232 cannot work is out of date |
| `JOINMAP.md`, `joins.json` | the chassis join map from Pepperdash Essentials (MIT), which the chassis's built-in program does not follow |
| `cip_proof_of_connect.py`, `cip_master_v1.py` | earlier attempts: posing as the stock XPanel, and connecting the wrong way round |
| `PLAN.md`, `PROTOCOL.md` | the plan as it stood at the start (2026-10-07 to 10-09) |

Re-running anything needs the chassis. Rebuilding the `.pkp` files needs the
DTP3 CP 42 donor package, which is vendor material and not in the repo.
