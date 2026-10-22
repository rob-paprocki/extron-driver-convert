# 29 - Chassis slot architecture resolved; ComPort via physical loopback

## TL;DR

Chassis has **two subsystems with different slot schemes**:

  - **Switcher matrix** at slots `0x21..0x28` (33-40): routing writes go
    here, one slot per output. Verified live (finding 28).

  - **Endpoint cluster** at slot `0x01` with second-level index 1-8:
    ComPort writes to RMC on output 1 at `[0x20][0x01][0x20][0x01]`.
    Verified live via Rob's physical TX<->RX jumper on the RMC output 1
    screw terminals: writing serial-15 at this path produces an echo
    of our bytes back as SERIAL15 feedback, through the actual RS-232
    pin + loopback jumper (NOT chassis-internal echo).

Phase 2 driver uses both paths correctly.

## Open: Relay + IR

Attempted at both slot 33 (output card) and slot 1 (endpoint cluster)
across many leaf-type + join variants in findings 27 and 29. Chassis
is silent on all of them.

The RMC-4K-SCALER-C has one RS-232, one IR emitter, one relay. All
three subsystems should be addressed under the endpoint cluster at
`[0x01, 0x01]` for output 1's RMC - likely with different leaf types
(serial-15 proven for RS-232; digital 0x00 and IR 0x16 untested for
their effect on the physical pins because we have no multimeter/IR
scope on the output).

**It's possible our Relay/IR writes DO fire the physical pins and the
chassis simply doesn't send a feedback event for them** - serial-15
only echoed back because of Rob's physical TX<->RX jumper, not because
the chassis generates serial feedback on its own.

## Live-probe results

With chassis as master-of-record at CID 3:

    [P1] serial-15 at [0x21, 0x01]  (output card slot 33)
         TX: 20 21 0e 20 01 0b 15 00 01 00 50 49 4e 47 34 32 0d
         chassis response: SILENT - no echo, no error
         Conclusion: writes to slot 33 serial-15 are ignored

    [P2] serial-15 at [0x01, 0x01]  (endpoint cluster slot 1)
         TX: 20 01 0e 20 01 0b 15 00 01 00 53 4c 4f 54 31 41 0d
         chassis response:
           SERIAL15 path=[1,1] join=0x0001 flags=0x03 b'SLOT1A\r'
         Conclusion: writes to slot 1 serial-15 reach the RMC's physical
         TX pin AND the physical loopback captures the echo back. This
         IS the real ComPort passthrough.

    [P3] digital 0x00 at [0x21, 0x01]: silent (all 8 variants)
    [P4] IR 0x16 at [0x21, 0x01]:     silent (all 6 variants)

Prior finding 27 similarly got silence at [0x01, 0x01] for digital/IR
with joins 1-5, with slot-1-input-card assumption. Combined evidence:
chassis simply doesn't send feedback for digital/IR writes regardless
of path. Verification would require physical multimeter on relay
contacts or IR receiver on emitter.

## Verifying Relay/IR definitively

Best path: deploy the .pkp into an Extron processor's GCP project with
a touch panel UI, press RelayClose and IRPulse buttons, physically
observe (multimeter clicks, IR scope). This IS Phase 4; the
alternative of continuing to probe-with-no-feedback has saturated.

Also pending for Phase 4:

  - Verify ComPort passthrough with an actual projector drive
    (replace loopback jumper with projector cable, send real
    protocol like PJLink or NEC, watch the projector respond)
  - Confirm routing responds to feedback: issue MatrixTieCommand,
    observe UpdateOutputTieStatus returns the right input
  - Confirm driver loads cleanly on IPL Pro / target hardware

## Slot architecture summary (for driver author reference)

Routing writes:
    [0x20][0x20 + output_num][len]       outer: switcher matrix output
    [0x20][0x01][len]                    inner: fixed 0x01
    [0x14][jh][jl][vh][vl]               analog leaf: join=2 for video,
                                         value = input card slot

Endpoint I/O (RMC):
    [0x20][0x01][len]                    outer: endpoint cluster
    [0x20][output_num][len]              inner: output index 1-8
    [leaf]                               leaf type = subsystem:
                                         - 0x15 (serial-15): RS-232
                                         - 0x00 (digital):    Relay? (unverified)
                                         - 0x16 (IR):         IR?    (unverified)

NB: for output 1, the inner slot is 0x01 which coincidentally equals
the outer. So the finding 24 path `[0x20][0x01][0x20][0x01]` is
genuinely two separate address components, not a doubled-up slot.
Writes to output 2 would be `[0x20][0x01][0x20][0x02]`.

Current driver's _rmc_output_container implementation already correct:

    def _rmc_output_container(output_slot, inner_body):
        return _wrap_container(0x01,                   # endpoint cluster
                               _wrap_container(output_slot, inner_body))

Wait - current implementation has it REVERSED. Let me re-check:
    inner_wrap = _wrap_container(0x01, inner_body)   # claims RMC sub-slot
    return _wrap_container(output_slot & 0xFF, inner_wrap)

This produces [0x20][output_slot][0x20][0x01][leaf]. For output 1 that's
[0x20][0x01][0x20][0x01] which happens to be correct ONLY because
output_slot=1 coincidentally equals the endpoint-cluster slot. For
output 2 it would produce [0x20][0x02][0x20][0x01] which is wrong -
should be [0x20][0x01][0x20][0x02].

** THIS IS A BUG for outputs 2-8. ** Fixing in next commit.
