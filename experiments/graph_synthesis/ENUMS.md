# ROADMAP R28 Phase 1 — the four enum vocabularies

`pkp_asset.py` writes graph fields against four value-type enums whose
members `tools/pkp_build.py` must know before it can author a package
from scratch instead of cloning a donor. Only `DriverAttributeEnum` was
decoded before this round.

**Source:** `C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Contracts.dll`,
decompiled with `ilspycmd 11.2.0.10050`. Decompile output lives in the
job's scratch dir, not the repo (vendor-derived). Line numbers below
refer to the single-file C# dump
`Extron.Configuration.Contracts.decompiled.cs`.

The Python form of these vocabularies is `tools/extron_enums.py`
(stdlib-only, importable from `pkp_asset.py` / `pkp_build.py`).

## Summary

| Enum | Backing | `[Flags]` | Members | NRBF field | Property |
|---|---|---|---|---|---|
| `DriverAttributeEnum` | Int32 | yes | 7 | `CommandAssetBase+_attributes` | `ICommandAsset.Attributes` |
| `ExtronCommandIdEnum` | Int32 | no  | 4 | `CommandAssetBase+_exCmdId` | `ICommandAsset.ExtronCommandId` `[Obsolete]` |
| `EthernetTypeEnum` | Int32 | no  | 3 | `EthernetProtocolAsset+_protocolSubType` | `IEthernetProtocolAsset.ProtocolSubType` `[Obsolete]` |
| `ProtocolCompatibilityFlags` | Int32 | yes | 16 (incl. aliases) | `ProtocolAsset+_compatibility` | `IProtocolAsset.Compatibility` |

All four are `Int32` (4-byte) backed — .NET default, no explicit
`: byte` / `: short` suffix. The NRBF stream writes each as a 4-byte
little-endian signed integer under the enum's class record.

Two of the four are reachable via `[Obsolete]` properties but the
underlying fields are still present in every shipped `.pkp` we've
dumped; an authored graph must write them to stay layout-compatible.

## DriverAttributeEnum

Line 3896 of the decompile.

```csharp
[Flags]
public enum DriverAttributeEnum
{
    ConfigurationVisible = 1,
    RuntimeVisible = 2,
    Alias = 4,
    RequiredPollingCommand = 8,
    EmulatedStatus = 0x10,
    LiveStatus = 0x20,
    WriteProtected = 0x40,
}
```

**Used by:** `ICommandAsset.Attributes` — the per-command attribute
mask GC reads when deciding whether to render a command in
Configuration vs. Runtime views, whether to treat it as a poll source,
and whether it emits live or emulated status.

**In-repo evidence:** `tools/pkp_asset.py:19` (header docstring):
> `CommandAssetBase+_attributes    DriverAttributeEnum bitfield`

and `pkp_asset.py:347-349`:

```python
def set_attributes(self, command_id, value):
    """Rewrite a command's DriverAttributeEnum bitfield."""
    self.set_enum_member(command_id, "CommandAssetBase+_attributes", value)
```

**Sample usage:** `finding 18`'s `1bynd_19_20024` writes
`RuntimeVisible | LiveStatus` (0x22) on every added polling command and
`RuntimeVisible | EmulatedStatus` (0x12) on the lightbar command for
which there is no inquiry.

## ExtronCommandIdEnum

Line 3958 of the decompile.

```csharp
public enum ExtronCommandIdEnum
{
    General,    // 0
    Power,      // 1
    Input,      // 2
    LampHour,   // 3
}
```

**Used by:** `ICommandAsset.ExtronCommandId` — marked **`[Obsolete]`**
at the property level (line 1638). Interface comment: the property is
kept for serialisation compatibility; new drivers set every command's
id to `General` (0). The backing field (`_exCmdId`) is written on every
shipping command asset in the sample set, so an authored graph has to
write it too, but the value is almost always `General`.

**In-repo evidence:** no direct consumer in `tools/`; it survives as a
graph field that `pkp_dump.py`'s member walker prints alongside
`_scriptName`, `_attributes`, and the display name. Finding 18's
`1bynd_19_20024` writes `ExtronCommandIdEnum.General` (0) on every
added command.

## EthernetTypeEnum

Line 3952 of the decompile.

```csharp
public enum EthernetTypeEnum
{
    TCP,     // 0
    HTTP,    // 1
    SSH,     // 2
}
```

**Used by:** `IEthernetProtocolAsset.ProtocolSubType` — marked
`[Obsolete("Use the Compability property to set the sub types.")]`
(line 2254). The backing field (`_protocolSubType`) is written on every
shipping ethernet protocol asset in the sample set.

Mapping to the modern `ProtocolCompatibilityFlags`:

| EthernetTypeEnum | ProtocolCompatibilityFlags equivalents |
|---|---|
| `TCP = 0` | `Ethernet_Telnet` (0x10) and `Ethernet_UDP` (0x20) |
| `HTTP = 1` | `Ethernet_HTTP` (0x40) |
| `SSH = 2` | `Ethernet_SSH` (0x200) |

**In-repo evidence:** `tools/pkp2cs.py:191` reads `_compatibility` (not
`_protocolSubType`) to pick a transport; the legacy sub-type is
preserved in the graph but no longer load-bearing for ControlScript
emission. Load-Package.ps1 already prints both enums' name-value maps
on every package it loads, so an authored value can be verified
against Extron's own reflection at runtime.

## ProtocolCompatibilityFlags

Line 4255 of the decompile. **The live one** — this is what GC and
ControlScript inspect to pick a transport.

```csharp
[Flags]
public enum ProtocolCompatibilityFlags
{
    None = 0,
    IR_RS232 = 1,
    IRHardware = IR_RS232,          // alias: same bit as IR_RS232
    Serial_RS232 = 2,
    Serial_RS422 = 4,
    Serial_RS485 = 8,
    SerialHardware = Serial_RS232 | Serial_RS422 | Serial_RS485,  // 0x00E
    Ethernet_Telnet = 0x10,
    Ethernet_UDP = 0x20,
    Ethernet_HTTP = 0x40,
    EthernetHardware = 0xE70,        // composite: 0x200 | 0x400 | 0x010 | 0x020 | 0x040 | 0x100 | 0x800
    CEC = 0x80,
    Embedded_Driver = 0x100,
    Ethernet_SSH = 0x200,
    Ethernet_Dante = 0x400,
    Ethernet_RoomScheduling = 0x800,
}
```

**Used by:** `IProtocolAsset.Compatibility` (line 2574). Every protocol
asset in every `.pkp` carries a value here; `_compatibility` is also
the field `tools/pkp2cs.py` reads to pick between `EthernetClass`,
`SSHClass` and the http fallback (lines 148, 181, 191).

**Sample usages, from `tools/pkp2cs.py` comments and residual messages:**

| Flag | Decimal | Where it shows up |
|---|---|---|
| `Ethernet_UDP` | 32 | `clau_dsp_CDT100_v1_0_3_0`'s UDP transport |
| `Ethernet_HTTP` | 64 | Automate VX (`1bynd_42_4279_v1_0_11`) |
| `Ethernet_SSH` | 512 | `1bynd_19_4743`'s SSH transport (`_port` 22023) |

`tools/pkp2cs.py:2127` explicitly reports `_compatibility=%r has no
known EthernetClass/SSHClass protocol mapping` when the value is
outside the expected set, so the 16-entry table above is already the
oracle `pkp2cs` builds against — Phase 2 can author values with full
confidence they parse correctly on the way back out.

**Caveat on aliases** (`IRHardware`, `SerialHardware`, `EthernetHardware`):
Python's `IntFlag` collapses same-bit aliases (`IRHardware == IR_RS232`)
to the first declared name when printing. `TYPE_META["ProtocolCompatibilityFlags"]["flags"]
= True` is enough for `pkp_build.py`'s authoring path; the alias names
only matter when round-tripping a human-written source back to bytes,
not when writing a value out.

## Not an enum, but worth noting

`ParamAttributeEnum` (line 4147) and `ParamAttributeFlags` (line 4165)
are a related pair we did NOT need for the four fields R28 targets,
but which shows the pattern we should expect if Phase 2 wants to author
parameter assets too: a non-flag "kind" enum plus a flags enum, with
an extension class (`ParamAttributeEnumExtensions`, line 4157)
providing `.ToFlag()`. Noted here so a future R28b (parameter asset
authoring) doesn't rediscover it.

## Where Phase 2 will consume this

`tools/pkp_asset.py`'s `set_enum_member(graph_id, type_name, value)`
already takes the `.NET` type name as a string. The next step is to
accept a `value` that is one of these `IntEnum`/`IntFlag` instances
(in addition to the current integer form), look up `TYPE_META` to get
the byte size and `[Flags]` behaviour, and write the correct NRBF
primitive record under the enum class record. See
`experiments/graph_synthesis/RESULTS.md` "R28" for the measured root
container shape that will consume the authored `IDriverCommandAsset`.

## Decompile provenance

| Field | Value |
|---|---|
| Assembly | `Extron.Configuration.Contracts.dll` |
| Install location | `C:\Program Files (x86)\Extron\GCP\` |
| Decompiler | `ilspycmd 11.2.0.10050` |
| Scratch dir (not in repo) | `C:\Users\<user>\.claude\jobs\133030b3\tmp\contracts-decompiled\` |
| Decompile line count | 6,347 |
| Enums examined | 4 of 56 declared in the DLL |

The other 52 enums are catalogued by `grep -nE "^[[:space:]]*public enum "`
in the decompile file; a future R28b that needs any of them (for
example a param-asset authoring pass) can reuse the same decompile
without re-running the tool.
