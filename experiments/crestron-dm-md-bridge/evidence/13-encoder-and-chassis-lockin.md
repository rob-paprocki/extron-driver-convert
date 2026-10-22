# 13 — L3 encoder working against fixtures; DM-RMC-in-chassis is firmware-locked

**Date:** 2026-10-11

## L3 encoder (`cresnet_cip.py`) — working

The nested-container Cresnet-over-CIP encoder from the research in evidence/12 is now implemented and passes all fixtures:

```
[selftest] docblock vector OK
[selftest] digital leaf OK
[selftest] serial leaf OK
[selftest] DM-RMC-4K-SCALER-C ComPort TX full-stack OK
[selftest] DM-RMC-4K-SCALER-C Relay1 close full-stack OK
```

The canonical fixture is the Crestron docblock example at `SimplSharpPro_exe.cs:114730-114772`:

```
MySwampE4.Zones[2].Bass.UShortValue = 25
  HierarchyList = [3, 4],  Device.ID = 2,  join = 7,  value = 25
  → 03 0B 20  04 08 20  02 05 14 00 07 00 19
```

Encoder covers:

- Container type auto-selection (`0x20` / `0x35` / `0x41` / `0x42`) with the correct deepest-level pattern: **the innermost level has NO container-type byte — the leaf's own type byte (`0x14` analog / `0x15` serial / `0x03` digital-control / `0x16` IR) serves as the type.** Only outer wrappers add a `0x20`.
- Leaf encoders: `encode_digital` (long-digital `0x03 0x00` for press/release), `encode_analog` (long-analog `0x14`), `encode_serial_15` (short serial), `encode_ir_start_by_uid` (IR 0x16 subtype 0x07).
- DM-RMC-4K-SCALER-C-specific join map (`DmRmc4kScalerCMap`): the two slots that matter are `SLOT_COM=1` (holding `Rmc200CCOMSlot` with a single ComPort at port index 0, TX serial join = 0), `SLOT_IR=2` (holding `Rmc200CIRSlot` with IR ports 0 and 1). Relays attach to the parent InternalDevice at magic cue numbers 110 / 160 (wire form 109 / 159).
- Full-stack frame builders: `encode_com_tx(bytes)`, `encode_relay_close(1|2)`, `encode_relay_open(1|2)`, `encode_ir_press(port, driver_crc, func_crc)`.

Verified sample DM-RMC-4K-SCALER-C ComPort TX frame for IPID `0x50`, text `"TEST\r"`:

```
50 0F 20 01 0C 20 00 09 15 00 00 00 54 45 53 54 0D
│  │  │  │  │  │  │  │  │  └── join hi/lo = 0 ──┘
│  │  │  │  │  │  │  │  │   serial leaf type 0x15, 'TEST\r'
│  │  │  │  │  │  │  │  flag byte (ASCII + single-string)
│  │  │  │  │  │  │  len=9 (leaf bytes)
│  │  │  │  │  │  device_id = 0 (port index)
│  │  │  │  │  (no container-type byte at the deepest level)
│  │  │  │  SLOT_COM container-type 0x20
│  │  │  len=12 (inside slot container)
│  │  SLOT_COM = 1
│  IPID container-type 0x20
│  len=15 (inside IPID container)
IPID = 0x50
```

The outer CIP transport layer still needs the sign-on handshake, so this encoder is a *library* — not a complete emulator — until the handshake is pinned by one pcap.

## Why `STOPPROGram` can't give us the sign-on pcap on this chassis

Attempted the "stop the OEM program → our ADDMaster takes effect → capture signon" path from evidence/12's experiment plan. **Blocked at the premise**:

```
> PROGREGister
No programs are registered
```

**This chassis has zero user SIMPL programs loaded.** What we've been calling the "OEM default program" is actually chassis firmware — the behavior comes from the CPU3's built-in DM-switcher application baked into the firmware image, not a user-space SIMPL# Pro program on a slot. `STOPPROGRAM -P:ALL` has nothing to stop.

**Architectural implication, now with evidence:** on this DM-MD8X8-CPU3-RPS, the DM-RMC's master relationship is enforced by firmware code that runs below any user-visible program slot. We cannot replace it via `STOPPROGRAM`, `PROGREGISTER`, or any other program-slot command. The ONLY way to redirect would be either:

1. **Replace the chassis firmware** — not viable (signed, not available).
2. **Load a user SIMPL# Pro program** that re-instantiates the DM endpoint objects with external-gateway constructors. The chassis's SIMPL# Pro program would then present ITSELF as the master to the RMC (and all other endpoints), with a secondary CIP connection to a non-Crestron master like an Extron. **This IS "two processors on paper" — the chassis is running a user-authored program.** Even if the hardware is one box, the architecture is two codebases.
3. **Hardware swap** — replace DM-RMC with Extron DTP3/NAV or Q-Sys I-O Flex receiver at each display.

## Live experiments corroborating the lock-in

- `ADDMaster 3 192.168.6.114 0 41794` on the RMC's console (via `:50322`) accepted the entry and showed it in `IPTABLE` with `Status: ONLINE`.
- After `REBOOT`, the RMC's IP table reverted to the chassis entry `183 Gway 169.254.0.1`. **Our stub listener on `0.0.0.0:41794` never received a connection.**
- Repeated with `AUTOdiscovery OFF` first — same result. The chassis's push happens regardless of the RMC's auto-discovery setting.
- No TCP SYN from the RMC's NAT'd IP (`192.168.6.14` source after chassis egress NAT) ever hit port 41794 on the Windows box after multiple reboots. The RMC never attempted to reach our stub.
- Repeated with REMMaster of the chassis entry attempted first — the RMC refused (`error code -1`).

## Workable deliverables as of this entry

- `experiments/crestron-dm-md-bridge/cresnet_cip.py` — the L3 encoder library, passing all fixtures. ~380 LoC. Portable to Extron ControlScript via `urllib.request` or a raw-TCP wrapper; portable to Q-Sys Lua via `TcpSocket` + the same encoding.
- Hard conclusion on this chassis's DM-RMC: non-redirectable without a chassis-side SIMPL program.
- Architecture still intact for **standalone-mode CIP devices** (`IvSamVx2`, `DIN-CEN-CN2`, standalone-ctor DM-RMC, keypads, lighting-over-Ethernet). The L3 encoder works for all of them. Only the sign-on handshake remains to be captured against any one standalone device.
