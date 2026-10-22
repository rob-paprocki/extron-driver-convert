"""cs_dm_md_ctp.py - Extron ControlScript driver for Crestron DM-MD CPU3/CPU4
chassis routing via CTP (TCP :41795).

Deploys inside an Extron IPL Pro / IPCP Pro ControlScript project. The driver
exposes command methods callable from the project's main logic, and populates
feedback-state attributes for route changes.

Verified protocol surface (from live experiments on DM-MD8X8-CPU3-RPS; see
experiments/crestron-dm-md-bridge/evidence/ in the research branch):
  SETVIDEOROUTE inputSlotId outputSlotId    -- 0 input breaks the route
  SETAUDIOROUTE inputSlotId outputSlotId
  SETAVROUTE inputSlotId outputSlotId       -- A+V together
  SETUSBROUTE inputSlotId outputSlotId
  SETAVUROUTE inputSlotId outputSlotId      -- A+V+USB
  SETAVALLROUTE inputSlotId                 -- one input to ALL outputs
  DUMPDMROUTEINFO [slotId]                  -- read route state
  REPORTDM                                  -- read attached endpoint info

NOT supported through this driver: endpoint RS-232 / IR / Relay. Firmware-
locked on the chassis - see evidence/13 in the research branch. Requires a
SIMPL# Pro add-on on the chassis side or per-room-local control hardware.

Slot numbering: chassis inputs are slots 1..N (N=8 for DM-MD8X8-CPU3-RPS),
outputs are 101..108. This driver takes 1-based output numbers in the public
API and converts to 101..108 internally.

Usage from a ControlScript project (sketch):

    from cs_dm_md_ctp import DmMdCtpDriver
    dm = DmMdCtpDriver("192.168.6.14", inputs=8, outputs=8)
    dm.on_route_change = lambda kind, out, inp: print("route", kind, out, inp)
    dm.start()
    dm.route_av(input=2, output=1)   # route AV from input 2 to output 1
    dm.break_output(3)               # break AV route on output 3

For a shipping .pkp this file becomes the DRIVER MODULE referenced by the
donor package's main script after transplantation by a build script in the
pattern of experiments/skeleton_i20/build_i20.py (see TODO at bottom).
"""
from __future__ import annotations

try:
    # Running on an Extron processor
    from extronlib.interface import EthernetClientInterface
    from extronlib.system import Wait, ProgramLog
    _ONDEVICE = True
except ImportError:
    # Running in a desktop test/dev environment: stub out extronlib
    _ONDEVICE = False
    class EthernetClientInterface:
        def __init__(self, host, port, protocol="TCP"):
            self.Hostname = host
            self.ServicePort = port
            self.Protocol = protocol
            self.Connected = None
            self.Disconnected = None
            self.ReceiveData = None
        def Connect(self, timeout=None): print(f"[stub] Connect {self.Hostname}:{self.ServicePort}")
        def Disconnect(self): print("[stub] Disconnect")
        def Send(self, data):
            try: print(f"[stub] TX: {data!r}")
            except Exception: pass
    def Wait(interval, action=None):
        import threading
        t = threading.Timer(interval, action)
        t.daemon = True; t.start()
        return t
    def ProgramLog(msg, severity="info"): print(f"[log/{severity}] {msg}")


# ---- Protocol helpers --------------------------------------------------------

def _in_to_chassis(input_num: int, inputs: int) -> int:
    """Map public 0..inputs -> chassis slot id (0 means break; 1..inputs are 1:1)."""
    if not 0 <= input_num <= inputs:
        raise ValueError(f"input {input_num} out of range [0, {inputs}]")
    return input_num


def _out_to_chassis(output_num: int, outputs: int) -> int:
    """Map public 1..outputs -> chassis slot id (101..100+outputs)."""
    if not 1 <= output_num <= outputs:
        raise ValueError(f"output {output_num} out of range [1, {outputs}]")
    return 100 + output_num


# ---- Driver -----------------------------------------------------------------

class DmMdCtpDriver:
    """CTP-based routing driver for Crestron DM-MD CPU3/CPU4 chassis."""

    def __init__(self, host: str, port: int = 41795,
                 inputs: int = 8, outputs: int = 8,
                 poll_interval_s: float = 10.0,
                 reconnect_backoff_s: float = 5.0):
        self.host = host
        self.port = port
        self.inputs = inputs
        self.outputs = outputs
        self.poll_interval_s = poll_interval_s
        self.reconnect_backoff_s = reconnect_backoff_s

        self._client: EthernetClientInterface | None = None
        self._rxbuf = bytearray()
        self._pending_response = None  # callable(text) -> None

        # Feedback state (public read-only)
        self.connected = False
        self.video_route = {i: 0 for i in range(1, outputs + 1)}   # output -> input (0 = disconnected)
        self.audio_route = {i: 0 for i in range(1, outputs + 1)}
        self.usb_route   = {i: 0 for i in range(1, outputs + 1)}
        self.last_error = ""

        # User-settable callbacks
        self.on_route_change = None  # callable(kind: str, output: int, input: int)
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

    def _open(self):
        self._client = EthernetClientInterface(self.host, self.port, "TCP")
        self._client.Connected = self._on_connected
        self._client.Disconnected = self._on_disconnected
        self._client.ReceiveData = self._on_data
        try:
            self._client.Connect(timeout=5)
        except Exception as e:
            ProgramLog(f"[dm-ctp] connect failed: {e}", "warning")
            self._schedule_reconnect()

    def _schedule_reconnect(self):
        Wait(self.reconnect_backoff_s, self._open)

    # ---- Transport callbacks ----

    def _on_connected(self, interface, state):
        self.connected = True
        ProgramLog(f"[dm-ctp] connected to {self.host}:{self.port}", "info")
        if callable(self.on_connect):
            try: self.on_connect()
            except Exception as e: ProgramLog(f"[dm-ctp] on_connect handler error: {e}", "warning")
        # Initial route poll
        self._enqueue("DUMPDMROUTEINFO", self._handle_dumpdmrouteinfo)
        self._start_poll_timer()

    def _on_disconnected(self, interface, state):
        self.connected = False
        ProgramLog(f"[dm-ctp] disconnected", "info")
        if callable(self.on_disconnect):
            try: self.on_disconnect()
            except Exception: pass
        self._schedule_reconnect()

    def _on_data(self, interface, data: bytes):
        self._rxbuf.extend(data)
        # Chassis prompts end with "\r\n" after a response. We accumulate until
        # the next prompt-like trailing bytes or until enough has arrived to
        # make the pending callback happy.
        if self._pending_response is not None and b"\n" in self._rxbuf:
            text = bytes(self._rxbuf).decode("utf-8", errors="replace")
            self._rxbuf = bytearray()
            cb = self._pending_response
            self._pending_response = None
            try:
                cb(text)
            except Exception as e:
                ProgramLog(f"[dm-ctp] response handler error: {e}", "warning")
                self.last_error = str(e)

    def _enqueue(self, cmd: str, response_handler=None):
        if not self.connected or self._client is None:
            ProgramLog(f"[dm-ctp] send skipped (not connected): {cmd}", "warning")
            return
        self._pending_response = response_handler
        try:
            self._client.Send((cmd + "\r\n").encode("ascii"))
        except Exception as e:
            ProgramLog(f"[dm-ctp] send error: {e}", "warning")
            self.last_error = str(e)

    def _start_poll_timer(self):
        def _tick():
            if self.connected:
                self._enqueue("DUMPDMROUTEINFO", self._handle_dumpdmrouteinfo)
            # Reschedule
            Wait(self.poll_interval_s, _tick)
        Wait(self.poll_interval_s, _tick)

    # ---- Public command surface ----

    def route_video(self, input: int, output: int):
        """SETVIDEOROUTE: route an input to an output (video only)."""
        i = _in_to_chassis(input, self.inputs)
        o = _out_to_chassis(output, self.outputs)
        self._enqueue(f"SETVIDEOROUTE {i} {o}")
        self.video_route[output] = input
        self._fire_route_change("video", output, input)

    def route_audio(self, input: int, output: int):
        i = _in_to_chassis(input, self.inputs)
        o = _out_to_chassis(output, self.outputs)
        self._enqueue(f"SETAUDIOROUTE {i} {o}")
        self.audio_route[output] = input
        self._fire_route_change("audio", output, input)

    def route_av(self, input: int, output: int):
        i = _in_to_chassis(input, self.inputs)
        o = _out_to_chassis(output, self.outputs)
        self._enqueue(f"SETAVROUTE {i} {o}")
        self.video_route[output] = input
        self.audio_route[output] = input
        self._fire_route_change("av", output, input)

    def route_usb(self, input: int, output: int):
        i = _in_to_chassis(input, self.inputs)
        o = _out_to_chassis(output, self.outputs)
        self._enqueue(f"SETUSBROUTE {i} {o}")
        self.usb_route[output] = input
        self._fire_route_change("usb", output, input)

    def route_avu(self, input: int, output: int):
        """SETAVUROUTE: audio + video + USB together."""
        i = _in_to_chassis(input, self.inputs)
        o = _out_to_chassis(output, self.outputs)
        self._enqueue(f"SETAVUROUTE {i} {o}")
        self.video_route[output] = input
        self.audio_route[output] = input
        self.usb_route[output] = input
        self._fire_route_change("avu", output, input)

    def route_all(self, input: int):
        """SETAVALLROUTE: route one input to ALL outputs (AV)."""
        i = _in_to_chassis(input, self.inputs)
        self._enqueue(f"SETAVALLROUTE {i}")
        for o in range(1, self.outputs + 1):
            self.video_route[o] = input
            self.audio_route[o] = input
            self._fire_route_change("av", o, input)

    def break_output(self, output: int):
        """Break the AV route on an output (input 0)."""
        self.route_av(0, output)

    def poll_routes(self):
        self._enqueue("DUMPDMROUTEINFO", self._handle_dumpdmrouteinfo)

    # ---- Response parsing ----

    def _handle_dumpdmrouteinfo(self, text: str):
        """Parse DUMPDMROUTEINFO text output and update feedback state."""
        current_output = None
        for line in text.splitlines():
            line = line.strip()
            # Section header for an output card
            import re
            m = re.search(r"Routing Information for Output Card at Slot (\d+)", line)
            if m:
                out_slot = int(m.group(1))
                current_output = out_slot - 100 if out_slot >= 101 else None
                continue
            if current_output is None:
                continue
            if "No Video connection" in line:
                self._set_route("video", current_output, 0)
                continue
            m = re.search(r"Video from Input Card at Slot (\d+)", line)
            if m:
                self._set_route("video", current_output, int(m.group(1)))
                continue
            if "No Audio connection" in line:
                self._set_route("audio", current_output, 0)
                continue
            m = re.search(r"Audio from Input Card at Slot (\d+)", line)
            if m:
                self._set_route("audio", current_output, int(m.group(1)))
                continue
            if "No USB connection" in line:
                self._set_route("usb", current_output, 0)
                continue
            m = re.search(r"USB from Input Card at Slot (\d+)", line)
            if m:
                self._set_route("usb", current_output, int(m.group(1)))
                continue

    def _set_route(self, kind, output, input):
        target = {"video": self.video_route, "audio": self.audio_route, "usb": self.usb_route}[kind]
        if target.get(output) != input:
            target[output] = input
            self._fire_route_change(kind, output, input)

    def _fire_route_change(self, kind, output, input):
        if callable(self.on_route_change):
            try: self.on_route_change(kind, output, input)
            except Exception as e: ProgramLog(f"[dm-ctp] on_route_change handler error: {e}", "warning")


# ---- Self-test / desktop stub test ----

def _selftest():
    """Run the parser against a known-good DUMPDMROUTEINFO sample.

    Known sample from the research synthesis evidence/06 and the live chassis
    (DUMPDMROUTEINFO on 192.168.6.14):
    """
    sample = """DM Routing Information for all Output cards
 Routing Information for Input Card at Slot 1
No USB connection
 Routing Information for Input Card at Slot 2
No USB connection
 Routing Information for Input Card at Slot 3
No USB connection
 Routing Information for Input Card at Slot 4
No USB connection
 Routing Information for Input Card at Slot 6
No USB connection
 Routing Information for Input Card at Slot 8
No USB connection
 Routing Information for Output Card at Slot 101
Video from Input Card at Slot 2
Audio from Input Card at Slot 2
No USB connection
 Hot plug is High
 Routing Information for Output Card at Slot 102
No Video connection
No Audio connection
No USB connection
 Hot plug is Low
 Routing Information for Output Card at Slot 103
Video from Input Card at Slot 1
Audio from Input Card at Slot 1
No USB connection
 Hot plug is High
"""
    d = DmMdCtpDriver("127.0.0.1", inputs=8, outputs=8)
    d.connected = True
    d._handle_dumpdmrouteinfo(sample)
    assert d.video_route[1] == 2, f"video out 1 wrong: {d.video_route[1]}"
    assert d.audio_route[1] == 2, f"audio out 1 wrong: {d.audio_route[1]}"
    assert d.usb_route[1] == 0, f"usb out 1 wrong: {d.usb_route[1]}"
    assert d.video_route[2] == 0, f"video out 2 wrong: {d.video_route[2]}"
    assert d.video_route[3] == 1, f"video out 3 wrong: {d.video_route[3]}"
    print("[selftest] DUMPDMROUTEINFO parse OK: V1=2 V2=0 V3=1")

    # Routing calls (stub mode just prints the TX)
    d.route_av(input=5, output=4)
    d.break_output(4)
    d.route_all(input=1)
    print("[selftest] command surface callable")


if __name__ == "__main__":
    _selftest()
