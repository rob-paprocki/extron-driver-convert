# Finding 03 — what a Crestron `.pkg` actually is

**Status: confirmed by direct inspection** of three first-party Crestron
drivers for one Samsung display (Serial, IP, IR).

## Container

A Crestron Certified Driver `.pkg` is a **plain ZIP**.

| package | members |
|---|---|
| Serial | `*.dat` (15 KB JSON) + `*.dll` (61 KB .NET assembly) |
| IP | `*.dat` (51 KB JSON) + `*.dll` (97 KB .NET assembly) |
| **IR** | `*.ir` (2.6 KB) + `*.dat` (17 KB JSON) + `*.pdf` — **no DLL** |

## The two-layer JSON

The outer `.dat` is a **capability manifest**, not a command table. It declares
`manufacturer`, `deviceTypeId` (`"FlatPanelDisplay"` — from a fixed Crestron
taxonomy), 146 `supportedModels`, `inputs`, `communication` defaults
(RS232 9600 8N1), and a 63-entry `features` list of `Supports*` booleans
(`SupportsDiscretePower`, `SupportsVolumePercentFeedback`, …). **No wire bytes.**

The actual driver definition is **embedded inside the DLL as plain, uncompressed
UTF-8 JSON** — 46 KB of the 61 KB Serial assembly. Extract by locating
`"SchemaVersion"` and brace-matching outward. Its sections:

```
SchemaVersion  GeneralInformation  UserAttributes  Transports  SupportedFeatures
CommandIds     Commands            Responses       Conditions  Transformations
Rules          Controllers         InputOutput
```

Serial: 50 Commands / 28 Responses / 15 Transformations / 12 Rules.
IP: 77 / 22 / 16 / 42.

The DLL's metadata names `Crestron.DeviceDrivers.Core.LegacyWrappers`, and the
JSON carries `"Type": "Simpl"` — consistent with the DLL being a thin shell
around the JSON rather than hand-written device logic. **The IR package having
no DLL at all is the strongest evidence for that reading.** (Under verification.)

## The command model is declarative and composable

Crestron builds wire traffic by template composition, not by code:

```jsonc
{ "Name": "PacketWithCheckSum", "Type": "Text",
  "Info": { "Content": "{Body}{CheckSum}" },
  "Transformations": [ { "Transformation": "CheckSum", "Input": "{Body}",
                         "Output": "CheckSumAsString" },
                       { "Transformation": "AsByte", "Input": "{CheckSumAsString}",
                         "Output": "CheckSum" } ] }

{ "Name": "Packet", "Type": "Template",
  "Info": { "CommandName": "PacketWithCheckSum",
            "Values": { "Body": "{:hex} 08 22 {Function}" } } }

{ "Name": "SetVolume", "Type": "Template",
  "Info": { "CommandName": "Packet",
            "Values": { "Function": "{:hex} 01 00 00 {Volume}" } } }
```

Responses are a decoder **tree**: `RootProcessingNode` (`AlwaysMatch`) →
`CommandResponseDecoders` → named per-capability decoders, with `Next` chaining
and `"Processing": "Stop"`.

This is arguably *more* structured than Extron's approach, which expresses the
same thing as imperative Python plus `re` patterns.

## The result that matters

Same device, both vendors, **byte-identical wire traffic**:

| | Extron ControlScript | Crestron Serial CCD |
|---|---|---|
| set volume | `self.build(0x01, 0x00, 0x00, int(value))` | `Function = "{:hex} 01 00 00 {Volume}"` |
| poll volume | `self.build(0xF0, 0x01, 0x00, 0x00)` | `Function = "{:hex} f0 01 00 00"` |

Extron's `build()` prepends the `0xAA` header and appends the checksum; Crestron's
`Packet` / `PacketWithCheckSum` templates do exactly the same framing declaratively.

Two vendors, two independent driver teams, two representations — and the same
bytes on the wire. That is the empirical basis for a shared intermediate
representation: the *device protocol* is the invariant, and each vendor format is
a projection of it.

Extron module line references: `samples/Samsung QNxxLS03DAFXZA/controlscript/
smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py:204` and `:211`.

## Open, under verification

- Is the DLL genuinely a thin wrapper, or is behaviour hidden in IL?
- Is a `.pkg` signed / certified before a processor will load it? **This single
  answer decides whether emitting Crestron drivers is possible at all.**
- Does the byte-level correspondence hold across the *full* command set, or only
  the commands checked so far?
