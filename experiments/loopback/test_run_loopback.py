#!/usr/bin/env python3
"""
test_run_loopback.py - rehearse a processor session on one PC.

A stand-in processor serves controlscript/console_core.py over TCP and drives
the real i20 module over a real socket - the code main.py runs on a processor,
minus extronlib. run_loopback.py then drives it exactly as it would a processor.

  [1] the console's request handling, error paths included
  [2] a whole session against --reply ack: every step matches on wire and read
  [3] the same session against --reply none: timeouts behave alike on both sides
  [4] --reply full, where this stand-in keeps unread data: the harness must see
      the reads diverge - proof it can catch that runtime behaviour, not a
      claim about what a processor does. Wire frames must still match, except
      for the one explained shape a shared inquiry's cache can produce here

Run: python3 experiments/loopback/test_run_loopback.py
"""

import contextlib
import io
import json
import os
import socket
import socketserver
import sys
import tempfile
import threading

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "controlscript"))

import run_loopback as rl             # noqa: E402
import console_core                   # noqa: E402
import loopback_steps                 # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "\n         " + detail))
    return cond


class SocketInterface(object):
    """A processor's EthernetClientInterface, over a real socket. Keeps unread data."""

    def __init__(self, Hostname=None, IPPort=None, *args, **kwargs):
        self.Hostname, self.IPPort, self.sock = Hostname, IPPort, None

    def Connect(self, timeout=None):
        self.sock = socket.create_connection((self.Hostname, self.IPPort), timeout or 5)
        return "Connected"

    def Disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def Send(self, data):
        self.sock.sendall(bytes(data))

    def SendAndWait(self, data, timeout, deliTag=None, **kwargs):
        self.sock.sendall(bytes(data))
        self.sock.settimeout(timeout)
        got = b""
        try:
            while not (deliTag and got.endswith(deliTag)):
                chunk = self.sock.recv(1)
                if not chunk:
                    break
                got += chunk
        except socket.timeout:
            pass
        return got


class StandInProcessor(object):
    """Serves console_core's protocol the way controlscript/main.py does."""

    def __init__(self):
        module = rl.load_module(SocketInterface)
        self.lock = threading.Lock()
        self.writers = []
        self.console = console_core.Console(module.EthernetClass, self.broadcast, 5500,
                                            {"platform": "stand-in"})
        stand_in = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                with stand_in.lock:
                    stand_in.writers.append(self.wfile)
                try:
                    for raw in self.rfile:
                        raw = raw.strip()
                        if raw:
                            reply = stand_in.console.handle(raw.decode("utf-8"),
                                                            self.client_address[0])
                            with stand_in.lock:
                                self.wfile.write(console_core.encode(reply))
                except OSError:
                    pass
                finally:
                    with stand_in.lock:
                        stand_in.writers.remove(self.wfile)

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self.server = Server(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_address[1]

    def broadcast(self, obj):
        data = console_core.encode(obj)
        with self.lock:
            for writer in list(self.writers):
                try:
                    writer.write(data)
                except OSError:
                    pass

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


def part1():
    print("\n[1] the console's request handling")
    events = []
    module = rl.load_module(rl.Recorder)
    console = console_core.Console(module.EthernetClass, events.append, 5500, {"platform": "unit"})

    def ask(obj):
        return console.handle(json.dumps(obj), "10.1.2.3")

    r = console.handle("not json", "10.1.2.3")
    check("a line that is not JSON is refused", not r["ok"] and r["error"].startswith("bad request"))
    r = ask({"id": 1, "op": "set", "command": "Power", "value": "On"})
    check("a command before 'target' is refused, id echoed",
          not r["ok"] and "no target" in r["error"] and r["id"] == 1, repr(r))
    r = ask({"id": 2, "op": "target"})
    check("'target' defaults to the caller's address and port 5500",
          r["ok"] and r["result"] == {"host": "10.1.2.3", "port": 5500}, repr(r))
    r = ask({"id": 3, "op": "info"})
    check("'info' reports the target and the command list",
          r["ok"] and r["result"]["target"] == ["10.1.2.3", 5500]
          and "TrackingFraming" in r["result"]["commands"], repr(r))
    r = ask({"id": 4, "op": "set", "command": "TrackingFraming", "value": "Start"})
    check("'set' runs the command and returns the status it wrote",
          r["ok"] and r["result"] == {"status": "Start"}, repr(r))
    check("... and the status change is pushed as an event",
          {"event": "status", "command": "TrackingFraming", "value": "Start",
           "qualifier": None} in events, repr(events[-3:]))
    r = ask({"id": 5, "op": "update", "command": "Zoom"})
    check("Update on a command without one reports the module's AttributeError",
          not r["ok"] and r["error"].startswith("AttributeError"), repr(r))
    r = ask({"id": 6, "op": "set", "command": "Focus", "value": "Far"})
    check("a missing required qualifier reports the module's TypeError",
          not r["ok"] and r["error"].startswith("TypeError"), repr(r))
    r = ask({"id": 7, "op": "set", "command": "PanTiltAngle",
             "qualifier": {"Pan Speed": 5, "Tilt Speed": 5}})
    check("a silent Discard is surfaced in 'errors'",
          r["ok"] and r["errors"] == ["Invalid Command for SetPanTiltAngle"], repr(r))
    r = ask({"id": 8, "op": "fly"})
    check("an unknown op is refused", not r["ok"] and "unknown op" in r["error"], repr(r))


def session(reply, response_timeout=None):
    stand_in = StandInProcessor()
    lines = []
    try:
        # The module on the stand-in prints its Error lines, as it would to a
        # processor's trace; keep them out of the test report.
        with contextlib.redirect_stdout(io.StringIO()):
            return rl.run("127.0.0.1", console_port=stand_in.port, listen_host="127.0.0.1",
                          listen_port=0, reply=reply, steps="all", settle=0.05,
                          response_timeout=response_timeout, captures=tempfile.mkdtemp(),
                          out=lines.append), lines
    finally:
        stand_in.stop()


def part2():
    print("\n[2] a whole session, --reply ack")
    report, lines = session("ack")
    total = len(loopback_steps.SEQUENCE)
    check("all %d steps ran" % total, len(report["steps"]) == total)
    check("every step's frames match the module run locally (%d/%d)" % (report["wire_ok"], total),
          report["wire_ok"] == total, "\n".join(lines[-60:]))
    check("every read matches the same module fed the same replies (%d/%d)"
          % (report["read_ok"], total), report["read_ok"] == total, "\n".join(lines[-60:]))
    s = report["summary"]
    check("the capture holds every T3 string, in order, nothing unknown",
          s["seen_all"] and s["in_order"] and s["odd"] == 0, repr(s))
    edge = [r for r in report["steps"] if r["note"] == "edge, expect -2448"][0]
    check("the processor side read -2448 at the pan edge",
          edge["processor"]["status"] == -2448, repr(edge["processor"]))


def part3():
    print("\n[3] --reply none: every step waits out its timeout on both sides")
    report, lines = session("none", response_timeout=0.05)
    total = len(report["steps"])
    check("frames still match on every step (%d/%d)" % (report["wire_ok"], total),
          report["wire_ok"] == total, "\n".join(lines[-40:]))
    check("reads still match: no reply means the same status on both sides (%d/%d)"
          % (report["read_ok"], total), report["read_ok"] == total, "\n".join(lines[-40:]))


# Update() calls that share one windowed request with another status
# (build_i20.py's _SharedInquiry): CameraOutput+IntelligentSwitching,
# PanAngleStatus+TiltAngleStatus, DeviceModel+RomVersion, and, from 20028,
# PanSpeedMaxStatus+TiltSpeedMaxStatus. _SharedInquiry only caches a reply it
# parsed without raising; in --reply full this stand-in's SendAndWait keeps
# unread data (by design - see the module docstring), so a status's own read
# can consume a stale ACK/Completion (3 bytes) instead of its real reply. Most
# of this driver's parsers slice (`res[2:6]`), which never raises on a short
# `res`; a few index directly (`res[7]`, `res[3]`) and do. When that happens
# the cache is left unwritten, and the *next* status sharing that inquiry
# sends its own, uncached, request - one extra, genuine wire frame, not a
# wrong one. LocalTwin never sees this: it replays the exact reply the
# listener sent for that step, not the processor's stale leftovers, so it
# always caches. That asymmetry is explained; any other wire mismatch is not.
SHARED_INQUIRY_UPDATES = {"CameraOutput", "IntelligentSwitching",
                          "PanAngleStatus", "TiltAngleStatus",
                          "DeviceModel", "RomVersion",
                          "PanSpeedMaxStatus", "TiltSpeedMaxStatus"}


def _explained_wire_diff(step):
    """A shared-inquiry cache miss: local sent nothing (cache hit), the
    processor sent one genuine extra request (cache miss on stale data)."""
    return (step["kind"] == "Update" and step["command"] in SHARED_INQUIRY_UPDATES
            and not step["expected"] and step["received"])


def part4():
    print("\n[4] --reply full against a runtime that keeps unread data")
    report, lines = session("full")
    total = len(report["steps"])
    diffs = [s for s in report["steps"] if not s["wire_ok"]]
    unexplained = [s for s in diffs if not _explained_wire_diff(s)]
    check("frames match on every step, or diverge only the shared-inquiry "
          "cache-miss way explained above (%d unexplained of %d total, "
          "%d explained)" % (len(unexplained), total, len(diffs) - len(unexplained)),
          not unexplained,
          "\n".join(lines[-40:]) + "\n" + "\n".join(
              "  step %d %s: received %s, expected %s"
              % (s["step"], s["command"], s["received"], s["expected"])
              for s in unexplained))
    check("the reads diverge, and the harness reports it (%d of %d differ)"
          % (total - report["read_ok"], total), report["read_ok"] < total)


def main():
    part1()
    part2()
    part3()
    part4()
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), len(PASS) + len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
