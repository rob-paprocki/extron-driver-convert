# DM-MD8x8-CPU3-RPS - Pepperdash EISC join map

> Sourced from Pepperdash Essentials DmChassisControllerJoinMap.cs (MIT) via
> the dm-md-cpu3-oem-joins research workflow 2026-10-07/08. These are the joins
> that appear across the EISC bridge Pepperdash exposes to a SIMPL program that
> drives a DmMd8x8Cpu3 / DmMd8x8Cpu3rps chassis.
>
> The OEM chassis default-program XPanel joins may differ from this map. The
> stock XPanel at CIP_ID=1 was authored by Crestron against the OEM program.
> The three ways to confirm the OEM joins exactly: (a) pktmon capture of the
> XPanel on 41794, (b) decompile the .c3p SWFs, (c) F1 on the DM-MD8x8 symbol
> in SIMPL Windows.

## Routing - what to drive

- Video route input N to output M: set analog A(100 + M) = N.
- Audio route input N to output M: set analog A(300 + M) = N.
- USB route: set analog A(500 + M) = N.
- Any route value of 0 breaks the connection.
- Our chassis is 8x8 so M in 1..8 for all three.


## Digital joins (59)

| # | Meaning |
|---|---|
| D1 | python-cipclient encodes digital join 1 as byte offset 0 in the join-high portion of the 7-byte 0x05 CIP data packet; packed_join = (cip_join//256) + ((cip_join%256)*256), high-bit set for value=0. CI |
| D4 | EnableAudioBreakaway -- FromSIMPL. Allows audio to route independently of video when high; audio follows video when low. |
| D4 | EnableAudioBreakaway â€” toggles audio-breakaway routing mode on the chassis (FromSIMPL) |
| D5 | EnableUsbBreakaway -- FromSIMPL. Allows USB to route independently of video. |
| D5 | EnableUsbBreakaway â€” toggles USB-breakaway routing mode (FromSIMPL) |
| D11 | IsOnline -- ToSIMPL. Chassis online status feedback. |
| D11 | IsOnline â€” chassis online feedback (ToSIMPL) |
| D100 | Repeated 'placeholder' DigitalJoin (appears on multiple widgets â€” likely 'reserved / unused' slot or a shared enable) |
| D101 | VideoSyncStatus (span 32: D101-D132) -- ToSIMPL. One digital feedback per input slot; high while a signal is present at that input. |
| D101 | VideoSyncStatus base â€” input video sync detect per input slot, span 32 (joins 101â€“108 for the 8x8 chassis). ToSIMPL. This is video-detected on the input, NOT HPD on an endpoint. |
| D501 | InputEndpointOnline (span 32: D501-D532) -- ToSIMPL. Per-input DM-TX/endpoint online feedback. |
| D501 | InputEndpointOnline base â€” per-input DM-TX endpoint online feedback, span 32 (joins 501â€“508 for 8x8). ToSIMPL. |
| D601 | Home page 'Instant Take' button press - commits a route the moment an output is selected |
| D701 | OutputEndpointOnline (span 32: D701-D732) -- ToSIMPL. Per-output DM-RMC/endpoint online feedback. |
| D701 | OutputEndpointOnline base â€” per-output DM-RMC endpoint online feedback, span 32 (joins 701â€“708 for 8x8). ToSIMPL. |
| D730 | Home page 'Take' button press - executes the pending route(s) |
| D732 | Home page 'Audio Follows Video' toggle (Advanced Button_1_2) |
| D733 | Home page 'USB Follows Video' toggle (Advanced Button_1_5) |
| D734 | Home page 'Audio Only' breakaway mode button |
| D736 | Home page 'USB Only' breakaway mode button |
| D750 | Home page 'Clear Selected' button press (visibility pair 753) |
| D751 | Home page 'Select All' button press (visibility pair 752) |
| D826 | Home page Menu/mode icon at top-right (position 832,4) - press join; opens the Menu/settings subpage |
| D830 | Home page icon button at position 1195,4 (visibility 831) - shown in one locked/unlocked state |
| D830 | Button_3_1 digital press join (project-level widget, likely a 'Home' or persistent top-bar button) â€” Environment.xml line 696 |
| D831 | Button_3_1 digital visibility join (controls whether the button is drawn) |
| D833 | Home page Video Window subpage visibility (Subpage Reference_2 -> Page 27 'Video Window') |
| D833 | Widget DigitalJoin |
| D835 | Home page icon button at position 1195,4 (visibility 836) - shown in the opposite state; a status lock icon (Image Object_1 at 1247,8) also tracks visibility 836, matching the manual's note about a lo |
| D837 | Home page _DM_Logo subpage visibility (Subpage Reference_1 -> Page 51) |
| D837 | Widget base DigitalJoin with per-type offsets 0/0/0 â€” classic SmartObject binding pattern (<DigitalJoinOffset>0</>, <AnalogJoinOffset>0</>, <SerialJoinOffset>0</>) |
| D840 | Home page 'PAGE 1' selector button press (Button_1_4) |
| D841 | Home page 'PAGE 2' selector button press (Button_1_5) |
| D845 | Home page 'PAGE 1' selector variant (Button_1_6) |
| D846 | Home page 'PAGE 2' selector variant (Button_59) |
| D847 | Home page Clockrate subpage visibility (Subpage Reference_12 -> Page 81) |
| D847 | Widget DigitalJoin on the same page cluster as 833/855/856 |
| D850 | Home page Source 4x1 grid rows visibility (eight Subpage References to Page 133 'Source Text List 4x1 Grid - Input (NEW)' with DigitalJoinOffsets 4999,5007,5015,5023,5031,5039,5047,5055; one 8-join st |
| D850 | Widget DigitalJoin (appears twice â€” likely a two-widget pair sharing one feedback) |
| D855 | Home page source list subpage visibility (Subpage Reference_23 -> Page 109 'Source Text List 8x2 Regular - Input'); DigitalJoinOffset=4999 so item buttons inside the subpage map to wire joins ~5000-50 |
| D855 | Widget DigitalJoin |
| D856 | Home page source list page-2 subpage visibility (Subpage Reference_43 -> Page 109), DigitalJoinOffset=5031 so items map to wire joins ~5032-5062 |
| D856 | Widget DigitalJoin |
| D875 | Home page Destination 4x1 grid rows visibility (eight Subpage References to Page 134 'Destination Grid List 4x1 (NEW)' with DigitalJoinOffsets 6999,7015,7031,7047,7063,7079,7095,7111; one 16-join stri |
| D880 | Home page destination list subpage visibility (Subpage Reference_25 -> Page 112 'Destination Text List 8x2 Regular List'); DigitalJoinOffset=6999 so item buttons map to wire joins ~7000-7030 |
| D880 | Widget DigitalJoin |
| D881 | Home page destination list page-2 subpage visibility (Subpage Reference_44 -> Page 112), DigitalJoinOffset=7063 so items map to wire joins ~7064-7094 |
| D881 | Widget DigitalJoin |
| D1001 | TxAdvancedIsPresent (span 32: D1001-D1032) -- ToSIMPL. Per-input advanced DM-TX presence. |
| D1001 | TxAdvancedIsPresent base â€” true when an 'advanced' DM-TX (per-slot) endpoint is attached, span 32. ToSIMPL. |
| D1201 | OutputDisabledByHdcp (span 32: D1201-D1232) -- ToSIMPL. Per-output HDCP block indicator. |
| D1201 | OutputDisabledByHdcp base â€” per-output 'this sink refuses to accept the current source's HDCP' feedback, span 32 (joins 1201â€“1208 for 8x8). ToSIMPL. |
| D1800 | Main (home) page visibility join - driven by program 0 to show the home page |
| D1800 | Project-level DigitalJoin (sibling of 1816, probably paired) |
| D1816 | Project-level DigitalJoin (likely the main-page selector or project enable) |
| D1850 | Settings subpage visibility (Subpage Reference_9 -> Page 8 'Settings') |
| D1851 | Diagnostics subpage visibility (Subpage Reference_10 -> Page 9 'Diagnostics') |
| D1853 | Error pop-up visibility (Subpage Reference_6 -> Page 71 'Error Pop Up') |
| D9000 | Subpage/SmartObject base DigitalJoin (large number is the Crestron convention for SmartObject reserved base) |

## Analog joins (19)

| # | Meaning |
|---|---|
| A1 | Analog join 1 CIP packet template: `05 00 08 00 00 05 14` + 2-byte big-endian cip_join + 2-byte big-endian value. 16-bit unsigned 0-65535. |
| A10 | SystemId (DigitalAnalog, ToFromSIMPL). Chassis system ID for cascaded units (2-64; 1 = default/non-cascaded). |
| A10 | SystemId â€” DigitalMedia system ID get/set/trigger (ToFromSIMPL, Digital+Analog combo) |
| A101 | OutputVideo (span 32: A101-A132) -- ToFromSIMPL. Per-output video source select (VideoOut1..N in the native symbol). Analog value = input number to route. |
| A101 | OutputVideo base â€” Video_Route per output: write=select input (1..8) routed to that output, read=current routed input. Span 32 (joins 101â€“108 for 8x8). ToFromSIMPL. Per-output offset = outputSlot- |
| A301 | OutputAudio (span 32: A301-A332) -- ToFromSIMPL. Per-output audio source select (gated by EnableAudioBreakaway). |
| A301 | OutputAudio base â€” Audio_Route per output: write=select input routed for audio to that output, read=current. Span 32 (joins 301â€“308 for 8x8). ToFromSIMPL (requires EnableAudioBreakaway for breakaw |
| A501 | OutputUsb (span 32: A501-A532) -- ToFromSIMPL. Per-output USB routing target. |
| A501 | OutputUsb base â€” USB_Route per output: write=select input routed for USB to that output, read=current. Span 32. ToFromSIMPL. |
| A701 | InputUsb (span 32: A701-A732) -- ToFromSIMPL. Per-input USB routing target. |
| A701 | InputUsb base â€” USB_Route per input, span 32. ToFromSIMPL. |
| A1001 | HdcpSupportState (span 32: A1001-A1032) -- ToSIMPL. Per-input HDCP active state feedback. |
| A1001 | HdcpSupportState base â€” HDCP support state per input, span 32. ToSIMPL feedback (metadata labels it ToSIMPL; also used as a FromSIMPL setter via SetHdcpStateAction at L1626/1819/1877). |
| A1201 | HdcpSupportCapability (span 32: A1201-A1232) -- FromSIMPL. Per-input HDCP capability setting. |
| A1201 | HdcpSupportCapability base â€” HDCP capability per input, span 32. Metadata says FromSIMPL, but code at DmChassisController.cs L1634/1639 writes trilist.UShortInput[â€¦].UShortValue so it is effective |
| A1501 | InputStreamCardState (span 32: A1501-A1532) -- FromSIMPL. Stream input cards: 1=Start, 2=Stop, 3=Pause. |
| A1501 | InputStreamCardState base â€” DMC-STR input: 1=Start, 2=Stop, 3=Pause; span 32. Metadata says FromSIMPL, but code at L1665 + L1688 both sets action AND LinkInputSigs feedback â€” effectively ToFromSIM |
| A1601 | OutputStreamCardState (span 32: A1601-A1632) -- FromSIMPL. Stream output cards: 1=Start, 2=Stop, 3=Pause. |
| A1601 | OutputStreamCardState base â€” DMC-STRO output: 1=Start, 2=Stop, 3=Pause; span 32. Same as input stream â€” effectively ToFromSIMPL per L1712+L1735. |

## Serial joins (23)

| # | Meaning |
|---|---|
| S1 | Name -- ToSIMPL. Chassis friendly name feedback. |
| S1 | DM Chassis Name (ToSIMPL) |
| S1 | Serial join 1 packet template: `12 00 00 00 00 00 00 34` + 2-byte big-endian cip_join + `03` + ASCII bytes. Payload-length byte at offset 2 and inner-length at offset 6 are rewritten to `8+len(value)` |
| S100 | NoRouteName -- ToSIMPL. String reported when an output has no input routed. |
| S100 | NoRouteName â€” label used when nothing is routed (ToSIMPL) |
| S101 | InputNames (span 32: S101-S132) -- ToSIMPL. Per-input friendly names. |
| S101 | InputNames base â€” human-readable input slot names, span 32 (ToSIMPL) |
| S301 | OutputNames (span 32: S301-S332) -- ToSIMPL. Per-output friendly names. |
| S301 | OutputNames base â€” human-readable output slot names, span 32 (ToSIMPL) |
| S501 | InputVideoNames (span 200: S501-S700) -- ToFromSIMPL. Per-input video-source labels (settable). |
| S501 | InputVideoNames base â€” long input-name/EDID-style strings, span 200 (ToFromSIMPL) |
| S701 | InputAudioNames (span 200: S701-S900) -- ToFromSIMPL. Per-input audio-source labels (settable). |
| S701 | InputAudioNames base â€” audio-input name strings, span 200 (ToFromSIMPL) |
| S901 | OutputVideoNames (span 200: S901-S1100) -- ToFromSIMPL. Per-output video labels (settable). |
| S901 | OutputVideoNames base â€” video-output name strings, span 200 (ToFromSIMPL) |
| S1101 | OutputAudioNames (span 200: S1101-S1300) -- ToFromSIMPL. Per-output audio labels (settable). |
| S1101 | OutputAudioNames base â€” audio-output name strings, span 200 (ToFromSIMPL) |
| S2001 | OutputCurrentVideoInputNames (span 32: S2001-S2032) -- ToSIMPL. Each output's currently routed video input name. |
| S2001 | OutputCurrentVideoInputNames base â€” per output, the serial name of whatever input is currently routed to it (span 32, ToSIMPL) |
| S2201 | OutputCurrentAudioInputNames (span 32: S2201-S2232) -- ToSIMPL. Each output's currently routed audio input name. |
| S2201 | OutputCurrentAudioInputNames base â€” per output, the serial name of whatever input is currently routed to it for audio (span 32, ToSIMPL) |
| S2401 | InputCurrentResolution (span 32: S2401-S2432) -- ToSIMPL. Per-input current detected resolution string. |
| S2401 | InputCurrentResolution base â€” per input, current detected resolution string (e.g. '1920x1080@60Hz'), span 32 (ToSIMPL) |
