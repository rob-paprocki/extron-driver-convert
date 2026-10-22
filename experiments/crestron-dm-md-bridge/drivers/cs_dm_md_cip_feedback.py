"""cs_dm_md_cip_feedback.py - Extron ControlScript real-time feedback driver
for Crestron DM-MD CPU3/CPU4 chassis via CIP XPanel masquerade (TCP :41794).

This is the FEEDBACK HALF of a complete DM chassis driver. It opens a passive
CIP session as the chassis's stock-XPanel slot (IPID 1 by default) and
subscribes to the chassis's push-based signal cache - digital, analog and
serial joins change in real time with no polling needed.

Pair with cs_dm_md_ctp.py (which sends routing commands via CTP :41795), or
with the chassis's SSH console if CTP is not enabled.

Verified protocol surface (see evidence/01-15 in the extron-driver-convert
research branch):
  Handshake:
    chassis -> master: 0F 00 01 02                     program-ready
    master  -> chassis: 01 00 0B 00 00 00 00 00 <IPID> 40 FF FF F1 01   register
    chassis -> master: 02 00 04 00 00 00 1F             REGISTER_OK
    master  -> chassis: 05 00 05 00 00 02 03 00         UPDATE_REQUEST
    chassis -> master: ...initial signal cache...       (digital/analog/serial)
    chassis -> master: 05 00 05 00 00 02 03 1C          end-of-query
    master  -> chassis: 05 00 05 00 00 02 03 1D         ACK end-of-query
    both -> both:     0D 00 02 00 00                    heartbeat every 15 s

  Framing: [op:1][len:2 BE][payload]
  Decoders: digital (op=05, sub-type 03), analog (op=05, sub-type 14),
            serial (op=12).

NOT included here: command surface (writes). This driver is receive-only. For
routing commands, use cs_dm_md_ctp.py or send CTP commands via the chassis's
SSH console separately. See evidence/13 for why pure-CIP routing against the
OEM default program is not currently proven.

IPID selection: the chassis's stock-XPanel slot is IPID 1. Observed to be
non-destructive when the real stock XPanel is not actively connected (which
is the normal state on an OEM-firmware-only chassis). If the real XPanel
connects, the chassis may evict one side; test in your installation.
"""
from __future__ import annotations

try:
    from extronlib.interface import EthernetClientInterface
    from extronlib.system import Wait, ProgramLog
    _ONDEVICE = True
except ImportError:
    _ONDEVICE = False
    class EthernetClientInterface:
        def __init__(self, host, port, protocol="TCP"):
            self.Hostname = host; self.ServicePort = port; self.Protocol = protocol
            self.Connected = None; self.Disconnected = None; self.ReceiveData = None
        def Connect(self, timeout=None): print(f"[stub] connect {self.Hostname}:{self.ServicePort}")
        def Disconnect(self): print("[stub] disconnect")
        def Send(self, data): pass
    def Wait(interval, action=None):
        import threading
        t = threading.Timer(interval, action); t.daemon = True; t.start()
        return t
    def ProgramLog(msg, severity="info"): print(f"[log/{severity}] {msg}")


# --- CIP protocol constants (verified in evidence/04 and evidence/12) --------

OP_PROGRAM_READY   = 0x0F
OP_REGISTER        = 0x01
OP_REGISTER_RESULT = 0x02
OP_DATA            = 0x05
OP_SERIAL          = 0x12
OP_HEARTBEAT       = 0x0D

REG_SUCCESS      = b"\x00\x00\x00\x1f"
REG_NOT_DEFINED  = b"\xff\xff\x02"
UPDATE_REQUEST   = bytes([0x05, 0x00, 0x05, 0x00, 0x00, 0x02, 0x03, 0x00])
END_OF_QUERY_ACK = bytes([0x05, 0x00, 0x05, 0x00, 0x00, 0x02, 0x03, 0x1D])
HEARTBEAT_PKT    = bytes([0x0D, 0x00, 0x02, 0x00, 0x00])
HEARTBEAT_INTERVAL_S = 15.0


def _build_registration(ipid: int) -> bytes:
    assert 1 <= ipid <= 254
    return bytes([0x01, 0x00, 0x0B,
                  0x00, 0x00, 0x00, 0x00, 0x00,
                  ipid,
                  0x40, 0xFF, 0xFF, 0xF1, 0x01])


def _decode_digital(payload: bytes):
    # payload: 00 00 03 TT LL HH    TT in {00, 27}
    if len(payload) < 6: return None
    ll, hh = payload[4], payload[5]
    join = (((hh & 0x7F) << 8) | ll) + 1
    state = ((hh & 0x80) >> 7) ^ 0x01
    return join, state


def _decode_analog(payload: bytes):
    # payload: 00 00 05 14 JH JL VH VL
    if len(payload) < 8: return None
    join = ((payload[4] << 8) | payload[5]) + 1
    value = (payload[6] << 8) | payload[7]
    return join, value


def _decode_serial(payload: bytes):
    # payload: 00 00 00 IL 34 JH JL FF <text>
    if len(payload) < 8 or payload[4] != 0x34: return None
    join = ((payload[5] << 8) | payload[6]) + 1
    return join, bytes(payload[8:])


class DmMdCipFeedback:
    """Passive CIP feedback subscriber for Crestron DM-MD CPU3/CPU4 chassis."""

    def __init__(self, host: str, port: int = 41794, ipid: int = 1,
                 reconnect_backoff_s: float = 5.0):
        self.host = host
        self.port = port
        self.ipid = ipid
        self.reconnect_backoff_s = reconnect_backoff_s

        self._client: EthernetClientInterface | None = None
        self._rxbuf = bytearray()
        self._registered = False
        self._end_of_query_seen = False
        self._heartbeat_timer = None

        # Feedback state (public read-only)
        self.connected = False
        self.digitals: dict[int, int] = {}
        self.analogs: dict[int, int] = {}
        self.serials: dict[int, bytes] = {}

        # User callbacks
        self.on_digital_change = None   # callable(join: int, state: int)
        self.on_analog_change  = None   # callable(join: int, value: int)
        self.on_serial_change  = None   # callable(join: int, text: bytes)
        self.on_ready = None            # fires once after end-of-query is acked
        self.on_connect = None
        self.on_disconnect = None

    # ---- Lifecycle ----

    def start(self):
        self._open()

    def stop(self):
        if self._client is not None:
            try: self._client.Disconnect()
            except Exception: pass
            self._client = None
            self.connected = False
            self._registered = False
            self._end_of_query_seen = False

    def _open(self):
        self._client = EthernetClientInterface(self.host, self.port, "TCP")
        self._client.Connected = self._on_connected
        self._client.Disconnected = self._on_disconnected
        self._client.ReceiveData = self._on_data
        try:
            self._client.Connect(timeout=5)
        except Exception as e:
            ProgramLog(f"[dm-cip] connect failed: {e}", "warning")
            Wait(self.reconnect_backoff_s, self._open)

    def _on_connected(self, interface, state):
        ProgramLog(f"[dm-cip] TCP connected to {self.host}:{self.port}", "info")
        self.connected = True
        self._registered = False
        self._end_of_query_seen = False
        self._rxbuf = bytearray()
        if callable(self.on_connect):
            try: self.on_connect()
            except Exception: pass

    def _on_disconnected(self, interface, state):
        self.connected = False
        self._registered = False
        if self._heartbeat_timer is not None:
            try: self._heartbeat_timer.Cancel()
            except Exception: pass
            self._heartbeat_timer = None
        ProgramLog(f"[dm-cip] disconnected; reconnect in {self.reconnect_backoff_s}s", "info")
        if callable(self.on_disconnect):
            try: self.on_disconnect()
            except Exception: pass
        Wait(self.reconnect_backoff_s, self._open)

    # ---- RX framing + dispatch ----

    def _on_data(self, interface, data: bytes):
        self._rxbuf.extend(data)
        while True:
            frame = self._peel_frame()
            if frame is None:
                break
            op, payload = frame
            self._handle_frame(op, payload)

    def _peel_frame(self):
        if len(self._rxbuf) < 3:
            return None
        op = self._rxbuf[0]
        plen = (self._rxbuf[1] << 8) | self._rxbuf[2]
        if len(self._rxbuf) < 3 + plen:
            return None
        payload = bytes(self._rxbuf[3:3 + plen])
        del self._rxbuf[:3 + plen]
        return op, payload

    def _send(self, b: bytes):
        if self._client is None or not self.connected:
            return
        try:
            self._client.Send(b)
        except Exception as e:
            ProgramLog(f"[dm-cip] send error: {e}", "warning")

    def _handle_frame(self, op: int, payload: bytes):
        if op == OP_PROGRAM_READY:
            # Chassis is ready to accept registration
            self._send(_build_registration(self.ipid))
            return

        if op == OP_REGISTER_RESULT:
            if payload == REG_SUCCESS:
                self._registered = True
                ProgramLog(f"[dm-cip] registered as IPID 0x{self.ipid:02X}", "info")
                self._send(UPDATE_REQUEST)
            elif payload == REG_NOT_DEFINED:
                ProgramLog(f"[dm-cip] IPID 0x{self.ipid:02X} not defined in chassis IP table", "warning")
            else:
                ProgramLog(f"[dm-cip] unexpected registration result: {payload.hex(' ')}", "warning")
            return

        if op == OP_HEARTBEAT:
            # Chassis heartbeat; echo
            self._send(HEARTBEAT_PKT)
            return

        if op == OP_SERIAL:
            got = _decode_serial(payload)
            if got:
                join, text = got
                self.serials[join] = text
                if callable(self.on_serial_change):
                    try: self.on_serial_change(join, text)
                    except Exception as e: ProgramLog(f"[dm-cip] on_serial_change error: {e}", "warning")
            return

        if op == OP_DATA:
            if len(payload) >= 5 and payload[0:4] == b"\x00\x00\x02\x03":
                marker = payload[4]
                if marker == 0x1C:
                    # End-of-query - ack it, start heartbeat
                    self._send(END_OF_QUERY_ACK)
                    self._send(HEARTBEAT_PKT)
                    self._end_of_query_seen = True
                    self._start_heartbeat_timer()
                    ProgramLog(f"[dm-cip] initial-cache end-of-query acked; D={len(self.digitals)} A={len(self.analogs)} S={len(self.serials)}", "info")
                    if callable(self.on_ready):
                        try: self.on_ready()
                        except Exception as e: ProgramLog(f"[dm-cip] on_ready error: {e}", "warning")
                return
            if len(payload) >= 6 and payload[0:3] == b"\x00\x00\x03":
                got = _decode_digital(payload)
                if got:
                    join, state = got
                    old = self.digitals.get(join)
                    self.digitals[join] = state
                    if old != state and callable(self.on_digital_change):
                        try: self.on_digital_change(join, state)
                        except Exception as e: ProgramLog(f"[dm-cip] on_digital_change error: {e}", "warning")
                return
            if len(payload) >= 8 and payload[0:4] == b"\x00\x00\x05\x14":
                got = _decode_analog(payload)
                if got:
                    join, value = got
                    old = self.analogs.get(join)
                    self.analogs[join] = value
                    if old != value and callable(self.on_analog_change):
                        try: self.on_analog_change(join, value)
                        except Exception as e: ProgramLog(f"[dm-cip] on_analog_change error: {e}", "warning")
                return

    def _start_heartbeat_timer(self):
        def _tick():
            if self.connected and self._registered and self._end_of_query_seen:
                self._send(HEARTBEAT_PKT)
            if self.connected:
                self._heartbeat_timer = Wait(HEARTBEAT_INTERVAL_S, _tick)
        self._heartbeat_timer = Wait(HEARTBEAT_INTERVAL_S, _tick)

    # ---- Convenience: pre-mapped DM-MD-CPU3-RPS state --------------------

    # From evidence/09-poe-cycle-finding and evidence/06-oem-discovered-joinmap:
    # - Input online state: analogs A5000, A5002, A5004, A5006, A5008, A5010, A5012, A5014
    #   value 2 = online (white panel label), value 1 = offline (grey)
    # - Output online state: analogs A7000, A7004, A7008, A7012, A7016, A7020, A7024, A7028
    # - System power: serial S3000 ("ON" / "OFF")
    # - Chassis IP (programmed): serial S3002
    # - Endpoint firmware roll: serials S4010..S4019

    def input_online(self, input_num: int) -> bool | None:
        """Return True/False for Input N online state, or None if unknown yet."""
        join = {1: 5000, 2: 5002, 3: 5004, 4: 5006, 5: 5008, 6: 5010, 7: 5012, 8: 5014}.get(input_num)
        if join is None: return None
        v = self.analogs.get(join)
        if v is None: return None
        return v == 2

    def output_online(self, output_num: int) -> bool | None:
        join = {1: 7000, 2: 7004, 3: 7008, 4: 7012, 5: 7016, 6: 7020, 7: 7024, 8: 7028}.get(output_num)
        if join is None: return None
        v = self.analogs.get(join)
        if v is None: return None
        return v == 2


# ---- Self-test (offline) -----------------------------------------------------

def _selftest():
    """Verify the frame peeler + decoders against known-good bytes from the
    evidence/08 and evidence/09 captures.
    """
    d = DmMdCipFeedback("127.0.0.1", ipid=1)
    d.connected = True

    # Program-ready frame
    d._rxbuf.extend(bytes.fromhex("0f 00 01 02"))
    f = d._peel_frame()
    assert f is not None and f[0] == 0x0F and f[1] == b"\x02", f"program-ready: {f}"
    print("[selftest] program-ready peel OK")

    # Register-OK result
    d._rxbuf.extend(bytes.fromhex("02 00 04 00 00 00 1f"))
    f = d._peel_frame()
    assert f is not None and f[0] == 0x02 and f[1] == REG_SUCCESS, f"reg-ok: {f}"
    print("[selftest] register-OK peel OK")

    # Digital leaf: join 1957 = 1 (from evidence/08)
    d._rxbuf.extend(bytes.fromhex("05 00 06 00 00 03 00 a4 07"))
    f = d._peel_frame()
    got = _decode_digital(f[1])
    assert got == (1957, 1), f"digital: {got}"
    print("[selftest] digital decode OK")

    # Analog leaf: A5010 = 2 (from evidence/09)
    d._rxbuf.extend(bytes.fromhex("05 00 08 00 00 05 14 13 91 00 02"))
    f = d._peel_frame()
    got = _decode_analog(f[1])
    # payload is [00 00 05 14 13 91 00 02] -> join = 0x1391 + 1 = 5010, value = 2
    assert got == (5010, 2), f"analog: {got}"
    print("[selftest] analog decode OK")

    # Serial leaf (from evidence/08): S3002 = '172.16.0.104'
    text = b"172.16.0.104"
    serial_body = bytes([0x00, 0x00, 0x00, len(text) + 4, 0x34]) + (3001).to_bytes(2, "big") + bytes([0xFF]) + text
    frame_bytes = bytes([0x12, (len(serial_body) >> 8) & 0xFF, len(serial_body) & 0xFF]) + serial_body
    d._rxbuf.extend(frame_bytes)
    f = d._peel_frame()
    got = _decode_serial(f[1])
    assert got == (3002, text), f"serial: {got}"
    print(f"[selftest] serial decode OK: S3002 = {text!r}")

    # High-level state (after analog A5010 was decoded above)
    d.analogs[5010] = 2
    assert d.input_online(6) is True
    d.analogs[5010] = 1
    assert d.input_online(6) is False
    print("[selftest] input_online() mapping OK")

    print("\nAll self-tests passed.")


if __name__ == "__main__":
    _selftest()
