# Copyright 2026 - DM-MD CPU3/CPU4 unified driver (CTP commands + CIP feedback)
#
# Derived from the shape of extr_15_17578 (Extron DTP3 CP 42) by build_dm_md_unified.py.
# The donor's matrix command surface is kept intact; this module reimplements its
# Write/Read methods to speak Crestron DM:
#   - COMMANDS go out as CTP text on TCP :41795 (chassis side)
#   - FEEDBACK comes in as CIP push on TCP :41794 as IPID 1 (XPanel masquerade)
#
# Both transports run in parallel: CTP is a short-lived request/response per command,
# CIP is a long-lived subscription that keeps route and online-state caches warm.
#
# Scope: routing only. DM endpoint RS-232/IR/Relay is firmware-locked on the chassis;
# see evidence/13 in the extron-driver-convert research branch.

from extronlib.interface import EthernetClientInterface
from extronlib.system import Wait, ProgramLog


_CIP_IPID = 1  # chassis's stock-XPanel slot; non-destructive when the real XPanel is offline
_CTP_PORT = 41795
_CIP_PORT = 41794


# Analog join numbers (zero-based wire form minus 1 = one-based public) that the OEM
# chassis publishes for input / output online state. Pinned in evidence/09.
_INPUT_ONLINE_JOINS  = {1: 5000, 2: 5002, 3: 5004, 4: 5006, 5: 5008, 6: 5010, 7: 5012, 8: 5014}
_OUTPUT_ONLINE_JOINS = {1: 7000, 2: 7004, 3: 7008, 4: 7012, 5: 7016, 6: 7020, 7: 7024, 8: 7028}


class extr_15_17578(object):
    """DM-MD CPU3/CPU4 matrix driver, unified CTP + CIP.

    Keeps the DTP3 CP 42 class name and command surface so the asset-graph in the
    donor .pkp is byte-identical to its original (apart from strings we rename).
    """

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 1.5
        self.Subscription = {}
        self.ReceiveData = self._ReceiveData
        self._receiveBuffer = b''
        self._maxBufferSize = 4096
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None

        # ---- CTP (command) transport state ----
        self._ctp_client = None   # EthernetClientInterface
        self._ctp_rxbuf = b''
        self._ctp_last_cmd = None

        # ---- CIP (feedback) transport state ----
        self._cip_client = None
        self._cip_rxbuf = bytearray()
        self._cip_registered = False
        self._cip_ready = False
        self._cip_digitals = {}
        self._cip_analogs = {}
        self._cip_serials = {}

        self.Commands = {
            'ConnectionStatus':         {'Status': {}},
            'MatrixTieCommand':         {'Parameters': ['Input', 'Output', 'Tie Type'],  'Status': {}},
            'OutputTieStatus':          {'Parameters': ['Output', 'Tie Type'],           'Status': {}},
            'InputTieStatus':           {'Parameters': ['Input', 'Output'],              'Status': {}},
            'InputSignalStatus':        {'Parameters': ['Input'],                        'Status': {}},
            'RefreshMatrix':            {'Parameters': [],                               'Status': {}},
            'InputOnlineStatus':        {'Parameters': ['Input'],                        'Status': {}},
            'OutputOnlineStatus':       {'Parameters': ['Output'],                       'Status': {}},
            'SystemPowerStatus':        {'Status': {}},
            'ChassisProgrammedIP':      {'Status': {}},
        }

    # ======================================================================
    # Lifecycle / connection management
    # ======================================================================

    def Initialize(self):
        self._ctp_ensure()
        self._cip_ensure()

    # ---- CTP ----

    def _ctp_ensure(self):
        if self._ctp_client is not None:
            return
        try:
            host = self.IPAddress
        except AttributeError:
            host = '192.168.6.14'
        c = EthernetClientInterface(host, _CTP_PORT, Protocol='TCP')
        c.Connected    = self._ctp_on_connected
        c.Disconnected = self._ctp_on_disconnected
        c.ReceiveData  = self._ctp_on_data
        self._ctp_client = c
        try: c.Connect(timeout=5)
        except Exception as e:
            ProgramLog('[dm-ctp] connect failed: %s' % e, 'warning')
            Wait(5, self._ctp_reconnect)

    def _ctp_reconnect(self):
        self._ctp_client = None
        self._ctp_ensure()

    def _ctp_on_connected(self, iface, state):
        ProgramLog('[dm-ctp] connected', 'info')

    def _ctp_on_disconnected(self, iface, state):
        ProgramLog('[dm-ctp] disconnected', 'info')
        self._ctp_client = None
        Wait(5, self._ctp_ensure)

    def _ctp_on_data(self, iface, data):
        self._ctp_rxbuf += data
        if b'\n' in self._ctp_rxbuf and self.Debug:
            try: ProgramLog('[dm-ctp] RX: %r' % self._ctp_rxbuf[:200], 'debug')
            except Exception: pass
            self._ctp_rxbuf = b''

    def _ctp_send(self, line):
        if self._ctp_client is None:
            self._ctp_ensure()
            return False
        try:
            self._ctp_client.Send((line + '\r\n').encode('ascii'))
            self._ctp_last_cmd = line
            return True
        except Exception as e:
            ProgramLog('[dm-ctp] send error: %s' % e, 'warning')
            return False

    # ---- CIP ----

    def _cip_ensure(self):
        if self._cip_client is not None:
            return
        try:
            host = self.IPAddress
        except AttributeError:
            host = '192.168.6.14'
        c = EthernetClientInterface(host, _CIP_PORT, Protocol='TCP')
        c.Connected    = self._cip_on_connected
        c.Disconnected = self._cip_on_disconnected
        c.ReceiveData  = self._cip_on_data
        self._cip_client = c
        try: c.Connect(timeout=5)
        except Exception as e:
            ProgramLog('[dm-cip] connect failed: %s' % e, 'warning')
            Wait(5, self._cip_reconnect)

    def _cip_reconnect(self):
        self._cip_client = None
        self._cip_registered = False
        self._cip_ready = False
        self._cip_ensure()

    def _cip_on_connected(self, iface, state):
        ProgramLog('[dm-cip] connected', 'info')
        self._cip_rxbuf = bytearray()
        self._cip_registered = False
        self._cip_ready = False

    def _cip_on_disconnected(self, iface, state):
        ProgramLog('[dm-cip] disconnected', 'info')
        self._cip_client = None
        self._cip_registered = False
        self._cip_ready = False
        Wait(5, self._cip_ensure)

    def _cip_send(self, b):
        if self._cip_client is None: return
        try: self._cip_client.Send(bytes(b))
        except Exception as e: ProgramLog('[dm-cip] send error: %s' % e, 'warning')

    def _cip_build_register(self, ipid):
        return bytes([0x01, 0x00, 0x0B,
                      0x00, 0x00, 0x00, 0x00, 0x00,
                      ipid,
                      0x40, 0xFF, 0xFF, 0xF1, 0x01])

    _OP_PROGRAM_READY = 0x0F
    _OP_REGISTER      = 0x01
    _OP_REG_RESULT    = 0x02
    _OP_DATA          = 0x05
    _OP_SERIAL        = 0x12
    _OP_HEARTBEAT     = 0x0D
    _REG_SUCCESS      = b'\x00\x00\x00\x1f'
    _UPDATE_REQUEST   = bytes([0x05, 0x00, 0x05, 0x00, 0x00, 0x02, 0x03, 0x00])
    _END_OF_QUERY_ACK = bytes([0x05, 0x00, 0x05, 0x00, 0x00, 0x02, 0x03, 0x1D])
    _HEARTBEAT_PKT    = bytes([0x0D, 0x00, 0x02, 0x00, 0x00])

    def _cip_on_data(self, iface, data):
        self._cip_rxbuf.extend(data)
        while len(self._cip_rxbuf) >= 3:
            op = self._cip_rxbuf[0]
            plen = (self._cip_rxbuf[1] << 8) | self._cip_rxbuf[2]
            if len(self._cip_rxbuf) < 3 + plen:
                break
            payload = bytes(self._cip_rxbuf[3:3 + plen])
            del self._cip_rxbuf[:3 + plen]
            self._cip_handle(op, payload)

    def _cip_handle(self, op, payload):
        if op == self._OP_PROGRAM_READY:
            self._cip_send(self._cip_build_register(_CIP_IPID))
            return
        if op == self._OP_REG_RESULT:
            if payload == self._REG_SUCCESS:
                self._cip_registered = True
                self._cip_send(self._UPDATE_REQUEST)
            return
        if op == self._OP_HEARTBEAT:
            self._cip_send(self._HEARTBEAT_PKT)
            return
        if op == self._OP_SERIAL:
            if len(payload) >= 8 and payload[4] == 0x34:
                join = ((payload[5] << 8) | payload[6]) + 1
                self._cip_serials[join] = bytes(payload[8:])
            return
        if op == self._OP_DATA:
            if len(payload) >= 5 and payload[0:4] == b'\x00\x00\x02\x03' and payload[4] == 0x1C:
                self._cip_send(self._END_OF_QUERY_ACK)
                self._cip_send(self._HEARTBEAT_PKT)
                self._cip_ready = True
                return
            if len(payload) >= 6 and payload[0:3] == b'\x00\x00\x03':
                ll, hh = payload[4], payload[5]
                join = (((hh & 0x7F) << 8) | ll) + 1
                state = ((hh & 0x80) >> 7) ^ 0x01
                self._cip_digitals[join] = state
                return
            if len(payload) >= 8 and payload[0:4] == b'\x00\x00\x05\x14':
                join  = ((payload[4] << 8) | payload[5]) + 1
                value = (payload[6] << 8)  | payload[7]
                self._cip_analogs[join] = value
                return

    # Legacy connection-helper method the BaseDriver may call
    def _ReceiveData(self, interface, data):
        # Delegate to whichever transport the interface belongs to
        if interface is self._ctp_client:
            self._ctp_on_data(interface, data)
        elif interface is self._cip_client:
            self._cip_on_data(interface, data)

    # ======================================================================
    # Command surface - matches the DTP3 CP 42 donor's method names
    # ======================================================================

    def WriteMatrixTieCommand(self, value, qualifier, context):
        """Routing command. qualifier = {'Input': int, 'Output': int, 'Tie Type': 'Video' | 'Audio' | 'Audio/Video'}."""
        self._ctp_ensure()
        i = int(qualifier.get('Input', 0))
        o = int(qualifier.get('Output', 1))
        tie = qualifier.get('Tie Type', 'Audio/Video')
        slot = 100 + o  # chassis internal: outputs 101..108
        if tie == 'Video':
            self._ctp_send('SETVIDEOROUTE %d %d' % (i, slot))
        elif tie == 'Audio':
            self._ctp_send('SETAUDIOROUTE %d %d' % (i, slot))
        else:
            self._ctp_send('SETAVROUTE %d %d' % (i, slot))

    def ReadOutputTieStatus(self, qualifier, context):
        """Feedback: current input routed to a given output."""
        # Route feedback via CIP isn't currently implemented - the OEM program's
        # routing joins aren't published to IPID 1 (see evidence/08-10). Return
        # None until a Phase 2 drive-and-diff experiment pins them.
        return None

    def WriteOutputTieStatus(self, value, qualifier, context):
        return None

    def ReadInputTieStatus(self, qualifier, context):
        return None

    def WriteInputTieStatus(self, value, qualifier, context):
        return None

    def ReadInputSignalStatus(self, qualifier, context):
        """Input signal detection: use the input online analog as a proxy."""
        self._cip_ensure()
        i = int(qualifier.get('Input', 1))
        j = _INPUT_ONLINE_JOINS.get(i)
        if j is None: return None
        v = self._cip_analogs.get(j)
        return "Signal Detected" if v == 2 else ("No Signal" if v == 1 else None)

    def WriteInputSignalStatus(self, value, qualifier, context):
        return None

    def WriteRefreshMatrix(self, value, qualifier, context):
        """Request a full state refresh. Resends the CIP update-request + polls CTP."""
        self._cip_send(self._UPDATE_REQUEST)
        self._ctp_send('DUMPDMROUTEINFO')

    def ReadRefreshMatrix(self, qualifier, context):
        return None

    def ReadConnectionStatus(self, qualifier, context):
        """Framework answers this - we track our own state."""
        ctp_ok = self._ctp_client is not None
        cip_ok = self._cip_client is not None and self._cip_ready
        return "Connected" if (ctp_ok and cip_ok) else "Disconnected"

    # ---- DM-specific feedback ----

    def ReadInputOnlineStatus(self, qualifier, context):
        self._cip_ensure()
        i = int(qualifier.get('Input', 1))
        j = _INPUT_ONLINE_JOINS.get(i)
        if j is None: return None
        v = self._cip_analogs.get(j)
        return "Online" if v == 2 else ("Offline" if v == 1 else None)

    def WriteInputOnlineStatus(self, value, qualifier, context):
        return None

    def ReadOutputOnlineStatus(self, qualifier, context):
        self._cip_ensure()
        o = int(qualifier.get('Output', 1))
        j = _OUTPUT_ONLINE_JOINS.get(o)
        if j is None: return None
        v = self._cip_analogs.get(j)
        return "Online" if v == 2 else ("Offline" if v == 1 else None)

    def WriteOutputOnlineStatus(self, value, qualifier, context):
        return None

    def ReadSystemPowerStatus(self, qualifier, context):
        self._cip_ensure()
        v = self._cip_serials.get(3000)
        return v.decode('ascii', errors='replace') if v else None

    def WriteSystemPowerStatus(self, value, qualifier, context):
        return None

    def ReadChassisProgrammedIP(self, qualifier, context):
        self._cip_ensure()
        v = self._cip_serials.get(3002)
        return v.decode('ascii', errors='replace') if v else None

    def WriteChassisProgrammedIP(self, value, qualifier, context):
        return None
