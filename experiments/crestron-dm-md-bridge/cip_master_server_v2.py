"""cip_master_server_v2.py - richer master-of-record server.

After chassis connects:
  Phase A (seconds 10-30): send varied ComPort writes (serial-15 + serial-34 types,
                           different join numbers, deeper nesting)
  Phase B (seconds 30-50): trigger SSH SETAVROUTE commands to generate specific
                           chassis state changes and correlate with observed DATA frames
  Phase C (continuing):    just log everything the chassis sends

All DATA frames are decoded with best-effort nested-container parse.
"""
from __future__ import annotations
import socket, struct, threading, time, sys, subprocess, re, io

# Force UTF-8 output to survive non-ASCII bytes in Cresnet payloads
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
except Exception:
    pass

HDR = struct.Struct(">BH")
U16 = struct.Struct(">H")

OP_NAMES = {
  0x02: "CONNECT_RESPONSE", 0x03: "DISCONNECT", 0x04: "DISCONNECT_RESPONSE",
  0x05: "DATA", 0x0A: "ALTERNATE_CONNECT", 0x0B: "AUTHENTICATE",
  0x0C: "AUTH_RESPONSE", 0x0D: "HEARTBEAT", 0x0E: "HEARTBEAT_RESPONSE",
  0x0F: "PROGRAM_READY", 0x12: "EXTENDED_LENGTH_DATA", 0x01: "CONNECT",
}
LEAF_TYPES = {0x14: "ANALOG", 0x15: "SERIAL15", 0x34: "SERIAL34",
              0x00: "DIGITAL", 0x03: "CONTROL"}


def _h(b): return b.hex(" ") if b else "(empty)"


def decode_payload(payload):
    """Best-effort decode of a chassis-sent payload."""
    if not payload:
        return "(empty)"
    # Try the SwampE4 container format: [ID][Len][Type][body] recursively
    # Known leaf types: 0x14 analog, 0x15 serial-15, 0x34 serial-34, 0x00 digital, 0x03 control
    # Known container type: 0x20 short/short
    def _p(buf, depth=0):
        if not buf: return []
        out = []
        i = 0
        while i < len(buf):
            b = buf[i]
            if b == 0x20 and i + 1 < len(buf):
                # bare 0x20 as container start seen in chassis frames
                # format: 0x20 [SubID] [SubLen] [subBody]
                if i + 2 >= len(buf): break
                sub_id = buf[i+1]
                sub_len = buf[i+2]
                if i + 3 + sub_len > len(buf): sub_len = len(buf) - i - 3
                body = buf[i+3:i+3+sub_len]
                out.append("  "*depth + "cont(0x20 id=0x%02X len=%d):" % (sub_id, sub_len))
                out.extend(_p(body, depth+1))
                i += 3 + sub_len
            elif b == 0x14 and i + 5 <= len(buf):
                # analog leaf [0x14][JoinHi JoinLo][ValHi ValLo]
                join = (buf[i+1] << 8) | buf[i+2]
                val = (buf[i+3] << 8) | buf[i+4]
                out.append("  "*depth + "ANALOG join=0x%04X(%d) val=0x%04X(%d)" % (join, join, val, val))
                i += 5
            elif b == 0x15 and i + 4 < len(buf):
                # serial-15 [0x15][JoinHi JoinLo][Flags][payload...] - need to find end
                join = (buf[i+1] << 8) | buf[i+2]
                flags = buf[i+3]
                # grab rest as payload
                rest = buf[i+4:]
                try: txt = rest.decode('ascii', errors='replace')[:40]
                except: txt = ''
                out.append("  "*depth + "SERIAL15 join=0x%04X(%d) flags=0x%02X payload=%s %r" % (join, join, flags, rest.hex(' '), txt))
                i = len(buf)
            elif b == 0x34 and i + 4 < len(buf):
                join = (buf[i+1] << 8) | buf[i+2]
                flags = buf[i+3]
                rest = buf[i+4:]
                try: txt = rest.decode('ascii', errors='replace')[:40]
                except: txt = ''
                out.append("  "*depth + "SERIAL34 join=0x%04X(%d) flags=0x%02X payload=%s %r" % (join, join, flags, rest.hex(' '), txt))
                i = len(buf)
            elif b == 0x00 and i + 3 <= len(buf):
                # digital leaf [0x00][JoinHi JoinLo]
                join = (buf[i+1] << 8) | buf[i+2]
                out.append("  "*depth + "DIGITAL join=0x%04X(%d) %s" % (join & 0x7FFF, join & 0x7FFF, "ON" if join & 0x8000 else "OFF"))
                i += 3
            elif b == 0x03 and i + 2 <= len(buf):
                # control [0x03][subtype]
                out.append("  "*depth + "CONTROL subtype=0x%02X" % buf[i+1])
                i += 2
            else:
                out.append("  "*depth + "RAW: %s" % _h(buf[i:]))
                i = len(buf)
        return out
    return "\n" + "\n".join(_p(payload))


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: raise ConnectionError("peer closed")
        buf += chunk
    return buf


def log(dir_, op, body):
    name = OP_NAMES.get(op, "UNK_0x%02X" % op)
    msg = "[%s] %s op=0x%02X (%20s) len=%3d body: %s" % (
        time.strftime("%H:%M:%S"), dir_, op, name, len(body), _h(body))
    if dir_ == "RX" and op in (0x05, 0x12) and len(body) >= 3:
        # peel outer: [Handler:2BE][CresnetLen:u8][payload] for 0x05
        if op == 0x05:
            handler = (body[0]<<8)|body[1]; clen = body[2]; cresnet = body[3:3+clen]
        else:
            handler = (body[0]<<8)|body[1]; clen = (body[2]<<8)|body[3]; cresnet = body[4:4+clen]
        msg += "\n    DECODE:" + decode_payload(cresnet)
    print(msg, flush=True)


def send_frame(sock, op, body):
    sock.sendall(HDR.pack(op, len(body)) + body)
    log("TX", op, body)


def recv_frame(sock):
    hdr = recv_exact(sock, 3)
    op, length = HDR.unpack(hdr)
    body = recv_exact(sock, length) if length else b""
    log("RX", op, body)
    return op, body


def ssh_cmd(cmd):
    """Run chassis SSH command in background thread, log result."""
    def _run():
        try:
            import paramiko
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect('192.168.6.14', username='admin', password='password', timeout=5,
                      allow_agent=False, look_for_keys=False)
            _, out, _ = c.exec_command(cmd, timeout=5)
            r = out.read().decode(errors='replace').strip()
            print("[SSH] %s -> %s" % (cmd, r[:200]), flush=True)
            c.close()
        except Exception as e:
            print("[SSH] FAIL %s: %s" % (cmd, e), flush=True)
    threading.Thread(target=_run, daemon=True).start()


def serve_one(conn, peer_addr):
    print("\n*** CHASSIS CONNECTED from %s ***" % (peer_addr,), flush=True)
    try:
        send_frame(conn, 0x0F, bytes([0x02]))
        op, body = recv_frame(conn)
        if op not in (0x0A, 0x01):
            send_frame(conn, 0x03, b"\x00\x00")
            conn.close(); return
        handler = 1
        send_frame(conn, 0x02, U16.pack(handler) + bytes([0x20, 0x00]))
        print("[+] CONNECTED, handler=%d" % handler, flush=True)

        conn.settimeout(2.0)
        t_start = time.monotonic()
        last_hb = time.monotonic()
        phase_a_done = False
        phase_b_done = False
        while True:
            now = time.monotonic()
            # PHASE A: ComPort probes at t+10 to t+30
            if not phase_a_done and now - t_start >= 10:
                phase_a_done = True
                print("\n[PHASE A] varied ComPort probes", flush=True)
                probes = [
                    ("serial-15 join=1 flat", bytes([0x15, 0x00, 0x01, 0x00]) + b"PINGa\r"),
                    ("serial-15 join=5 flat", bytes([0x15, 0x00, 0x05, 0x00]) + b"PINGb\r"),
                    ("serial-15 join=29 flat", bytes([0x15, 0x00, 0x1D, 0x00]) + b"PINGc\r"),
                    ("serial-34 join=1 flat", bytes([0x34, 0x00, 0x01, 0x00]) + b"PINGd\r"),
                    ("serial-34 join=5 flat", bytes([0x34, 0x00, 0x05, 0x00]) + b"PINGe\r"),
                    ("serial-34 join=29 flat", bytes([0x34, 0x00, 0x1D, 0x00]) + b"PINGf\r"),
                    ("nested 0x20->0x01->0x01 serial-15 join=1", bytes([
                        0x20, 0x01, 0x0B, 0x20, 0x01, 0x08, 0x15, 0x00, 0x01, 0x00]) + b"PINGg\r"),
                ]
                for label, pl in probes:
                    print("[probe] %s" % label, flush=True)
                    db = U16.pack(handler) + bytes([len(pl)]) + pl
                    try: send_frame(conn, 0x05, db)
                    except OSError as e: print("send failed:", e); break
                    time.sleep(0.4)

            # PHASE B: SSH routing commands at t+30 (triggers chassis activity)
            if not phase_b_done and now - t_start >= 30:
                phase_b_done = True
                print("\n[PHASE B] SSH SETAVROUTE triggers", flush=True)
                for cmd in ["SETAVROUTE 1 33", "SETAVROUTE 2 33", "SETAVROUTE 0 33"]:
                    print("[trigger-%d] %s" % (int(now - t_start), cmd), flush=True)
                    ssh_cmd(cmd)
                    time.sleep(3)

            try:
                op, body = recv_frame(conn)
            except socket.timeout:
                if time.monotonic() - last_hb > 15:
                    send_frame(conn, 0x0D, U16.pack(handler))
                    last_hb = time.monotonic()
                continue
            except (ConnectionError, OSError) as e:
                print("[!] peer closed: %s" % e, flush=True)
                break

            if op == 0x0D:
                h = body[:2] if len(body) >= 2 else U16.pack(handler)
                send_frame(conn, 0x0E, h)
            elif op == 0x03:
                send_frame(conn, 0x04, body[:2] if len(body) >= 2 else b"\x00\x00")
                break
            # DATA frames already decoded in log()
    finally:
        try: conn.close()
        except: pass
        print("*** session closed ***\n", flush=True)


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 41794))
    srv.listen(5)
    print("[*] v2 listening on 0.0.0.0:41794", flush=True)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=serve_one, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
