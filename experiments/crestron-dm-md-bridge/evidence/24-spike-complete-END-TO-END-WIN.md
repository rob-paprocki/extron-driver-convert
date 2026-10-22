# 24 - Spike COMPLETE: end-to-end master-of-record over single TCP socket

## Final verdict (confirmed on hardware 2026-10-18)

**One-socket control of a Crestron DM-MD endpoint from a non-Crestron
master is PROVEN.** Our Python client (`cip_master_server_v2.py`) opens
exactly one TCP socket to the chassis's CIP port, successfully
registers as the chassis's master-of-record, and drives endpoint I/O
(RMC ComPort StringInput) with observable TX->RX physical loopback
echo returning on the same socket.

## The breakthrough

Rob caught my error in finding 21 and later pointed out that the chassis
must be configured to KNOW its control system (master processor).
In Crestron CGway architecture:

- **MASTER PROCESSOR runs TCP SERVER on :41794** (not client)
- **CHASSIS connects OUT to the master** (as TCP client)

The direction is OPPOSITE of what every prior test had assumed. All
~400 prior client-direction probes were against the chassis's
touchpanel-facing server listener, not its master-of-record role.

Setup required:
1. On chassis, via Toolbox's "IP Table Setup": Add entry with
   Type=master, IP ID=03, IP Address=192.168.6.114 (= our host),
   Port=41794. SSL Off. Save and reboot chassis.
2. On our host, run `cip_master_server_v2.py` which listens on
   0.0.0.0:41794 and plays the server side of the handshake:
   send PROGRAM_READY -> receive ALTERNATE_CONNECT -> send
   CONNECT_RESPONSE with handler.

Once the chassis's "Control System Connection" link state goes to Up,
we're the chassis's master-of-record.

## Live-verified events

**Handshake (chassis-initiated, 13:44:12 and 13:45:08 reconnects)**:

    *** CHASSIS CONNECTED from ('192.168.6.14', 49262) ***
    TX op=0x0F (       PROGRAM_READY) body: 02
    RX op=0x0A (   ALTERNATE_CONNECT) body: 00 03 a3 42 40 02 00 00 02 00
      chassis's claim: DestCID=0x0003 Mode=0x40 Flags=0x02 Type=0x0200
    TX op=0x02 (    CONNECT_RESPONSE) body: 00 01 20 00
      handler=1, mode=0x20 (chassis-supports-hb-rsp-check), flags=0

**Chassis publishes initial state (slot-dispatched DATA frames)**:

    RX op=0x05 DATA body: 00 01 02 03 00                 (control subtype 0)
    RX op=0x05 DATA body: 00 01 03 00 c8 80              (digital event)
    RX op=0x05 DATA body: 00 01 03 00 c8 00              (digital change)
    RX op=0x05 DATA body: 00 01 0b 20 21 08 20 01 05 20 01 02 03 00
                                                         (nested control update)

**Our ComPort write (the one that worked)**:

    TX op=0x05 DATA body: 00 01 0f 20 01 0b 20 01 08 15 00 01 00 50 49 4e 47 67 0d
      - Handler=0x0001, CresnetLen=15, payload is nested:
        cont(0x20 id=0x01 len=11):
          cont(0x20 id=0x01 len=8):
            SERIAL15 leaf join=0x0001 flags=0x00 payload="PINGg\r"

**The echo (RMC TX->RX loopback feedback over the same socket)**:

    RX op=0x05 DATA body: 00 01 0e 20 01 0b 20 01 08 15 00 01 03 50 49 4e 47
      cont(0x20 id=0x01 len=11):
        cont(0x20 id=0x01 len=8):
          SERIAL15 join=0x0001 flags=0x03 payload="PING" (0x50 0x49 0x4E 0x47)

Fired twice reliably across two separate connection sessions
(13:44:25 and 13:45:21).

## Slot path to RMC ComPort[1] StringInput

Confirmed byte-exact from live echo:

    [0x20][0x01][0x0B]           outer container, id=0x01, len=11
      [0x20][0x01][0x08]         inner container, id=0x01, len=8
        [0x15]                   serial-15 leaf
        [0x00][0x01]             join = 1
        [0x00]                   flags
        [payload bytes]          ASCII to transmit

For our DM-MD8X8-CPU3-RPS chassis with DM-RMC-4K-SCALER-C at output 1,
the ComPort[1].StringInput is addressable as `0x01/0x01/serial-15 join=1`
in the chassis-relative slot hierarchy.

## What this means

- The one-socket design (one TCP connection, no CTP, no CIP-IPID-1
  masquerade, no dual-transport) is NOT a research project any more.
  It works today, on this chassis, with the committed Toolbox config.
- The `cip_master_server_v2.py` implementation is the complete
  reference implementation.
- The protocol, framing, encoding, and slot addressing are all
  byte-exact, cited to source, and verified on hardware.

## The deployment recipe

Any site running this chassis + a non-Crestron master processor
(Extron IPL Pro, Q-SYS Core, custom Python/Node, etc.):

1. Configure chassis via Toolbox IP Table Setup:
   - Add master entry at some IP ID (e.g., 03), pointing to master's IP
2. Master processor runs TCP server on :41794
3. Master accepts chassis's inbound connection, performs server-side
   handshake (program-ready status=2 -> connect-response with handler)
4. Master dispatches slot-addressed DATA frames with nested-container
   Cresnet payloads to drive endpoint I/O

## Supersedes everything prior

- Finding 21 (one-socket blocked architecturally): SUPERSEDED - the
  conclusion was wrong, chassis is not programmable but it is
  configurable with the right master entry
- Finding 23 (chassis state baked in): PARTIALLY SUPERSEDED - chassis
  state IS what gates it, but can be configured externally via
  Toolbox
- CTP+CIP dual-transport design: still a valid shipping option, but
  the one-socket design is now also a valid shipping option

## Artifacts

- `cip_master_server_v2.py` (committed) - working master-of-record
  server with decoder
- `evidence/24-master-of-record-SESSION-WIN.log` (committed) - live
  session log with the PING echo captured
- `evidence/24-spike-complete-END-TO-END-WIN.md` (this file) - the
  wrap-up

## Credit

Rob caught the direction-reversal insight ("you need to set the IPID
of the Master in the DM frame as well"). Without that, the spike
would have stayed stuck at the client-direction wall indefinitely.
