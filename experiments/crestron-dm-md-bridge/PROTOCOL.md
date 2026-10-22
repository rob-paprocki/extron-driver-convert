# Protocol - Extron ControlScript to Crestron DM-MD-CPU3 over CIP

## Transport
- TCP on port 41794 on the chassis (172.16.0.104). Plain, no SSL.
- Persistent. Keepalive 0D 00 02 00 00 every 15 s after handshake.
- Big-endian byte order throughout.

## Frame format
```
offset  bytes            meaning
0       1                type / opcode
1-2     u16 big-endian   payload length  (payload only, no header)
3+      payload          content depends on opcode
```

## Handshake (verified from four OSS implementations)

```
chassis to client   0F 00 01 02                     program-ready / accept
client  to chassis  01 00 0B 00 00 00 00 00         registration (14 bytes)
                    <ipid> 40 FF FF F1 01           (ipid at byte offset 8)
chassis to client   02 00 04 00 00 00 1F            registration SUCCESS
                    02 00 03 FF FF 02               registration err (unknown IPID)
client  to chassis  05 00 05 00 00 02 03 00         update request
chassis to client   <0x05 and 0x12 frames...>       initial signal cache
chassis to client   05 00 05 00 00 02 03 1C         end-of-query
client  to chassis  05 00 05 00 00 02 03 1D         ack
client  to chassis  0D 00 02 00 00                  heartbeat, every 15 s
```

## Join opcodes

### Digital (press/release)
```
type  len     subtype  LL HH   wire layout
0x05  00 06   00       LL HH   latched digital
0x05  00 06   27       LL HH   button-style (auto-release)
```
Where:
- (LL, HH) encodes (join - 1) byte-swapped (low byte first).
- Bit 7 of HH is the inverted-active flag: 0 = pressed/high, 1 = released/low.
- Pack:   swapped = ((join-1) and 0xFF) shift-left 8  OR  ((join-1) shift-right 8)
          if value == 0: OR 0x80.
- Unpack: join  = (((HH and 0x7F) shift-left 8) OR LL) + 1
          state = ((HH and 0x80) shift-right 7) XOR 1

### Analog (set)
```
type  len     subtype  JH JL VH VL
0x05  00 08   14       JH JL VH VL
```
Plain big-endian: JH:JL = (join - 1), VH:VL = value (0..65535).

### Serial (set)
```
type  len     00 00 00 IL  34 JH JL FF  <text bytes>
0x12  LH LL   outer length is strlen+8 (LH:LL big-endian); IL inner len = strlen+4
```
- 0x34 is the serial marker, JH:JL = (join - 1), FF is a flags byte
  (bit 0 end-of-message, bit 1 start-of-message, bits 2..4 encoding).
- Text is raw bytes (not NUL-terminated; length comes from the frame).

## Driver to chassis logical commands

Routing uses **analog joins** (not digital):

| Command            | Analog join       | Value              |
|--------------------|-------------------|--------------------|
| ROUTE_V in,out     | A(100 + out)      | in (0 = break)     |
| ROUTE_A in,out     | A(300 + out)      | in                 |
| ROUTE_USB in,out   | A(500 + out)      | in                 |
| ROUTE_AV in,out    | A(100+out) and A(300+out) | in         |
| BREAK out          | A(100+out)=0 and A(300+out)=0 | -      |

Breakaway control uses digital joins:
- D4 EnableAudioBreakaway - set 1 to allow independent audio routing.
- D5 EnableUsbBreakaway - set 1 to allow independent USB routing.

(Values given are from the Pepperdash EISC map. The OEM default program own
joins may remap these - confirm via pktmon capture of the stock XPanel; see
PLAN.md Phase 2.)

## Chassis to driver feedback

Interesting incoming joins (not exhaustive):

| Join | Meaning |
|------|---------|
| D11            | Chassis online |
| D101..D108     | Per-input VideoSyncStatus |
| D501..D508     | Per-input endpoint online |
| D701..D708     | Per-output endpoint online |
| A101..A108     | Current routed input per output (echoed) |
| S1             | Chassis friendly name |
| S101..S108     | Per-input friendly names |
| S301..S308     | Per-output friendly names |

The driver parses incoming 0x05 and 0x12 frames the same way the state
machine unpacks digital/analog/serial, caches the latest value per join
number, and surfaces whatever subset the GCP widgets need.
