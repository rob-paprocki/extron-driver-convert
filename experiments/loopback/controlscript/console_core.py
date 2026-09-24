"""
console_core.py - the command console main.py serves on the processor.

A client sends one JSON object per line and gets one JSON object per line back.
The console drives the i20 ControlScript module exactly as a program on the
processor would - Set, Update, ReadStatus - so a PC can exercise every command
without a touch panel, and see what the module read back.

Requests:
    {"id": 1, "op": "ping"}
    {"id": 2, "op": "info"}
    {"id": 3, "op": "target", "port": 5500}           host defaults to the caller
    {"id": 4, "op": "connect"}
    {"id": 5, "op": "set", "command": "Zoom", "value": "Tele", "qualifier": {"Speed": 5}}
    {"id": 6, "op": "update", "command": "TrackingFraming"}
    {"id": 7, "op": "read", "command": "TrackingFraming"}
    {"id": 8, "op": "timeout", "seconds": 0.3}
    {"id": 9, "op": "disconnect"}

Every reply carries "id", "ok", then "result" or "error", and "errors": the
module's own Error/Discard lines raised while serving that request. Status
changes and those error lines are also pushed to every client as
{"event": "status", ...} and {"event": "error", ...}.

Kept free of extronlib, and to Python 3.5 syntax, so the repo's tests run this
same code against the listener on one PC.
"""

import json


class Console(object):
    def __init__(self, make_camera, broadcast, default_port=5500, info=None):
        self.make_camera = make_camera      # (host, port) -> a module EthernetClass
        self.broadcast = broadcast          # callable(dict), sends to every client
        self.default_port = default_port
        self.info = dict(info or {})
        self.cam = None
        self.target = None
        self.errors = []

    def handle(self, line, client_ip):
        """Serve one request line; always returns a reply dict."""
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("a request must be a JSON object")
        except ValueError as e:
            return {"id": None, "ok": False, "error": "bad request: %s" % e, "errors": []}
        self.errors = []
        reply = {"id": request.get("id")}
        try:
            reply["result"] = self._dispatch(request, client_ip)
            reply["ok"] = True
        except Exception as e:  # report every failure to the caller, never swallow
            reply["ok"] = False
            reply["error"] = "%s: %s" % (type(e).__name__, e)
        reply["errors"] = list(self.errors)
        return reply

    def _dispatch(self, request, client_ip):
        op = request.get("op")
        if op == "ping":
            return "pong"
        if op == "info":
            info = dict(self.info)
            info["target"] = list(self.target) if self.target else None
            info["commands"] = sorted(self.cam.Commands) if self.cam else None
            return info
        if op == "target":
            return self._retarget(request.get("host") or client_ip,
                                  int(request.get("port") or self.default_port))

        if op not in ("connect", "disconnect", "timeout", "set", "update", "read"):
            raise ValueError("unknown op %r" % op)
        cam = self.cam
        if cam is None:
            raise RuntimeError("no target yet: send {\"op\": \"target\"} first")
        if op == "connect":
            return cam.Connect(float(request.get("timeout", 5)))
        if op == "disconnect":
            cam.Disconnect()
            return "Disconnected"
        if op == "timeout":
            cam.DefaultResponseTimeout = float(request["seconds"])
            return cam.DefaultResponseTimeout

        command = request.get("command")
        if not command:
            raise ValueError("%r needs a command" % op)
        qualifier = request.get("qualifier")
        if op == "set":
            cam.Set(command, request.get("value"), qualifier)
        elif op == "update":
            cam.Update(command, qualifier)
        return {"status": cam.ReadStatus(command, qualifier)}

    def _retarget(self, host, port):
        if self.cam is not None:
            try:
                self.cam.Disconnect()
            except Exception:  # the old socket may already be gone; the new one matters
                pass
        cam = self.make_camera(host, port)
        self._attach(cam)
        self.cam, self.target = cam, (host, port)
        return {"host": host, "port": port}

    def _attach(self, cam):
        console = self
        original = cam.Error

        def error(message):
            text = message[0] if isinstance(message, (list, tuple)) and message else str(message)
            console.errors.append(text)
            console.broadcast({"event": "error", "message": text})
            original(message)

        def status(command, value, qualifier):
            console.broadcast({"event": "status", "command": command,
                               "value": value, "qualifier": qualifier})

        cam.Error = error           # Discard() calls self.Error, so this catches both
        for name in cam.Commands:
            cam.SubscribeStatus(name, None, status)


def encode(obj):
    """One JSON object per line, as bytes."""
    return (json.dumps(obj, sort_keys=True) + "\n").encode("utf-8")
