# Finding 06 — can we emit a `.pkg`, and does the Extron converter generalise?

From the re-run of three previously-failed dimensions: **39 confirmed,
2 refuted, 2 overstated, 1 uncertain.**

## Emitting a Crestron driver: strategy A works, and was demonstrated

Not argued — **executed**, end-to-end in `/tmp`, against the real Samsung Serial
DLL.

The embedded JSON resource sits at file offset `0x1068` as a 4-byte
little-endian length prefix (`0xb454` = 46,164) followed by a UTF-8 BOM and the
JSON. It lives as **raw bytes in `.text`, not inside a metadata heap** — so a
same-length in-place edit needs **zero PE/CLI-header surgery**. The patched file
still parses cleanly with `pefile` and the resource re-extracts as valid JSON.

Growth headroom is bounded and known: `.text` has exactly **1,653 bytes of
trailing slack** (between the end of the Import Directory at `0xc98b` and the end
of `.text` raw data at `0xd000`). Beyond that you need a section-size bump with
RVA shifts for `.rsrc` and `.reloc`.

A full product rename cascades further — `Module.Name`, `TypeDef.Name`/
`Namespace`, `Assembly.Name`, `ManifestResource.Name`, the base class ref, plus a
UTF-16LE copy — resizing the `#Strings` and `#US` heaps. Fiddly, not blocked.

**Signature:** Authenticode-signed (Security Directory at `0xf000`, size `0x4a0`,
1,176-byte PKCS#7), **not strong-name signed** (`StrongNameSignature RVA=0
Size=0`). Any edit invalidates it. Nothing in the documented load path checks it.

## Strategy B is harder than expected — for this driver family

The DLL's `AssemblyRef` names **mscorlib Version=3.5.0.0, PublicKeyToken
`969db8053d3322ac`** — the **.NET Compact Framework** corlib token, not desktop
.NET. Crestron's own docs mandate the EOL, Windows-only **Visual Studio 2008 +
WinCE/.NET CF** toolchain for any "commercial application or 3-Series control
system" driver.

The current DevKit / ManifestUtil NuGet packages (v27.0.24) do target net8.0 and
net47 and are nominally cross-platform. But that modern path builds against the
newer **RAD-Framework interfaces, not the `DisplayWrapperSerial`/`DisplayWrapperTcp`
LegacyWrappers this sample uses** — so it cannot reproduce this driver's shape,
only a differently-architected equivalent.

*(Verifier marked UNCERTAIN whether this particular driver is bound by the VS2008
requirement or falls on the residential/4-Series VS2019 path.)*

*(2026-09-23, `notes/desk-research-2026-09.md` §2: the "mandate" above is
narrower than written. Crestron's VS2008 requirement is for **SIMPL# Pro
programs** (Compact Framework 3.5, support answer 1145). The Certified Drivers
SDK's own Create-a-Project pages, V1 and V2, accept Visual Studio 2019, 2022 or
2008 with a desktop .NET Framework class library. Which toolchain built *this*
CF-bound DLL is still open. The claim that the modern path builds RAD-Framework
drivers rather than LegacyWrappers ones was not re-checked.)*

**Recommendation: strategy A.** The format is nearly trivial and the patch is
proven. Strategy B is a toolchain archaeology project.

**The single hardest blocker is not cryptographic or technical. It is Crestron's
partner/dealer gate** — on the SDK licence, on Toolbox, and on VC-4.

## Serial and IP are two drivers, not one driver with two bindings

Different `Guid`s. Different `DriverVersion` (1.0200.0001 vs 1.0100.0006).
Different `MinSdkVersion` (21 vs 14). Built ~9 months apart. Different claimed
scope — Serial covers 4 series / 149 models, IP covers 1 series / 23 models.
Crestron's own catalogue treats them as separate artifacts.

Their grammars do not even share a vocabulary:

| section | Serial-only | IP-only |
|---|---|---|
| Commands | — | `WakeOnLan` |
| Responses | `BinaryPacket`, `Regex`, `AlwaysMatch`, `CaptureAll` | `Json` |
| Rules | `SequencedEntry` | `SetOtherState`, `SetOtherFeedback` |
| Conditions | — | `And`, `Or`, `Exists` |
| SupportedFeatures | `Simpl`, `SerialComport` | `Tcp` |

IP's transport is `Type: Http` with a full request descriptor
(`https://{_Host_}:{_Port_}`, port 1516, `KeepAlive`, `RequestType: Post`) versus
Serial's five flat timing fields. IP adds a `Configuration` block
(`DriverInstanceIdentifier: {_MacAddress_}`) that Serial has no equivalent for —
there is no port address to key identity on.

**Worth flagging on its own:** IP sets `Secure: true` but
`HostVerification: false` and `PeerVerification: false`. TLS verification is
disabled at both ends.

The 71-vs-12 `InputOutput` gap is not a richer encoding of the same concepts —
it is a 56-entry Samsung app catalogue (`CustomMediaServiceId`) that is
meaningless over RS-232.

**An IR must either union both vocabularies or normalise to an abstraction below
both.** It cannot treat transports as bindings on one driver.

## Does the Extron converter generalise to third-party devices?

**Partly — and the part that fails is the part that matters less.**

- ✅ **The `### BEGIN/END AUTO GENERATION OF COMMAND DEF` markers generalise.**
  Both embedded scripts carry them, on a Samsung device.
- ✅ **The `BaseDriver` API surface generalises** — 46 locally-defined methods,
  inherited `AddMatchString` / `Disable` / `Discard` / `Error` / `Mutex` /
  `PostNewStatusEx` / `QueryDelayTimerIsRunning` / `StartQueryDelayTimer`.
- ✅ **The SIS-specific shell simply is not there** — no `w0echo` / `w3cv`
  handshake, no `E##` error table. `OnConnected()` is an empty `pass`. Liveness
  falls to the generic poll-and-timeout path (`update_next()`, `CallBackTimer`,
  `__ResponseTimeout`). The earlier worry that the SIS handshake would have to be
  replaced turns out to be a non-problem: for non-SIS devices there is nothing to
  replace.
- ⚠️ **Line overlap is much lower.** 46.1% stripped / 37.8% exact against the
  serial script, versus 75.9% for Extron's own DSC. The command tables inside
  individual `Set`/`Update` methods are nearly identical; the surrounding runtime
  shell differs structurally. **So acceptance really must be defined on the
  wire-string table, not on line overlap** — the earlier recommendation, now with
  a second data point proving why.

The shipped ControlScript module derives from the **serial** script only: all 4
`AddMatchString` regexes identical, 0 matching the ethernet script. **Extron
ships no IP-path ControlScript module for this device at all**, despite the
`.pkp` carrying a fully built-out JSON-RPC driver.

## How to detect a multi-transport package

Not two top-level `ProtocolAsset`s. The Samsung package has **12
`DriverModelAsset`s = 6 physical sizes × 2 transports**, each owning exactly one
`ProtocolAsset` child (`SerialProtocolAsset` or `EthernetProtocolAsset`) and its
own `_scriptFileName` / `_scriptClassName` pointer.

> **Converter rule:** iterate `DriverModelAsset._scriptFileName` across all models
> sharing a `_deviceTypeName`/manufacturer, then group by the transport class of
> each model's single `ProtocolAsset` child.

Package-wide counts: 154 `DriverCommandAsset`, 113 `EnumParamAsset`, 375
`DecimalParamAsset`, 474 `EnumStateAsset`, 12 `DriverModelAsset`. Per-model
command counts are 11 (serial) and 12 (ethernet), summing to 138 — **16
package-level commands are not reachable from any model**, matching the orphaned-
command pattern seen in Extron's own DTP3 package.
