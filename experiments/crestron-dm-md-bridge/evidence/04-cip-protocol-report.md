# Extron IPL Pro CIP-Masquerade Driver — Implementation Brief

## Executive summary

Yes, this is buildable. An Extron IPL Pro (ControlScript Pro 3.13.39, Python 3.5) can masquerade as a Crestron XPanel against the DM-MD8X8-CPU3-RPS by opening a plain TCP connection to the chassis on port 41794, speaking the reverse-engineered CIP (Crestron Internet Protocol) wire format, and registering with an IP-ID that is already declared in the running SIMPL program. The user's working XPanel is the single most important piece of evidence we have: it confirms the chassis has a SIMPL program loaded, that the program instantiates an XPanel-family symbol, that the IP table has at least one usable IP-ID, and that CIP on 41794 is open on the network path. The driver is a plain async bytes-in / bytes-out state machine — EthernetClientInterface, a `Connected` event handler for the handshake, a `ReceiveData` handler that reassembles length-prefixed frames out of 1024-byte chunks, a `Timer` for the 15-second heartbeat, and GCP-dispatched `Set<Command>` methods that emit CIP digital/analog/serial frames. The three big risks are: (1) the running SIMPL program may use Smart Object (0x38/0x39) envelopes for the matrix tiles, which must be decoded before the single-join decoder runs or every array item collapses to join 1; (2) the exact Join→Matrix-operation mapping is unknown until we read the live `.smw`/`.sgd` or packet-capture the working XPanel; (3) IP-ID collision behavior on this firmware is folklore, not spec, so we need an unused slot or empirical confirmation that concurrent registration works.

## CIP wire protocol

**Framing.** Every CIP frame on 41794 (and TLS-wrapped 41796) is a 3-byte header followed by payload:

```
[type:1][length:2 big-endian][payload: length bytes]
```

`length` counts the payload only, not the 3-byte header. The 16-bit length is unambiguously big-endian: in every documented sample frame the field equals the number of bytes that follow (a little-endian read of `00 0A` as 2560 does not fit the 10-byte observed payload). Confirmed against Crestron's Toolbox help, SHOWRUNNER wiki, the SANS port registry, the independent Ruby `cresip` gem, and four open-source clients (klenae, artnavsegda, rdriscoll, pycrestron-cip).

**Handshake (step by step, actual bytes with IP-ID 0x03 shown as the example).**

```
S<- 0F 00 01 02   -- processor's 'program ready' frame. 0x02 trailing byte is
                     undocumented; both 0F 00 00 (zero payload) and 0F 00 01 XX
                     forms are seen in the wild. Ignore the payload content.

S-> 01 00 0B 00 00 00 00 00 03 40 FF FF F1 01
                  -- 14-byte registration. Payload length 0x000B.
                     Offset 8 (payload offset 5) carries the IP-ID.
                     Trailing 40 FF FF F1 01 are opaque signature bytes.

S<- 02 00 04 00 00 00 1F   -- registration accepted (success)
                              OR
    02 00 03 FF FF 02      -- 'IPID not defined in the running program'

S-> 05 00 05 00 00 02 03 00   -- update request (please dump all non-default joins)

S<- 05 00 06 00 00 03 00 LL HH            -- stream of digital joins
S<- 05 00 08 00 00 05 14 JH JL VH VL      -- stream of analog joins
S<- 12 00 LL 00 00 00 IL 34 JH JL FF ...  -- stream of serial joins
    ... (optionally 0x38/0x39 Smart Object envelopes) ...
S<- 05 00 05 00 00 02 03 1C   -- end-of-query marker

S-> 05 00 05 00 00 02 03 1D   -- end-of-query ack
S-> 0D 00 02 00 00            -- first heartbeat; now every 15 s
```

From here on both sides exchange join frames symmetrically; a client write and a feedback update use the same byte layout, so one encoder/decoder pair serves both directions.

**Three outbound/inbound join frame families.**

*Digital* — frame type `0x05`, sub-type `0x00` (latched) or `0x27` (button-style, auto-release on disconnect):
```
05 00 06 00 00 03 TT LL HH
```
where `TT ∈ {0x00, 0x27}`, `LL = (join-1) & 0xFF`, and `HH = ((join-1) >> 8) & 0x7F` with bit 7 of `HH` set when the join is INACTIVE/released. The join number is **byte-swapped on the wire** — this is unique to digital frames. Example: pulse digital join 100 ⇒ press `05 00 06 00 00 03 27 63 00`, release `05 00 06 00 00 03 27 63 80`.

*Analog* — frame type `0x05`, sub-type `0x14`:
```
05 00 08 00 00 05 14 JH JL VH VL
```
`JH:JL = join-1` as big-endian uint16, `VH:VL = value` 0..65535. No byte-swap. Example: analog join 200 to value 32768 ⇒ `05 00 08 00 00 05 14 00 C7 80 00`.

*Serial (long form, strings ≥7 chars)* — frame type `0x12`:
```
12 LH LL 00 00 00 IL 34 JH JL FF <text-bytes>
```
`LH:LL` = outer payload length = `strlen+8`, `IL` = inner length = `strlen+4`, `0x34` is the serial marker, `JH:JL = join-1`, `FF` is a flags byte (0x03 for ASCII start+end; 0x07 for UTF-16LE). Short strings (<7 chars) may ride inside an `0x05` frame with sub-type `0x15`.

**Feedback frames** have the same layouts — there is no direction bit. The sub-type at `payload[3]` is the discriminator: `0x00` latched digital, `0x27` button digital, `0x14` analog, `0x15` serial short, `0x03` command (update sequence 0x00/0x16/0x1C/0x1D), `0x08` date/time, `0x38` Smart Object wrapper. Top-level `0x12` always carries serial-long.

**Smart Object envelopes (critical for the matrix).** XPanel 2.0 Smart Graphics projects — likely for DM-MD8X8 input/output tile grids — wrap analog arrays in `0x38` and serials in `0x39`:
```
Analog array (one frame carries many joins):
05 00 LL 00 00 LL' 38 00 00 00 01 LL'' 14 (JH JL VH VL)*

Smart-object serial:
12 00 <strlen+15> 00 00 00 <strlen+11> 39 00 00 00 <SO-id> 00 <strlen+4> 34 JH JL 03 <text>
```
Any decoder MUST check for `0x38`/`0x39` before applying the single-join decoders — otherwise a 16-element analog array (think: 16 outputs' current input numbers) gets misread as a single join update at offset 5. The Home-Assistant Crestron integration documents this exact bug as "the Music Player 3 problem."

**Keepalive.** Client sends `0D 00 02 00 00` every 15 s since its last TX; processor may answer with the same bytes or with `0E 00 02 00 00`. If the processor sends a `0x0D` ping, mirror it back as `0x0E`. Liveness timeout: ~35 s without receive → treat as dead.

**Disconnect / errors.** Processor-initiated close is `03 00 00`. Registration failure (`02 00 03 FF FF 02`) is permanent for that IP-ID until the SIMPL program is reloaded with a matching slot. Beyond those, TCP RST/FIN is the only other signal.

## Masquerade registration

**IP-ID selection.** The valid range is `0x03..0xFE` (252 slots total, per Crestron's 3-Series Reference Manual and the 4-Series API doc's explicit `MaxEntries: 0-252`). `0x00..0x02` and `0xFF` are reserved. The processor's IP table scopes entries to a program slot (1–10 on 3-Series). The driver cannot pick a slot it likes and expect to be accepted — the slot must already exist in the compiled SIMPL program (as an XPanel/XPanel 2.0 Smart Graphics/EISC symbol) or must be added at runtime by a console operator.

**How to find a free IP-ID on THIS chassis.** The user's working XPanel confirms the SIMPL program is loaded and declares at least one XPanel symbol. The two viable paths:

1. **Read the live IP table over SSH/Telnet to the chassis's Toolbox console** (port 22 or 23). Useful commands:
   ```
   IPTable                       -- list all slots
   ipt -P:all                    -- all program slots, verbose
   ipt -P:1                      -- just slot 1 (SIMPL is usually there)
   ipt -t -P:1                   -- detailed form with connection state
   who                           -- active CIP connections (shows XPanel's slot)
   progcomments                  -- program metadata
   HELP ADD*                     -- enumerate ADD* commands this firmware exposes
   ADDSlave ?                    -- the exact syntax (verify before use)
   ```
2. **Pull the compiled program via Toolbox > IP Table Setup > Load from Device** and save a `.dip` backup before any destructive command.

**Candidate ADDSlave syntax to try** (verify with `ADDSlave ?` first — the flag position and the `-P:` form are confirmed in Chief Integrations' wiki but not independently cross-checked against this exact firmware):
```
ADDSlave <IPID-hex> <IP-or-hostname> -P:<slot>
```
Example (adding the Extron processor at 192.168.1.42 as an XPanel-equivalent slave at IP-ID 05 in SIMPL slot 1):
```
ADDSlave 05 192.168.1.42 -P:1
ipt -P:1               -- verify
```
There is **no evidence that `ADDSTATION` exists** as a stock console command on 3-Series firmware. A specific program may expose it as a user-defined SIMPL# `CrestronConsole.AddNewConsoleCommand`, but assume it doesn't until `HELP ADD*` on the live chassis says otherwise.

**Address-based ACL.** If the XPanel-family symbol in the SIMPL program was placed with IP Net Address `0.0.0.0`, any client IP can register at that IP-ID. If it was placed with a specific address, only that source IP is accepted. The user's working XPanel implies at least one symbol accepts the XPanel PC's IP; whether the Extron's IP also fits is a per-symbol setting.

**Collision behavior.** Not officially specified. Field convention (and the Home-Assistant integration's documented testing on 3-Series firmware ≥1.5xx) is that a second registration on an in-use IP-ID is tolerated on modern 3-Series firmware — both clients hold and both receive the same feedback. On older firmware the second register may evict the first. The safe path: pick an IP-ID that is NOT the one the XPanel is using, by inspection of `ipt -P:all` and `who`. If the SIMPL program only declares one XPanel slot and no spare, the integrator must either add a second XPanel symbol to the program and recompile, or run `ADDSlave` to insert a slot (which does not survive a program reload).

**Secure CIP note.** Port 41796 is byte-identical CIP wrapped in TLS against the processor's self-signed cert. The `pycrestron-cip` reference turns it on by building an SSL context with `check_hostname=False; verify_mode=CERT_NONE`. If the chassis has `securegateway default` set and plain CIP is disabled, the Extron driver cannot speak it directly — Extron ControlScript's `EthernetClientInterface` supports no TLS beyond SSH, so the deployment either turns plain CIP back on or stands up a `scip2cip` bump-in-the-wire.

## Extracting the join map from the XPanel project file

The user needs to share the file; recipe branches by extension.

**Magic-byte probe first (always):**
```python
head = open(path, 'rb').read(8)
if head[:4] == b'PK\x03\x04': ...   # zip (.ch5z, maybe .cpz, maybe .vtz)
if head[:8] == bytes.fromhex('D0CF11E0A1B11AE1'): ...   # OLE2 CFB (likely .vtp)
if head[:1] == b'[':  ...           # INI-section plain text (.smw / .sgd)
```

**`.sgd` (SIMPL Graphics Definition) — most likely primary source.** Verified structure: CRLF plain text; each section is a line consisting of just `[`, several `key=value` lines, then a line consisting of just `]` (this is NOT standard INI — `configparser` will NOT parse it, a custom ~30-line reader is required). The first section is `ObjTp=FSgntr`/`Sgntr=SGD`. The companion `.vtp` filename appears exactly **once** in the top-level `ObjTp=Hd` header (`ProjectFile=panel.vtp`), not per Symbol. Each `ObjTp=Symbol` section carries `SmartObjId=<n>`, `Name=...`, and pin-indexed `InputCue{N}=<label>` + `InputSigType{N}=...` and `OutputCue{N}=<label>` + `OutputSigType{N}=...`. **Important correction:** the SigType enum is wider than "Digital|Analog|Serial" — real files contain the value `String` and literal composite values like `Digital|Analog|Serial|String` where the pipe is literal content, not an enum shorthand. The parser must treat SigType as free text, not as a strict enum.

```python
def parse_sgd(path):
    text = open(path, encoding='latin-1', errors='replace').read()
    sections, cur = [], None
    for raw in text.splitlines():
        line = raw.rstrip('\r')
        if line == '[':   cur = {}
        elif line == ']': 
            if cur is not None: sections.append(cur)
            cur = None
        elif cur is not None and '=' in line and not line.startswith(';'):
            k, _, v = line.partition('=')
            cur[k.strip()] = v.strip()
    return sections
```

**`.smw` (SIMPL Windows program).** Same INI-with-bracket-on-own-line format. First real section `ObjTp=FSgntr`/`Sgntr=SimplWindow`. Devices are `ObjTp=Dv` with `H=<handle>`, `Nm=<name>`, `DvC=<device-class-code>`, and child handles `C1..CN` pointing at symbols. Join numbers live inside symbol input/output objects referenced from devices — numeric joins are the labels in `.sgd` resolved via the handle graph.

**`.ch5z` (CH5 archive).** Zip containing one inner `.ch5` (also a zip) plus a manifest JSON. The signal contract lives at `config/contract.cse2j` (JSON). If no contract is present, scan HTML for `sendEventOn*` / `receiveState*` attributes and JS/TS for `CrComLib.subscribeState('b'|'n'|'s', join, cb)` / `publishEvent('b'|'n'|'s', join, value)` — `b`=digital, `n`=analog, `s`=serial.

**`.vtp` (VTPro-e project).** Third-party reports describe it as Microsoft Compound File (OLE2/CFB, magic `D0 CF 11 E0 A1 B1 1A E1`). Not independently verified against a real file. If `.vtp` is the only thing we get, prefer `olefile` to enumerate streams and look for the companion `.sgd` first. If the user instead has the compiled `.vtz` / `.c3p`, magic-byte probe before guessing — Crestron's own XPanel page notes that renaming an XPanel bundle lets it run on a PC, which hints `.vtz`/`.c3p` may share a container with `.ch5z` (unverified).

**Not Crestron:** `.c4z` is a Control4 driver archive; `.c4wp` has no public evidence as a Crestron format; `.cws` is not a Crestron extension in any source searched (likely conflated from a Reddit post or AI hallucination). Crestron Studio uses `.ct_system_x` and `.ct_core3_design`. If the user actually has one of those, we need a fresh look.

## Extron ControlScript implementation

Verified against the stub library (`EthernetClientInterface.__init__(Hostname, IPPort, Protocol='TCP', ServicePort=0, Credentials=None, bufferSize=4096)`), the Timer/Wait classes, and the GS corpus pattern. `struct` is in the stdlib and in use by 50+ production GS drivers — it is not on the disallowed list; `threading`, `socket`, `select`, `asyncio`, `logging`, `sys`, `os` are. Timer minimum interval is 0.1 s; `SendAndWait` cannot be called from inside `ReceiveData` and loses data when unsolicited traffic is possible, so the driver must be fully async. `Send(str)` applies UTF-8 encoding — CIP frames must be passed as `bytes` or any byte ≥0x80 is mangled.

```python
# cip_xpanel.py — lives inside the .pkp, Python 3.5
from extronlib.interface import EthernetClientInterface
from extronlib.system import Timer, Wait
from struct import pack, unpack

CIP_PORT      = 41794
HEARTBEAT_SEC = 15.0

class DeviceClass:
    def __init__(self):
        self.Unidirectional = 'False'
        self.Subscription   = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Digital':  {'Parameters': ['Join'], 'Status': {}},
            'Analog':   {'Parameters': ['Join'], 'Status': {}},
            'Pulse':    {'Parameters': ['Join'], 'Status': {}},
        }
        self._buf = bytearray()
        self._registered = False
        self._ready      = False
        self._hb         = None
        self._ipid       = 0x05           # set via GCP param; must match SIMPL symbol

        # GS template idiom: handlers are settable events on the mixin
        self.ReceiveData  = self._on_data
        self.Connected    = self._on_connect
        self.Disconnected = self._on_disconnect

    # ---- socket events (NOT the template's OnConnected — that's status bookkeeping) ----
    def _on_connect(self, interface, state):
        self._buf = bytearray()
        self._registered = False
        self._ready      = False
        # processor sends 0x0F first; we reply from _on_data when we see it.
        if self._hb is None:
            self._hb = Timer(HEARTBEAT_SEC, self._beat)
        else:
            self._hb.Restart()
        self.WriteStatus('ConnectionStatus', 'TCP-up')

    def _on_disconnect(self, interface, state):
        if self._hb is not None: self._hb.Stop()
        self._registered = self._ready = False
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        Wait(2.0, lambda: self.Connect(10))

    def _beat(self, timer, count):
        self.Send(b'\x0D\x00\x02\x00\x00')

    # ---- byte-level receive: 1024-byte max chunks, split at arbitrary boundaries ----
    def _on_data(self, interface, data):
        self._buf.extend(data)
        while len(self._buf) >= 3:
            plen = (self._buf[1] << 8) | self._buf[2]
            if len(self._buf) < 3 + plen: return
            ft, payload = self._buf[0], bytes(self._buf[3:3+plen])
            del self._buf[:3+plen]
            self._dispatch(ft, payload)

    def _dispatch(self, ft, payload):
        if ft == 0x0F:                                    # program ready
            self.Send(b'\x01\x00\x0B\x00\x00\x00\x00\x00'
                      + bytes([self._ipid]) + b'\x40\xFF\xFF\xF1\x01')
        elif ft == 0x02:
            if payload == b'\x00\x00\x00\x1F':
                self._registered = True
                self.Send(b'\x05\x00\x05\x00\x00\x02\x03\x00')
                self.WriteStatus('ConnectionStatus', 'Registered')
            elif payload == b'\xFF\xFF\x02':
                self.WriteStatus('ConnectionStatus', 'IPID not in program')
        elif ft == 0x03:
            self.WriteStatus('ConnectionStatus', 'ProcessorDisconnect')
        elif ft == 0x0D:                                  # processor ping
            self.Send(b'\x0E\x00\x02\x00\x00')
        elif ft == 0x0E:
            pass
        elif ft == 0x12:
            self._on_serial_long(payload)
        elif ft == 0x05 and len(payload) >= 4:
            # Smart Object array check FIRST (otherwise multi-item frames collapse)
            if payload[3] == 0x38 and len(payload) >= 14 and payload[9] == 0x14:
                body = payload[10:]
                for i in range(0, len(body)-3, 4):
                    j = ((body[i]<<8) | body[i+1]) + 1
                    v = (body[i+2]<<8) | body[i+3]
                    self.WriteStatus('Analog', v, {'Join': str(j)})
                return
            sub = payload[3]
            if sub in (0x00, 0x27):
                join  = (((payload[5] & 0x7F) << 8) | payload[4]) + 1
                state = ((payload[5] & 0x80) >> 7) ^ 0x01
                self.WriteStatus('Digital', bool(state), {'Join': str(join)})
            elif sub == 0x14:
                join  = ((payload[4]<<8) | payload[5]) + 1
                value = (payload[6]<<8) | payload[7]
                self.WriteStatus('Analog', value, {'Join': str(join)})
            elif sub == 0x03 and payload[4] == 0x1C:      # end-of-query
                self.Send(b'\x05\x00\x05\x00\x00\x02\x03\x1D')
                self.Send(b'\x0D\x00\x02\x00\x00')
                self._ready = True
                self.WriteStatus('ConnectionStatus', 'Ready')

    # ---- GCP command dispatch (DriverCommandAsset._scriptName -> SetXxx) ----
    def Set(self, command, value, qualifier=None):
        getattr(self, 'Set' + command)(value, qualifier)

    def SetDigital(self, value, qualifier):
        j = int(qualifier['Join']) - 1
        packed = (j // 256) + ((j % 256) * 256)
        if not value: packed |= 0x80
        self.Send(b'\x05\x00\x06\x00\x00\x03\x00' + pack('>H', packed))

    def SetAnalog(self, value, qualifier):
        j = int(qualifier['Join']) - 1
        self.Send(b'\x05\x00\x08\x00\x00\x05\x14'
                  + pack('>H', j) + pack('>H', int(value) & 0xFFFF))

    def SetPulse(self, _unused, qualifier):
        # Button-style: press (0x27 sub, bit7 clear) then release (bit7 set) ~100ms later
        j = int(qualifier['Join']) - 1
        packed = (j // 256) + ((j % 256) * 256)
        self.Send(b'\x05\x00\x06\x00\x00\x03\x27' + pack('>H', packed))
        Wait(0.1, lambda: self.Send(b'\x05\x00\x06\x00\x00\x03\x27'
                                    + pack('>H', packed | 0x80)))

class EthernetClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort=CIP_PORT, Protocol='TCP',
                 ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        DeviceClass.__init__(self)
```

Note the mixin pattern (one GS-template convention): assign `self.ReceiveData`, `self.Connected`, and `self.Disconnected` **inside** `DeviceClass.__init__`. Do not also use `@event(dev, 'Connected')` at the host-program level — the `@event` decorator rule is "last handler wins," so a host-level wiring will silently replace the driver's handshake handler. Pick one wiring strategy and keep it inside the DeviceClass.

GCP wiring: each exposed command (`Digital`, `Analog`, `Pulse`, …) must correspond to a `DriverCommandAsset` whose `_scriptName` matches a key in `self.Commands`. The `Join` child asset becomes `qualifier['Join']` at the Python callback — nothing enforces that the GCP asset tree and the Python dict agree on names, so a quick smoke test after any rename is required.

## Risks / uncertainties

- **Verification "contradicted" — `.sgd` schema:** The claim that each Smart Object section carries its own `ProjectFile=<path>.vtp` is false in a real sample (the key appears once in the top-level `Hd` section). Also, the SigType enum is wider than "Digital|Analog|Serial" — it includes `String` and literal composite values like `Digital|Analog|Serial|String`. The brief's parser treats SigType as free text and reads `ProjectFile` from `Hd` only.
- **Verification "inconclusive" — `.vtp` as OLE2/CFB:** The claim is only third-party; we have no primary-source confirmation. If the user has a real `.vtp`, run the magic-byte probe before committing to `olefile`.
- **Verification "unknown" — the trailing `0x02` in `0F 00 01 02`:** No open-source implementation documents what it means. rdriscoll's reference server emits it as a hard-coded constant; klenae's and ESP32 captures see `0F 00 00` (no payload). Both forms must be handled identically — clients ignore the payload.
- **Verification "unknown" — the 0x0B/0x0C authenticate frames:** For TLS CIP with username/password on 41796, the pycrestron-cip library builds auth frames in a `protocol.py` module we did not fetch; the field layout is not in any open-source dissector. A packet-capture against a real auth-enabled chassis is the only way to pin it down. For plain CIP on 41794 (the user's situation) this is irrelevant.
- **Verification "unknown" — collision behavior on this specific firmware:** The Home-Assistant integration documents coexistence on "modern" 3-Series; the DM-MD8X8-CPU3 is probably new enough, but we have not independently confirmed it on this chassis's firmware revision. Prefer an unused IP-ID until proven otherwise.
- **Verification "unknown" — `ADDSlave` exact flag position:** The `-P:<slot>` form is community-documented. Always run `ADDSlave ?` first.
- **Extron Python stdlib surface not confirmed:** `struct` is confirmed present and widely used; `select` and `socket` are confirmed banned; `olefile` is a third-party module, so `.vtp` parsing cannot run on-processor — it belongs in an off-device extraction tool. Also unconfirmed: whether `Send` of a frame larger than any undocumented TCP send-size cap gets fragmented silently.
- **The matrix join numbers themselves are not known.** The DM-MD8X8-CPU3-RPS SIMPL program may use Crestron's standalone matrix template OR a bespoke program; without reading `.smw`/`.sgd` or packet-capturing the working XPanel, we cannot know whether "press join N routes input X to output Y." The driver can be built generically (`SetDigital(join)`, `SetAnalog(join, value)`), but the GCP-level "RouteInputToOutput(X, Y)" wrapper that turns matrix semantics into joins requires the join map.
- **GCP main-program glue not inspected:** Whether the generated GCP main program calls `dev.Connect()` itself, or whether the driver must schedule its own connect in `DeviceClass.__init__`, is not visible from the samples we have. If GCP does not call it, add `Wait(0.1, lambda: self.Connect(10))` at the end of `EthernetClass.__init__`.

## First-run bring-up checklist

1. **Characterize the live chassis.** SSH or Telnet to the DM-MD8X8-CPU3-RPS's Toolbox console. Run:
   ```
   ver                           -- firmware revision
   progcomments                  -- loaded program name
   ipt -P:all                    -- every IP-table slot, every program
   who                           -- live CIP connections (shows XPanel's IP-ID)
   HELP ADD*                     -- which ADD* commands the firmware exposes
   ADDSlave ?                    -- confirm flag positions
   DUMPDMROUTEINFO               -- current input→output routing matrix
   ```
   Save the output. If any destructive command is contemplated, run Toolbox > IP Table Setup > Save to File first.

2. **Pick a free IP-ID.** From `ipt -P:all` note the XPanel's slot. If a spare XPanel-family slot exists (symbol declared, no active `who` entry), use it. Otherwise either (a) add a new XPanel symbol to the SIMPL program and recompile — a program change, needs the integrator — or (b) run `ADDSlave <ipid> 0.0.0.0 -P:<slot>` on the console (verify syntax first); note this does not survive a program reload.

3. **Open the socket.** Launch the driver with `host=<chassis IP>`, `port=41794`, `ipid=<chosen>`. Expect to see within ~1 s on the wire:
   ```
   S<- 0F 00 01 02   (or 0F 00 00 — handle both)
   ```
   The driver logs `TCP-up` on `_on_connect`.

4. **Send registration, see success.** Driver automatically emits on seeing `0x0F`:
   ```
   S-> 01 00 0B 00 00 00 00 00 <ipid> 40 FF FF F1 01
   S<- 02 00 04 00 00 00 1F     -- success
   ```
   Status flips to `Registered`. If instead `S<- 02 00 03 FF FF 02` arrives, the IP-ID is not declared in the running program — go back to step 2.

5. **Observe the join dump complete.** Driver emits `05 00 05 00 00 02 03 00`, receives a burst of 0x05/0x12 frames (log them raw, hex, for later join-map decoding), and sees `05 00 05 00 00 02 03 1C`. Driver replies with `03 1D` ack and `0D 00 02 00 00` first heartbeat. Status flips to `Ready`.

6. **Baseline route check.** On a second SSH session: `DUMPDMROUTEINFO`. Note the current input routed to output 1.

7. **Pulse the known digital join that drives route-1-to-output-1.** This is the test that proves the whole chain. The join number comes from the join map (`.sgd`/`.smw`/packet-capture); if unknown, start with the Crestron standalone matrix template convention (digital join 11..18 = output 1..8 input selectors in some templates, or 101..108 — this is template-specific). From the driver's GCP exposed `Pulse` command: `Pulse(Join=<N>)`. On the wire:
   ```
   S-> 05 00 06 00 00 03 27 <LL> <HH>      -- press
   S-> 05 00 06 00 00 03 27 <LL> <HH|0x80> -- release (~100 ms later)
   ```

8. **Verify the route changed.** Re-run `DUMPDMROUTEINFO`. If output 1 now shows input 1, the full stack works end to end: registration, write, SIMPL program, DM matrix routing. If nothing changed, two things to check: (a) was the SIMPL program actually programmed to route on that join? (packet-capture the XPanel pressing the same button to confirm the join); (b) did we send to the right IP-ID? (check `who` — our connection should be present).

9. **Watch feedback.** Press a button on the working XPanel; the driver should log the corresponding `WriteStatus('Digital', ...)` within milliseconds. If no feedback arrives but writes work, suspect a Smart Object envelope — check that the 0x38/0x39 decode path triggered for an incoming frame starting `05 00 .. 00 00 .. 38 ..`.

10. **Soak.** Leave the driver connected overnight. Confirm it survives `>35 s` idle periods (heartbeat exchange working), survives the chassis's periodic time broadcasts (0x05 sub 0x08, ignored by the driver), and re-connects cleanly if the chassis is rebooted (`03 00 00` or TCP FIN → `_on_disconnect` → `Wait(2.0, Connect(10))`).