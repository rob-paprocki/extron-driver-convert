# Copyright 2026 - DM-MD CPU3 master-of-record driver (one-socket design)
#
# Phase 2 complete: full ControlScript port of cip_master_server_v2.py.
# WE are the TCP SERVER on :41794; chassis dials OUT to us as TCP CLIENT.
#
# Byte-for-byte reference impl is cip_master_server_v2.py (standalone Python,
# proven on hardware per finding 24). This file ports that logic into the
# extronlib.interface.EthernetServerInterfaceEx event-driven idiom while
# keeping the DTP3 CP 42 (`extr_15_17578`) class name + Commands shape intact
# for the asset-graph in the surrounding .pkp.

from extronlib.interface import EthernetServerInterfaceEx
from extronlib.system import Wait, ProgramLog


_LISTEN_PORT = 41794


# ------------------------------------------------------------------
# Nested-container Cresnet payload builders
# ------------------------------------------------------------------
# Format per evidence/20 and confirmed byte-exact via finding 24 PING echo:
#   outer container:  [0x20][container_id][len][body]
#   inner container:  [0x20][container_id][len][body]
#   leaf (serial-15): [0x15][join_hi][join_lo][flags][payload]
#   leaf (serial-34): [0x34][join_hi][join_lo][flags][payload]
#   leaf (analog):    [0x14][join_hi][join_lo][val_hi][val_lo]
#   leaf (digital):   [0x00][join_hi][join_lo | 0x8000 for ON]
#   leaf (IR):        [0x16][join_hi][join_lo][...]  (format TBD, Phase 3)
#   leaf (control):   [0x03][subtype]
#
# len counts bytes from the 0x20 type-byte through the end of body.
# Known-good from finding 24 live loopback echo (output 1 ComPort[1]):
#   [0x20][0x01][0x0B][0x20][0x01][0x08][0x15][0x00][0x01][0x00] + ascii_payload

_LEAF_SERIAL15 = 0x15
_LEAF_SERIAL34 = 0x34
_LEAF_ANALOG   = 0x14
_LEAF_DIGITAL  = 0x00
_LEAF_IR       = 0x16
_LEAF_CONTROL  = 0x03

_OP_CONNECT_RESPONSE     = 0x02
_OP_DISCONNECT           = 0x03
_OP_DISCONNECT_RESPONSE  = 0x04
_OP_DATA                 = 0x05
_OP_ALTERNATE_CONNECT    = 0x0A
_OP_AUTHENTICATE         = 0x0B
_OP_AUTH_RESPONSE        = 0x0C
_OP_HEARTBEAT            = 0x0D
_OP_HEARTBEAT_RESPONSE   = 0x0E
_OP_PROGRAM_READY        = 0x0F
_OP_EXTENDED_LENGTH_DATA = 0x12


def _wrap_container(container_id, body):
    """Wrap body in a [0x20][container_id][len][body] container.

    len = len(body) exactly (bytes AFTER the len byte). Verified against
    finding 24 echo: [0x20][0x01][0x0B] wraps 11-byte body, inner
    [0x20][0x01][0x08] wraps 8-byte serial-15 leaf body.
    """
    if len(body) > 255:
        raise ValueError("single-byte container len overflow (%d B)" % len(body))
    return bytes([0x20, container_id & 0xFF, len(body)]) + body


def _serial15_leaf(join, flags, payload):
    """Serial-15 leaf for ComPort StringInput/StringOutput."""
    return bytes([_LEAF_SERIAL15,
                  (join >> 8) & 0xFF, join & 0xFF, flags & 0xFF]) + payload


def _ir_leaf(join, data):
    """IR leaf - exact subfield layout is still TBD (Phase 3)."""
    return bytes([_LEAF_IR,
                  (join >> 8) & 0xFF, join & 0xFF]) + data


def _digital_leaf(join, on):
    """Digital leaf - high bit of join encodes ON/OFF per finding 24 decoder."""
    j = (join & 0x7FFF) | (0x8000 if on else 0)
    return bytes([_LEAF_DIGITAL, (j >> 8) & 0xFF, j & 0xFF])


def _analog_leaf(join, value):
    """Analog symmetric leaf [0x14][jh][jl][vh][vl]."""
    return bytes([_LEAF_ANALOG,
                  (join >> 8) & 0xFF, join & 0xFF,
                  (value >> 8) & 0xFF, value & 0xFF])


def _rmc_output_container(output_slot, inner_body):
    """Wrap a leaf for the RMC on physical output `output_slot` (1-8).

    Finding 29 resolved slot architecture:
      - Outer container = 0x01 (chassis's endpoint cluster, fixed)
      - Inner container = output index 1-8 (which output's RMC)
      - Leaf type encodes subsystem (serial-15=RS-232; others TBD)

    For output 1 the path is `[0x20][0x01][0x20][0x01][leaf]`, which was
    where finding 24's bug-camouflaging coincidence came from (outer=0x01
    AND inner=0x01). For outputs 2-8 the inner-id must be the output
    index, not 0x01.
    """
    inner_wrap = _wrap_container(output_slot & 0xFF, inner_body)  # output index
    return _wrap_container(0x01, inner_wrap)                       # endpoint cluster


# Chassis slot numbering (verified empirically):
#   Input cards:  slot 1..8  (= input_num)
#   Output cards: slot 33..40 (= 32 + output_num; 0x21..0x28)
_OUTPUT_CARD_SLOT_BASE = 0x20
_ROUTE_JOIN_VIDEO = 0x0002


def _output_card_slot(output_num):
    return _OUTPUT_CARD_SLOT_BASE + (output_num & 0xFF)


def _route_write_payload(output_num, input_num, join=_ROUTE_JOIN_VIDEO):
    """Verified live (finding 28): routes input_num -> output_num.

      [0x20][OutputCardSlot=0x21..0x28][0x20][0x01][len][0x14][jh][jl][vh][vl]
    After this write, SSH DUMPDMROUTEINFO <slot> reports the new route.
    """
    leaf = _analog_leaf(join, input_num)
    inner = _wrap_container(0x01, leaf)
    return _wrap_container(_output_card_slot(output_num), inner)


# ------------------------------------------------------------------
# Main driver class (keeps donor's class name intact)
# ------------------------------------------------------------------

class extr_15_17578(object):
    """DM-MD CPU3 one-socket master-of-record driver (Phase 2)."""

    def __init__(self):
        # Standard Extron driver boilerplate
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 1.5
        self.Subscription = {}
        self.ReceiveData = self._NullReceiveData
        self._receiveBuffer = b''
        self._maxBufferSize = 4096
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None

        # Session state
        self._srv = None             # EthernetServerInterfaceEx
        self._session = None         # ClientObject bound after chassis connects
        self._handler = 1            # session handle we assign in CONNECT_RESPONSE
        self._rxbuf = bytearray()
        self._session_up = False
        self._last_tx_mono = 0.0
        self._hb_wait = None         # Wait handle for pending heartbeat tick

        # Chassis-side state cache
        self._routing = {}           # Output -> Input (0 = no route)
        self._input_online = {}
        self._output_online = {}
        self._relay_state = {}
        self._comport_last_rx = {}
        self._output_route = {}

        # Commands table (asset-graph binding)
        self.Commands = {
            'MatrixTieCommand':      {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus':       {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'InputTieStatus':        {'Parameters': ['Input', 'Output'], 'Status': {}},
            'ComPortSendString':     {'Parameters': ['Output'], 'Status': {}},
            'ComPortReceivedString': {'Parameters': ['Output'], 'Status': {}},
            'IRPulse':               {'Parameters': ['Output', 'IR Code'], 'Status': {}},
            'RelayClose':            {'Parameters': ['Output'], 'Status': {}},
            'RelayOpen':             {'Parameters': ['Output'], 'Status': {}},
            'RelayStatus':           {'Parameters': ['Output'], 'Status': {}},
            'InputOnlineStatus':     {'Parameters': ['Input'],  'Status': {}},
            'OutputOnlineStatus':    {'Parameters': ['Output'], 'Status': {}},
            'SystemPowerStatus':     {'Parameters': [], 'Status': {}},
            'ChassisProgrammedIP':   {'Parameters': [], 'Status': {}},
            'ConnectionStatus':      {'Parameters': [], 'Status': {}},
            'Firmware':              {'Parameters': [], 'Status': {}},
            'MACAddress':            {'Parameters': [], 'Status': {}},
            'SerialNumber':          {'Parameters': [], 'Status': {}},
            'HDCPInputStatus':       {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus':      {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution':      {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus':     {'Parameters': ['Input'], 'Status': {}},
        }

        # Autostart server on construction
        self._start_server()

    # --------------------------------------------------------------
    # TCP server lifecycle
    # --------------------------------------------------------------

    def _start_server(self):
        if self._srv is not None:
            return
        try:
            self._srv = EthernetServerInterfaceEx(_LISTEN_PORT, Protocol='TCP')
            self._srv.Connected = self._on_chassis_connected
            self._srv.Disconnected = self._on_chassis_disconnected
            self._srv.ReceiveData = self._on_chassis_rx
            self._srv.StartListen()
            if self.Debug:
                print('DM-MD master: listening on :%d' % _LISTEN_PORT)
        except Exception as e:
            ProgramLog('DM-MD master: StartListen failed: %s' % e, 'error')

    def _on_chassis_connected(self, client, state):
        self._session = client
        self._rxbuf = bytearray()
        self._session_up = False
        if self.Debug:
            print('DM-MD master: chassis connected from %s' % getattr(client, 'IPAddress', '?'))
        # Immediately send PROGRAM_READY (status=2 = ready)
        self._send_frame(_OP_PROGRAM_READY, bytes([0x02]))

    def _on_chassis_disconnected(self, client, state):
        if self.Debug:
            print('DM-MD master: chassis disconnected')
        self._session = None
        self._session_up = False
        try:
            self.NewConnectionStatus('Disconnected', None)
        except Exception:
            pass

    def _on_chassis_rx(self, client, data):
        self._rxbuf.extend(data)
        while True:
            frame = self._try_pop_frame()
            if frame is None:
                break
            try:
                self._dispatch_frame(*frame)
            except Exception as e:
                ProgramLog('DM-MD master: dispatch error: %s' % e, 'warning')

    def _try_pop_frame(self):
        if len(self._rxbuf) < 3:
            return None
        op = self._rxbuf[0]
        length = (self._rxbuf[1] << 8) | self._rxbuf[2]
        if len(self._rxbuf) < 3 + length:
            return None
        body = bytes(self._rxbuf[3:3 + length])
        del self._rxbuf[:3 + length]
        return op, body

    def _send_frame(self, op, body):
        if self._session is None:
            return
        length = len(body)
        hdr = bytes([op, (length >> 8) & 0xFF, length & 0xFF])
        try:
            self._session.Send(hdr + body)
            self._last_tx_mono = _mono()
        except Exception as e:
            ProgramLog('DM-MD master: send failed op=0x%02X: %s' % (op, e), 'error')

    # --------------------------------------------------------------
    # Frame dispatch
    # --------------------------------------------------------------

    def _dispatch_frame(self, op, body):
        if op == _OP_ALTERNATE_CONNECT:
            # Chassis is announcing itself. Grant handler=1, mode=0x20
            # (support heartbeat-response-check), flags=0.
            self._send_frame(_OP_CONNECT_RESPONSE,
                             bytes([(self._handler >> 8) & 0xFF,
                                    self._handler & 0xFF, 0x20, 0x00]))
            self._session_up = True
            try:
                self.NewConnectionStatus('Connected', None)
            except Exception:
                pass
            self._schedule_heartbeat()
        elif op == _OP_HEARTBEAT:
            # Mirror handler bytes
            h = body[:2] if len(body) >= 2 else bytes([(self._handler >> 8) & 0xFF,
                                                        self._handler & 0xFF])
            self._send_frame(_OP_HEARTBEAT_RESPONSE, h)
        elif op == _OP_HEARTBEAT_RESPONSE:
            pass   # noted
        elif op == _OP_DATA:
            self._parse_data_frame(body, extlen=False)
        elif op == _OP_EXTENDED_LENGTH_DATA:
            self._parse_data_frame(body, extlen=True)
        elif op == _OP_DISCONNECT:
            # Mirror + close
            self._send_frame(_OP_DISCONNECT_RESPONSE, body[:2] if len(body) >= 2
                             else bytes([(self._handler >> 8) & 0xFF, self._handler & 0xFF]))
            self._session_up = False
        else:
            if self.Debug:
                print('DM-MD master: unhandled op 0x%02X len=%d' % (op, len(body)))

    def _parse_data_frame(self, body, extlen):
        if extlen:
            if len(body) < 4:
                return
            handler = (body[0] << 8) | body[1]
            clen = (body[2] << 8) | body[3]
            payload = body[4:4 + clen]
        else:
            if len(body) < 3:
                return
            handler = (body[0] << 8) | body[1]
            clen = body[2]
            payload = body[3:3 + clen]
        self._walk_payload(payload, path=[])

    def _walk_payload(self, buf, path):
        """Walk nested-container payload and emit feedback on each leaf."""
        i = 0
        while i < len(buf):
            b = buf[i]
            if b == 0x20 and i + 2 < len(buf):
                sub_id = buf[i + 1]
                sub_len = buf[i + 2]
                if i + 3 + sub_len > len(buf):
                    return
                sub = buf[i + 3:i + 3 + sub_len]
                self._walk_payload(sub, path + [sub_id])
                i += 3 + sub_len
            elif b == _LEAF_SERIAL15 and i + 4 <= len(buf):
                join = (buf[i + 1] << 8) | buf[i + 2]
                flags = buf[i + 3]
                payload = bytes(buf[i + 4:])
                self._on_serial_feedback(path, join, flags, payload, kind=15)
                i = len(buf)
            elif b == _LEAF_SERIAL34 and i + 4 <= len(buf):
                join = (buf[i + 1] << 8) | buf[i + 2]
                flags = buf[i + 3]
                payload = bytes(buf[i + 4:])
                self._on_serial_feedback(path, join, flags, payload, kind=34)
                i = len(buf)
            elif b == _LEAF_ANALOG and i + 5 <= len(buf):
                join = (buf[i + 1] << 8) | buf[i + 2]
                value = (buf[i + 3] << 8) | buf[i + 4]
                self._on_analog_feedback(path, join, value)
                i += 5
            elif b == _LEAF_DIGITAL and i + 3 <= len(buf):
                raw = (buf[i + 1] << 8) | buf[i + 2]
                join = raw & 0x7FFF
                on = bool(raw & 0x8000)
                self._on_digital_feedback(path, join, on)
                i += 3
            elif b == _LEAF_CONTROL and i + 2 <= len(buf):
                subtype = buf[i + 1]
                self._on_control_feedback(path, subtype)
                i += 2
            else:
                return   # unknown; bail

    # --------------------------------------------------------------
    # Feedback routing
    # --------------------------------------------------------------

    def _on_serial_feedback(self, path, join, flags, payload, kind):
        """Serial-15/34 leaf from chassis. If path matches an output's
        ComPort structure (outer=output, inner=0x01, join=1), surface as
        ComPortReceivedString."""
        if self.Debug:
            print('serial-%d path=%s join=0x%04X flags=0x%02X payload=%d B'
                  % (kind, path, join, flags, len(payload)))
        output = self._path_to_output(path)
        if output is not None and join == 1:
            # ComPort[1] receive on this output
            self._comport_last_rx[output] = payload
            try:
                self.NewComPortReceivedString(payload, {'Output': output})
            except Exception as e:
                if self.Debug:
                    print('NewComPortReceivedString raise: %s' % e)

    def _on_analog_feedback(self, path, join, value):
        if self.Debug:
            print('analog path=%s join=0x%04X val=%d' % (path, join, value))

    def _on_digital_feedback(self, path, join, on):
        if self.Debug:
            print('digital path=%s join=0x%04X %s' % (path, join, 'ON' if on else 'OFF'))

    def _on_control_feedback(self, path, subtype):
        if self.Debug:
            print('control path=%s subtype=0x%02X' % (path, subtype))

    def _path_to_output(self, path):
        """Map nested-container path to output slot number (1-8) if possible."""
        if not path:
            return None
        # Finding 24: path [0x01, 0x01] = output 1's RMC
        # Hypothesis: [N, 0x01] where N in 1..8 = output N's RMC
        if 1 <= path[0] <= 8 and (len(path) < 2 or path[1] == 0x01):
            return path[0]
        return None

    # --------------------------------------------------------------
    # Heartbeat (idle keepalive)
    # --------------------------------------------------------------

    def _schedule_heartbeat(self):
        try:
            if self._hb_wait is not None:
                try:
                    self._hb_wait.Cancel()
                except Exception:
                    pass
            self._hb_wait = Wait(15, self._heartbeat_tick)
        except Exception as e:
            if self.Debug:
                print('schedule_heartbeat: %s' % e)

    def _heartbeat_tick(self):
        if not self._session_up or self._session is None:
            return
        try:
            if _mono() - self._last_tx_mono >= 14:
                self._send_frame(_OP_HEARTBEAT,
                                 bytes([(self._handler >> 8) & 0xFF, self._handler & 0xFF]))
        finally:
            self._schedule_heartbeat()

    # --------------------------------------------------------------
    # Command handlers (Set* / Update*)
    # --------------------------------------------------------------

    def SetMatrixTieCommand(self, value, qualifier):
        inp = int(qualifier.get('Input', 0))
        out = int(qualifier.get('Output', 0))
        tie = qualifier.get('Tie Type', 'Audio/Video')
        if not (1 <= out <= 8):
            if self.Debug:
                print('MatrixTie: invalid Output=%d' % out)
            return
        if not (0 <= inp <= 8):
            if self.Debug:
                print('MatrixTie: invalid Input=%d (0 = disconnect)' % inp)
            return
        if self.Debug:
            print('MatrixTie input=%d output=%d tie=%s' % (inp, out, tie))
        full = _route_write_payload(out, inp)
        self._send_data_payload(full)
        self._output_route[out] = inp

    def UpdateOutputTieStatus(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        return self._output_route.get(out)

    def UpdateInputTieStatus(self, value, qualifier):
        inp = int(qualifier.get('Input', 1))
        for o, i in self._output_route.items():
            if i == inp:
                return o
        return None

    def SetComPortSendString(self, value, qualifier):
        """Write `value` to RMC[Output].ComPort[1].StringInput over our session.

        Byte-exact slot path per finding 24 confirmed live loopback echo:
          [0x20][OutputSlot][len][0x20][0x01][len2][0x15][0x00][0x01][0x00] + value
        """
        out = int(qualifier.get('Output', 1))
        if not 1 <= out <= 8:
            if self.Debug:
                print('SetComPortSendString: invalid Output=%d' % out)
            return
        if isinstance(value, str):
            payload = value.encode('latin-1', errors='replace')
        else:
            payload = bytes(value)
        leaf = _serial15_leaf(join=1, flags=0, payload=payload)
        full = _rmc_output_container(out, leaf)
        self._send_data_payload(full)

    def UpdateComPortReceivedString(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        last = self._comport_last_rx.get(out)
        if last is not None:
            return last

    def SetIRPulse(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        code = qualifier.get('IR Code', 0)
        if self.Debug:
            print('IRPulse output=%d code=%s - Phase 3 slot path TBD' % (out, code))
        # Phase 3 TODO: construct IR leaf per discovered slot path

    def SetRelayClose(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        if self.Debug:
            print('RelayClose output=%d - Phase 3 slot path TBD' % out)
        # Phase 3 TODO: construct digital leaf (0x00) ON for this output's relay

    def SetRelayOpen(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        if self.Debug:
            print('RelayOpen output=%d - Phase 3 slot path TBD' % out)

    def UpdateRelayStatus(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        return 'Closed' if self._relay_state.get(out, False) else 'Open'

    def UpdateInputOnlineStatus(self, value, qualifier):
        inp = int(qualifier.get('Input', 1))
        return 'Online' if self._input_online.get(inp, False) else 'Offline'

    def UpdateOutputOnlineStatus(self, value, qualifier):
        out = int(qualifier.get('Output', 1))
        return 'Online' if self._output_online.get(out, False) else 'Offline'

    def UpdateSystemPowerStatus(self, value, qualifier):
        return 'On' if self._session_up else 'Unknown'

    def UpdateChassisProgrammedIP(self, value, qualifier):
        # Return the IP of the connected chassis if any
        return getattr(self._session, 'IPAddress', '') if self._session else ''

    def UpdateConnectionStatus(self, value, qualifier):
        return 'Connected' if self._session_up else 'Disconnected'

    def UpdateFirmware(self, value, qualifier):
        pass

    def UpdateMACAddress(self, value, qualifier):
        pass

    def UpdateSerialNumber(self, value, qualifier):
        pass

    def UpdateHDCPInputStatus(self, value, qualifier):
        pass

    def UpdateHDCPOutputStatus(self, value, qualifier):
        pass

    def UpdateOutputResolution(self, value, qualifier):
        pass

    def UpdateInputSignalStatus(self, value, qualifier):
        pass

    # --------------------------------------------------------------
    # Internal: send a DATA frame carrying a Cresnet payload
    # --------------------------------------------------------------

    def _send_data_payload(self, cresnet_payload):
        if not self._session_up:
            if self.Debug:
                print('DM-MD master: session not up, dropping %d B send' % len(cresnet_payload))
            return
        body = bytes([(self._handler >> 8) & 0xFF, self._handler & 0xFF,
                      len(cresnet_payload)]) + cresnet_payload
        self._send_frame(_OP_DATA, body)

    def _NullReceiveData(self, interface, data):
        """Not used in server mode (ReceiveData is bound per-client via
        the server's own ReceiveData callback)."""
        pass


# ------------------------------------------------------------------
# Monotonic time shim (ControlScript doesn't always expose time.monotonic)
# ------------------------------------------------------------------

def _mono():
    try:
        import time
        if hasattr(time, 'monotonic'):
            return time.monotonic()
        return time.time()
    except Exception:
        return 0.0
