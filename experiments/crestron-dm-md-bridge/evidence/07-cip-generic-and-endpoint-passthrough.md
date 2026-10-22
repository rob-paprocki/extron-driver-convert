# 07 — Generic CIP handler + DM endpoint pass-through: research synthesis

**Produced:** 2026-10-10 by workflow `wf_7e563f2c-bc1` (5 parallel readers → adversarial verify → single-writer synthesis).
**Status:** research-grade. External library claims below (Pepperdash join maps, SIMPL# Pro method signatures) were pulled by subagents via web search and are not independently re-verified against the current upstream source. Verify before coding against any specific class name, join number, or constructor signature.

---

# Logistics (worktree + private repo)

- `<repo>` IS a git repo (the current session's env flag misread an SMB mount quirk). Current branch `crestron-dm-bridge` is 3 commits ahead of main; a sibling worktree `C:/Users/<user>/wk-dm-bridge` on branch `crestron-dm-bridge-wt` is prunable. If you want library-ization in its own worktree: `git worktree add ../extron-driver-convert.cip-library feature/cip-library` from this checkout.
- Yes, private repo. Chassis profiles encode OEM reverse-engineering output; endpoint credentials and IP tables don't belong beside library code. Recommended split: `cip-client/` (library, could go public later) + `cip-profiles/` (private, one file per chassis+firmware with evidence/*.md citations) + `cip-apps/` (private, deployed drivers). Keep `experiments/crestron-dm-md-bridge/` where it is as the evidence log — don't delete it even after the library ships.

# Can we make a more generic CIP handler?

Yes, and we're ~85% of the way there by LOC. The 299-line proof-of-connect at `experiments/crestron-dm-md-bridge/cip_proof_of_connect.py` is already chassis-agnostic in the parts that matter — opcodes, framing, handshake, decoders, RX pump. What's missing is the TX side, a background pump with callbacks, reconnect, and a declarative `DeviceProfile` that binds raw joins to semantic names. Call it +900–1,100 LOC to ship a reusable library covering those, landing at ~1,200–1,400 LOC total with tests, in roughly a focused week.

## What's already chassis-agnostic

Keepable as library core after stripping `main()` + summary dump (~250 of 299 lines):

- Lines 24–36 — `OP_*` opcodes and protocol constants (`REG_SUCCESS`, `UPDATE_REQUEST`, `END_OF_QUERY_ACK`, `HEARTBEAT`). Verified against four OSS implementations.
- Lines 41–49 — hex/log helpers (log needs an injectable logger — stderr is hardwired today).
- Lines 52–60 — `build_registration(ipid)` takes IPID as parameter, emits the 14-byte REGISTER frame.
- Lines 63–91 — Decoders: digital (LL/HH swap + `0x80` inverted-active flag), analog (`0x05 0x14`), serial (`0x12 0x34`).
- Lines 109–150 — Transport, send, recv, length-prefixed frame parser.
- Lines 152–193 — Handshake: `0x0F` program-ready + REGISTER + REGISTER_RESULT; update-request.
- Lines 195–257 — RX pump + heartbeat + opcode dispatch (`0x0D`, `0x05` subtypes, `0x12`, end-of-query `0x1C` with `0x1D` ack).

## What needs to split out

| file-or-concept | current state | target state | effort (LOC) |
|---|---|---|---|
| `__main__` + CLI + stdout summary dump (260–294) | defaults wired to this chassis | `examples/dump_initial_cache.py` outside library | move, ~30 |
| `--host 172.16.0.104` default (line 262) | hard-coded to one chassis | required ctor arg, no default | trivial |
| `recv_some` 2.0s timeout (line 112) doubles as pump tick | fine for a probe, wrong for a library | separate RX daemon thread + lock around `sendall` | ~80 |
| `log()` writes to stderr unconditionally (line 41) | debug util | injected `logging.Logger`; `.getChild('cip')` per-component | ~10 |
| `ConnectionError` returns silently (line 202) | no reconnect | `_supervise()` with exp backoff + jitter, IPID-rejection jumps straight to `backoff_max` (steal from Antonio112009) | ~40 |
| `self.digitals/analogs/serials` plain dicts (103–105) | poll-only | event bus: `on_digital(cb) → unsubscribe`, `(type, join, smart_object) → value` keying, output replay on END_OF_QUERY | ~80 |
| `process_frames(hold_seconds)` blocking pump (195) | one-shot | background thread; `wait_until_ready(timeout)` composes `registered` / `program` / `synced` futures | ~20 |
| Class docstring "Passive by design: does NOT send ..." (line 8) | no TX | full write-side (next section) | ~50 |
| No profile layer | raw int joins only | `DeviceProfile` descriptors + `CipDevice` wrapper | ~220 |
| No concrete profile | n/a | `DmMd8x8Cpu3RpsOem` from evidence/06 | ~80 |
| No tests | n/a | `FakeProcessor` + codec round-trips + handshake + TX vectors | ~300–400 |
| No package scaffold | script | `__init__.py`, `pyproject.toml`, `py.typed` | ~50 |

## Write-side we don't have yet

Pure wire encoding is only ~50 LOC; the surrounding threading / callbacks / reconnect is the bulk.

```python
def press(self, join: int) -> None
def release(self, join: int) -> None
def pulse(self, join: int, duration_s: float = 0.1) -> None
def set_analog(self, join: int, value: int) -> None  # 0..65535
def send_serial(self, join: int, text: Union[str, bytes],
                encoding: str = 'utf-8', flags: int = 0xFF) -> None
def send_update_request(self) -> None  # force full cache re-push
```

Frame encodings (from current decoder work + PROTOCOL.md):

| verb | frame |
|---|---|
| press / release | `0x05 0x00 0x06 0x00 LL HH` where `swapped = ((join-1) & 0xFF) << 8 \| ((join-1) >> 8)`; release sets `HH \|= 0x80` |
| set_analog | `0x05 0x00 0x08 0x14 JH JL VH VL` — big-endian |
| send_serial | `0x12 LH LL 0x00 0x00 0x00 IL 0x34 JH JL FF <text>` — outer_len big-endian, inner_len single byte (bounds text at 251 B/frame; chunk with SOM/EOM flags for longer) |
| update_request | `0x05 0x00 0x05 0x00 0x00 0x02 0x03 0x00` |

Subscriber API (steal Antonio112009's `JoinUpdate(type, join, value, smart_object)` frozen dataclass):

```python
def on_digital(self, cb: Callable[[int, int], None]) -> Callable[[], None]  # returns unsubscribe
def on_analog(self,  cb: Callable[[int, int], None]) -> Callable[[], None]
def on_serial(self,  cb: Callable[[int, bytes], None]) -> Callable[[], None]
def on_ready(self,   cb: Callable[[], None]) -> Callable[[], None]
def on_connect / on_disconnect similarly
```

## Device-profile / join-map abstraction

Two-level split: `CipClient` speaks raw ints; `DeviceProfile` declares named joins; `CipDevice` composes them. Descriptor types: `DigitalPoint(join)`, `AnalogPoint(join)`, `SerialPoint(join)`, `DigitalRow(base, stride, rows, col=0)` and Analog/Serial equivalents, plus `Grid(point_type, row_base, row_stride, rows, col_base, col_stride, cols)` for the 2D output×input matrix.

```python
class DmMd8x8Cpu3RpsOem(DeviceProfile):
    model    = 'DM-MD8X8-CPU3-RPS'
    firmware = 'v1.8001.5769.27432'
    power_state    = SerialPoint(3000)
    chassis_label  = SerialPoint(3001)
    programmed_ip  = SerialPoint(3002)
    input_name     = SerialRow(base=900,  stride=10, rows=8, col=1)
    input_hdcp     = SerialRow(base=900,  stride=10, rows=8, col=6)
    input_sync     = SerialRow(base=900,  stride=10, rows=8, col=9)
    output_name    = SerialRow(base=1200, stride=12, rows=8, col=1)
    output_sync    = SerialRow(base=1200, stride=12, rows=8, col=9)
    output_fw      = SerialRow(base=1200, stride=12, rows=8, col=11)
    # Pending Phase-2 drive-and-diff:
    # video_route  = AnalogRow(base=?, stride=1, rows=8)
    # audio_route  = AnalogRow(base=?, stride=1, rows=8)
    # Endpoint IO joins slot in HERE if a SIMPL# add-on exposes them (see Part 2).

with CipDevice(CipClient('172.16.0.104', ipid=3), DmMd8x8Cpu3RpsOem()) as d:
    d.wait_until_ready(10)
    print(d.read('input_name', 1))        # b'Input 1 : DMC-4KZ-HD'
    d.write('video_route', 2, index=1)    # once pinned
    d.on_change('output_sync', lambda i, v: print(f'out{i} sync -> {v}'))
```

Steal rellis-erigon's `JoinData` schema for `store_key = f'{processor}/{semantic_name}'` — survives config reloads, and lets a `.c3p/.vtz` panel-file import eventually populate profiles automatically.

## Recommendation

Yes, do it, in a private repo split `cip-client/` + `cip-profiles/` + `cip-apps/`. Model the API on Antonio112009/pycrestron-cip (codec/transport split, explicit lifecycle waiters, output replay on END_OF_QUERY, backoff with jitter) and layer rellis-erigon's `JoinData` idiom on top; endpoint-IO joins stay gated on the Part 2 experiment and slot into whichever profile the add-on surfaces them under (chassis or EISC virtual device).

# Can we do RS-232 / IR / Relay over DM to the endpoints?

## What the OEM default program exposes

Nothing for endpoint IO. Dispositive evidence from the cache-passthrough-hunt against evidence/05 (structured in evidence/06):

- **Smart Object 0x01 (top-level menu)** enumerates exactly `{Inputs, Outputs, Ethernet, System Overview, Password, Naming, System}`. No endpoint-control tab exists at all.
- The only other decodable smart objects: input-group picker (0x05), output-group picker (0x06), single-input picker (0x0d), per-input EDID dropdowns (0x10/0x11/0x12), audio format Stereo/5.1/6.1/7.1 (0x17), sample rate 192/96/48/44.1 (0x18). No COM/IR/relay/VersiPort widget anywhere.
- **No RX-side feedback joins** (COM-receive serials, relay-state digitals, VersiPort-state) appear in the initial-cache dump. This is the strongest evidence — feedback joins MUST be published for subscribers to see them; a write-only invisible pass-through is implausible since the control side needs to know a byte arrived.
- The `commandDispatch` channel at `S4002='Idle'` / `S4019='Command completed.'` + the 9-row `S4010–S4018` pipe-delimited table publishes one specific operation's output (endpoint firmware inventory with DM-TX-4K-100-C-1G flagged `update-pending=YES`). Two-string response vocabulary — not a generic console shell.

Caveat: CIP initial-cache dumps only publish non-empty server-to-client state, so client-to-server-only joins could in principle exist unseen. The experiment in the last section closes that door.

## What PepperDash reference programs do

PepperDash's DM endpoint EISC bridges wire VIDEO behavior only — zero joins for IR, RS-232 TX/RX, relay, VersiPort, or CEC on the DM endpoint's own bridge. Full tables:

| join type | `DmRmcControllerJoinMap` | `DmTxControllerJoinMap` |
|---|---|---|
| digitals | D1 IsOnline, D2 HdmiInputSync, D3–D5 VideoMute On/Off/Toggle | D1 IsOnline, D2 VideoSyncStatus, D3 FreeRunEnabled, D4–D6 Input1/2/3 VideoSync |
| analogs | A1 AudioVideoSource, A2 HdcpSupportCapability, A3–A4 Port1/2 HdcpState, A5 HdcpInputPortCount | A1 VideoInput, A2 AudioInput, A3 HdcpSupportCapability, A4–A5 Port1/2 HdcpState, A6 VgaBrightness, A7 VgaContrast, A8 Port3 HdcpState, A9 HdcpInputPortCount |
| serials | S1 CurrentOutputResolution, S2–S5 Edid*, S6 Name | S1 CurrentInputResolution, S2 Name |
| IR / COM / Relay / VersiPort | **NONE** | **NONE** |

Citations: `PepperDash/Essentials:src/PepperDash.Essentials.Core/Bridges/JoinMaps/DmRmcControllerJoinMap.cs` and `DmTxControllerJoinMap.cs`. `LinkDmRmcToApi` in `PepperDash.Essentials.DM:src/Endpoints/Receivers/DmRmcHelper.cs:46–170` and `LinkDmTxToApi` in `src/Endpoints/Transmitters/DmTxHelpers.cs` contain zero IR/COM/Relay/VersiPort `LinkInputSig` calls.

PepperDash's actual pattern for endpoint IO: separate `EssentialsBridgeableDevice` plugins (`versiportinput`, `ComPortController`, generic IR/Relay) with `portDeviceKey + portNumber` config. Factory casts the referenced device to `IIOPorts` / `IIROutputPorts` / `IComPorts` / `IRelayPorts` and indexes `.VersiPorts[dc.PortNumber]` (reference: `GenericVersiportInputDevice.cs:124–155`).

Specific to Rob's hardware — interfaces implemented on the PepperDash controller classes:

| endpoint (slot) | class | IR | COM | Relay | VersiPort | CEC |
|---|---|---|---|---|---|---|
| DM-RMC-4K-SCALER-C (output 101) | `DmRmc4kScalerCController` | yes | yes | yes | **NO** (physical VersiPort exists, wrapper doesn't implement `IIOPorts`) | yes |
| DM-TX-4K-100-C-1G (input 6) | `DmTx4k100Controller` | yes | yes | n/a | n/a | yes |
| DM-TX-201-C (input 8, wallplate) | `DmTx201CController` | **NO** (physical IR exists, wrapper lacks `IIROutputPorts`) | **NO** (physical RS-232 exists, wrapper lacks `IComPorts`) | n/a | n/a | NO |

So even with the Pepperdash reference, driving IR + RS-232 on the wallplate (input 8) requires extending `DmTx201CController` first; VersiPort on the RMC requires extending `DmRmc4kScalerCController`.

## SIMPL# Pro endpoint API (fallback)

Hardware is fully driveable from managed C# — SimplSharpPro exposes `ComPort`, `IROutputPort`, `Relay`, and `Cec` on every endpoint object once `.Register()` is called:

| endpoint | ns | ComPorts | IROutputPorts | RelayPorts | VersiPorts | HDMI CEC |
|---|---|---|---|---|---|---|
| `DmRmc4kScalerC` | `Crestron.SimplSharpPro.DM.Endpoints.Receivers` | 1 | 1 | 2 | 0 | `rmc.HdmiOutput.StreamCec` |
| `DmTx201C` | `Crestron.SimplSharpPro.DM.Endpoints.Transmitters` | 1 | 1 | 0 | 0 | `tx.HdmiInput.StreamCec` + `.HdmiOutput.StreamCec` |
| `DmTx4K100C1G` *(note caps)* | `Crestron.SimplSharpPro.DM.Endpoints.Transmitters` | 1 | 1 | 0 | 0 | `tx.StreamCec` |

Correction: the class is `DmTx4K100C1G` (uppercase K/C/G) — `DmTx4k100C1g` won't resolve. Also: the plain `DmRmc4kScalerC` has **NO VersiPorts** on the SIMPL# Pro surface (VersiPorts live on wallplate keypads and DMPS output cards, not RMCs).

Constructors: `new DmXxx(DMInput|DMOutput endpoint)` for DM-attached, or `(uint ipid, CrestronControlSystem)` for IPID-direct. Core methods:

- `tx.ComPorts[1].SetComPortSpec(ComspecBaudRate9600, DataBits8, ParityNone, StopBits1, RS232, HHS_None, SHS_None, false); tx.ComPorts[1].Register(); tx.ComPorts[1].Send("hello\r"); tx.ComPorts[1].SerialDataReceived += OnRx;`
- `rmc.IROutputPorts[1].LoadIRDriver(@"\USER\display.ir"); rmc.IROutputPorts[1].PressAndRelease("POWER_ON", 100);` — compiled `.ir` driver file (Crestron IR Designer), not raw Pronto hex.
- `rmc.RelayPorts[1].Close()` / `.Open()` / `.StateChange` event.
- `rmc.HdmiOutput.StreamCec.Send.StringValue = cecBytes;`

Public developer docs do NOT state the DM-MD8X8-CPU3-RPS factory firmware instantiates these endpoint classes and bridges their ports to CIP IPIDs. The CPU3's "no-programming" scope is video routing, EDID, HDCP, and CEC-over-HDMI only. Every third-party open-source Crestron DM project (PepperDash, ICDSystems, kielthecoder, alvaroyurrita, rdriscoll) treats endpoint IO as something the user program stands up — which there'd be no demand for if the OEM default did it.

The fallback is a ~300-LOC SIMPL# Pro program that:

1. Instantiates `DmMd8x8Cpu3rps(0x03, this)` + `.Register()`.
2. Instantiates the three endpoints bound to `chassis.Outputs[1].Endpoint` / `chassis.Inputs[6].Endpoint` / `chassis.Inputs[8].Endpoint`. Confirm the "output 101" → `chassis.Outputs[?]` slot mapping against the chassis manual — "101" is Crestron labeling for "output card 1 output 1".
3. `SetComPortSpec` + `.SerialDataReceived += OnRx` + `.Register()` on each ComPort; `LoadIRDriver` on each IROutputPort.
4. `new EthernetIntersystemCommunications(0xA1, "127.0.0.2", this).Register()` — one virtual device, one flat join map.
5. Bidirectional sig handler bridges joins ↔ port methods.

Flat EISC join contract the Python CIP client speaks to:

| direction | type | join | meaning |
|---|---|---|---|
| → chassis | string | 1 / 2 / 3 | COM TX for RMC101 / TX6 / TX8 |
| chassis → | string | 11 / 12 / 13 | COM RX for RMC101 / TX6 / TX8 |
| → chassis | string | 21 / 22 / 23 | IR command name (`PressAndRelease 100 ms`) for RMC101 / TX6 / TX8 |
| → chassis | digital | 31 / 32 | RMC101 Relay1/2 close(true) / open(false) |
| chassis → | digital | 41 / 42 | RMC101 Relay1/2 state feedback |
| ↔ chassis | ushort | 51 | Video route for output 1 (set / feedback) |

This is also the "more generic CIP handler" answer — Python side speaks ONE protocol (CIP joins) to ONE IPID with one flat Boolean/UShort/String join table. The C# add-on is the only place that knows about DM endpoint classes.

Deployment caveats: the CPU3 has a **single program slot**, so loading this REPLACES the shipping default. Take a Toolbox backup first. The CPU3 is 3-Series, not 4-Series — reference `Crestron.SimplSharpPro.DM.dll` from the 3-Series SDK. This is why the add-on belongs in the private repo: it becomes custom firmware for Rob's unit.

## Verdict

**No** — the OEM default program on the DM-MD8X8-CPU3-RPS does not expose endpoint RS-232 / IR / relays, with ~95% confidence. Four independent investigations converge: (1) OEM top-level smart-object menu has no endpoint-control tab (dispositive); (2) no RX-side endpoint feedback joins in the initial cache (dispositive — those appear even in idle state); (3) the mature Pepperdash reference doesn't put these joins on the DM endpoint's own bridge, which it would if the OEM did; (4) SIMPL# Pro API conventions require explicit instantiation + `.Register()` + EISC bridging, and no Crestron sell-sheet or manual claims these are auto-exposed. The remaining 5% uncertainty is that CIP initial-cache dumps only carry non-empty server-to-client state, so client-to-server-only joins could in principle exist unseen — but absence of ANY feedback makes a working pass-through implausible. The experiment below settles it in <30 min.

## The one experiment to run next

RS-232 RX injection — passive on the chassis side, no CIP writes, under 30 min:

**Prereq:** add a `--log-all-frames` flag to `cip_proof_of_connect.py` that hex-dumps every raw RX frame (currently `handle_frame` logs only state changes). ~5 LOC change at the top of `handle_frame` to print `hexs(frame)` before dispatch.

1. In session A, run the proof-of-connect in continuous RX mode:

   ```powershell
   python experiments\crestron-dm-md-bridge\cip_proof_of_connect.py --host 192.168.6.14 --ipid 1 --hold 300 --log-all-frames 2>&1 | Tee-Object rx_capture.log
   ```

2. Attach a USB-to-RS232 dongle to the RS-232 port on the DM-TX-4K-100-C-1G at input 6 (known-online — chassis endpoint inventory shows its firmware update is pending, so the endpoint is reachable). Configure 9600 8N1. From a laptop, inject for 60 s:

   ```python
   import serial, time
   p = serial.Serial('COMx', 9600, 8, 'N', 1)
   for n in range(300):
       p.write(f'EXTRON-PROBE-{n:08d}\r\n'.encode())
       time.sleep(0.2)
   ```

3. During the same window, physically unplug and replug the HDMI cable at the DM-RMC-4K-SCALER-C's HDMI OUT (output 101) to force an HPD transition. Secondary probe for "does the OEM bridge ANY endpoint-side feedback?"

4. Grep the capture:

   ```powershell
   Select-String -Path rx_capture.log -Pattern 'EXTRON-PROBE'
   Select-String -Path rx_capture.log -Pattern '^0x12' -Context 0,3   # any new serial frames
   ```

**Decision rule:**

- **Any** frame carries the probe string, OR a new serial-join index absent from evidence/06 → OEM IS bridging endpoint COM RX. Overturn the verdict and re-mine the dump for the responsible join cluster. The still-unexplained smart objects 0x13 (20 items), 0x16 (6), 0x1e (14), 0x20 (7), 0x21 (7) are candidates since they're truncated at 32 bytes in current logging — re-capture with full payload.
- **Zero** probe frames over 60 s + no new joins from HPD toggle → verdict confirmed `needs-simpl-add-on`. Proceed with the ~300-LOC EISC bridge; profiles treat `ep101_com_tx`, `ep101_com_rx`, `ep601_com_tx`, `ep801_ir_cmd`, etc. as `SerialPoint` / `DigitalRow` entries on the EISC-device profile, not the chassis profile.

# Impact on PLAN.md

- **Phase 2 (drive-and-diff):** run the RX-injection experiment above FIRST, before any CIP write probes. Verdict determines whether endpoint-IO joins become a chassis-profile concern or a SIMPL#-add-on concern.
- **New Phase 2b (library-ization):** parallel-track the ~1-week library refactor against the proof-of-connect while Phase 2 completes. Repo mechanics: `git init` + private remote + `git worktree add ../extron-driver-convert.cip-library feature/cip-library`. Nothing in Phase 2 blocks library work since the library is chassis-agnostic.
- **New Phase 3 (SIMPL# add-on):** becomes the baseline plan if Phase 2 confirms `needs-simpl-add-on` (expected). ~300 LOC C# against the 3-Series SDK (CPU3 is 3-Series — reference `Crestron.SimplSharpPro.DM.dll` from the 3-Series SDK, NOT the 4-Series). Toolbox-backup the OEM program before deploy. Deploy to the single program slot. Python CIP client then talks to one EISC virtual device at IPID 0xA1 with the flat join contract above.
- **Phase 4 (deployment):** unchanged, except the private-repo split (`cip-client/` + `cip-profiles/` + `cip-apps/`) becomes the shipping shape; `experiments/crestron-dm-md-bridge/` stays as the evidence log.