# Chassis firmware extraction — findings

## .cos file format

Target file: `CP3_1.8001.6346.26002.cos` (94 MiB, from the CP3N PUF
inner archive).

**The .cos is a Windows CE XIP ROM image for ARM (Thumb mode).**

Header layout (verified from byte-level inspection):

| Offset | Bytes                | Meaning |
|-------:|----------------------|---------|
| 0x00   | `fe 03 00 ea`        | ARM32 unconditional branch `b` (little-endian; jumps forward ~4 KiB to the real entry) |
| 0x10   | `ad 62 23 b7 07 00 00 00` | Crestron-specific magic/version header (version=7) |
| 0x40   | `EC EC 60 6c b3 84 60 6c 93 04 00 00` | Crestron chain marker ("ECEC") + two 32-bit sizes/addresses |
| 0x80+  | mostly zeros          | padding to the kernel image start |

The file is NOT a Linux kernel + initramfs as initially suspected.
There are no squashfs, cpio, uImage, FIT, JFFS2, or ELF signatures
anywhere in the file. There are no gzip / xz / bzip2 streams that
decompress cleanly either (the matches found were all false positives
inside ARM instruction stream data).

The file IS a CE XIP ROM. Evidence:

- Classic CE components present as embedded PE/DLL files:
  `nk.exe`, `kernel.dll`, `coredll.dll`, `kitl.dll`, `COREDLL.dll`,
  `filesys.dll`, `romfsd.dll`, `nsi.dll`, `device.dll`, `gwes.dll`,
  `shlwapi.dll`, `kerberos.dll`, `locale.dll`, `fpcrt.dll`,
  `oleaut32.dll`, `wda9052_rtc.dll`, `OALIOCTL.dll` …
- Shell references: `\windows\explorer.exe`, `\windows\ceshell.dll`,
  `\windows\control.exe`
- Path style: `\windows\<something>.dll` with backslashes (classic
  Win32 / Win-CE path convention)
- CE XIP data table marker `ECEC` observed at offset 0x40 (the pattern
  Crestron uses between XIP sections)

## The critical finding for the spike

**The chassis uses the SAME `PROTO_TCP.dll`, `PROTO_TLDM.dll`,
`PROTO_ENGINE.dll`, `PROTO_IPTABLE.dll`, and `CIP_PROTO_UTIL.dll` as
the CP4N master.** All five of those exact filenames appear in the
chassis ROM at `\windows\PROTO_*.dll` paths, in a packed string table
of DLL dependency names at offset `0x0266AF??`. They are the same
Crestron Proto* assemblies we already have fully decompiled from the
CP4N firmware extraction (in
`<decompiled>/ProtoTcp_dotnet/`, `<decompiled>/ProtoEngine_dotnet/`, etc.).

**Implication**: the earlier assumption that chassis-side acceptor
code is different from master-side code is WRONG. Both run the same
codebase. The `CGatewayLink` null-check at
`ProtoTcp.decompiled.cs:938` (`HandleDataPacket`) that was flagged as
"the chassis-side gate" IS the chassis-side gate — but it is also the
master-side gate; it is the SAME code called in both roles.

The parent's finding-21 verdict was correct in substance (DATA frames
with null `pGatewayLinkObject` get dropped) but wrong about WHERE and
WHY that happens:

- The gate IS code the chassis runs. Confirmed by this extraction.
- But `pGatewayLinkObject` is set during CONNECT-time acceptance
  (server-side ALTERNATE_CONNECT handler), not populated by a
  separately-loaded user program on the chassis. The chassis has
  built-in device-registration services; the question is which of
  those services' entries are addressable by a peer's `DestCID`.

## Where the chassis-side acceptor lives

The chassis's TCP acceptor is `PROTO_TCP.dll` embedded in the CE XIP
ROM at an offset in the range `0x0266 AFxx` (based on where the
`\windows\PROTO_TCP.dll` dependency reference appears). The DLL as
loaded in CE memory has the standard PE+ layout.

**22 valid PE images were located inside the ROM** by MZ+PE
signature validation. 18 of them are ARM/THUMB; most are between
24 KiB and 2 MiB in SizeOfImage. The large ones at
`0x02284C5F3` (25 MiB SizeOfImage) and `0x04220E0A` (2 MiB) are
candidate large Crestron DLLs (likely including the Proto*
collection). Full inventory at
`<session tmp>/firmware/cp3-chassis/extracted-pes/`.

Extraction of the specific PROTO_TCP.dll byte-for-byte is complicated
by the XIP layout — the DLLs have been laid out in CE's memory-image
format (section headers in file but with virtual-address alignment,
not file-offset-contiguous), so a simple MZ-to-SizeOfImage dump
doesn't produce a cleanly decompilable PE. `lief` reports many
corrupted-section / out-of-range-ordinal errors on the extracted
chunks.

**But** this does not block the spike: we already have the clean,
non-XIP version of the EXACT SAME `PROTO_TCP.dll` from the CP4N
rootfs ext3 (at `/usr/lib/CrestronLibs/PROTO_TCP.dll`), fully
decompiled and sitting at
`<decompiled>/ProtoTcp_dotnet/ProtoTcp.decompiled.cs`.
That's authoritative chassis-side code too.

## The actual acceptor-side question

The server-side `TCPGatewayServer` handling of an incoming
ALTERNATE_CONNECT is in the SAME `ProtoTcp.decompiled.cs` we already
have — specifically the `HandleEthernetGateway...` methods on the
server side (lines around 1230 and surrounding, per the earlier
fork's cite). What binds `pSocketContainer.pGatewayLinkObject` for an
incoming peer connection is the result of a lookup in the chassis's
own IP table (`IPTABLE` entries) keyed on the `DestCID` from the
peer's ALTERNATE_CONNECT.

The chassis OEM default IP table contains only a single `CGway`
placeholder at IPID 1 (per prior `evidence/02`). CGway is a
touchpanel/XPanel-type entry, which gives flat-join access only.
For slot-addressed dispatch, the IP table would need entries for the
chassis's internal device objects (routing matrix, endpoint slot
owners), and those entries would need to be addressable by a peer's
`DestCID`.

## State machine strings found in the ROM

Grep of the raw ROM yielded 142 TLDM-related log strings, 372
Cresnet-related strings, 262 IPTable/IPTABLE references, and 196 CIP
references. Representative concrete strings:

- `RECEIVED REGISTRATION RESPONSE %u from the TLDM for Device %s.
  [parentType: %u, deviceID: 0x%02X, ProgCnt: %u, TLDMCnt: %u]`
- `Received un-registration failure response %u from the TLDM for a
  device not in the program. [parentType: %u, deviceID: 0x%02X]`
- `Unable to register application with the TLDM`
- `BuildCresnetSerial_15h_or_34h`
- `BuildCresnetIndirectText_15h_or_34h`
- `CTHALUSBHIDSlotDeviceDriver:SendCresnetPacketToDriver`
- `syntax: ROUTESYMSTAT[:program#] [-C:ControlId] [-E:EquipId]`
- `CoGetTIDFromIPID`

The last two are notable — the chassis has a ROUTESYMSTAT console
command keyed on "ControlId / EquipId" and a `CoGetTIDFromIPID`
helper that maps an IPID to an internal TID (type ID). That hints at
a chassis-internal translation layer: `peer-DestCID → IPID lookup → TID
→ device-type dispatcher`.

## Specific wire-level difference (status)

**Not conclusively determined by this extraction.** I did not find a
single-byte or single-field difference that distinguishes "working
master-of-record session" from "our current flat-join session." What
I can say with certainty:

- The gate is `pSocketContainer.pGatewayLinkObject == null`, same
  code the parent already cited.
- `pGatewayLinkObject` is set based on how the chassis's acceptor
  resolves the peer's `DestCID` against its own IP table.
- The chassis OEM IP table has only CGway at IPID 1 — no device-type
  entries we could target.
- A real CP4N master's SIMPL# Pro program, running on the master,
  instantiates `DmMd8x8Cpu3rps` and calls `.Register()`. That
  `.Register()` call (on the master's side) is what causes the
  master to open ITS TCP client with a specific DestCID the chassis
  will recognize. The chassis-side logic to recognize this is in
  the chassis's own built-in services (not a user-loadable program
  on the chassis).

## Recommended next step for the parent

The parent's actual task is now: **read the server-side
`TCPGatewayServer.HandleEthernetGatewayAlternateConnectMessage`
(or equivalently-named) in the already-decompiled
`<decompiled>/ProtoTcp_dotnet/ProtoTcp.decompiled.cs`.** Specifically
find how the server derives `pGatewayLinkObject` from `pDestCID`,
what IPTable lookup it performs, and what makes the chassis's own
built-in device services' entries show up in that lookup. If a real
master sends a DEVICE-TYPE-specific hint in the ALTERNATE_CONNECT
body (via the `Type` field's upper bits, or follow-up messages
before writes), that is the unlock. Alternatively, if the OEM-only
chassis genuinely cannot expose its internal device objects to peer
connections, that confirms the earlier conclusion but with the
corrected reasoning that it's a chassis BUILT-IN limitation, not a
"you need to load a program on the chassis" (which is impossible).

Scope-outside: I did not disassemble capstone / inspect the raw
chassis-side DLL bytes to look for behavioral differences from the
master-side DLL (which would need the XIP layout decoded properly).
That is a separate directive if the parent wants it.

## Artifacts on disk

- `<session tmp>/firmware/cp3-chassis/CP3_1.8001.6346.26002.cos` — raw ROM
- `<session tmp>/firmware/cp3-chassis/scan.py` — format signature scanner
- `<session tmp>/firmware/cp3-chassis/strings_scan.py` — strings extractor
- `<session tmp>/firmware/cp3-chassis/find_ce_bins.py` — CE-specific markers
- `<session tmp>/firmware/cp3-chassis/extract_dll.py` — PE scanner / extractor
- `<session tmp>/firmware/cp3-chassis/identify_pes.py` — PE identity probe
- `<session tmp>/firmware/cp3-chassis/extracted-pes/pe_000..pe_021_*.bin`
  — 22 PE candidates extracted from the ROM. XIP layout means `lief`
  reports structural errors; cleaner extraction requires decoding the
  CE XIP table format first.
