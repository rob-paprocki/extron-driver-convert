#!/usr/bin/env python3
"""
visca_listener.py - stand in for the i20 on the network, and say what arrived.

Point a driver at this machine instead of a camera - an Extron processor running
the ControlScript module, or a Global Configurator project built with
1bynd_19_20024 - and this records every VISCA frame the processor sends, decodes
it against the i20 command set, and can answer the way the camera's
documentation says the camera would.

What a session against it can show: the exact bytes Extron's runtime puts on the
wire, whether Build / Upload / Control work at all, what GC hands the script for
the composed parameters, and whether the module's reply parsers survive on a
processor. What it cannot show: how a real i20 answers. Every reply here comes
from Crestron's VISCA documentation, so a feedback result against this listener
tests the parser against our reading of the docs, not against the camera.

Nothing is guessed. A frame the decoder does not recognise is recorded as
UNKNOWN, and an unexpected byte inside a known frame is shown as `?XX`; both are
counted by --summarize.

Run:
    python3 experiments/loopback/visca_listener.py                 # record only, TCP 5500
    python3 experiments/loopback/visca_listener.py --reply ack     # + ACK, and answer inquiries
    python3 experiments/loopback/visca_listener.py --reply full    # + ACK and Completion, as documented
    python3 experiments/loopback/visca_listener.py --summarize experiments/loopback/captures/X.tsv

While it runs, type to change what the "camera" reports - the camera-side
change the feedback test needs:
    state | tracking start|stop | power on|off | freeze on|off | zoom N
    output N | switching on|off | camera N connected|disconnected
"""

import argparse
import datetime
import os
import socketserver
import sys
import threading
import time
from collections import Counter, namedtuple

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CAPTURES = os.path.join(_HERE, "captures")

Decoded = namedtuple("Decoded", "kind name detail")

ON_OFF = {0x02: "On", 0x03: "Off"}
AUTO_EXPOSURE = {0x00: "Full Auto", 0x03: "Manual", 0x0A: "Shutter Priority",
                 0x0B: "Iris Priority", 0x0D: "Bright"}
WHITE_BALANCE = {0x00: "Auto", 0x01: "Indoor", 0x02: "Outdoor", 0x03: "One Push",
                 0x05: "Manual"}
UP_DOWN_RESET = {0x02: "Up", 0x03: "Down", 0x00: "Reset"}
PRESET_ACTION = {0x00: "Reset", 0x01: "Save", 0x02: "Recall"}
PAN_TILT_DIRECTION = {
    (0x03, 0x01): "Up", (0x03, 0x02): "Down", (0x01, 0x03): "Left",
    (0x02, 0x03): "Right", (0x01, 0x01): "Up Left", (0x02, 0x01): "Up Right",
    (0x01, 0x02): "Down Left", (0x02, 0x02): "Down Right", (0x03, 0x03): "Stop",
}
LIGHT_COLOUR = {0x0: "Green", 0x1: "Red", 0x3: "Yellow"}
LIGHT_BRIGHTNESS = {0x0: "Off", 0x1: "Dim", 0x2: "Medium", 0x3: "Bright"}


def _reserved_presets():
    """Recalled presets the i20 module uses as feature switches (finding 13)."""
    r = {0x00: "TrackingShot Home", 0x01: "TrackingShot Tracking",
         0x50: "TrackingFraming Start", 0x51: "TrackingFraming Stop",
         0x52: "GroupTracking Enable",
         0x53: "PresenterTracking Enable (docs: Pause Group Tracking)",
         0x5F: "Menu", 0x63: "Reboot"}
    for i in range(1, 5):
        r[0x64 + i] = "PresetZone %d" % i
        r[0x68 + i] = "TrackingProfile %d" % i
    return r


RESERVED_PRESETS = _reserved_presets()

# PROTOCOL.md's T3 control table and T3b, as the bytes each step must put on
# the wire. --summarize checks a capture against these, in order.
EXPECTED_T3 = [
    ("T3 1", "Power On", "81 01 04 00 02 FF"),
    ("T3 2", "Preset Recall 1", "81 01 04 3F 02 01 FF"),
    ("T3 3", "Zoom Tele, Speed 5", "81 01 04 07 25 FF"),
    ("T3 4", "Auto Tracking Start", "81 01 04 3F 02 50 FF"),
    ("T3 5", "poll Auto Tracking", "81 09 08 01 FF"),
    ("T3 6", "Auto Tracking Stop", "81 01 04 3F 02 51 FF"),
    ("T3 7", "poll Auto Tracking", "81 09 08 01 FF"),
    ("T3 8", "Zoom Position 6699, Speed 3", "81 01 04 47 03 01 0A 02 0B FF"),
    ("T3 9", "Freeze Frame On", "81 01 04 62 02 FF"),
    ("T3 9", "Freeze Frame Off", "81 01 04 62 03 FF"),
    ("T3 10", "Indicator Light Full Red Bright", "81 C1 0D 0D 0D 0D FF"),
    ("T3 11", "Indicator Light Half Green Dim", "81 C1 00 04 04 00 FF"),
    ("T3 12", "Indicator Light None", "81 C1 00 00 00 00 FF"),
    ("T3 13", "Tracking Profile 2", "81 01 04 3F 02 6A FF"),
    ("T3 14", "Camera Output 2", "81 C2 01 08 02 FF"),
    ("T3 15", "Intelligent Switching Resume", "81 C2 01 08 00 FF"),
    ("T3 16", "Intelligent Switching Pause", "81 C2 01 0B 00 FF"),
    ("T3b 1", "Group Tracking Enable", "81 01 04 3F 02 52 FF"),
    ("T3b 2", "Presenter Tracking Enable", "81 01 04 3F 02 53 FF"),
]

# README Path B's Global Configurator macro (controlscript/loopback_steps.py
# GC_MACRO), as bytes. test_visca_listener.py [6] drives each step through the
# module and fails if any string here is not what it sends.
EXPECTED_GC_MACRO = [
    ("GC 1", "Power On", "81 01 04 00 02 FF"),
    ("GC 2", "Preset Recall 1", "81 01 04 3F 02 01 FF"),
    ("GC 3", "Zoom Tele, Speed 5", "81 01 04 07 25 FF"),
    ("GC 4", "Auto Tracking Start", "81 01 04 3F 02 50 FF"),
    ("GC 5", "Auto Tracking Stop", "81 01 04 3F 02 51 FF"),
    ("GC 6", "Zoom Position 6699, Speed 3", "81 01 04 47 03 01 0A 02 0B FF"),
    ("GC 7", "Freeze Frame On", "81 01 04 62 02 FF"),
    ("GC 8", "Freeze Frame Off", "81 01 04 62 03 FF"),
    ("GC 9", "Indicator Light Full Red Bright", "81 C1 0D 0D 0D 0D FF"),
    ("GC 10", "Indicator Light Half Green Dim", "81 C1 00 04 04 00 FF"),
    ("GC 11", "Indicator Light None", "81 C1 00 00 00 00 FF"),
    ("GC 12", "Tracking Profile 2", "81 01 04 3F 02 6A FF"),
    ("GC 13", "Camera Output 2", "81 C2 01 08 02 FF"),
    ("GC 14", "Intelligent Switching Resume", "81 C2 01 08 00 FF"),
    ("GC 15", "Intelligent Switching Pause", "81 C2 01 0B 00 FF"),
    ("GC 16", "Group Tracking Enable", "81 01 04 3F 02 52 FF"),
    ("GC 17", "Presenter Tracking Enable", "81 01 04 3F 02 53 FF"),
    ("GC 18", "Pan Tilt Angle -2448 / -1296", "81 01 06 02 01 01 0F 06 07 00 0F 0A 0F 00 FF"),
    ("GC 19", "Pan Tilt Angle 2448 / 1296", "81 01 06 02 18 14 00 09 09 00 00 05 01 00 FF"),
    ("GC 20", "Zoom Position 16384, Speed 7", "81 01 04 47 07 04 00 00 00 FF"),
    ("GC 21", "Camera Output 5", "81 C2 01 08 05 FF"),
]

EXPECTED_SETS = {
    "t3": ("PROTOCOL T3 wire strings", EXPECTED_T3),
    "gc-macro": ("GC macro wire strings (README Path B)", EXPECTED_GC_MACRO),
}


def hexs(data):
    return " ".join("%02X" % b for b in data)


def nibbles_value(data):
    """VISCA packs one nibble per byte, most significant first."""
    v = 0
    for b in data:
        v = (v << 4) | (b & 0x0F)
    return v


def to_nibbles(value, count):
    return [(value >> (4 * (count - 1 - i))) & 0x0F for i in range(count)]


def signed16(value):
    return value - 0x10000 if value & 0x8000 else value


def _pick(table, value):
    """Name a byte, or mark it `?XX` so an unexpected value is counted, not guessed."""
    return table.get(value, "?%02X" % value)


def _drive(byte, names):
    """A VISCA drive byte: 00 stop, 02/03 standard speed, 2p/3p variable speed p."""
    hi, lo = byte >> 4, byte & 0x0F
    if byte == 0x00:
        return "Stop"
    if hi == 0 and lo in names:
        return "%s (standard speed)" % names[lo]
    if hi in names:
        return "%s speed %d" % (names[hi], lo)
    return "?%02X" % byte


def _lightbar(segments):
    """Name the 0xC1 payload: one byte per segment, (brightness << 2) | colour."""
    raw = "segments " + hexs(segments)
    if any(s > 0x0F or (s & 0x3) not in LIGHT_COLOUR for s in segments):
        return "?" + raw
    if all(s == 0 for s in segments):
        return "None (%s)" % raw
    a, b, c, d = segments
    if a == b == c == d:
        return "Full %s %s (%s)" % (LIGHT_COLOUR[a & 0x3], LIGHT_BRIGHTNESS[a >> 2], raw)
    if a == d and b == c and (a & 0x0C) == 0 and (a & 0x3) == (b & 0x3):
        return "Half %s %s (%s)" % (LIGHT_COLOUR[b & 0x3], LIGHT_BRIGHTNESS[b >> 2], raw)
    return "?" + raw


_ONE_BYTE_SETS = {
    0x38: ("AutoFocus", ON_OFF), 0x33: ("Backlight", ON_OFF),
    0x39: ("AutoExposure", AUTO_EXPOSURE), 0x35: ("WhiteBalance", WHITE_BALANCE),
    0x0B: ("Iris", UP_DOWN_RESET), 0x0C: ("Gain", UP_DOWN_RESET),
    0x0A: ("Shutter", UP_DOWN_RESET), 0x62: ("FreezeFrame", ON_OFF),
}

_INQUIRIES = {
    b"\x09\x04\x00": "Power", b"\x09\x04\x38": "AutoFocus",
    b"\x09\x04\x33": "Backlight", b"\x09\x04\x39": "AutoExposure",
    b"\x09\x04\x35": "WhiteBalance", b"\x09\x04\x47": "ZoomPosition",
    b"\x09\x04\x62": "FreezeFrame", b"\x09\x08\x01": "TrackingFraming",
    b"\x09\x06\x12": "PanTiltPosition", b"\xC2\x09\x08": "CameraOutput",
}


def decode(frame):
    """Name one VISCA frame (header .. FF) against the i20 command set."""
    f = bytes(frame)
    if not f or f[-1] != 0xFF:
        return Decoded("partial", "PARTIAL", "no FF terminator")
    if len(f) < 3 or (f[0] & 0xF0) != 0x80:
        return Decoded("unknown", "UNKNOWN", "no 8x header")
    b = f[1:-1]
    n = len(b)
    k = b[:3]

    if b[0] == 0x01:
        if k == b"\x01\x04\x00" and n == 4:
            return Decoded("command", "Power", _pick(ON_OFF, b[3]))
        if k == b"\x01\x04\x3F" and n == 5:
            detail = "%s %d" % (_pick(PRESET_ACTION, b[3]), b[4])
            if b[3] == 0x02 and b[4] in RESERVED_PRESETS:
                detail += " = " + RESERVED_PRESETS[b[4]]
            return Decoded("command", "Preset", detail)
        if k == b"\x01\x04\x07" and n == 4:
            return Decoded("command", "Zoom", _drive(b[3], {2: "Tele", 3: "Wide"}))
        if k == b"\x01\x04\x08" and n == 4:
            return Decoded("command", "Focus", _drive(b[3], {2: "Far", 3: "Near"}))
        if k == b"\x01\x04\x47" and n == 8:
            return Decoded("command", "ZoomPosition",
                           "%d speed %d" % (nibbles_value(b[4:8]), b[3]))
        if k == b"\x01\x04\x47" and n == 7:
            return Decoded("command", "ZoomPosition",
                           "%d (standard VISCA, no speed byte)" % nibbles_value(b[3:7]))
        if k == b"\x01\x04\x10" and n == 4 and b[3] == 0x05:
            return Decoded("command", "WhiteBalance", "One Push Trigger")
        if n == 4 and b[1] == 0x04 and b[2] in _ONE_BYTE_SETS:
            name, table = _ONE_BYTE_SETS[b[2]]
            return Decoded("command", name, _pick(table, b[3]))
        if k == b"\x01\x06\x01" and n == 7:
            direction = PAN_TILT_DIRECTION.get((b[5], b[6]), "?%02X%02X" % (b[5], b[6]))
            return Decoded("command", "PanTilt", "%s, pan speed %d tilt speed %d"
                           % (direction, b[3], b[4]))
        if k == b"\x01\x06\x02" and n == 13:
            return Decoded("command", "PanTiltAngle",
                           "pan %d tilt %d, pan speed %d tilt speed %d"
                           % (signed16(nibbles_value(b[5:9])),
                              signed16(nibbles_value(b[9:13])), b[3], b[4]))
        if b == b"\x01\x06\x04":
            return Decoded("command", "PanTilt", "Home")
        if b == b"\x01\x06\x05":
            return Decoded("command", "PanTiltHome", "Reset (also PanTilt Reset)")

    if n == 5 and b[0] == 0xC1:
        return Decoded("command", "IndicatorLight", _lightbar(b[1:5]))
    if n == 4 and k == b"\xC2\x01\x08":
        if b[3] == 0:
            return Decoded("command", "CameraOutput", "0 = IntelligentSwitching Resume")
        return Decoded("command", "CameraOutput",
                       "%d" % b[3] if b[3] <= 5 else "?%02X" % b[3])
    if b == b"\xC2\x01\x0B\x00":
        return Decoded("command", "IntelligentSwitching", "Pause")
    if b == b"\xC2\x01\x01\x0A":
        return Decoded("command", "Identify", "")

    if b in _INQUIRIES:
        return Decoded("inquiry", _INQUIRIES[b], "")
    if n == 4 and k == b"\xC2\x09\x0D":
        return Decoded("inquiry", "CameraConnectionStatus", "camera %d" % b[3])
    return Decoded("unknown", "UNKNOWN", "")


class Framer(object):
    """Split a byte stream into VISCA frames on the FF terminator.

    Nibble encoding keeps FF out of every payload the i20 set sends, so the
    terminator is unambiguous - with one exception the decoder cannot fix:
    Preset 255 puts a literal FF inside the frame.
    """

    def __init__(self):
        self.buffer = b""

    def feed(self, data):
        self.buffer += bytes(data)
        frames = []
        while True:
            i = self.buffer.find(b"\xFF")
            if i < 0:
                return frames
            frames.append(self.buffer[:i + 1])
            self.buffer = self.buffer[i + 1:]

    def flush(self):
        rest, self.buffer = self.buffer, b""
        return rest


ACK, COMPLETION = 0x41, 0x51


class CameraModel(object):
    """What the listener answers: documented reply layouts over a small state.

    Commands get `y0 41 FF` (ack), or `y0 41 FF` then `y0 51 FF` (full).
    Inquiries get `y0 50 <payload> FF`. A frame the decoder does not know gets
    a syntax error, `y0 60 02 FF`, which is what the module's own error check
    expects a camera to send.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.state = {
            "power": 0x02, "autofocus": 0x02, "backlight": 0x03,
            "autoexposure": 0x00, "whitebalance": 0x00, "freeze": 0x03,
            "zoom": 0, "pan": 0, "tilt": 0, "tracking": 0x03,
            "switching": True, "output": 1,
            "connected": {2: True, 3: True, 4: True, 5: True},
        }

    def respond(self, frame, mode):
        f = bytes(frame)
        if mode == "none" or len(f) < 3 or (f[0] & 0xF0) != 0x80 or f[-1] != 0xFF:
            return []
        y = (((f[0] & 0x0F) + 8) << 4) & 0xFF
        kind = decode(f).kind
        with self.lock:
            if kind == "command":
                self._apply(f[1:-1])
                replies = [bytes([y, ACK, 0xFF])]
                if mode == "full":
                    replies.append(bytes([y, COMPLETION, 0xFF]))
                return replies
            if kind == "inquiry":
                return [bytes([y, 0x50]) + self._inquiry(f[1:-1]) + b"\xFF"]
        return [bytes([y, 0x60, 0x02, 0xFF])]

    def _apply(self, b):
        s, n, k = self.state, len(b), b[:3]
        one = {b"\x01\x04\x00": "power", b"\x01\x04\x38": "autofocus",
               b"\x01\x04\x33": "backlight", b"\x01\x04\x39": "autoexposure",
               b"\x01\x04\x35": "whitebalance", b"\x01\x04\x62": "freeze"}
        if n == 4 and k in one:
            s[one[k]] = b[3]
        elif k == b"\x01\x04\x47" and n == 8:
            s["zoom"] = nibbles_value(b[4:8])
        elif k == b"\x01\x04\x47" and n == 7:
            s["zoom"] = nibbles_value(b[3:7])
        elif k == b"\x01\x06\x02" and n == 13:
            s["pan"] = signed16(nibbles_value(b[5:9]))
            s["tilt"] = signed16(nibbles_value(b[9:13]))
        elif k == b"\x01\x04\x3F" and n == 5 and b[3] == 0x02 and b[4] in (0x50, 0x51):
            s["tracking"] = 0x02 if b[4] == 0x50 else 0x03
        elif k == b"\xC2\x01\x08" and n == 4:
            if b[3] == 0:
                s["switching"] = True
            else:
                s["output"] = b[3]
        elif b == b"\xC2\x01\x0B\x00":
            s["switching"] = False

    def _inquiry(self, b):
        s = self.state
        one = {b"\x09\x04\x00": "power", b"\x09\x04\x38": "autofocus",
               b"\x09\x04\x33": "backlight", b"\x09\x04\x39": "autoexposure",
               b"\x09\x04\x35": "whitebalance", b"\x09\x04\x62": "freeze",
               b"\x09\x08\x01": "tracking"}
        if b in one:
            return bytes([s[one[b]]])
        if b == b"\x09\x04\x47":
            return bytes(to_nibbles(s["zoom"], 4))
        if b == b"\x09\x06\x12":
            return bytes(to_nibbles(s["pan"] & 0xFFFF, 4) + to_nibbles(s["tilt"] & 0xFFFF, 4))
        if b == b"\xC2\x09\x08":
            # VISCA-Intelligent-Switching-Commands.md, Get Output:
            # y0 50 01 0Z FF with switching on, y0 50 00 0Z FF with it off.
            return bytes([0x01 if s["switching"] else 0x00, s["output"]])
        # Check Connection Status: y0 50 00 01 FF connected, y0 50 00 00 FF not.
        return bytes([0x00, 0x01 if s["connected"].get(b[3]) else 0x00])

    def describe(self):
        s = self.state
        return ("power %s, tracking %s, freeze %s, zoom %d, pan %d, tilt %d, "
                "switching %s, output %d, connected %s"
                % (ON_OFF[s["power"]], {0x02: "start", 0x03: "stop"}[s["tracking"]],
                   ON_OFF[s["freeze"]], s["zoom"], s["pan"], s["tilt"],
                   "on" if s["switching"] else "off", s["output"],
                   ",".join(str(c) for c, up in sorted(s["connected"].items()) if up) or "none"))

    def control(self, line):
        """Apply a console command. Returns a message, or None for a blank line."""
        words = line.strip().lower().split()
        if not words:
            return None
        s = self.state
        with self.lock:
            try:
                w = words[0]
                if w == "tracking":
                    s["tracking"] = {"start": 0x02, "stop": 0x03}[words[1]]
                elif w in ("power", "freeze"):
                    s[w] = {"on": 0x02, "off": 0x03}[words[1]]
                elif w in ("zoom", "output"):
                    s[w] = int(words[1])
                elif w == "switching":
                    s["switching"] = {"on": True, "off": False}[words[1]]
                elif w == "camera":
                    s["connected"][int(words[1])] = {"connected": True,
                                                     "disconnected": False}[words[2]]
                elif w != "state":
                    return "unknown control: %s" % line.strip()
            except (IndexError, KeyError, ValueError):
                return "could not parse: %s" % line.strip()
            return "camera state: " + self.describe()


class Capture(object):
    """Every frame in and out, as TSV. The file holds no paths, only traffic."""

    COLUMNS = ("time", "peer", "dir", "hex", "kind", "name", "detail")

    def __init__(self, path=None, echo=True):
        self.path, self.echo = path, echo
        self.lock = threading.Lock()
        self.rows = []
        self.fh = None
        if path:
            self.fh = open(path, "w", encoding="utf-8", newline="\n")
            self.fh.write("\t".join(self.COLUMNS) + "\n")
            self.fh.flush()

    def record(self, peer, direction, data=b"", kind="", name="", detail=""):
        row = (datetime.datetime.now().isoformat(timespec="milliseconds"), peer,
               direction, hexs(data), kind, name, detail)
        with self.lock:
            self.rows.append(dict(zip(self.COLUMNS, row)))
            if self.fh:
                self.fh.write("\t".join(row) + "\n")
                self.fh.flush()
            if self.echo:
                print("%s  %-21s %-5s %-44s %s %s"
                      % (row[0][11:], peer, direction, row[3], name, detail))

    def close(self):
        if self.fh:
            self.fh.close()
            self.fh = None


class Listener(object):
    def __init__(self, host="0.0.0.0", port=5500, mode="none", capture=None,
                 model=None, udp=False):
        self.host, self.port, self.mode, self.udp = host, port, mode, udp
        self.capture = capture or Capture(echo=False)
        self.model = model or CameraModel()
        self.server = None

    def handle_frame(self, peer, frame, send):
        d = decode(frame)
        self.capture.record(peer, "rx", frame, d.kind, d.name, d.detail)
        for reply in self.model.respond(frame, self.mode):
            send(reply)
            self.capture.record(peer, "tx", reply, "reply")

    def start(self):
        listener = self

        class TCPHandler(socketserver.BaseRequestHandler):
            def handle(self):
                peer = "%s:%d" % self.client_address[:2]
                listener.capture.record(peer, "open")
                framer = Framer()
                try:
                    while True:
                        data = self.request.recv(4096)
                        if not data:
                            break
                        for frame in framer.feed(data):
                            listener.handle_frame(peer, frame, self.request.sendall)
                except OSError as e:
                    listener.capture.record(peer, "error", detail=str(e))
                rest = framer.flush()
                if rest:
                    d = decode(rest)
                    listener.capture.record(peer, "rx", rest, d.kind, d.name, d.detail)
                listener.capture.record(peer, "close")

        class UDPHandler(socketserver.BaseRequestHandler):
            def handle(self):
                data, sock = self.request
                peer = "%s:%d" % self.client_address[:2]
                addr = self.client_address
                for frame in Framer().feed(data):
                    listener.handle_frame(peer, frame, lambda r: sock.sendto(r, addr))

        base = socketserver.ThreadingUDPServer if self.udp else socketserver.ThreadingTCPServer

        class Server(base):
            allow_reuse_address = True
            daemon_threads = True

        self.server = Server((self.host, self.port), UDPHandler if self.udp else TCPHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self.server.server_address[:2]

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None


def read_capture(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    return [dict(zip(Capture.COLUMNS, line.split("\t"))) for line in lines[1:] if line]


def summarize(rows, expect="t3"):
    """Counts, anomalies, and a checklist of expected wire strings. Returns (text, result)."""
    title, expected = EXPECTED_SETS[expect]
    rx = [r for r in rows if r.get("dir") == "rx"]
    out = ["%d frame(s) received over %d connection(s)"
           % (len(rx), sum(1 for r in rows if r.get("dir") == "open"))]
    for (kind, name), count in sorted(Counter((r["kind"], r["name"]) for r in rx).items()):
        out.append("  %5d  %-8s %s" % (count, kind, name))

    odd = [r for r in rx if r["kind"] in ("unknown", "partial") or "?" in r["detail"]]
    out.append("%d unknown, partial or unexpected-value frame(s)" % len(odd))
    for r in odd[:50]:
        out.append("  %s  %s  %s %s" % (r["time"], r["hex"], r["name"], r["detail"]))

    hexes = [r["hex"] for r in rx]
    out.append(title + ":")
    position, seen_all, in_order = 0, True, True
    for step, label, want in expected:
        if want not in hexes:
            seen_all = False
            mark = "MISSING"
        elif want in hexes[position:]:
            position = hexes.index(want, position) + 1
            mark = "ok"
        else:
            in_order = False
            mark = "ok (out of order)"
        out.append("  %-18s %-6s %-32s %s" % (mark, step, label, want))
    out.append("all %d seen: %s; in order: %s"
               % (len(expected), "yes" if seen_all else "no",
                  "yes" if seen_all and in_order else "no"))
    return "\n".join(out), {"received": len(rx), "odd": len(odd),
                            "seen_all": seen_all, "in_order": seen_all and in_order}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="0.0.0.0", help="address to bind (default all)")
    ap.add_argument("--port", type=int, default=5500, help="default 5500, the i20's port")
    ap.add_argument("--udp", action="store_true", help="listen on UDP instead of TCP")
    ap.add_argument("--reply", choices=("none", "ack", "full"), default="none",
                    help="none: record only; ack: ACK commands, answer inquiries; "
                         "full: ACK then Completion, as the docs describe")
    ap.add_argument("--captures", default=DEFAULT_CAPTURES, help="where capture TSVs go")
    ap.add_argument("--summarize", metavar="CAPTURE", help="summarize a capture and exit")
    ap.add_argument("--expect", choices=sorted(EXPECTED_SETS), default="t3",
                    help="which wire-string checklist --summarize applies")
    args = ap.parse_args(argv)

    if args.summarize:
        print(summarize(read_capture(args.summarize), args.expect)[0])
        return 0

    os.makedirs(args.captures, exist_ok=True)
    name = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S") + ".tsv"
    capture = Capture(os.path.join(args.captures, name))
    listener = Listener(args.host, args.port, args.reply, capture, CameraModel(), args.udp)
    host, port = listener.start()
    print("listening on %s %s:%d, reply mode '%s'; capture %s"
          % ("UDP" if args.udp else "TCP", host, port, args.reply, name))
    print("type 'state', 'tracking start|stop', ... to change the camera; Ctrl+C to stop")
    try:
        while True:
            line = sys.stdin.readline()
            if not line:            # no console: keep serving until interrupted
                time.sleep(1)
                continue
            message = listener.model.control(line)
            if message:
                print(message)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        capture.close()
        print()
        print(summarize(capture.rows)[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
