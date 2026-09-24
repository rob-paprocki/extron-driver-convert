#!/usr/bin/env python3
"""
run_loopback.py - drive the i20 module on a processor step by step, and check
every frame it puts on the wire.

This PC plays both ends. It runs the VISCA listener (the "camera"), connects to
the command console controlscript/main.py serves on the processor, points the
module at this PC, and sends each step of controlscript/loopback_steps.py. For
every step it compares two things:

  wire   the frames the listener received      against  the frames the same
                                                         module sends on this PC
  read   what the module on the processor       against  what the same module
         read back from the listener's reply             reads from those bytes

The local run replays the processor's calls in the same order on one module
instance, so a difference on either count is a difference between Extron's
runtime and CPython running identical code - which is what this experiment is
for. Nothing is asserted about a real camera: every reply is documentation.

Run:
    python3 experiments/loopback/run_loopback.py --processor 192.168.254.1
    python3 experiments/loopback/run_loopback.py --processor 192.168.254.1 --reply full

Each run writes captures/<time>.tsv (every frame) and captures/<time>-report.json.
"""

import argparse
import contextlib
import datetime
import importlib.util
import io
import json
import os
import socket
import sys
import time
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "controlscript"))

import visca_listener as vl           # noqa: E402
import loopback_steps                 # noqa: E402

MODULE = os.path.join(_ROOT, "experiments", "skeleton_i20", "out",
                      "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")

STEP_SETS = {
    "all": loopback_steps.SEQUENCE,
    "t3": loopback_steps.T3,
    "edges": loopback_steps.EDGES,
    "polls": loopback_steps.POLLS,
}


class Recorder(object):
    """extronlib stand-in: records what the module sends, replays canned replies."""

    def __init__(self, Hostname=None, IPPort=None, *args, **kwargs):
        self.Hostname, self.IPPort = Hostname, IPPort
        self.sent, self.canned = [], []

    def Send(self, data):
        self.sent.append(bytes(data))

    def SendAndWait(self, data, timeout, **kwargs):
        self.sent.append(bytes(data))
        return self.canned.pop(0) if self.canned else b""

    def Connect(self, timeout=None):
        return "Connected"

    def Disconnect(self):
        pass


_loads = [0]


def load_module(interface):
    """Import the i20 module with extronlib's interfaces replaced by `interface`."""
    pkg = types.ModuleType("extronlib")
    iface = types.ModuleType("extronlib.interface")
    setattr(iface, "SerialInterface", interface)
    setattr(iface, "EthernetClientInterface", interface)
    setattr(pkg, "interface", iface)
    sys.modules["extronlib"] = pkg
    sys.modules["extronlib.interface"] = iface
    _loads[0] += 1
    spec = importlib.util.spec_from_file_location("i20_module_%d" % _loads[0], MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _normalise(value):
    """Compare statuses the way they arrive from the processor: through JSON."""
    return json.loads(json.dumps(value))


def _error_type(text):
    return text.split(":", 1)[0] if text else None


class LocalTwin(object):
    """The module on this PC, fed the processor's calls and the listener's replies."""

    def __init__(self):
        self.cam = load_module(Recorder).EthernetClass("192.0.2.1", 5500)
        self.errors = []
        twin = self

        def error(message):
            twin.errors.append(message[0] if isinstance(message, (list, tuple)) and message
                               else str(message))

        self.cam.Error = error

    def step(self, kind, command, value, qualifier, replies):
        self.cam.sent, self.cam.canned, self.errors = [], list(replies), []
        raised = None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                if kind == "Set":
                    self.cam.Set(command, value, qualifier)
                else:
                    self.cam.Update(command, qualifier)
            except Exception as e:
                raised = "%s: %s" % (type(e).__name__, e)
        return {"sent": [vl.hexs(f) for f in self.cam.sent],
                "status": _normalise(self.cam.ReadStatus(command, qualifier)),
                "raised": raised, "errors": list(self.errors)}


class ConsoleClient(object):
    """Newline-delimited JSON to controlscript/console_core.py."""

    def __init__(self, host, port, timeout=10.0):
        self.sock = socket.create_connection((host, port), timeout)
        self.sock.settimeout(timeout)
        self.buffer = b""
        self.next_id = 0
        self.events = []

    def request(self, op, **fields):
        self.next_id += 1
        message = dict(fields)
        message["id"], message["op"] = self.next_id, op
        self.sock.sendall((json.dumps(message) + "\n").encode("utf-8"))
        while True:
            obj = self._read()
            if "event" not in obj and obj.get("id") == self.next_id:
                return obj
            self.events.append(obj)

    def _read(self):
        while b"\n" not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("the console closed the connection")
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line.decode("utf-8"))

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def run(processor, console_port=5600, listen_host="0.0.0.0", listen_port=5500,
        reply="ack", steps="all", settle=0.2, response_timeout=None,
        captures=vl.DEFAULT_CAPTURES, out=print):
    """One session. Returns the report dict, which is also written beside the capture."""
    os.makedirs(captures, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    capture = vl.Capture(os.path.join(captures, stamp + ".tsv"), echo=False)
    listener = vl.Listener(listen_host, listen_port, reply, capture)
    _, port = listener.start()
    twin = LocalTwin()
    results, info, console = [], None, None
    try:
        console = ConsoleClient(processor, console_port)
        info = console.request("info").get("result")
        out("processor: %s" % json.dumps(info, sort_keys=True))
        out("target:    %s" % json.dumps(console.request("target", port=port)))
        if response_timeout is not None:
            console.request("timeout", seconds=response_timeout)
            twin.cam.DefaultResponseTimeout = response_timeout
        connected = console.request("connect")
        out("connect:   %s" % json.dumps(connected))
        if not connected.get("ok") or "Connected" not in str(connected.get("result")):
            raise RuntimeError("the module on the processor could not reach this PC on "
                               "TCP %d - check the firewall and the address it targeted" % port)
        time.sleep(settle)

        for n, (kind, command, value, qualifier, note) in enumerate(STEP_SETS[steps], 1):
            mark = len(capture.rows)
            fields = {"command": command}
            if kind == "Set":
                fields["value"] = value
            if qualifier is not None:
                fields["qualifier"] = qualifier
            remote = console.request("set" if kind == "Set" else "update", **fields)
            time.sleep(settle)
            rows = capture.rows[mark:]
            received = [r["hex"] for r in rows if r["dir"] == "rx"]
            replies = [bytes.fromhex(r["hex"]) for r in rows if r["dir"] == "tx"]
            local = twin.step(kind, command, value, qualifier, replies)

            remote_status = (remote.get("result") or {}).get("status")
            wire_ok = received == local["sent"]
            read_ok = (remote_status == local["status"]
                       and _error_type(remote.get("error")) == _error_type(local["raised"]))
            results.append({
                "step": n, "kind": kind, "command": command, "value": value,
                "qualifier": qualifier, "note": note,
                "wire_ok": wire_ok, "read_ok": read_ok,
                "received": received, "expected": local["sent"],
                "replies": [vl.hexs(r) for r in replies],
                "processor": {"status": remote_status, "error": remote.get("error"),
                              "errors": remote.get("errors", [])},
                "local": {"status": local["status"], "error": local["raised"],
                          "errors": local["errors"]},
            })
            out("%3d %-6s %-22s wire %-4s read %-4s %s"
                % (n, kind, command, "ok" if wire_ok else "DIFF",
                   "ok" if read_ok else "DIFF", note))
            if not wire_ok:
                out("      received %s\n      expected %s" % (received, local["sent"]))
            if not read_ok:
                out("      processor %r / %r\n      this PC   %r / %r"
                    % (remote_status, remote.get("error"), local["status"], local["raised"]))
        try:
            console.request("disconnect")
        except (OSError, ValueError):
            pass
    finally:
        if console:
            console.close()
        listener.stop()
        capture.close()

    text, summary = vl.summarize(capture.rows)
    report = {
        "when": stamp, "reply_mode": reply, "steps_set": steps, "processor_info": info,
        "wire_ok": sum(1 for r in results if r["wire_ok"]),
        "read_ok": sum(1 for r in results if r["read_ok"]),
        "steps": results, "summary": summary,
        "console_events": len(console.events) if console else 0,
    }
    with open(os.path.join(captures, stamp + "-report.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    out("")
    out(text)
    out("steps: %d; wire matches %d; reads match %d; report %s-report.json"
        % (len(results), report["wire_ok"], report["read_ok"], stamp))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--processor", required=True, help="processor address")
    ap.add_argument("--console-port", type=int, default=5600)
    ap.add_argument("--listen-host", default="0.0.0.0")
    ap.add_argument("--listen-port", type=int, default=5500)
    ap.add_argument("--reply", choices=("none", "ack", "full"), default="ack")
    ap.add_argument("--steps", choices=sorted(STEP_SETS), default="all")
    ap.add_argument("--settle", type=float, default=0.2,
                    help="seconds to wait after each step for frames to arrive")
    ap.add_argument("--response-timeout", type=float, default=None,
                    help="set the module's DefaultResponseTimeout on both sides")
    ap.add_argument("--captures", default=vl.DEFAULT_CAPTURES)
    args = ap.parse_args(argv)
    report = run(args.processor, args.console_port, args.listen_host, args.listen_port,
                 args.reply, args.steps, args.settle, args.response_timeout, args.captures)
    total = len(report["steps"])
    return 0 if total and report["wire_ok"] == total and report["read_ok"] == total else 1


if __name__ == "__main__":
    sys.exit(main())
