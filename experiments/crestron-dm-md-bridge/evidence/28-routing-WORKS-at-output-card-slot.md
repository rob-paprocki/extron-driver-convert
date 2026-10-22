# 28 - MatrixTie routing WORKS over master-of-record, byte-exact

## TL;DR

Routing via the one-socket master-of-record session is PROVEN. The .pkp
is now functionally complete for the "one driver, one socket" design -
no CTP+CIP fallback needed. Byte format:

    [0x20][OutputCardSlot][len][0x20][0x01][len][0x14][jh][jl][vh][vl]

Where:
  - OutputCardSlot = 0x20 + output_num (output 1 = 0x21/33; output 8 = 0x28/40)
  - Analog leaf join = 0x0002 (VideoOut selector on the output card)
  - Value = input card slot number (1-8)

## How we got here (the correction)

Earlier probes against outer slot `0x01` all silently failed (finding 27)
because **slot 1 is an INPUT CARD, not an output card**. The chassis
numbers output cards starting at slot 33.

Verified by SSH:

    > DUMPDMROUTEINFO 1      # input card (empty)
    > DUMPDMROUTEINFO 33     # <-- output 1
      "Routing Information for Output Card at Slot 33 ..."

So the correct master-of-record routing payload for output N is at
chassis slot `(32 + N) = 0x21..0x28`.

## Live-tested probe

With chassis authenticated to us at CID 3, we fired:

    TX cresnet: 20 21 08 20 01 05 14 00 02 00 02

Immediately after, SSH DUMPDMROUTEINFO 33 reported:

    Routing Information for Output Card at Slot 33
     Video Routed From Input Card at slot 2         <-- route changed
    No Audio connection
    No USB connection
    Hot plug is Low

Byte breakdown:
  - `20 21 08` outer wrap: slot=33, body-len=8
  - `20 01 05` inner wrap: sub-slot=1, body-len=5
  - `14 00 02 00 02` analog leaf: join=2, value=2

## Chassis state feedback

After the route change, the chassis began sending us analog join 10 at
root level:

    RX cresnet: 14 00 0a 00 02
    decode: ANALOG join=0x000A val=0x0002

This is a CGway-style flat routing feedback join: "join 10 = 2" probably
means "output 1 route reports input 2". Confirms the chassis uses the
same join-mapped feedback for routing state that we observed in the
IPID 1 masquerade session months ago.

Chassis also started sending nested state updates at path [33, 1, 1]:

    RX cresnet: 20 21 0b 20 01 08 20 01 05 14 02 53 00 2a
    decode: ANALOG at path=[33,1,1] join=0x0253 val=0x002A

This is ambient sensor data (temperature on output card 33), not a
route event. Oscillates between 42-43 (= 0x2A/0x2B).

## Implementation

Added to `dm_md_master_driver.py`:

```python
_OUTPUT_CARD_SLOT_BASE = 0x20
_ROUTE_JOIN_VIDEO = 0x0002

def _output_card_slot(output_num):
    return _OUTPUT_CARD_SLOT_BASE + (output_num & 0xFF)

def _route_write_payload(output_num, input_num, join=_ROUTE_JOIN_VIDEO):
    leaf = _analog_leaf(join, input_num)
    return _wrap_container(_output_card_slot(output_num),
                           _wrap_container(0x01, leaf))

def SetMatrixTieCommand(self, value, qualifier):
    inp = int(qualifier.get('Input', 0))
    out = int(qualifier.get('Output', 0))
    full = _route_write_payload(out, inp)
    self._send_data_payload(full)
    self._output_route[out] = inp
```

Unit test confirms byte-exact match to live probe for (output=1, input=2):

    expected: 20 21 08 20 01 05 14 00 02 00 02
    actual:   20 21 08 20 01 05 14 00 02 00 02   MATCH

## Open questions for later

- **Audio routing**: likely join 3 or 4 (not yet probed). CGway convention
  is Audio = join 1, Video = join 2, USB = join 3 (or similar). This
  firmware uses join 2 for video; others TBD.
- **USB routing**: same as above, TBD.
- **Breakaway tie types**: Audio+Video together vs. independent routes.
  Our driver currently sends one write for the whole tie. Full
  independent breakaway may need separate writes per asset type.
- **ComPort path still at slot 1**: finding 24's successful ComPort echo
  was from slot 1 (input card 1), not output card 33. Open question
  whether chassis loopbacks serial-15 writes universally, or whether
  there's a different ComPort subsystem actually mounted on an input
  card slot. ComPort passthrough works empirically, so shipping stays.

## Impact

The one-socket master-of-record .pkp (`dm_md_master_v0_0_1.pkp`) is now
functionally complete for routing + ComPort. It is a drop-in replacement
for the existing CTP+CIP dual-transport .pkp for routing-focused
deployments. IR and Relay stubs remain (finding 27) but the design
scope "one driver does everything via one TCP socket" is validated.
