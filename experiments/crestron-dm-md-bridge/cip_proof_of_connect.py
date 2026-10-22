"""
CIP proof-of-connect - Crestron DM-MD8X8-CPU3-RPS

Opens TCP to a Crestron 3-Series on 41794, registers as a chosen IP-ID,
consumes the initial signal cache, dumps every join + value, holds the
connection a few seconds to prove feedback flows, then clean-shuts.

Passive by design: does NOT send any digital/analog/serial write packets.

Protocol references cross-cited by the research workflow against
rdriscoll/Crestron-CIP, klenae/python-cipclient, rellis-erigon/Crestron-CIP-HA,
Antonio112009/pycrestron-cip, thatinjury2011/Dotnet-CrestronCIP.

Stdlib only - ports verbatim to the Extron IPL Pro ControlScript side later.
"""

from __future__ import annotations
import argparse
import socket
import sys
import time


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
HEARTBEAT        = bytes([0x0D, 0x00, 0x02, 0x00, 0x00])

HEARTBEAT_INTERVAL = 15.0


def log(msg):
    sys.stderr.write("[" + time.strftime("%H:%M:%S") + "] " + msg + "\n")
    sys.stderr.flush()


def hexs(b, limit=32):
    if len(b) <= limit:
        return b.hex(" ")
    return b[:limit].hex(" ") + " ...(+" + str(len(b)-limit) + " B)"


def build_registration(ipid):
    if not (1 <= ipid <= 254):
        raise ValueError("IPID out of range")
    return bytes([
        0x01, 0x00, 0x0B,
        0x00, 0x00, 0x00, 0x00, 0x00,
        ipid,
        0x40, 0xFF, 0xFF, 0xF1, 0x01,
    ])


def build_press(join, state=1):
    # TX frame: 05 00 06 00 LL HH   where swap((join-1)) low byte then high byte;
    # state 0 (release) sets HH bit 7.
    if not (1 <= join <= 65535):
        raise ValueError('join out of range')
    j = join - 1
    LL = j & 0xFF
    HH = (j >> 8) & 0x7F
    if state == 0:
        HH |= 0x80
    return bytes([0x05, 0x00, 0x06, 0x00, LL, HH])


def build_set_analog(join, value):
    # TX frame: 05 00 08 14 JH JL VH VL
    if not (1 <= join <= 65535):
        raise ValueError('join out of range')
    if not (0 <= value <= 0xFFFF):
        raise ValueError('value out of range')
    j = join - 1
    return bytes([0x05, 0x00, 0x08, 0x14,
                  (j >> 8) & 0xFF, j & 0xFF,
                  (value >> 8) & 0xFF, value & 0xFF])


def build_send_serial(join, text):
    # TX frame: 12 LH LL 00 00 00 IL 34 JH JL FF <text>
    # outer_len = len(text) + 8 big-endian in LH LL
    # inner_len = len(text) + 4 single byte at offset 3 of payload (IL)
    # FF = flags; 0xFF = single self-contained message
    if isinstance(text, str):
        text = text.encode('utf-8')
    if not (1 <= join <= 65535):
        raise ValueError('join out of range')
    if len(text) > 251:
        raise ValueError('text too long for single frame (max 251 B)')
    outer = len(text) + 8
    inner = len(text) + 4
    j = join - 1
    return bytes([0x12,
                  (outer >> 8) & 0xFF, outer & 0xFF,
                  0x00, 0x00, 0x00, inner & 0xFF,
                  0x34,
                  (j >> 8) & 0xFF, j & 0xFF,
                  0xFF]) + text


def decode_digital(payload):
    # payload: 00 00 03 TT LL HH   (TT in {0x00, 0x27})
    if len(payload) < 6:
        return None
    LL = payload[4]
    HH = payload[5]
    join = (((HH & 0x7F) << 8) | LL) + 1
    state = ((HH & 0x80) >> 7) ^ 0x01
    return (join, state)


def decode_analog(payload):
    # payload: 00 00 05 14 JH JL VH VL
    if len(payload) < 8:
        return None
    join = ((payload[4] << 8) | payload[5]) + 1
    value = (payload[6] << 8) | payload[7]
    return (join, value)


def decode_serial(payload):
    # payload: 00 00 00 IL 34 JH JL FF <text>
    if len(payload) < 8 or payload[4] != 0x34:
        return None
    JH = payload[5]
    JL = payload[6]
    join = ((JH << 8) | JL) + 1
    text = payload[8:]
    return (join, text)


class CipClient(object):

    def __init__(self, host, port=41794, ipid=3, timeout=10.0):
        self.host = host
        self.port = port
        self.ipid = ipid
        self.timeout = timeout
        self.sock = None
        self.rxbuf = bytearray()
        self.digitals = {}
        self.analogs = {}
        self.serials = {}
        self.registered = False
        self.saw_end_of_query = False
        self.log_all_frames = False

    def connect(self):
        log("connecting to " + self.host + ":" + str(self.port))
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(2.0)
        log("TCP connected")

    def close(self):
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
            self.sock = None

    def send(self, b):
        if self.sock is None:
            return
        log("TX " + str(len(b)) + " B: " + hexs(b))
        self.sock.sendall(b)

    def recv_some(self):
        try:
            chunk = self.sock.recv(65536)
        except socket.timeout:
            return b""
        if not chunk:
            raise ConnectionError("peer closed")
        return chunk

    def feed(self, b):
        self.rxbuf.extend(b)
        frames = []
        while len(self.rxbuf) >= 3:
            op = self.rxbuf[0]
            plen = (self.rxbuf[1] << 8) | self.rxbuf[2]
            if len(self.rxbuf) < 3 + plen:
                break
            payload = bytes(self.rxbuf[3:3 + plen])
            frames.append((op, payload))
            del self.rxbuf[:3 + plen]
        return frames

    def handshake(self):
        got_ready = False
        deadline = time.monotonic() + self.timeout
        while not got_ready and time.monotonic() < deadline:
            data = self.recv_some()
            if not data:
                continue
            log("RX " + str(len(data)) + " B: " + hexs(data))
            for op, payload in self.feed(data):
                if op == OP_PROGRAM_READY:
                    log("program-ready; payload=" + hexs(payload))
                    got_ready = True
                else:
                    log("unexpected pre-registration op=0x" + ("%02X" % op))
        if not got_ready:
            raise RuntimeError("no 0x0F program-ready frame from chassis")

        self.send(build_registration(self.ipid))

        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            data = self.recv_some()
            if not data:
                continue
            log("RX " + str(len(data)) + " B: " + hexs(data))
            for op, payload in self.feed(data):
                if op == OP_REGISTER_RESULT:
                    if payload == REG_SUCCESS:
                        log("REGISTER OK  ipid=0x" + ("%02X" % self.ipid))
                        self.registered = True
                        return
                    if payload == REG_NOT_DEFINED:
                        raise RuntimeError(
                            "IPID 0x" + ("%02X" % self.ipid) + " not defined in chassis IP table. "
                            "Run ADDS or ADDPEER first, or try --ipid 1."
                        )
                    raise RuntimeError("unexpected 0x02 payload: " + hexs(payload))
                log("unexpected post-registration op=0x" + ("%02X" % op))
        raise RuntimeError("no registration result from chassis")

    def request_initial_state(self):
        self.send(UPDATE_REQUEST)

    def press(self, join):
        self.send(build_press(join, state=1))

    def release(self, join):
        self.send(build_press(join, state=0))

    def pulse(self, join, duration_s=0.1):
        self.press(join)
        time.sleep(duration_s)
        self.release(join)

    def set_analog(self, join, value):
        self.send(build_set_analog(join, value))

    def send_serial(self, join, text):
        self.send(build_send_serial(join, text))


    def process_frames(self, hold_seconds):
        last_hb = time.monotonic()
        hold_until = time.monotonic() + hold_seconds
        while time.monotonic() < hold_until:
            try:
                data = self.recv_some()
            except ConnectionError:
                log("peer closed")
                return
            if data:
                if self.log_all_frames:
                    log("RX chunk " + str(len(data)) + " B: " + data.hex(" "))
                for op, payload in self.feed(data):
                    self.handle_frame(op, payload)
            if self.saw_end_of_query and (time.monotonic() - last_hb) >= HEARTBEAT_INTERVAL:
                self.send(HEARTBEAT)
                last_hb = time.monotonic()

    def handle_frame(self, op, payload):
        if self.log_all_frames:
            log("FRAME op=0x%02X len=%d: %s" % (op, len(payload), payload.hex(" ")))
        if op == OP_HEARTBEAT:
            log("HEARTBEAT RX: " + hexs(payload))
            return

        if op == OP_SERIAL:
            got = decode_serial(payload)
            if got:
                join, text = got
                self.serials[join] = text
                safe = text.decode("utf-8", errors="replace")
                log("SERIAL S" + str(join) + " = " + repr(safe) + "  (" + str(len(text)) + " B)")
            else:
                log("SERIAL unparsed payload: " + hexs(payload))
            return

        if op == OP_DATA:
            if len(payload) >= 5 and payload[0:4] == b"\x00\x00\x02\x03":
                marker = payload[4]
                log("ADMIN marker=0x" + ("%02X" % marker))
                if marker == 0x1C:
                    log("end-of-query received, acking")
                    self.send(END_OF_QUERY_ACK)
                    self.send(HEARTBEAT)
                    self.saw_end_of_query = True
                return

            if len(payload) >= 6 and payload[0:3] == b"\x00\x00\x03":
                got = decode_digital(payload)
                if got:
                    join, state = got
                    self.digitals[join] = state
                    log("DIGITAL D" + str(join) + " = " + str(state) + "  (sub=0x" + ("%02X" % payload[3]) + ")")
                    return

            if len(payload) >= 8 and payload[0:4] == b"\x00\x00\x05\x14":
                got = decode_analog(payload)
                if got:
                    join, value = got
                    self.analogs[join] = value
                    log("ANALOG  A" + str(join) + " = " + str(value))
                    return

            log("DATA unknown payload: " + hexs(payload))
            return

        log("UNKNOWN op=0x" + ("%02X" % op) + " payload: " + hexs(payload))


def main():
    ap = argparse.ArgumentParser(description="CIP proof-of-connect")
    ap.add_argument("--host", default="172.16.0.104")
    ap.add_argument("--port", type=int, default=41794)
    ap.add_argument("--ipid", type=lambda s: int(s, 0), default=3,
                    help="CIP IP-ID to claim (decimal or 0xHH). Default 3. "
                         "Use 1 to reuse the stock XPanel slot.")
    ap.add_argument("--hold", type=float, default=10.0)
    ap.add_argument("--log-all-frames", action="store_true",
                    help="Hex-dump every RX chunk and every decoded frame BEFORE structural "
                         "decode. Catches joins the structural decoder doesn't recognise, "
                         "and shows if TCP reads are splitting CIP frames.")
    args = ap.parse_args()

    client = CipClient(args.host, args.port, args.ipid)
    client.log_all_frames = args.log_all_frames
    try:
        client.connect()
        client.handshake()
        client.request_initial_state()
        client.process_frames(hold_seconds=args.hold)
    except Exception as exc:
        log("ERROR: " + repr(exc))
        client.close()
        return 2
    client.close()

    print()
    print("--- SUMMARY ---")
    print("Digital joins observed: " + str(len(client.digitals)))
    for j in sorted(client.digitals):
        print("  D" + str(j) + " = " + str(client.digitals[j]))
    print("Analog joins observed:  " + str(len(client.analogs)))
    for j in sorted(client.analogs):
        print("  A" + str(j) + " = " + str(client.analogs[j]))
    print("Serial joins observed:  " + str(len(client.serials)))
    for j in sorted(client.serials):
        text = client.serials[j].decode("utf-8", errors="replace")
        print("  S" + str(j) + " = " + repr(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
