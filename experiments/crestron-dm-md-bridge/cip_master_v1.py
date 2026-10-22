"""cip_master_v1.py - minimal Crestron master-side proprietary-peer client.

Opens TCP to chassis_ip:41794, performs the GATEWAY handshake per
evidence/19 spec, spins a receive loop, sends/responds to heartbeats,
and exposes send_data() to transmit a Cresnet payload wrapped in
GATEWAY_DATA_MSG opcode 5.

Framing (BIG-endian):
   MsgType:u8  MsgLength:u16 BE  body:MsgLength bytes
   total wire = MsgLength + 3 ; validator MsgLength + 3 < 1200 ; MsgType <= 40
"""
from __future__ import annotations
import argparse, socket, struct, sys, threading, time

HDR = struct.Struct(">BH")
U16 = struct.Struct(">H")

CIP_PORT = 41794

OP_CONNECT_RESPONSE     = 0x02
OP_DISCONNECT           = 0x03
OP_DISCONNECT_RESPONSE  = 0x04
OP_DATA                 = 0x05
OP_ALTERNATE_CONNECT    = 0x0A
OP_AUTHENTICATE         = 0x0B
OP_AUTH_RESPONSE        = 0x0C
OP_HEARTBEAT            = 0x0D
OP_HEARTBEAT_RESPONSE   = 0x0E
OP_PROGRAM_READY        = 0x0F
OP_EXTENDED_LENGTH_DATA = 0x12

OPCODE_NAMES = {
  0x02: "CONNECT_RESPONSE", 0x03: "DISCONNECT", 0x04: "DISCONNECT_RESPONSE",
  0x05: "DATA", 0x0A: "ALTERNATE_CONNECT", 0x0B: "AUTHENTICATE",
  0x0C: "AUTH_RESPONSE", 0x0D: "HEARTBEAT", 0x0E: "HEARTBEAT_RESPONSE",
  0x0F: "PROGRAM_READY", 0x12: "EXTENDED_LENGTH_DATA",
}


def _hex(b):
    return b.hex(" ") if b else "(empty)"


class CIPMasterClient:
    def __init__(self, host, cid=0x0001, hb_interval=15.0, on_data=None, verbose=True):
        self.host = host
        self.port = CIP_PORT
        self.cid  = cid & 0xFFFF
        self.hb_interval = hb_interval
        self.on_data = on_data
        self.verbose = verbose
        self.sock = None
        self.handler = None
        self.connected = False
        self._stop = threading.Event()
        self._last_tx = 0.0
        self._rx_thread = None
        self._hb_thread = None
        self._write_lock = threading.Lock()

    def _log(self, direction, op, body):
        if self.verbose:
            name = OPCODE_NAMES.get(op, "UNK_0x%02X" % op)
            print("[%s] %s op=0x%02X (%20s) len=%3d body: %s" %
                  (time.strftime("%H:%M:%S"), direction, op, name, len(body), _hex(body)),
                  flush=True)

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("peer closed")
            buf += chunk
        return buf

    def _recv_frame(self):
        hdr = self._recv_exact(3)
        op, length = HDR.unpack(hdr)
        if length + 3 >= 1200 or op > 40:
            raise ValueError("invalid frame op=0x%02X len=%d" % (op, length))
        body = self._recv_exact(length) if length else b""
        self._log("RX", op, body)
        return op, body

    def _send_frame(self, op, body):
        if len(body) + 3 >= 1200 or op > 40:
            raise ValueError("frame too big or bad op op=0x%02X len=%d" % (op, len(body)))
        with self._write_lock:
            self.sock.sendall(HDR.pack(op, len(body)) + body)
            self._last_tx = time.monotonic()
        self._log("TX", op, body)

    def connect(self, timeout=10.0):
        print("[*] opening TCP %s:%d" % (self.host, self.port), flush=True)
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(timeout)

        deadline = time.time() + timeout
        while time.time() < deadline:
            op, body = self._recv_frame()
            if op == OP_PROGRAM_READY:
                status = body[-1] if len(body) >= 1 else -1
                print("[*] PROGRAM_READY status=%d (2=ready)" % status, flush=True)
                if status == 2:
                    break
                continue
            print("[!] unexpected op 0x%02X before PROGRAM_READY" % op, flush=True)
        else:
            raise TimeoutError("no PROGRAM_READY with status=2 within timeout")

        body = (U16.pack(self.cid)
                + U16.pack(0)
                + bytes([0x40, 0x02])
                + U16.pack(0)
                + U16.pack(0x0200))
        self._send_frame(OP_ALTERNATE_CONNECT, body)

        self.sock.settimeout(timeout)
        op, body = self._recv_frame()
        if op != OP_CONNECT_RESPONSE:
            raise RuntimeError("expected CONNECT_RESPONSE, got op=0x%02X" % op)
        if len(body) < 3:
            raise RuntimeError("CONNECT_RESPONSE body too short: %s" % _hex(body))
        self.handler = (body[0] << 8) | body[1]
        mode = body[2]
        flags = body[3] if len(body) > 3 else 0
        print("[*] CONNECT_RESPONSE handler=0x%04X mode=0x%02X flags=0x%02X" %
              (self.handler, mode, flags), flush=True)
        if mode & 0x40:
            raise RuntimeError("chassis requires auth (Mode & 0x40). Not implemented in v1.")
        if mode & 0xDF:
            raise RuntimeError("CONNECT_RESPONSE denied mode=0x%02X" % mode)
        print("[+] CONNECTED. handler=0x%04X" % self.handler, flush=True)
        self.connected = True

        self.sock.settimeout(1.0)
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True, name="CIPMaster-rx")
        self._hb_thread = threading.Thread(target=self._hb_loop, daemon=True, name="CIPMaster-hb")
        self._rx_thread.start()
        self._hb_thread.start()

    def _rx_loop(self):
        while not self._stop.is_set() and self.connected:
            try:
                op, body = self._recv_frame()
            except socket.timeout:
                continue
            except (ConnectionError, OSError) as e:
                if not self._stop.is_set():
                    print("[!] rx loop exit on %s" % e, flush=True)
                self.connected = False
                return
            except ValueError as e:
                print("[!] bad frame: %s" % e, flush=True)
                continue

            if op == OP_HEARTBEAT:
                h_be = body[:2] if len(body) >= 2 else U16.pack(self.handler)
                self._send_frame(OP_HEARTBEAT_RESPONSE, h_be)
            elif op == OP_HEARTBEAT_RESPONSE:
                pass
            elif op == OP_DATA or op == OP_EXTENDED_LENGTH_DATA:
                if self.on_data and len(body) >= 3:
                    cresnet_len = body[2]
                    cresnet = body[3:3 + cresnet_len]
                    try:
                        self.on_data(cresnet)
                    except Exception as e:
                        print("[!] on_data callback error: %s" % e, flush=True)
            elif op == OP_DISCONNECT:
                print("[!] chassis sent DISCONNECT; replying + closing", flush=True)
                self._send_frame(OP_DISCONNECT_RESPONSE, U16.pack(self.handler))
                self.connected = False
                return
            else:
                print("[?] unhandled op 0x%02X (%s)" %
                      (op, OPCODE_NAMES.get(op, "?")), flush=True)

    def _hb_loop(self):
        while not self._stop.is_set() and self.connected:
            now = time.monotonic()
            idle = now - self._last_tx
            if idle >= self.hb_interval:
                try:
                    self._send_frame(OP_HEARTBEAT, U16.pack(self.handler))
                except OSError as e:
                    print("[!] hb send failed: %s" % e, flush=True)
                    self.connected = False
                    return
            time.sleep(1.0)

    def send_data(self, cresnet_payload):
        if not self.connected:
            raise RuntimeError("not connected")
        if len(cresnet_payload) > 250:
            raise ValueError("payload too large for short-length DATA frame")
        body = U16.pack(self.handler) + bytes([len(cresnet_payload)]) + cresnet_payload
        self._send_frame(OP_DATA, body)

    def disconnect(self):
        self._stop.set()
        if self.connected:
            try:
                self._send_frame(OP_DISCONNECT, U16.pack(self.handler or 0))
            except OSError:
                pass
        self.connected = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", default="192.168.6.14")
    ap.add_argument("--cid", type=lambda s: int(s, 0), default=0x0001)
    ap.add_argument("--hb-interval", type=float, default=15.0)
    ap.add_argument("--idle", type=float, default=20.0)
    args = ap.parse_args()

    cli = CIPMasterClient(args.host, cid=args.cid, hb_interval=args.hb_interval,
                          on_data=lambda b: print("[+] cresnet payload rx: %s" % _hex(b), flush=True))
    try:
        cli.connect(timeout=10.0)
        print("[*] session established. holding for %.1fs" % args.idle, flush=True)
        time.sleep(args.idle)
    except Exception as e:
        print("[FATAL] %s" % e, flush=True)
        sys.exit(1)
    finally:
        cli.disconnect()
        print("[*] disconnected", flush=True)


if __name__ == "__main__":
    main()
