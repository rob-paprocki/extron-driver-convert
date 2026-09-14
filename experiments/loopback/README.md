# loopback/ — an Extron processor talking to a PC instead of a camera

The first way this project runs on Extron hardware without an i20. A processor
drives the i20 driver as it would in a room, but the "camera" address belongs to
a PC running `visca_listener.py`. The listener records every frame, decodes it
against the i20 command set, and can answer the way Crestron's VISCA
documentation says the camera would.

## What a session can and cannot settle

| settles | does not settle |
|---|---|
| the exact bytes Extron's runtime sends for every command, from ControlScript and from GC | how a real i20 answers |
| whether the module imports and runs on the processor's Python (ROADMAP H1) | firmware behaviour: preset 83, lightbar segments, zoom speed |
| Build → Upload → Control for the `.pkp`, with everything but the camera real (H4) | whether the camera's pan/tilt replies are signed |
| what GC hands the script for the composed parameters, at their range edges | |
| what Extron's `SendAndWait` does with an ACK followed by a Completion (`--reply full`) | |

Every reply the listener sends comes from the documentation. A poll that parses
here proves the parser matches the docs *on a processor*, not that the docs
match the camera.

## Files

| file | runs on | what it does |
|---|---|---|
| `visca_listener.py` | the PC | TCP 5500 listener, frame decoder, documented-reply camera model, TSV capture, `--summarize` |
| `controlscript/main.py` | the processor | connects to the PC, runs the sequence one step every 1.5 s, logs every step, value read and status change |
| `controlscript/loopback_steps.py` | the processor | the sequence: PROTOCOL T3 and T3b, the composed commands at their range edges, then every `Update()` |
| `test_visca_listener.py` | anywhere | 50 checks, including the whole sequence end to end over localhost TCP |
| `captures/` | — | capture TSVs from real sessions; commit the ones a finding cites |

## Setup

1. **Network.** Cable the processor's LAN port to a spare Ethernet port on the
   PC, or put both on one switch. Give that PC port a static address on the
   processor's subnet, and check or set the processor's address with Toolbelt.
   For example, from an **administrator** PowerShell, for a processor on
   192.168.254.x:

       New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.254.10 -PrefixLength 24

2. **Firewall.** Windows blocks inbound connections by default. Allow TCP 5500
   on that port only:

       New-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)" -Direction Inbound -Protocol TCP -LocalPort 5500 -InterfaceAlias "Ethernet" -Action Allow

   and remove it afterwards with
   `Remove-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)"`.

3. **Listener.** `python experiments/loopback/visca_listener.py --reply ack`.
   It prints each frame as it arrives and writes `captures/<time>.tsv`. Type
   `state`, `tracking start`, `switching off` and so on to change what the
   "camera" reports; that is the camera-side change the feedback test needs.

## Path A — ControlScript

1. In VS Code, run *Extron: Create New Project* (Extron Default Template) and
   give it the processor model and address.
2. Copy into the project's `src/`, replacing the template's `main.py`:
   `controlscript/main.py`, `controlscript/loopback_steps.py`, and
   `experiments/skeleton_i20/out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py`.
3. Set `LISTENER_IP` in `main.py` to the PC's address from setup step 1.
4. Deploy. The sequence starts by itself; watch the listener and the processor's
   trace.
5. Run it twice: once against `--reply ack`, once against `--reply full`.

## Path B — Global Configurator

Use the GCP project from ROADMAP H0, with the device on Ethernet Port 1 pointed
at the PC's address instead of a camera. The package pins TCP 5500. Build,
Upload, then drive the commands from the touch panel in PROTOCOL T3 order.

## After a session

    python experiments/loopback/visca_listener.py --summarize experiments/loopback/captures/<time>.tsv

The summary counts frames by command, lists anything UNKNOWN, PARTIAL or
carrying an unexpected byte (`?XX`), and checks that every PROTOCOL T3 wire
string arrived, and in order. Keep the processor's program log too: its
`loopback:` lines record what the module *read* on every poll.

Look at these first:

- **Any UNKNOWN frame.** The module cannot produce one — `test_visca_listener.py`
  [2] decodes all 198 frames it can send — so an UNKNOWN frame means the
  runtime sent something the module did not, such as GC's own polling.
- **`--reply ack` against `--reply full`.** Offline, with a `SendAndWait` that
  keeps unread data, each Completion lands on the *next* call and polls go
  stale. If a processor does the same, every driver built on this template
  misreads a camera that sends both. Worth a finding either way.
- **The edge reads** (`expect -2448`, `expect 5` in the log). These exercise the
  two parser fixes below on a processor.

## What building this found, before any hardware

- **`UpdateCameraOutput` read the switching flag, not the camera.** The Get
  Output reply is documented on Crestron's Intelligent Switching page as
  `y0 50 0S 0Z FF`; the parser read byte 2. Fixed in both emitters, and pinned
  by `test_i20_wire.py` [13] and `test_i20_cs_wire.py` [10].
- **Negative pan/tilt positions read back as 63088 and 64240.** The module
  writes positions as two's complement and read them back unsigned. They are
  now read the way they are written; whether the camera uses two's complement
  is still unmeasured (ROADMAP H3).
- **Preset 255 cannot be sent.** The module accepts 0–255, but 255 is VISCA's
  `FF` terminator, so the camera would see a truncated frame. This is Extron's
  original range check; recorded, not changed.
- **Two pairs of commands share their bytes.** `Preset Recall 1` is
  `TrackingShot Tracking`, and `CameraOutput 0` is `IntelligentSwitching Resume`.
  A capture cannot tell either pair apart, so the decoder names both.
