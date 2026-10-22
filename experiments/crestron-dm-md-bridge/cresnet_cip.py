"""Cresnet-over-CIP wire encoder/decoder for Crestron Category-A slave devices.

Based on the reverse-engineering of Crestron.SimplSharpPro.* assemblies in
`experiments/crestron-dm-md-bridge/evidence/12-dm-protocol-reverse-engineered.md`.

Scope: the L3 sig-dispatch envelope — nested containers (0x20 / 0x35 / 0x41 /
0x42) with inner Cresnet-leaf packets. This library DOES NOT implement the
TCP transport (L1) or sign-on handshake (L2). It encodes/decodes the body
that eventually rides inside a CIP opcode-0x05 "data" container.

Fixtures: the canonical docblock example at SimplSharpPro_exe.cs:114730-114772 —
    MySwampE4.Zones[2].Bass.UShortValue = 25
    HierarchyList = [3, 4],  Device.ID = 2,  join = 7,  value = 25
    produces bytes: 03 0B 20 04 08 20 02 05 14 00 07 00 19
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# ---------- container type bytes ---------------------------------------------

CONTAINER_SHORT          = 0x20  # [id:1][len:1][...] - the workhorse
CONTAINER_SHORT_LONGLEN  = 0x35  # [id:1][len_be:2][...]
CONTAINER_32B_ID         = 0x41  # [id_be:4][len:1][...]
CONTAINER_LONG_32B_ID    = 0x42  # [id_be:4][len_be:2][...]


# ---------- inner Cresnet leaf types (subset we need for DM-RMC) --------------

CRES_DIGITAL             = 0x00  # (variant codes in enum CresnetTypes at :496431)
CRES_ANALOG_SHORT        = 0x01
CRES_ANALOG_REALLY_SHORT = 0x02
CRES_CRESNET_CONTROL     = 0x03
CRES_ANALOG_LONG_14      = 0x14
CRES_SERIAL_15           = 0x15
CRES_IR_DATA             = 0x16
CRES_INTERNAL_CONTROL    = 0x18
CRES_SERIAL_EXTENDED_34  = 0x34  # extended-length serial for long payloads


# ---------- Dotfuscator-free encoder primitives ------------------------------

def _choose_container_type(id_: int, body_len: int) -> int:
    """Pick 0x20/0x35/0x41/0x42 based on id size and body length — matches
    AddEncapsulationToPacket at SimplSharpPro_exe.cs:114775."""
    long_id = id_ > 0xFF
    long_len = body_len > 0xFF
    if long_id and long_len:
        return CONTAINER_LONG_32B_ID
    if long_id:
        return CONTAINER_32B_ID
    if long_len:
        return CONTAINER_SHORT_LONGLEN
    return CONTAINER_SHORT


def encode_container(id_: int, body: bytes) -> bytes:
    """Wrap `body` as a single Cresnet container around a given id.

    Byte layout:
      0x20: [id:1][len:1][body...]
      0x35: [id:1][len:2 BE][body...]
      0x41: [id:4 BE][len:1][body...]
      0x42: [id:4 BE][len:2 BE][body...]

    The length field counts bytes AFTER itself through end-of-container,
    including the container-type byte of the first inner element.
    """
    t = _choose_container_type(id_, len(body))
    if t == CONTAINER_SHORT:
        assert 0 <= id_ <= 0xFF and len(body) <= 0xFF
        return bytes([id_, len(body) + 1, t]) + body
    if t == CONTAINER_SHORT_LONGLEN:
        assert 0 <= id_ <= 0xFF
        return bytes([id_, (len(body) + 1) >> 8 & 0xFF, (len(body) + 1) & 0xFF, t]) + body
    if t == CONTAINER_32B_ID:
        assert len(body) <= 0xFF
        return (id_.to_bytes(4, "big")
                + bytes([len(body) + 1, t])
                + body)
    # CONTAINER_LONG_32B_ID
    return (id_.to_bytes(4, "big")
            + bytes([(len(body) + 1) >> 8 & 0xFF, (len(body) + 1) & 0xFF, t])
            + body)


def wrap_hierarchy(hierarchy: Iterable[int], device_id: int, leaf: bytes) -> bytes:
    """Wrap a leaf packet in a chain of containers for the hierarchy walk.

    IMPORTANT: the DEEPEST level has NO container-type byte — the leaf's own
    type byte (0x14 analog, 0x15 serial, 0x03 digital-control, 0x16 IR...)
    serves as the type. Only OUTER levels get a 0x20 (or 0x35/0x41/0x42) byte.

    Example from the docblock (SimplSharpPro_exe.cs:114730-114772):

        MySwampE4.Zones[2].Bass.UShortValue = 25
        HierarchyList = [3, 4],  Device.ID = 2, join = 7, value = 25
        leaf = [0x14, 0x00, 0x07, 0x00, 0x19]
        wrap_hierarchy([3, 4], 2, leaf)
          -> [03 0B 20  04 08 20  02 05 14 00 07 00 19]
             │ outer │ │  mid  │ └── device_id | len | LEAF ──┘
                                     (no 0x20 — the 0x14 leaf-type is the type byte)
    """
    # Deepest level: [device_id][len][leaf_bytes...] — len counts the leaf bytes.
    # Length limit of 0xFF at this level — longer payloads need the 0x35 long-length form,
    # which we don't currently emit at the leaf level (serial 0x34 handles that path).
    assert len(leaf) <= 0xFF, "use CRES_SERIAL_EXTENDED_34 for leaf > 255 B"
    buf = bytes([device_id, len(leaf)]) + leaf
    # Outer containers: [parent_id][len=len(inner)+1][0x20][inner...]
    # (len+1 accounts for the 0x20 container-type byte we're about to add)
    for parent_id in reversed(list(hierarchy)):
        inner = buf
        t = _choose_container_type(parent_id, len(inner))
        if t == CONTAINER_SHORT:
            buf = bytes([parent_id, len(inner) + 1, t]) + inner
        elif t == CONTAINER_SHORT_LONGLEN:
            buf = bytes([parent_id,
                         (len(inner) + 1) >> 8 & 0xFF,
                         (len(inner) + 1) & 0xFF, t]) + inner
        elif t == CONTAINER_32B_ID:
            buf = parent_id.to_bytes(4, "big") + bytes([len(inner) + 1, t]) + inner
        else:  # CONTAINER_LONG_32B_ID
            buf = parent_id.to_bytes(4, "big") + bytes([(len(inner) + 1) >> 8 & 0xFF,
                                                         (len(inner) + 1) & 0xFF, t]) + inner
    return buf


# ---------- leaf encoders -----------------------------------------------------

def encode_digital(join: int, press: bool) -> bytes:
    """Long-digital 0x03 0x00 leaf (BuildAndSendCresnetLongDigital_00h_Internal
    at SimplSharpPro_exe.cs:99862). Press = state 1, release = state 0 with the
    0x80 bit set on JoinHi.

    Byte layout:  [0x03][0x00][join_lo][join_hi | (release ? 0x80 : 0)]
    `join` is zero-based (= public one-based join minus 1).
    """
    assert 0 <= join <= 0x7FFF
    jh = (join >> 8) & 0x7F
    jl = join & 0xFF
    if not press:
        jh |= 0x80
    return bytes([CRES_CRESNET_CONTROL, 0x00, jl, jh])


def encode_analog(join: int, value: int) -> bytes:
    """Long-analog 0x14 leaf. join is zero-based.

    Byte layout:  [0x14][join_hi][join_lo][value_hi][value_lo]   — all big-endian
    """
    assert 0 <= join <= 0xFFFF
    assert 0 <= value <= 0xFFFF
    return bytes([CRES_ANALOG_LONG_14,
                  (join >> 8) & 0xFF, join & 0xFF,
                  (value >> 8) & 0xFF, value & 0xFF])


def encode_serial_15(join: int, payload: bytes, encoding: int = 0, text_mode: int = 0,
                     encrypted: bool = False) -> bytes:
    """Short-serial 0x15 leaf (BuildCresnetSerial_Internal_15h at :102721).

    Byte layout:  [0x15][join_hi][join_lo][flagByte][payload...]
    where flagByte = (encoding) | (textMode) | (encrypted ? 0x20 : 0).

    Encoding values from the SIMPL# Pro ComPort config (not spelled out in the
    docblock; infer from eStringEncoding — 0x00 is typically ASCII):
      0x00 ASCII,  0x01 UTF-8,  0x02 UTF-16LE,  0x03 UTF-16BE,  0x04 raw
    textMode:
      0x00 single-string (self-contained),  0x08 continuation,  0x10 final-of-chain
    """
    assert 0 <= join <= 0xFFFF
    assert len(payload) <= 251, "use 0x34 extended-serial for payloads > 251 B"
    flag = (encoding & 0x07) | (text_mode & 0x18) | (0x20 if encrypted else 0)
    return bytes([CRES_SERIAL_15,
                  (join >> 8) & 0xFF, join & 0xFF,
                  flag]) + payload


def encode_ir_start_by_uid(port_index: int, driver_crc: int, function_crc: int,
                           counter: int = 0, flags: int = 0) -> bytes:
    """IR_DATA 0x16, subtype 0x07 'start-by-UID' (BuildAndSendIRStartByUID at :305541).

    IR has NO join; it is keyed by raw port_index (0-based). driver_crc and
    function_crc are 32-bit CRCs of the loaded IR driver file and the specific
    command within it; counter is a monotonic sequence number.

    Byte layout:
      [0x16][0x07][port_index][driver_crc_be:4][function_crc_be:4][counter_be:2][flags]
    """
    assert 0 <= port_index <= 0xFF
    assert 0 <= driver_crc <= 0xFFFFFFFF
    assert 0 <= function_crc <= 0xFFFFFFFF
    assert 0 <= counter <= 0xFFFF
    return (bytes([CRES_IR_DATA, 0x07, port_index])
            + driver_crc.to_bytes(4, "big")
            + function_crc.to_bytes(4, "big")
            + counter.to_bytes(2, "big")
            + bytes([flags]))


# ---------- decoder (lenient — unknown types pass through as raw) ------------

@dataclass
class Node:
    """A node in a decoded hierarchy tree. Either a container (has children) or a leaf."""
    is_container: bool
    id_or_type: int
    children: list["Node"] | None = None  # for containers
    body: bytes | None = None             # for leaves


def decode(data: bytes, offset: int = 0, end: int | None = None) -> list[Node]:
    """Decode a bytes buffer into a list of Nodes. Robust to unknown types."""
    if end is None:
        end = len(data)
    out: list[Node] = []
    i = offset
    while i < end:
        if end - i < 2:
            # Dangling byte — treat as raw
            out.append(Node(is_container=False, id_or_type=data[i], body=data[i:end]))
            break
        head = data[i]
        # Containers: head is an id/first-byte; next byte(s) are a length,
        # then container-type byte. We detect by SNIFFING forward 2-3 bytes
        # for a container-type (0x20/0x35/0x41/0x42).
        # The outer caller must give us the slice *inside* a container, so
        # here we assume the stream alternates containers at the top level.
        # Try container short:
        if end - i >= 3 and data[i + 2] in (CONTAINER_SHORT, CONTAINER_SHORT_LONGLEN,
                                             CONTAINER_32B_ID, CONTAINER_LONG_32B_ID):
            # Can't be — these are 4-byte-ID containers, head here is wrong
            pass
        # Simple short container: [id:1][len:1][type=0x20][body...]
        if end - i >= 3 and data[i + 2] == CONTAINER_SHORT:
            id_ = data[i]
            length = data[i + 1]
            # body = length-1 bytes AFTER the type byte
            body_start = i + 3
            body_end = i + 2 + length
            if body_end > end:
                break
            kids = decode(data, body_start, body_end)
            out.append(Node(is_container=True, id_or_type=id_, children=kids))
            i = body_end
            continue
        # [id:1][len_hi:1][len_lo:1][type=0x35][body...]
        if end - i >= 4 and data[i + 3] == CONTAINER_SHORT_LONGLEN:
            id_ = data[i]
            length = (data[i + 1] << 8) | data[i + 2]
            body_start = i + 4
            body_end = i + 3 + length
            if body_end > end:
                break
            kids = decode(data, body_start, body_end)
            out.append(Node(is_container=True, id_or_type=id_, children=kids))
            i = body_end
            continue
        # Leaf — read 1-byte type and keep the rest to end
        node = _try_decode_leaf(data, i, end)
        out.append(node)
        break
    return out


def _try_decode_leaf(data: bytes, i: int, end: int) -> Node:
    """Interpret the remaining bytes as a single leaf of a known type."""
    t = data[i]
    body = bytes(data[i:end])
    return Node(is_container=False, id_or_type=t, body=body)


# ---------- DM-RMC-4K-SCALER-C join map --------------------------------------
# Source: experiments/crestron-dm-md-bridge/evidence/12-dm-protocol-reverse-engineered.md
# plus Rmc200CCOMSlot ID=1, Rmc200CIRSlot ID=2, Relay1 magic=110, Relay2 magic=160
# from decompiled DmRmcScalerC.cs. Joins here are ZERO-BASED (wire form).

@dataclass(frozen=True)
class DmRmc4kScalerCMap:
    """Join map for DM-RMC-4K-SCALER-C under a given IPID.

    All join numbers are the zero-based wire form (public one-based minus 1).
    """
    ipid: int

    # Slot IDs
    SLOT_COM = 1
    SLOT_IR = 2
    SLOT_SCALER = 3
    SLOT_DMINPUT = 4

    # Within SLOT_COM, the Rmc200CCOMSlot has a single ComPort with port index 0.
    # ComPortJoins.Joins[portIndex=0][14] = 0 is the TX serial join (zero-based).
    COM_PORT_INDEX = 0
    COM_TX_SERIAL_JOIN = 0   # zero-based

    # IR has no join — keyed by raw port index. Rmc200CIRSlot has IR ports 0 and 1.
    IR_PORT_INDICES = (0, 1)

    # Relays attach to the parent InternalDevice at magic cue numbers 110 and 160.
    # Wire-level setter sends MagicCueNumber-1 as a zero-based digital join.
    RELAY1_DIGITAL_JOIN = 109
    RELAY2_DIGITAL_JOIN = 159

    def encode_com_tx(self, text: bytes | str) -> bytes:
        """Encode a ComPort TX frame. Returns the Cresnet-wrapped payload ready
        to prepend outer CIP framing to."""
        if isinstance(text, str):
            text = text.encode("ascii")
        leaf = encode_serial_15(self.COM_TX_SERIAL_JOIN, text,
                                encoding=0, text_mode=0)
        # Hierarchy: outer IPID → SLOT_COM(1) → device_id = port 0
        return wrap_hierarchy([self.ipid, self.SLOT_COM], self.COM_PORT_INDEX, leaf)

    def encode_relay_close(self, relay_number: int) -> bytes:
        """relay_number: 1 or 2."""
        join = self.RELAY1_DIGITAL_JOIN if relay_number == 1 else self.RELAY2_DIGITAL_JOIN
        leaf = encode_digital(join, press=True)
        # Relays are children of the parent InternalDevice — hierarchy is just [ipid]
        # (no slot container). Device.ID for Relay is 0 (the parent InternalDevice).
        return wrap_hierarchy([self.ipid], 0, leaf)

    def encode_relay_open(self, relay_number: int) -> bytes:
        join = self.RELAY1_DIGITAL_JOIN if relay_number == 1 else self.RELAY2_DIGITAL_JOIN
        leaf = encode_digital(join, press=False)
        return wrap_hierarchy([self.ipid], 0, leaf)

    def encode_ir_press(self, ir_port: int, driver_crc: int, function_crc: int,
                        counter: int = 0) -> bytes:
        """ir_port: 0 or 1 (zero-based)."""
        leaf = encode_ir_start_by_uid(ir_port, driver_crc, function_crc, counter)
        return wrap_hierarchy([self.ipid, self.SLOT_IR], 0, leaf)


# ---------- small self-test ---------------------------------------------------

def _selftest() -> None:
    """Verify against the canonical docblock example.

    From SimplSharpPro_exe.cs:114730-114772:
      MySwampE4.Zones[2].Bass.UShortValue = 25
      HierarchyList = [3, 4],  Device.ID = 2,  join = 7,  value = 25
      -> [03 0B 20  04 08 20  02 05 14 00 07 00 19]
    """
    leaf = encode_analog(join=7, value=25)
    assert leaf == bytes.fromhex("14 00 07 00 19"), f"analog leaf wrong: {leaf.hex()}"

    wrapped = wrap_hierarchy([3, 4], 2, leaf)
    expected = bytes.fromhex("03 0B 20 04 08 20 02 05 14 00 07 00 19")
    assert wrapped == expected, f"hierarchy wrap wrong:\n  got      {wrapped.hex(' ')}\n  expected {expected.hex(' ')}"

    # Round-trip decode
    tree = decode(wrapped)
    assert len(tree) == 1 and tree[0].is_container and tree[0].id_or_type == 3
    assert tree[0].children[0].id_or_type == 4
    assert tree[0].children[0].children[0].id_or_type == 2
    print("[selftest] docblock vector OK")

    # Digital press on join 109 (Relay1 close)
    d = encode_digital(109, True)
    assert d == bytes.fromhex("03 00 6D 00"), f"digital press wrong: {d.hex()}"
    d = encode_digital(109, False)
    assert d == bytes.fromhex("03 00 6D 80"), f"digital release wrong: {d.hex()}"
    print("[selftest] digital leaf OK")

    # Serial 0x15, join 0, 'TEST\r' ASCII
    s = encode_serial_15(0, b"TEST\r")
    expected = bytes.fromhex("15 00 00 00") + b"TEST\r"
    assert s == expected, f"serial leaf wrong: {s.hex()}"
    print("[selftest] serial leaf OK")

    # Full DM-RMC-4K-SCALER-C ComPort TX for IPID 0x50
    rmc = DmRmc4kScalerCMap(ipid=0x50)
    pkt = rmc.encode_com_tx("TEST\r")
    # Hierarchy: 0x50 (ipid) -> 0x01 (SLOT_COM) -> device_id=0x00 (port) -> leaf
    # leaf (serial 0x15, join 0, 'TEST\r'):          [15 00 00 00] + "TEST\r" = 9 bytes
    # deepest level (no 0x20):   [00][09][leaf]                              = 11 bytes
    # SLOT_COM container:        [01][0C][20][inner]                         = 14 bytes
    # IPID container:            [50][0F][20][inner]                         = 17 bytes
    expected = bytes.fromhex("50 0F 20 01 0C 20 00 09 15 00 00 00") + b"TEST\r"
    assert pkt == expected, f"RMC ComPort TX wrong:\n  got      {pkt.hex(' ')}\n  expected {expected.hex(' ')}"
    print("[selftest] DM-RMC-4K-SCALER-C ComPort TX full-stack OK")

    # Relay1 close - no slot container; relay sits directly under IPID's InternalDevice
    pkt = rmc.encode_relay_close(1)
    # leaf (long-digital):       [03 00 6D 00]                               = 4 bytes
    # deepest (device_id=0):     [00][04][leaf]                              = 6 bytes
    # IPID container:            [50][07][20][inner]                         = 9 bytes
    expected = bytes.fromhex("50 07 20 00 04 03 00 6D 00")
    assert pkt == expected, f"RMC Relay1 close wrong:\n  got      {pkt.hex(' ')}\n  expected {expected.hex(' ')}"
    print("[selftest] DM-RMC-4K-SCALER-C Relay1 close full-stack OK")

    print("\nAll self-tests passed. L3 encoder matches the Crestron docblock example.")


if __name__ == "__main__":
    _selftest()
