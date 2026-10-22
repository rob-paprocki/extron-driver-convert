# CIP IPID-addressable device survey

Join maps for the three Crestron device families that register with a control
system over CIP (TCP :41794) by IPID, as declared in Crestron's own SIMPL
device database (`<CRESDB>/Programming/symlib.tio`):

- **IV-SAM-VX2** (Automate VX2 — camera auto-switcher)
- **DM-NVX-35x** (encoder/decoder endpoint, 350/360/363 class)
- **DM-NVX-DIR-ENT / DM-NVX-DIR2** (NVX director — routing orchestrator)

The join maps are the control-system contract: what the device will send to a
master over CIP, and what command joins it accepts. The on-wire format is the
same CGway envelope reverse-engineered in `experiments/crestron-dm-md-bridge/`
(findings 19, 24, 28, 29): `[op:u8][len:u16][body]` with op `0x05 DATA`
carrying nested-container payloads whose leaves are typed join values
(0x00 digital, 0x14 analog, 0x15 serial-15, 0x34 serial-34, 0x16 IR).

## Totals

| Device family | Named joins | Symbols | Primary role |
|---|---|---|---|
| IV-SAM-VX2 | 276 | 9 | Camera auto-switcher |
| DM-NVX-35x | 286 | 11 | AV-over-IP encoder/decoder |
| DM-NVX-DIR-ENT | 6006 | 7 | 1000-endpoint routing matrix |

## IV-SAM-VX2

| Symbol | Joins | Purpose |
|---|---|---|
| `IV-SAM-VX2` (main) | 39 | Device control (wake, autoswitch, output, manual switch) |
| `IV-SAM-VX2 System` | 4 | System-level signals |
| `IV-SAM-VX2 Layouts` | 26 | Layout selection |
| `IV-SAM-VX2 Config Names` | 100 | 100 named config slots (serial feedback) |
| `IV-SAM-VX2 Camera Names` | 1 | Camera-name feedback envelope |
| `IV-SAM-VX2 Scenario Names` | 100 | 100 named scenario slots |
| `IV-SAM-VX2 Advanced Settings` | 6 | Advanced controls |
| `IV-SAM-VX2 Room Configs` | 0 | Empty container (names live in Config Names) |
| `IV-SAM-VX2 Scenarios` | 0 | Empty container (names live in Scenario Names) |

The main symbol has `Wake`, `Sleep`, `Start/Stop_Autoswitch`, `Start/Stop_Output`,
`Toggle_Output`, `Manual_Switch_Camera`, plus 8 directional PTZ joins
(Up/Down/Left/Right and diagonals).

## DM-NVX-35x (encoder/decoder)

| Symbol | Joins | Purpose |
|---|---|---|
| `DM-NVX-35x` (main) | 55 | Device control: Start/Stop, routing (VideoSource/AudioSource analog), AutomaticInputRouting*, LEDs, StreamLocation, DeviceName |
| `(v2) Stream Transmit` | 30 | Encoder-side stream parameters |
| `(v2) Stream Receive` | 17 | Decoder-side stream parameters |
| `(v2) HDMI In 1` | 20 | HDCP/resolution/audio-format feedback |
| `(v2) HDMI In 2` | 20 | Same for input 2 |
| `(v2) HDMI Out` | 58 | Resolution control, HDCP, color space, CEC name/transmit/receive |
| `(v2) USB` | 40 | USB routing + status |
| `(v2) Network` | 32 | Network state + control |
| `(v2) Text Overlay` | 14 | On-screen-text overlay |
| `(v2) Automatic Power Settings` | ~ | Power management |
| `(v2) COM` | 0 | Container only - port TX is out-of-band |
| `(v2) IR` | 0 | Container only - port TX is out-of-band |

**COM and IR are not named-join addressable.** Just like the DM-MD-RMC's
ComPort passthrough (finding 29), per-port I/O rides a different mechanism
inside the same TCP :41794 pipe: nested-container slot-path writes whose
exact format must be reverse-engineered against live hardware. The named-join
envelope above covers streaming, routing, and feedback — not port I/O.

## DM-NVX-DIR-ENT (Director)

| Symbol | Joins | Purpose |
|---|---|---|
| `DM-NVX-DIR-ENT` (main) | 0 | Pure container (hierarchy only) |
| `DM-NVX-DIR-ENT Domains` | 2 | Domain partitioning |
| `DM-NVX-DIR-ENT Global Domain USB` | **2002** | USB fabric routing surface |
| `DM-NVX-DIR-ENT USB Route by Route ID` | 2000 | 1000 numbered USB routes |
| `DM-NVX-DIR-ENT USB Route by Route Name` | 2000 | 1000 named USB routes |

The main symbol is a container; its DeviceCode (19971) links to the IoDevice
with the actual hardware definition. Child symbols carry the operational
join surface. **At ~6000 joins the Director is by far the largest IPID-
addressable surface in this survey.**

Also present: `DM-NVX-DIR2` (newer variant) with same structure, 7 symbols
total but fewer joins declared on this firmware revision.

## Legacy variants (deprecated)

The database also contains deprecated symbol trees for prior revisions:
- `IV-SAM-VX2 (Deprecated)` and 9 children (18298-18308 range)
- `DM-NVX-35x (Deprecated)` with first-generation symbol codes (5180-5192, 5665-5971)
- `DM-XIO-DIR-80 / DIR-ENT (Deprecated)` (6193-7185)

These predate the (v2) and renaming-to-NVX-DIR revisions and are kept for
backward-compatibility with older SIMPL programs. Not surveyed in detail here
but reachable via the same `crestron_symbols.py find` tool.

## How to drive these from a non-Crestron master

Given the DM-MD finding 24 result — the chassis dials out, we accept —
the same pattern applies to each device family here. Each registers as a
CIP peer on IPID X at the master's address:port 41794. From the Extron
side (or Q-Sys, etc.):

1. Reserve an IPID (03 is conventional) in the device's IP Table / peer
   gateway config, pointing at the master's host/port.
2. On the master, run `experiments/crestron-dm-md-bridge/cip_master_server_v2.py`
   (or a device-specific variant). It accepts the inbound connection, replies
   with the CGway handshake, and dispatches named-join writes/reads over the
   established session.
3. Use this survey's TSVs as the catalog: join number + direction + type +
   name are everything needed to encode a leaf write or decode a feedback event.
4. For COM/IR passthrough on NVX, a separate slot-path RE pass is still
   needed (same approach as DM-RMC in finding 29, Phase 3).

## Open questions

- **NVX DIR vs DIR-ENT vs DIR2**: three overlapping product variants. Which
  one(s) are current, and which to prioritize? (Likely DM-NVX-DIR2.)
- **NVX COM/IR slot paths**: need live-chassis probe analogous to DM-MD
  finding 27 to find the inner slot path for COM TX, if any.
- **Director routing writes**: 6000 joins is a lot; which ones actually drive
  real-time route changes vs. configuration-only? Live capture would reveal.
- **Peer-Gateway vs classic CIP**: NVX endpoints are documented as outbound-
  only Peer-Gateway clients via `IpTableV2`. VX2 and Director — same?
  Confirm per device if the master-of-record TCP-server pattern applies.

## Files

- 27 TSVs (one per non-empty symbol surveyed) under this directory.
- The reader is `experiments/dm_md/crestron_symbols.py` (currently
  private-only; see EXCLUDE in `tools/public_sync.py`).


## Crestron Connected Display (and the broader Connected family)

Any display certified Crestron Connected (projectors + flat-panels from
Panasonic, Sony, NEC, LG, Samsung, Epson, Christie, Barco, ...) registers
with a control system over CIP :41794 by IPID. Two coexisting symbol shapes
appear in the device DB:

### Legacy single-symbol form: `RoomView Connected Display`

| Symbol | Joins | Code |
|---|---|---|
| `RoomView Connected Display` | **183** | 2560, 4330 |

One envelope covering the full driver surface: `Power_On/Off`, 15 slots
of `Source_Select_1..15`, `Volume` / `Volume_Fb`, `Image_Mute_On/Off`,
`Color_Level` / `Brightness_Level` / `Contrast_Level` / `Sharpness_Level`
with `_Fb` outputs, `Lamp_Hours_Fb`, `Warming_Up_Progress`,
`Cooling_Down_Progress`, `Temperature`, 15 source-name text slots,
`Projector_Name`, `Room_Name`, `Assigned_To_Name`, `Help_Message`,
`Emergency_Message`.

### Modern modular form: `Crestron Connected Display` + sub-symbols

| Symbol | Joins |
|---|---|
| `Crestron Connected Display` (main) | 0 (container) |
| `Crestron Connected Power` | 4 |
| `Crestron Connected Warm Up/Cool Down` | 4 |
| `Crestron Connected Video` | 0 (container) |
| `Crestron Connected Source` | 24 |
| `Crestron Connected Image Control` | 15 |
| `Crestron Connected Image Configuration` | 21 |
| `Crestron Connected Source Name` | 41 |
| `Crestron Connected Audio` | 9 |
| `Crestron Connected Messaging` | 7 |
| `Crestron Connected Connection Information` | 7 |
| `Crestron Connected Device Information` | 18 |
| `Crestron Connected Consumables` | 0 (container) |
| `Crestron Connected Lamp` | 11 |
| **Total** | **161** |

Same control surface as the legacy form, split across 14 sub-symbols for
cleaner SIMPL authoring. Both forms sit on the same wire protocol:
CIP peer registration on IPID X at the master's host:41794.

### `Crestron Connected AVR` (receiver / zone box)

| Symbol | Joins |
|---|---|
| `Crestron Connected AVR` (main) | 13 |
| `AVR Zone 1..5` | 5 symbols |
| `AVR Tuner 1..5` | 5 symbols |
| `AVR Media Player 1..5` | 5 symbols |

A multi-zone receiver device class with the same IPID peer registration;
not surveyed in sub-symbol detail here but same mechanism.

### Implication

**A single Extron master-of-record .pkp built against the 183-join
RoomView-shape (or 161-join modular shape) can drive any Crestron
Connected display — a very wide third-party ecosystem.**

This is architecturally the same as the DM-MD CPU3 integration (finding 24):
one TCP socket, chassis dials out, named-join writes over the CGway
envelope. The 183/161-join contract is already fully declared here; no
further RE needed before building the driver.

### Updated totals

| Device family | Named joins | Symbols | Primary role |
|---|---|---|---|
| IV-SAM-VX2 | 276 | 9 | Camera auto-switcher |
| DM-NVX-35x | 286 | 11 | AV-over-IP encoder/decoder |
| DM-NVX-DIR-ENT | 6006 | 7 | 1000-endpoint routing matrix |
| **RoomView Connected Display** | **183** | 1 | **Any certified display (legacy)** |
| **Crestron Connected Display** | **161** | 14 | **Any certified display (modern)** |
| Crestron Connected AVR | 13+ | 16 | Multi-zone receiver |
