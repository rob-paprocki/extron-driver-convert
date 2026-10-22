# 27 - Phase 3: IR + Relay slot path discovery - NEGATIVE on simple hypothesis

## Summary

Phase 3 of the one-socket master-of-record .pkp build: discover slot paths
and leaf encodings for the DM-RMC-4K-SCALER-C's **IR port** and **Relay**
outputs, analogous to the ComPort TX path confirmed in finding 24.

**Result**: NEGATIVE on the simple hypothesis. 16 probe variants
(8 Relay digital-leaf + 8 IR 0x16-leaf) sent to the chassis produced
no visible feedback. Only ambient analog sensor oscillation (`join
0x0253 at path=[33,1,1]` jittering between 42 and 43).

## Probes fired

With chassis in authenticated master-of-record session as our master
at CID 3, we sent via the same nested-container shape that worked for
ComPort (`[0x20][output_slot][len][0x20][0x01][len][leaf]`):

**Relay** (hypothesis: digital leaf type 0x00):

    [0x20][0x01][0x06][0x20][0x01][0x03][0x00][0x80][join]   # CLOSE (join | 0x8000)
    [0x20][0x01][0x06][0x20][0x01][0x03][0x00][0x00][join]   # OPEN
    for join in [1, 2, 3, 5], CLOSE and OPEN each
    = 8 probes

**IR** (hypothesis: leaf type 0x16, two subfield-layout guesses):

    v1 `[0x20][...][0x16][join_hi][join_lo][data_bytes]`
       for join 1-2, data [0x00], [0x01 0x02 0x03], [0x11 0x22 0x33 0x44 0x55]
       = 6 probes
    v2 `[0x20][...][0x16][join_hi][join_lo][flags][data]`
       for join 1-2, flags=0, data=[0x01 0x02 0x03 0x04]
       = 2 probes

## Observed chassis responses during probe window

Only one unique chassis event over 30+ seconds:

    ANALOG path=[33, 1, 1] join=0x0253 val=0x002A  (= 42)
    ANALOG path=[33, 1, 1] join=0x0253 val=0x002B  (= 43)

...repeating 42 <-> 43 at roughly 1-2 Hz. This is clearly an **ambient
analog sensor** (temperature, fan speed, or similar diagnostic), not a
response to our probes. (Confirmed by comparing to the baseline value
pre-probe; it was already oscillating in the same range.)

Zero DIGITAL feedback. Zero IR-type feedback. Zero control-type ACKs
specifically referencing our probes.

## Interpretation

The RMC's IR port and Relay subsystems are addressed via a different
path shape or leaf encoding than the ComPort TX path, OR they are
designed to accept writes silently without any feedback event.

Likely candidate reasons (not pursued further here):

- 3-level container nesting (chassis's own responses use path depth 3,
  e.g., `[33,1,1]`, whereas our ComPort path is 2-level `[1,1]`)
- Leaf type bytes other than 0x16/0x00 (e.g., 0x1C BuildAndSendSingleStringParameter
  seen in finding 20, or 0x40/0x50 class)
- Root-level writes (no container nesting at all)
- Different join numbering convention (we tried 1-5; maybe 29, 100, etc.)

The combinatorial search would require significant probe time and
risks accidentally hitting unrelated chassis config writes. Deferred.

## Shipping impact

The one-socket .pkp (dm_md_master_v0_0_1.pkp) stays with:

- **ComPortSendString / ComPortReceivedString**: FULLY IMPLEMENTED
  (byte-exact per finding 24; the 99% use case for DM-RMC endpoints
  controlling projectors/displays over RS-232)
- **MatrixTieCommand** (routing): architecturally reachable but the
  chassis-side routing-write grammar hasn't been fully reverse-
  engineered either; the committed CTP+CIP dual-transport .pkp handles
  routing today independently
- **IRPulse / RelayClose / RelayOpen / RelayStatus**: STUBBED with
  logging only; marked clearly in the ControlScript driver source as
  Phase 3 TBD

If a specific deployment needs IR or Relay via the master-of-record
.pkp, future work paths:

1. Capture a real CP4N session with a loaded SIMPL program that
   drives IR and Relay against this chassis - pcap would reveal the
   exact slot paths
2. More systematic probe sweep (3-level nesting x many leaf types x
   many join numbers) - combinatorial, slow
3. Decompile the Crestron-authored RMC driver code if available
   (DM_EndPoint_Output_C_Slot / DM-RMC-4K-SCALER-C driver)

For most DM-RMC deployments (projector/display RS-232 control is the
dominant use case), ComPort-only coverage is production-adequate.
