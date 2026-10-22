# PROTO_TLDM master-side proprietary-peer protocol - byte-level spec

## TL;DR for the parent

The TCP speaker is NOT the TLDM ARM daemon. It is a managed .NET
assembly PROTO_TLDM.dll (dotfuscated) with cleaner .NET Standard twin
ProtoTldm.dll. The actual client-side session class
`TCPGatewayClient` lives in PROTO_TCP.dll / ProtoTcp.dll
alongside all the message classes.

**Everything needed to implement the master-side protocol in Python
is in the managed decompile. No ARM disassembly needed.**

Protocol summary:

- Port: 41794 (CIP_PORT in ProtoEngine_dotnet:1801, also
  default of CrestronCIPPort property).
- Clear TCP; **no SSL/auth required** on a baseline connect. SSL only
  if isSSLEnabled && Username && Password. Auth challenge handled
  via opcodes 11/12 (optional path).
- **3-byte frame header** on every message: `[MsgType:u8]
  [MsgLength:u16 BE] [body:MsgLength bytes]`. All multi-byte integers
  are **big-endian** (Endian.SwapInt16, (x >> 8) & 0xFF; x & 0xFF).
- Master is the TCP CLIENT, chassis is the TCP SERVER.

Handshake order (observed in
ProtoTcp.decompiled.cs:8288..8469 dispatcher and
:8810..9050 connect thread, plus
:979 program-ready handler):

1. Master opens TCP chassis_ip:41794.
2. Chassis sends GATEWAY_PROGRAM_READY_MSG (opcode 15):
   `[0F][00][01][Status]`. Status: 0=loading, 1=no program, 2=ready.
3. On Status==2, master sends GATEWAY_ALTERNATE_CONNECT_MSG
   (opcode 10) with Mode=64, Flags=2, Type=capability-bits.
4. Chassis sends GATEWAY_CONNECT_RESPONSE_MSG (opcode 2).
   - If Mode == 0 or Mode & 0x40: SUCCESS (0x40 = also needs auth).
   - Handler (short, BE) is the session handle. **Save this.**
   - On Mode & 0x40: master sends GATEWAY_AUTHENTICATE_MSG (op 11)
     with ASCII `[domain\]user:password` as body; chassis responds
     with opcode 12 to accept/reject.
5. Steady state: master sends GATEWAY_DATA_MSG (opcode 5) with
   Handler + Cresnet payload (finding-12 L3 bytes). Chassis sends
   same opcode back for RX data; same HandleIncomingPacketsFromTLDM
   path.
6. Heartbeat every m_iMaxCIPDataIdleTimeInMs of idle:
   GATEWAY_HEARTBEAT_MSG (opcode 13):
   `[0D][00][02][Handler_BE]`. Chassis replies opcode 14 same shape.

## Opcode table (EGatewayMessageTypes, ProtoEngine_dotnet:2062)

| Opcode | Name                                     | Direction | Notes |
|-------:|------------------------------------------|-----------|-------|
| 0      | eDUMMY                                   | -         | |
| 1      | eCONNECT                                 | master->  | legacy connect; master uses alternate-connect |
| 2      | eCONNECT_RESPONSE                        | chassis-> | ACK to alternate-connect |
| 3      | eDISCONNECT                              | both      | request to close |
| 4      | eDISCONNECT_RESPONSE                     | both      | |
| **5**  | **eDATA**                                | **both**  | **payload-carrying frame, wraps Cresnet packet** |
| 6      | eSERVER_PERSISTENCE                      | -         | |
| 7      | eDATA_STATUS                             | -         | |
| 8      | eBUFFER_THRESHOLD                        | -         | |
| 9      | eBUFFER_SIZE_REQUEST                     | -         | |
| **10** | **eALTERNATE_CONNECT**                   | master->  | **what master sends to establish session** |
| 11     | eAUTHENTICATE                            | master->  | ASCII creds |
| 12     | eAUTHENTICATE_RESPONSE                   | chassis-> | |
| **13** | **eHEARTBEAT**                           | both      | **keepalive** |
| **14** | **eHEARTBEAT_RESPONSE**                  | both      | **keepalive-ack** |
| **15** | **ePROGRAM_READY**                       | chassis-> | **first frame on connect** |
| 17     | ePRODIGY_CONNECT                         | -         | |
| 18     | eEXTENDED_LENGTH_DATA                    | both      | large-payload data (same role as 5) |
| 26-37  | various (CLOUD_SOCKET, FITC, EX_SERVICE) | -         | not needed for DM-MD |
| 38     | eDEVICEROUTER_CONNECT_REQUEST            | master->  | used for DEISC (DeviceIdType=21) not DM-MD |
| 39     | eDEVICEROUTER_CONNECT_RESPONSE           | chassis-> | DEISC-only |
| 40     | eTESPECIFIC_CLOUD_SOCKET_IDENTIFIER      | -         | |
| 42     | eDEVICE_ROUTER_LICENSE_RESPONSE          | -         | |

## Message bytes - every class we need

### GATEWAY_MESSAGE_HDR (ProtoEngine_dotnet:2305)

3 bytes on wire; the class has a 5-byte read for convenience
(Spare + PacketWithID are the first two body bytes, kept here just to
illustrate the wire layout for simple msgs).

    Byte 0:   MsgType       (u8)
    Byte 1-2: MsgLength     (u16, BIG-ENDIAN)
    Byte 3+:  body ...

Total wire size = MsgLength + 3.

Max MsgLength + 3 < 1200 and MsgType <= 40 per
ValidateIncomingData at ProtoTcp.decompiled.cs:7853.

### GATEWAY_PROGRAM_READY_MSG (opcode 15) - inbound

    [0F][00 01][Status]                            # 4 bytes total

Status: 0=LOADING_FIRMWARE, 1=NO_PROGRAM, 2=PROGRAM_READY. Act on
value 2 by sending alternate-connect.

### GATEWAY_ALTERNATE_CONNECT_MSG (opcode 10) - **master sends this**

(ProtoEngine_dotnet:2729)

    Offset Field          Size  Notes
    ------ -------------  ----  -----
    0      MsgType        1     = 0x0A
    1-2    MsgLength      2 BE  = 10 if HostName null, else 10+len(HostName)
    3-4    DestCID        2 BE  our master CIP_ID (e.g. 0x0001 for IPID 1)
    5-6    PortNumber     2 BE  typically 0
    7      Mode           1     = 0x40 per observed Crestron master
    8      Flags          1     = 0x02 per observed Crestron master
    9-10   TimeOut        2 BE  = 0
    11-12  Type           2 BE  capability bits:
                                base       0x0200
                                +ExtLen    0x0200|0xC000|0x1000 = 0xD200
                                +NewRCB    0xD200|0x0400         = 0xD600
    13+    HostName       var   optional ASCII, no NUL-termination

Minimal wire bytes for a baseline connect (no HostName, no caps):

    0A 00 0A  00 01  00 00  40 02  00 00  02 00
    ^type ^len=10 ^cid=1 ^port=0 ^M ^F ^to=0 ^type=0x0200

Then masterLen = 10 + 3 = 13 bytes. Verified: array[0..12] from
ConvertMessageToByteArray is 13 bytes.

### GATEWAY_CONNECT_RESPONSE_MSG (opcode 2) - **chassis responds**

(ProtoEngine_dotnet:2441)

    Offset Field    Size  Notes
    ------ -------  ----  -----
    0      MsgType  1     = 0x02
    1-2    Length   2 BE  = 3 (if no flags byte) or 4 (with flags)
    3-4    Handler  2 BE  session handle - save this verbatim
    5      Mode     1     & 0x20 = chassis-supports-hb-response-check
                          & 0x40 = chassis-requires-auth (then send op 11)
                          Mode & 0xDF == 0: SUCCESS
                          Mode == 3: disconnected / error
    6      Flags    1     (if Length==4):
                          & 0x04 = LooneyCodeSupport
                          & 0x08 = ExtendedLengthPacketSupport (then shift
                                   >>4 gives max-pkt-size code 1-3)
                          & 0x80 = NewRCBMechanism

### GATEWAY_HEARTBEAT_MSG (opcode 13) - **both directions**

(ProtoEngine_dotnet:3624)

    [0D][00 02][Handler_BE]                       # 5 bytes

### GATEWAY_HEARTBEAT_RESPONSE_MSG (opcode 14)

(ProtoEngine_dotnet:3676) - same shape, type = 0x0E.

### GATEWAY_DATA_MSG (opcode 5) - **payload frame**

(ProtoEngine_dotnet:2634)

Outbound (master sends Cresnet packet to chassis), as constructed by
TCPGatewayClient.HandleIncomingPacketsFromTLDM
(ProtoTcp.decompiled.cs:9065..9115):

    Offset Field              Size   Value
    ------ ----------------  -----   -----
    0      MsgType            1      = 0x05
    1-2    MsgLength          2 BE   = cresnet_len + 3 (where
                                       cresnet_len = pCresnetPacket[0])
    3-4    Handler            2 BE   session handle (from CONNECT_RESPONSE)
    5      CresnetPacketLen   1      = pCresnetPacket[0]  (first byte of
                                       the Cresnet payload == payload length)
    6+     CresnetPayload     var    = pCresnetPacket[1..CresnetPacketLen+1]
                                       - this is the finding-12 L3 bytes

Inbound (chassis sends RX data to master, same shape).

### GATEWAY_AUTHENTICATE_MSG (opcode 11) - optional

(ProtoEngine_dotnet:3499)

    [0B][MsgLen_BE][Handler_BE][ASCII of domain\user:password or user:password]

Only sent if the chassis's connect-response Mode had 0x40 set. For
unauth deployments, skip entirely.

### GATEWAY_AUTH_RESPONSE_MSG (opcode 12)

(ProtoEngine_dotnet:3566)

    [0C][00 03][Handler_BE][Mode]
    Mode == 0 means FAILED (close socket). Non-zero = authenticated.

### DEVICEROUTER_CONNECT_MESSAGE (opcode 38) - DEISC path only

Not needed for DM-MD-CPU3. For completeness: 211-byte base body with
CIP_ID, Mode, Type, ExtraFlags, MAC(6), Make(50), Model(50),
ProgramInstanceId(32), Hostname(64), optional auth. See
ProtoEngine_dotnet:2833.

## Where everything lives

Verified references, use for implementation and debugging:

| What                                           | File                                        | Line |
|------------------------------------------------|---------------------------------------------|------|
| CIP_PORT = 41794                               | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 1801 |
| EGatewayMessageTypes enum                      | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2062 |
| GATEWAY_MESSAGE_HDR                            | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2305 |
| GATEWAY_CONNECT_RESPONSE_MSG                   | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2441 |
| GATEWAY_DATA_MSG                               | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2634 |
| GATEWAY_ALTERNATE_CONNECT_MSG                  | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2729 |
| DEVICEROUTER_CONNECT_MESSAGE                   | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 2833 |
| DEVICEROUTER_CONNECT_RESPONSE_MSG              | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3108 |
| GATEWAY_AUTHENTICATE_MSG                       | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3499 |
| GATEWAY_AUTH_RESPONSE_MSG                      | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3566 |
| GATEWAY_HEARTBEAT_MSG                          | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3624 |
| GATEWAY_HEARTBEAT_RESPONSE_MSG                 | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3676 |
| GATEWAY_PROGRAM_READY_MSG                      | ProtoEngine_dotnet/ProtoEngine.decompiled.cs | 3728 |
| TCPGatewayClient class                         | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 7720 |
| ValidateIncomingData (framing rule)            | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 7853 |
| HandleEthernetGatewayClientConnectResponseMsg  | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8042 |
| HandleEthernetGatewayClientDataMessage         | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8208 |
| ProcessIncomingTCPGatewayClientData dispatcher | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8288 |
| SendDeviceRouterConnectRequestMessage          | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8473 |
| SendTCPGatewayClientMessage (generic sender)   | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8517 |
| GatewayClientConnectThreadFunction             | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8810 |
| HandleEthernetGatewayClientProgramReadyResponseMessage | ProtoTcp_dotnet/ProtoTcp.decompiled.cs | 8678 |
| HandleEthernetGatewayClientHeartBeatMessage    | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 8678+ |
| HandleIncomingPacketsFromTLDM (outbound DATA)  | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 9065 |
| SendHeartbeatMessageToMaster (triggers hb)     | ProtoTcp_dotnet/ProtoTcp.decompiled.cs       | 9191 |

The dotfuscated PROTO_TCP.decompiled.cs and PROTO_ENGINE.decompiled.cs
contain the exact same classes (same byte layouts, same opcodes); use
them as a sanity cross-check if any method body reads oddly in the
.NET Standard twin.

## Minimal Python state machine (what the prototype must do)

    1. open TCP to chassis:41794
    2. read 4-byte frame -> expect opcode 0x0F GATEWAY_PROGRAM_READY_MSG
       - if Status != 2: wait or retry on timer; keep reading
    3. send bytes 0A 00 0A 00 <CID_HI> <CID_LO> 00 00 40 02 00 00 02 00
       (13 bytes - ALTERNATE_CONNECT, DestCID = our chosen master id)
    4. read 3-byte header -> expect opcode 0x02, read Length bytes body
       - parse Handler (2 BE), Mode byte, Flags byte
       - if Mode & 0x40: send AUTHENTICATE frame; read AUTH_RESPONSE
       - if Mode & 0xDF == 0: connected. keep Handler.
    5. steady state receive loop: dispatch by MsgType
       - 0x05/0x12 eDATA / eEXTENDED_LENGTH_DATA: parse Handler, extract
         Cresnet payload (starts at offset 5, prefixed by its own 1-byte
         length byte), feed to cresnet_cip.py decoder
       - 0x0D eHEARTBEAT: respond with 0x0E GATEWAY_HEARTBEAT_RESPONSE
         carrying same Handler
       - 0x0E eHEARTBEAT_RESPONSE: decrement UnAckHeartBeatMsgCount
       - 0x03 eDISCONNECT: send 0x04 eDISCONNECT_RESPONSE, close
    6. heartbeat send: every ~15s of idle, send 0x0D GATEWAY_HEARTBEAT_MSG
       with Handler
    7. send data: wrap finding-12 L3 Cresnet payload bytes in
       GATEWAY_DATA_MSG opcode 5 with Handler

## No cryptography

Verified: no AES, SHA, HMAC, SSL/TLS, cert, nonce, token in the
baseline (non-SSL) path. The only auth path is ASCII user:password
over clear TCP, triggered only if chassis responds with
CONNECT_RESPONSE.Mode & 0x40. Our chassis in testing didn't require
this (CIP IPID 1 masquerade already worked on :41794).

## Framing invariants to enforce

From ValidateIncomingData at ProtoTcp.decompiled.cs:7853:

- MsgLength + 3 < 1200
- MsgType <= 40

Frame-sync strategy: if either invariant fails, slide 1 byte, retry.
Same as managed implementation.

## Gaps for implementation (none blocking)

- MasterCID to use: pick any unique u16, e.g. 0x0001. The chassis
  recognizes it only as a session key; nothing on the chassis side
  compares it to a well-known registry.
- m_iMaxCIPDataIdleTimeInMs default: not seen in this harvest, but
  commonly 15000 ms in Crestron. Idle longer than this triggers a
  heartbeat; implementation can send one every ~15s regardless.
- The Cresnet payload semantics (finding 12) are unchanged - the
  outer gateway frame just carries them opaquely.
