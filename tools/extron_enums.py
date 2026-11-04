#!/usr/bin/env python3
"""extron_enums.py - the four value-type enum vocabularies that pkp_asset
and pkp_build need to author graph fields from scratch (ROADMAP R28).

Every value here was read from `Extron.Configuration.Contracts.dll`
version shipped with GCP (ilspycmd 11.2.0.10050 decompile); see
experiments/graph_synthesis/ENUMS.md for the citations.

All four enums have .NET default integer backing (int32 = 4 bytes). The
NRBF stream writes an enum's value inline as the backing primitive. The
`TYPE_META` dict below encodes that, plus whether each is a `[Flags]`
bitfield.

Standard library only. Import by module path; no I/O at import time.
"""
from __future__ import annotations

from enum import IntEnum, IntFlag


class DriverAttributeEnum(IntFlag):
    """CommandAssetBase._attributes -- per-command attribute bitfield.

    Fully-qualified .NET type:
      Extron.Configuration.Contracts.DriverAttributeEnum
    Underlying type: Int32 (4 bytes).
    [Flags] = True.
    """
    ConfigurationVisible = 0x01
    RuntimeVisible = 0x02
    Alias = 0x04
    RequiredPollingCommand = 0x08
    EmulatedStatus = 0x10
    LiveStatus = 0x20
    WriteProtected = 0x40


class ExtronCommandIdEnum(IntEnum):
    """CommandAssetBase._exCmdId -- legacy per-command well-known command
    id. Marked `[Obsolete]` at the property level
    (`ICommandAsset.ExtronCommandId`); the underlying field is still
    serialised, so an authored graph must write it. Safe default is 0
    (General) unless the driver is one of the legacy well-known cases.

    Fully-qualified .NET type:
      Extron.Configuration.Contracts.ExtronCommandIdEnum
    Underlying type: Int32 (4 bytes).
    [Flags] = False.
    """
    General = 0
    Power = 1
    Input = 2
    LampHour = 3


class EthernetTypeEnum(IntEnum):
    """EthernetProtocolAsset._protocolSubType -- legacy TCP/HTTP/SSH
    subtype. Marked `[Obsolete("Use the Compability property to set the
    sub types.")]` at the property level (`IEthernetProtocolAsset.
    ProtocolSubType`), but the underlying field is still serialised in
    shipping .pkp streams, so an authored graph must write it.

    Fully-qualified .NET type:
      Extron.Configuration.Contracts.EthernetTypeEnum
    Underlying type: Int32 (4 bytes).
    [Flags] = False.
    """
    TCP = 0
    HTTP = 1
    SSH = 2


class ProtocolCompatibilityFlags(IntFlag):
    """ProtocolAsset._compatibility -- the live field GC and the
    ControlScript runtime read to pick a transport. Modern replacement
    for the obsolete EthernetTypeEnum path; the NRBF stream still writes
    both, but `_compatibility` is the one the runtime and tools/pkp2cs.py
    decode into transport classes.

    Fully-qualified .NET type:
      Extron.Configuration.Contracts.ProtocolCompatibilityFlags
    Underlying type: Int32 (4 bytes).
    [Flags] = True.

    Note the aliases: `IRHardware` reuses `IR_RS232`'s bit, and
    `SerialHardware`, `EthernetHardware` are composite masks declared in
    the enum body itself.
    """
    None_ = 0                       # Python keyword: name uses trailing underscore
    IR_RS232 = 0x001
    IRHardware = 0x001              # alias for IR_RS232
    Serial_RS232 = 0x002
    Serial_RS422 = 0x004
    Serial_RS485 = 0x008
    SerialHardware = 0x002 | 0x004 | 0x008   # 0x00E
    Ethernet_Telnet = 0x010
    Ethernet_UDP = 0x020
    Ethernet_HTTP = 0x040
    CEC = 0x080
    Embedded_Driver = 0x100
    Ethernet_SSH = 0x200
    Ethernet_Dante = 0x400
    Ethernet_RoomScheduling = 0x800
    EthernetHardware = 0xE70                 # composite mask declared in the DLL


# Per-enum metadata consumed by pkp_asset / pkp_build when they need to
# know how many bytes to emit and whether to treat a value as a bitfield
# when authoring a NRBF enum record.
TYPE_META = {
    "DriverAttributeEnum": {
        "dotnet": "Extron.Configuration.Contracts.DriverAttributeEnum",
        "underlying": "Int32",
        "size": 4,
        "flags": True,
        "obsolete": False,
    },
    "ExtronCommandIdEnum": {
        "dotnet": "Extron.Configuration.Contracts.ExtronCommandIdEnum",
        "underlying": "Int32",
        "size": 4,
        "flags": False,
        "obsolete": True,   # property marked [Obsolete]; field still serialised
    },
    "EthernetTypeEnum": {
        "dotnet": "Extron.Configuration.Contracts.EthernetTypeEnum",
        "underlying": "Int32",
        "size": 4,
        "flags": False,
        "obsolete": True,   # property marked [Obsolete]; field still serialised
    },
    "ProtocolCompatibilityFlags": {
        "dotnet": "Extron.Configuration.Contracts.ProtocolCompatibilityFlags",
        "underlying": "Int32",
        "size": 4,
        "flags": True,
        "obsolete": False,
    },
}


# Reverse-lookup convenience: name -> IntEnum/IntFlag class.
ENUMS_BY_NAME = {
    "DriverAttributeEnum": DriverAttributeEnum,
    "ExtronCommandIdEnum": ExtronCommandIdEnum,
    "EthernetTypeEnum": EthernetTypeEnum,
    "ProtocolCompatibilityFlags": ProtocolCompatibilityFlags,
}


def _member_count(cls) -> int:
    """Count distinct declared members, counting aliases once (Python's
    IntFlag/IntEnum collapses same-value declarations into one member;
    this count matches that model)."""
    return len(cls.__members__)


if __name__ == "__main__":
    print("extron_enums -- enum vocabularies decoded from "
          "Extron.Configuration.Contracts.dll")
    print()
    for name, cls in ENUMS_BY_NAME.items():
        meta = TYPE_META[name]
        tags = []
        if meta["flags"]:
            tags.append("[Flags]")
        if meta["obsolete"]:
            tags.append("[Obsolete property]")
        tag = (" " + " ".join(tags)) if tags else ""
        print(f"  {name}: {_member_count(cls)} members, "
              f"{meta['underlying']} ({meta['size']} bytes){tag}")
