# Finding 01 — what a `.pkp` actually is

**Status: confirmed by direct inspection** of two first-party Extron drivers
(DSC 12G-HD, DTP3 CrossPoint 42). Reproduce with `tools/pkp_dump.py`.

## Container

A `.pkp` is **gzip**. Decompressed, it is a **.NET BinaryFormatter stream** —
the .NET Remoting Binary Format, publicly documented as [MS-NRBF].

```
$ file extr_17_17677_v1_0_0.pkp
gzip compressed data, max speed, from FAT filesystem, original size 629733

$ gzip -dc extr_17_17677_v1_0_0.pkp | xxd -l 17
00000000: 0001 0000 00ff ffff ff01 0000 0000 0000 00
          ^ SerializationHeaderRecord: rootId=1, headerId=-1, v1.0
```

**No encryption. No signing.** The container is open to anyone willing to walk
the record stream. That removes the single most likely blocker for the
`.pkp` → `.py` direction before any other question is asked.

## Assemblies

`BinaryLibrary` records name three assemblies, all `Version=13.26.0.15`:

- `Extron.Configuration.Drivers`
- `Extron.Configuration.Contracts`
- `Extron.Configuration.Core`

## Asset types present

`DriverModelAsset`, `DriverCommandAsset`, `DriverFileAsset`,
`EnumParamAsset`, `DecimalParamAsset`, `StringParamAsset`, `EnumStateAsset`,
`EthernetProtocolAsset`, `DanteAsset`, `StreamResourceAsset`,
`RevisionHistoryAsset`, `UTF8Password`.

Enumerations: `ExtronCommandIdEnum`, `DriverAttributeEnum`, `ParamAttributeFlags`,
`OperatorFlags`, `ProtocolCompatibilityFlags`, `DriverConditionTypeFlags`,
`EthernetTypeEnum`, `HTTPAuthenticationSchemesEnum`, `CertificationEnum`,
`DanteNicEnum`, `DriverPackageStateEnum`.

## The finding that reframes the whole question

**Each `.pkp` already contains a complete Python driver.** Not a command table
to be translated into Python — actual Python source, ~2,100–2,300 lines:

```python
from Extron2.BaseDriver import BaseDriver
import Extron.Timer as CallBackTimer
from Extron import Platform, Version

class extr_17_17677(BaseDriver):
    """Created on 06/24/2026 14:12:40
       Supported Models: DSC 12G-HD A
       DRIVER STYLE: Ethernet - Asynchronous update command responses
    """
```

So `.pkp` → ControlScript is **not a data-format conversion**. Both artifacts
are Python; they target different runtimes:

| | inside the `.pkp` | shipped ControlScript module |
|---|---|---|
| import | `Extron2.BaseDriver` | `extronlib.interface`, `extronlib.system` |
| entry class | `class extr_<id>(BaseDriver)` | `class DeviceClass:` |
| transports | handled by `BaseDriver` | `SSHClass(EthernetClientInterface, DeviceClass)` etc. |
| command table | (see finding 02) | `self.Commands` dict |
| lines (DSC / DTP3) | 2135 / 2325 | 1238 / 1335 |

The real question is therefore **runtime translation**, not format decoding.

## Incidental

The DSC package carries an absolute path from the machine that built it:
`C:\Users\billywong\OneDrive - Extron\Desktop\pakage holding folder\extr_17_17677_v1_0_0.pkp`.
Irrelevant to conversion, but it confirms these are Extron-authored packages
rather than field exports, and that the packager preserves build-host paths.
