# DM-MD8X8-CPU3-RPS OEM Join Reference

## Executive summary

**Authoritative docs found: Partial.** No Crestron OEM programmer's reference PDF for the DM-MD8X8-CPU3 / -RPS exists on the public web; the standalone title does not appear in Crestron's `getmedia` catalog and is almost certainly CAIP/dealer-gated. The authoritative artifact we DO have on this bench is the Crestron OEM XPanel pack `D:\Downloads\DM-CPU3_2.000.0013.c3p` (and the identical copy in `D:\Downloads\Default-XPanels`). It is a plain ZIP (`PK\x03\x04` magic) and inside it `swf/Environment.xml` carries the full join map in readable XML — this is the one authoritative source for what the OEM firmware program at slot 0 of this chassis actually responds to. Supporting metadata: `~.LocalInfo.vtpage` declares `VTZ=DMC-CPU3_V1.0_desktop.vtz, Panel=XPANEL Core 3 UI, VTpro-e=6200, Date=September 21 2020, ProjectPlatform=Smart Graphics`, and `Environment.xml` declares `PanelType=XPANEL 2.0 Smart Graphics, Page_Count=117, FirstToLoad=66 "Loading"` and connects to `IPID 1 @ 172.16.0.104:41794`. The 386 KB `swf/themes/Black Glass for DM 2.0.xml` is pure visual styling (fonts, categories, control states) with zero join references — it is NOT the join sidecar. Second-tier reference: PepperDash `DmChassisControllerJoinMap.cs` — the de-facto community EISC-bridge convention; useful to understand the Crestron SIMPL# Pro `DmMd8x8Cpu3rps` API surface, but its join numbers DO NOT apply here because this chassis is not running a Pepperdash program. Third-tier: Crestron DM-MD-CPU3 Product Manual (DOC 8418A) and the spec sheet (`ss_dm-md8x8_cpu3`) are hardware-/web-UI-focused and carry no join tables. The `digitalmedia_3.04.16.puf` is firmware-only (ini + csu + zip; no symbol metadata) and, per its chassis INI, does not even target the CPU3 variants — the correct firmware is `dmc3cpu_*.cos` (seen as `dmc3cpu_1.8001.5769.27432.cos` in a sibling PUF). The user's own evidence note at `<repo>\experiments\crestron-dm-md-bridge\evidence\02-xpanel-config.md` contains an outdated claim that no join sidecar exists in this pack — `swf/Environment.xml` IS the sidecar; that note needs a retraction + pointer.

## Join reference (what we're confident about)

**Scope note:** these are the joins the OEM Smart Graphics XPanel pack declares against the chassis's embedded program at slot 0 — i.e., what the Extron Peer registration will actually drive end-to-end. Confidence HIGH where the join is read directly from `swf/Environment.xml` in `DM-CPU3_2.000.0013.c3p` — the OEM shipping artifact on this bench. Confidence MEDIUM where the subpage-reference offset is HIGH but the per-cell internal join is interpolated from a sampled offset. All join numbers below are decimal. Type: D=digital, A=analog, S=serial.

### Chassis-wide / mode / page

| Type | Join # | Meaning | Confidence | Source |
|------|-------:|---------|:----------:|--------|
| D | 601 | **Instant Take** button — commits a route the instant a destination is pressed (no separate Take). FromSIMPL. | HIGH | Environment.xml, Main page Child "Instant Take" |
| D | 730 | **Take** button — commits the pending source→destination route. FromSIMPL. | HIGH | Environment.xml, Main page Child Button_2 |
| D | 732 | **Audio Follows Video** mode toggle. ToFromSIMPL. | HIGH | Environment.xml, Main Child Advanced Button_1_2 |
| D | 733 | **USB Follows Video** mode toggle. ToFromSIMPL. | HIGH | Environment.xml, Main Child Advanced Button_1_5 |
| D | 734 | **Audio Only** mode button (audio breakaway). FromSIMPL. | HIGH | Environment.xml, Main Child Button_77 |
| D | 736 | **USB Only** mode button (USB breakaway). FromSIMPL. | HIGH | Environment.xml, Main Child Button_76 |
| D | 750 | **Clear Selected** press (D753 visibility pair). FromSIMPL. | HIGH | Environment.xml, Main Child Button_5 |
| D | 751 | **Select All** press (D752 visibility pair). FromSIMPL. | HIGH | Environment.xml, Main Child Button_4 |
| D | 826 | Menu / settings icon press. FromSIMPL. | HIGH | Environment.xml, Main Child Button_1_1 |
| D | 830 / 835 | Lock-icon state pair (visibility 831 / 836); icon tracks password-set state per DOC 8418A. ToSIMPL. | HIGH | Environment.xml, Button_3_1 / Button_3 / Image Object_1 |
| D | 840 / 841 | **PAGE 1 / PAGE 2** source-dest page selectors. For 8x8 only PAGE 1 is populated; PAGE 2 is hidden by firmware. FromSIMPL. | HIGH | Environment.xml, Main Children Button_1_4 / Button_1_5 |
| D | 845 / 846 | PAGE 1 / PAGE 2 selector variants (alternate visual). FromSIMPL. | HIGH | Environment.xml |
| D | 1800 | **Main (home) page** visibility — asserted by the chassis program to display the home page. ToSIMPL. | HIGH | Environment.xml, `Page uid=1 Name=Main DigitalJoin` |
| D | 833 | Video Window subpage visibility (SubpageRef_2 → Page 27). ToSIMPL. | HIGH | SubpageReference uid 2 |
| D | 837 | DM logo subpage visibility (SubpageRef_1 → Page 51). ToSIMPL. | HIGH | SubpageReference uid 1 |
| D | 847 | Clockrate subpage visibility (SubpageRef_12 → Page 81). ToSIMPL. | HIGH | SubpageReference uid 12 |
| D | 1850 | **Settings** subpage visibility (SubpageRef_9 → Page 8). ToSIMPL. | HIGH | SubpageReference uid 9 |
| D | 1851 | **Diagnostics** subpage visibility (SubpageRef_10 → Page 9). ToSIMPL. | HIGH | SubpageReference uid 10 |
| D | 1853 | **Error popup** visibility (SubpageRef_6 → Page 71). Chassis asserts on transient routing error. ToSIMPL. | HIGH | SubpageReference uid 6 |

### Source grid (routing — press to select source)

Each row is a SubpageReference to Page 133 "Source Text List 4x1 Grid - Input (NEW)" with these DigitalJoinOffsets and an 8-join stride per row: 4999, 5007, 5015, 5023, 5031, 5039, 5047, 5055. Each subpage holds 4 source cells internally at DigitalPressJoin 1..4. Wire join = offset + internal. For an 8x8 chassis, only rows 1-2 (sources 1-8) carry live buttons; rows 3-8 are hidden.

| Type | Join # | Meaning | Confidence | Source |
|------|-------:|---------|:----------:|--------|
| D | 5000, 5001, 5002, 5003 | **Source 1-4 press** (row 1, offset 4999). FromSIMPL. | HIGH range / MEDIUM per-cell | SubpageRef uid 45 + inner Page 133 structure; cross-ref hunt sampled Page 109 cells 1 → 5000 and 31 → 5030 |
| D | 5008, 5009, 5010, 5011 | **Source 5-8 press** (row 2, offset 5007). FromSIMPL. | HIGH / MEDIUM | SubpageRef uid 51 |
| D | 5016-5063 | Sources 9-32 — hidden on 8x8. FromSIMPL. | HIGH | SubpageRefs uid 46-52 |
| D | 850 | Source 4x1 grid-rows visibility gate. ToSIMPL. | HIGH | Environment.xml |
| D | 855 / 856 | Source list variants (Page 109 "8x2 Regular") visibility; offsets 4999 / 5031. ToSIMPL. | HIGH | SubpageReferences uid 23 / 43 |

### Destination grid (routing — press to select destination)

Each row is a SubpageReference to Page 134 "Destination Grid List 4x1 (NEW)" with these DigitalJoinOffsets and a 16-join stride per row: 6999, 7015, 7031, 7047, 7063, 7079, 7095, 7111. Each subpage holds 4 destination cells internally (4 cells × 4 joins each = 16, likely press / feedback / vis / enable). For an 8x8 chassis, only rows 1-2 (dests 1-8) carry live buttons.

| Type | Join # | Meaning | Confidence | Source |
|------|-------:|---------|:----------:|--------|
| D | 7000, 7001, 7002, 7003 | **Destination 1-4 press** (row 1, offset 6999). FromSIMPL. | HIGH range / MEDIUM per-cell | SubpageRef uid 53 + inner Page 134 structure |
| D | 7016, 7017, 7018, 7019 | **Destination 5-8 press** (row 2, offset 7015). FromSIMPL. | HIGH / MEDIUM | SubpageRef uid 54 |
| D | 7032-7127 | Destinations 9-32 — hidden on 8x8. FromSIMPL. | HIGH | SubpageRefs uid 55-60 |
| D | 875 | Destination 4x1 grid-rows visibility gate. ToSIMPL. | HIGH | Environment.xml |
| D | 880 / 881 | Destination list variants (Page 112 "8x2 Regular") visibility; offsets 6999 / 7063. ToSIMPL. | HIGH | SubpageReferences uid 25 / 44 |

### DM-RMC-4K-SCALER-C at output 1 ("output 101")

**Not identified in the sampled portion of Environment.xml.** The chassis-level routing UI exposes only source/destination selection; a per-endpoint scaler/output-settings page was not located in the hunt sweep. See item 3 of "What we still don't know".

## Unverified candidates

These are the PepperDash `DmChassisControllerJoinMap` numbers — the de-facto community EISC-bridge convention. **They are NOT the joins the OEM firmware at slot 0 responds to.** Listed only because many integrators treat them as a reference for this chassis class. Use them if (and only if) you ever load a PepperDash SIMPL# Pro program on the chassis — never against the stock OEM firmware.

| Type | Join # | Meaning | Confidence | Source |
|------|-------:|---------|:----------:|--------|
| D | 4 | EnableAudioBreakaway (FromSIMPL) | LOW | PepperDash DmChassisControllerJoinMap.cs; verifier found no independent source |
| D | 5 | EnableUsbBreakaway (FromSIMPL) | LOW | PepperDash DmChassisControllerJoinMap.cs |
| D | 11 | IsOnline chassis feedback (ToSIMPL) | LOW | PepperDash DmChassisControllerJoinMap.cs |
| D | 101-108 | VideoSyncStatus per input slot (ToSIMPL, span 32 in map) | LOW | PepperDash DmChassisControllerJoinMap.cs |
| D | 501-508 | **InputEndpointOnline** per input DM-TX (ToSIMPL, span 32) | MED | DmpsRoutingControllerJoinMap.cs (verbatim 501); DmChassisController.cs explicit DM-MD-CPU3 wiring |
| D | 701-708 | OutputEndpointOnline per DM-RMC (ToSIMPL, span 32) | LOW | PepperDash only |
| D | 1001-1008 | **TxAdvancedIsPresent** per input (ToSIMPL, span 32) | MED | DmBladeChassisControllerJoinMap.cs (same 1001 start); DmChassisController.LinkAdvancedTxToApi |
| D | 1201-1208 | **OutputDisabledByHdcp** per output (ToSIMPL, span 32) | MED | DmChassisController.cs (semantic); epi-crestron-nvx NvxApplicationJoinMap.cs (literal 1201) |
| A | 10 | **SystemId** DigitalAnalog ToFromSIMPL | MED | EssentialsSIMPLWindowsBridgeExample `Essentials EiscApi Test.smw` hard-coded slot 4011 |
| A | 101-108 | OutputVideo route select per output (ToFromSIMPL, span 32) | LOW | PepperDash; devttys1 example corroborates the native API semantic only |
| A | 301-308 | OutputAudio route select | LOW | PepperDash |
| A | 501-508 | OutputUsb route select | LOW | PepperDash |
| A | 701-708 | InputUsb route | LOW | PepperDash |
| A | 1001-1008 | HdcpSupportState per input (ToSIMPL) | LOW | PepperDash |
| A | 1201-1208 | HdcpSupportCapability per input (metadata FromSIMPL; actual code ToSIMPL — mismatch) | LOW | PepperDash — metadata vs code mismatch at DmChassisController.cs L1634 |
| A | 1501-1508 | InputStreamCardState (1=Start 2=Stop 3=Pause) | LOW | PepperDash |
| A | 1601-1608 | OutputStreamCardState (1=Start 2=Stop 3=Pause) | LOW | PepperDash |
| S | 1 | Chassis Name (ToSIMPL) | LOW | PepperDash |
| S | 100 | NoRouteName label (ToSIMPL) | LOW | PepperDash |
| S | 101-108 | InputNames (ToSIMPL, span 32) | LOW | PepperDash |
| S | 301-308 | OutputNames (ToSIMPL, span 32) | LOW | PepperDash |
| S | 501-700 | InputVideoNames (ToFromSIMPL, span 200) | LOW | PepperDash |
| S | 701-900 | InputAudioNames (ToFromSIMPL, span 200) | LOW | PepperDash |
| S | 901-1100 | OutputVideoNames (ToFromSIMPL) | LOW | PepperDash |
| S | 1101-1300 | OutputAudioNames (ToFromSIMPL) | LOW | PepperDash |
| S | 2001-2008 | OutputCurrentVideoInputNames (ToSIMPL) | LOW | PepperDash |
| S | 2201-2208 | OutputCurrentAudioInputNames (ToSIMPL) | LOW | PepperDash |
| S | 2401-2408 | InputCurrentResolution (ToSIMPL) | LOW | PepperDash |

## IP table setup recipe

The current IP table has only CIP_ID=1 → 127.0.0.1 (Gway, OFFLINE) — **do not touch it**; that is the chassis's own Gateway Server loopback (used for Internet-CIP-Gateway and XPanel-via-Gateway traffic). Pick a free IP-ID; `03` is the convention Crestron's own Remote Annotation Quickstart Guide uses, but `02` and anything up to `FE` are equally valid. **Case: this chassis is on 3-Series firmware (DMC-CPU3) — the add commands are `ADDPeer` / `ADDMaster`, NOT `ADDSLAVE` (that was 2-Series).** The firmware's own `ADDPeer -h` text reads "Add a peer(slave) entry to IP table", confirming Peer=Slave on 3-Series.

**Primary (recommended) variant — explicit Extron IP, program 1:**

```
addpeer 03 <extron-ip> -P:1
progres -p:1
iptable -t
sendiptable 1
```

Expected console echo after `addpeer`: `Master List set. Restart program to take effect.` After `progres` the chassis bounces its SIMPL program; `iptable -t` then shows CIP_ID=3 in tabular form; `sendiptable 1` persists the entry to internal flash so a `progload` or firmware reload will not wipe it.

**Variant A — wildcard source (UNVERIFIED on CPU3; test first):**

```
addpeer 03 0.0.0.0 -P:1
progres -p:1
```

Rationale: the CIP handshake authenticates via the IP-ID carried in the client's register packet, not the TCP source IP; wildcard-`0.0.0.0` as "accept from any source" is integrator folklore, not documented in Crestron OEM material. Test empirically before relying on it.

**Variant B — explicit CIP port and program (for completeness; port 41794 is the default):**

```
addpeer 03 <extron-ip> -P:1 -C:41794
progres -p:1
```

**Variant C — if program slot 1 is empty on this chassis (the user's "slot 0 OEM firmware program" framing may mean the stock program is NOT in slot 1):**

```
# first query what program slot is live:
progreg
# then target that slot's IP table. If slot 2:
addpeer 03 <extron-ip> -P:2
progres -p:2
sendiptable 2
```

**Verification sanity-check before writing driver:** before shipping the Extron driver, point VTPro-e's XPanel runtime at the chassis using the OEM `DM-CPU3_2.000.0013.c3p` with its Host rewritten to this chassis's IP and IPID bumped from 1 to the free IPID you ADDPeer'd — confirms the OEM join wiring works end-to-end against known-good Crestron software.

**Handshake return codes seen in the CIP payload** (byte 1-2 = length, bytes 3+ = payload):
- `02 00 03 FF FF 02` — IPID does not exist in the IP table for this program (ADDPeer not applied, program not restarted, or wrong `-P:` slot).
- `02 00 04 00 00 00 1F` — registration successful, client is live.

**CIP-auth caveat:** the user has confirmed SSH auth is ON but SSL-for-CIP is OFF. There is a separate `SETCSAUTHENTICATION` toggle for whether CIP peers need credentials. If the Extron ADDPeer is correct and the handshake still rejects, run `SETCSAUTHENTICATION` on the console with no args to see the current setting; disable it for CIP, or add the Extron to the "Connects" group with credentials. The Chief Integrations wiki notes that adding an IP-table entry before credentials are configured can land the client address on the blocked list — if that happens, `BLOCKEDIP -R` clears it.

## XPanel registration packet shape

Target: TCP to `<chassis-ip>:41794` (plain CIP — port 41796 is the TLS variant and is irrelevant here since SSL-for-CIP is OFF). Byte sequences below are hex; multibyte integers are big-endian. Reference implementation: `klenae/python-cipclient` (`cipclient.py`), which is the only widely-used open-source implementation of this protocol.

**Step 1 — processor announces (server → client), immediately after TCP accept:**

```
0F 00 01 02
```

Type `0x0F` = register-request. The `02` after the 2-byte length is a protocol version tag.

**Step 2 — register as XPanel panel class (client → server):**

```
01 00 07 00 00 00 00 00 <IPID>
```

Where `<IPID>` is the hex IP-ID (same number from `addpeer` — `03` in the primary recipe). Type `0x01` = register-reply. The byte at offset 8 is the IP-ID the client claims. **For an OEM XPanel-equivalent registration (which is what the chassis's slot-0 program expects on this IPID), use `0x01` (panel class).** The alternative is `0x0A` (EISC/device class); the practical difference is only which SIMPL symbol the processor-side program is wired against. For driving the OEM firmware you MUST use panel class.

**Step 3 — processor accepts or rejects (server → client):**

```
02 00 04 00 00 00 1F   # SUCCESS — client is now registered on this IPID
02 00 03 FF FF 02      # FAIL — IPID not in IP table for the running program
```

Type `0x02` = status / registration-ack.

**Step 4 — follow-up prompts (server → client):**
Within a few hundred ms of a successful registration the processor sends an update-request (type `0x05` with a specific payload) prompting the client to send its initial join state. A safe response is to send nothing — the chassis will push its current source/destination state to the client within one heartbeat cycle. If you need the exact bytes, mirror `python-cipclient._processPayload`.

**Step 5 — ongoing CIP traffic:**

- **Digital join set/clear** (client → server):
  ```
  05 00 06 00 00 03 00 <packed-join-lo> <packed-join-hi>
  ```
  Where `packed_join = (cip_join // 256) + ((cip_join % 256) * 256)`, and the high bit of the result encodes the digital value (set vs clear). From `_cip_packet['d']`.

- **Analog join** (16-bit unsigned, big-endian value):
  ```
  05 00 08 00 00 05 14 <join-hi> <join-lo> <value-hi> <value-lo>
  ```

- **Serial join** (variable length):
  ```
  12 00 <len-hi> 00 00 <inner-len-lo> 00 34 <join-hi> <join-lo> 03 <ASCII...>
  ```
  Where `<len>` = `8 + length(ASCII)` and `<inner-len>` = `4 + length(ASCII)`.

- **Heartbeat** (client → server, every ~15 s; `HEARTBEATTIMEOUT` default on the chassis is 30 s):
  ```
  0D 00 02 00 00
  ```

- **Pings from server** (type `0x0E`) — echo back the same type byte to keep the socket warm.

**For the Extron driver, concretely at IPID 03:** the Step 2 packet is literally `01 00 07 00 00 00 00 00 03`. After success, drive source N (1..8) by pulsing digital join `5000..5003` for N=1-4 or `5008..5011` for N=5-8, then drive destination N (1..8) by pulsing digital join `7000..7003` for N=1-4 or `7016..7019` for N=5-8. If Instant Take (D601) is engaged, the route commits automatically on destination press; otherwise press Take (D730) after both selections.

## Fallback — SWF/XML decompile recipe

**For THIS pack, no decompile is needed.** The 386 KB `swf/themes/Black Glass for DM 2.0.xml` is a pure visual-theme file (fonts, images, categories, control-style state tables) with zero joins — grep for `<Digital*Join|<AnalogJoin|<SerialJoin|<SmartObject` returns nothing (there is one hit for the string "Digital Date Time" at line 317 as a widget-category *name*, but no join assignments). All joins live in the sibling `swf/Environment.xml` as plain XML.

**Shortest working path (unpack and grep):**

```
# .c3p is a plain Zip — no renaming needed:
unzip DM-CPU3_2.000.0013.c3p -d dm-cpu3/

# Project header lives on the <Crestron> root in Environment.xml:
#   PanelType=XPANEL 2.0 Smart Graphics, Page_Count=117
# All joins show up as readable XML tags:
rg -n "<Digital(Press|Visibility|Enable|)Join|<AnalogJoin|<SerialJoin|<IndirectTextJoin|<DigitalJoin>|<DigitalJoinOffset>|<AnalogJoinOffset>|<SerialJoinOffset>" dm-cpu3/swf/Environment.xml

# Pair widgets to their joins by walking <ObjectName> + <ControlName>:
rg -n "<ObjectName>|<ControlName>|<DigitalPressJoin>|<AnalogJoin>|<SerialJoin>" dm-cpu3/swf/Environment.xml > joins.txt
```

**To pin down the exact per-cell source and destination joins** (which this reference reports only as ranges):

```
# Extract page 133 (source grid cells) and page 134 (destination grid cells):
awk '/<Page uid="133"/,/<\/Page>/' dm-cpu3/swf/Environment.xml > page133.xml
awk '/<Page uid="134"/,/<\/Page>/' dm-cpu3/swf/Environment.xml > page134.xml

# Each cell has an ObjectName and internal DigitalPressJoin.
# Wire join of cell C in row R = row_offsets[R] + DigitalPressJoin[C].
# For sources: row_offsets = [4999, 5007, 5015, 5023, 5031, 5039, 5047, 5055]
# For destinations: row_offsets = [6999, 7015, 7031, 7047, 7063, 7079, 7095, 7111]
```

**SmartObject semantics** (relevant inside Pages 133/134): a SmartObject declares a base `<DigitalJoin>N</DigitalJoin>` plus `<DigitalJoinOffset>K</>`/`<AnalogJoinOffset>K</>`/`<SerialJoinOffset>K</>`; each child widget's wire join is `offset + its_inner_join`. Confirmed by Environment.xml structure at lines 165-169, 236-238, 696-699.

**Optional — SWF decompile (only needed if you ever want to learn the widget schema, e.g. what tag names `BaseObjectsRSL.swf` expects for a given widget):**

```
# JPEXS Free Flash Decompiler (FFDec), GPL v3, needs Java 8+:
#   https://github.com/jindrapetrik/jpexs-decompiler/releases
ffdec -export script,binaryData out/ dm-cpu3/swf/controls/BaseObjectsRSL.swf
grep -rE "Join|digitalJoin|_press|_feedback" out/
```

That dumps the AS3 class fields a widget's XML attribute names map to. You will NOT find per-project join assignments there — those live only in `Environment.xml`.

## What we still don't know

1. **Per-cell source and destination join numbers inside Pages 133 / 134.** We have row offsets with HIGH confidence (sources 4999..5055 at 8-join stride; destinations 6999..7111 at 16-join stride) and a sampled Page 109 cell showing internal-press 1 → wire 5000 and internal-press 31 → wire 5030 — but the exact mapping of {source N → digital K} / {destination N → digital K} inside the 4x1-grid pages has not been dumped. **Next move:** run the `awk` extraction in the recipe above against `page133.xml` / `page134.xml` — a 10-minute job.

2. **Does the OEM firmware at slot 0 actually implement every join Environment.xml declares?** The XPanel pack is a client declaration; the chassis's embedded program is the server. A declared visibility join such as D1800 or D1853 is useful only if the chassis actually drives it. **Next move:** either (a) wire the user's existing `DM-MD32X32-CPU3-RPS_2.000.0012_172.22.0.10.c3p` XPanel at a free IPID against this chassis and watch which joins get driven in the XPanel debug console, or (b) run a 60-second Wireshark capture on port 41794 against the OEM XPanel while it drives a route — the capture reveals exactly which joins the chassis asserts.

3. **DM-RMC-4K-SCALER-C scaler controls at output 1 ("output 101").** The chassis-level XPanel pack does not expose a scaler-control page in the parts of Environment.xml the lenses examined. The DM-RMC-4K-SCALER-C has its own feature set (output scaling, mute, HDCP, HPD, link status) which, on a CPU3 chassis, is addressed by output slot (no per-endpoint IPID — per DOC 8418A and PepperDash's "Must use different constructor for CPU3 chassis types. No IPID" comment). **Next move:** (a) walk every `<Page>` in Environment.xml by `Name=` — grep for `RMC|Scaler|Output Settings|Output Resolution|HDCP`; (b) if the OEM pack genuinely has no scaler-control UI, we have two options: (i) ship routing-only in v1 and expose scaler controls through the chassis's HTTPS web UI (REST calls); (ii) load a small SIMPL# Pro bridge program on the chassis that exposes an EISC with per-endpoint joins — a bigger architectural change.

4. **Does the chassis actually require CIP authentication?** User confirmed SSH auth is ON; CIP auth is a separate `SETCSAUTHENTICATION` toggle. **Next move:** `SETCSAUTHENTICATION` with no args on the console displays the setting.

5. **Is the OEM XPanel pack we have (`DM-CPU3_2.000.0013.c3p`, dated Sep 21 2020, VTpro-e 6200) matched to the firmware this chassis is actually running?** The chassis's firmware revision (likely in the `1.8001.x` family per `dmc3cpu_1.8001.5769.27432.cos` in sibling PUFs) must at least implement the same joins. **Next move:** `ver` on the chassis console gives the firmware string; cross-check that version's release notes for join additions since 2.000.0013.

6. **Does `addpeer <ipid> 0.0.0.0` act as a true wildcard on this firmware?** Only observed as integrator folklore; not confirmed in any Crestron OEM doc located in the hunt. **Next move:** empirical — ADDPeer with 0.0.0.0 and connect from an unrelated client IP; if the handshake succeeds the source IP is advisory, if it rejects it is strict.

7. **Which program slot is actually running the OEM firmware's SIMPL program?** The user's framing "OEM firmware program at slot 0" is unusual — Crestron program slots are typically 1-10. **Next move:** `progreg` on the console lists loaded programs per slot; target that slot number in `-P:` on ADDPeer and `-p:` on `progres`.

8. **A standalone Crestron "DM-MD8X8-CPU3 Programmer's Reference" PDF behind the dealer/CAIP portal.** None found publicly; search for `mg_pr_dm-md8X8_cpu3` returned no hits. **Next move:** True Blue Support (1-888-CRESTRON) — ask whether a document titled `mg_pr_dm-md8X8_cpu3` (or similar) exists and can be sent to a registered dealer account.

9. **Housekeeping:** the user's own evidence note at `<repo>\experiments\crestron-dm-md-bridge\evidence\02-xpanel-config.md` carries an outdated claim ("No joins.xml / joins.json sidecar in this package"). `swf/Environment.xml` IS the sidecar — a one-line retraction + pointer to this reference is in order. **Next move:** parent agent edits that note before publication.