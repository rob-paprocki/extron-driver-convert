# loopback/ — an Extron processor driving the i20 driver at a PC

The first way this project runs on Extron hardware without an i20. The driver
runs on a real processor, but the "camera" is a PC: `visca_listener.py` takes
TCP 5500, records every frame, decodes it against the i20 command set, and can
answer the way Crestron's VISCA documentation says the camera would.

There are two ways to make the processor send commands, and they test different
things:

| | Path A — ControlScript | Path B — Global Configurator |
|---|---|---|
| driver under test | `onebynd_camera_IV_CAM_I20_v1_0_0_0.py` | `1bynd_19_20024`, the synthesised `.pkp` |
| who sends commands | this PC, through a console the program serves | a GC macro, started by a monitor |
| checks | every step's wire *and* read, against the module run locally | every wire string, against the macro's expected bytes |
| needs | the ControlScript Deployment Utility and a **certified** project | Global Configurator Pro; no panel, no certification |
| also settles | — | ROADMAP H0 and H4 minus the camera: Build and Upload of a synthesised package |

## What a session can and cannot settle

| settles | does not settle |
|---|---|
| the exact bytes Extron's runtime sends for every command | how a real i20 answers |
| whether the driver loads and runs on the processor | firmware behaviour: preset 83, lightbar segments, zoom speed |
| what Extron's `SendAndWait` does with an ACK followed by a Completion (`--reply full`) | whether the camera's pan/tilt replies are signed |

Every reply the PC sends comes from the documentation. A read that matches proves
the parser behaves the same on a processor, not that the docs match the camera.

## Files

| file | runs on | what it does |
|---|---|---|
| `visca_listener.py` | the PC | the camera: TCP 5500 listener, decoder, documented-reply model, captures, `--summarize` |
| `run_loopback.py` | the PC | Path A: drives the console step by step; writes `captures/<time>.tsv` and `<time>-report.json` |
| `controlscript/main.py` | the processor | Path A: serves the command console on TCP 5600 |
| `controlscript/console_core.py` | the processor | Path A: the console protocol, free of extronlib so the tests run this same code |
| `controlscript/loopback_steps.py` | the PC | both paths' sequences: `SEQUENCE` for Path A, `GC_MACRO` for Path B |
| `controlscript/make_project.py` | the PC | Path A: assembles `controlscript/build/i20-loopback/` for the Deployment Utility (git-ignored) |
| `test_visca_listener.py` | anywhere | decoder, framing, reply model, the sequence end to end over TCP, and every Path B macro string |
| `test_run_loopback.py` | anywhere | Path A sessions rehearsed against a stand-in processor running `console_core.py` |
| `captures/` | — | captures and reports from real sessions; commit the ones a finding cites |

## Setup, both paths

1. **Network.** Cable the PC to the processor's network. A processor's AV LAN port
   can serve DHCP; for example, a processor at 192.168.254.1 hands the PC an
   address on 192.168.254.x.
2. **Firewall.** Windows blocks inbound connections by default. From an
   **administrator** PowerShell, allow the camera port on the lab adapter only:

       New-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)" -Direction Inbound -Protocol TCP -LocalPort 5500 -InterfaceAlias "<lab adapter>" -Action Allow

   and remove it afterwards with
   `Remove-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)"`.

## Path B — Global Configurator, no panel needed

GC Pro runs driver commands without a touch panel. In its own help, *"a macro is
a reusable action list that can be invoked by a button press, schedule, or
monitor"*, and a monitor fires *"when all of these conditions are met"* and
*"re-arms automatically"* when they stop being true. So one monitor can start
the whole sequence the moment the driver connects to the PC.

1. **Driver.** Install the current `experiments/skeleton_i20/out/1bynd_19_20024_v1_0_0.pkp`
   into GC's driver library with GC closed (`experiments/skeleton_i20/PROTOCOL.md`,
   *Install 20024*). A library that holds an older 20024 needs it replaced.
2. **Project.** In a new Pro project:
   - add the processor as the controller, by its address and web credentials;
   - on one of its Ethernet ports add *1 Beyond / IV-CAM-I20 v1.2*, addressed to
     the PC. The package pins TCP 5500.
3. **Macro** `i20 T3`, from the device's commands, in this order:

   | # | GC command | parameters | the listener should see |
   |---|---|---|---|
   | 1 | Power | Value On | `81 01 04 00 02 FF` |
   | 2 | Preset | Action Recall, Value 1 | `81 01 04 3F 02 01 FF` |
   | 3 | Zoom | Value Tele, Speed 5 | `81 01 04 07 25 FF` |
   | 4 | Auto Tracking | Value Start | `81 01 04 3F 02 50 FF` |
   | 5 | Auto Tracking | Value Stop | `81 01 04 3F 02 51 FF` |
   | 6 | Zoom Position | Value 6699, Speed 3 | `81 01 04 47 03 01 0A 02 0B FF` |
   | 7 | Freeze Frame | Value On | `81 01 04 62 02 FF` |
   | 8 | Freeze Frame | Value Off | `81 01 04 62 03 FF` |
   | 9 | Indicator Light | Value Full, Color Red, Brightness Bright | `81 C1 0D 0D 0D 0D FF` |
   | 10 | Indicator Light | Value Half, Color Green, Brightness Dim | `81 C1 00 04 04 00 FF` |
   | 11 | Indicator Light | Value None, Color Green, Brightness Off | `81 C1 00 00 00 00 FF` |
   | 12 | Tracking Profile | Value 2 | `81 01 04 3F 02 6A FF` |
   | 13 | Camera Output | Value 2 | `81 C2 01 08 02 FF` |
   | 14 | Intelligent Switching | Value Resume | `81 C2 01 08 00 FF` |
   | 15 | Intelligent Switching | Value Pause | `81 C2 01 0B 00 FF` |
   | 16 | Group Tracking | Value Enable | `81 01 04 3F 02 52 FF` |
   | 17 | Presenter Tracking | Value Enable | `81 01 04 3F 02 53 FF` |
   | 18 | Pan Tilt Angle | Pan -2448, Tilt -1296, Pan Speed 1, Tilt Speed 1 | `81 01 06 02 01 01 0F 06 07 00 0F 0A 0F 00 FF` |
   | 19 | Pan Tilt Angle | Pan 2448, Tilt 1296, Pan Speed 24, Tilt Speed 20 | `81 01 06 02 18 14 00 09 09 00 00 05 01 00 FF` |
   | 20 | Zoom Position | Value 16384, Speed 7 | `81 01 04 47 07 04 00 00 00 FF` |
   | 21 | Camera Output | Value 5 | `81 C2 01 08 05 FF` |

   Every string in the last column is what the driver sends for those
   parameters (`test_visca_listener.py` [6] checks all 21). Rows 18 and 19 are
   also the first measurement of what GC hands the script for Pan and Tilt.
4. **Monitor** `run i20 T3`: conditions System → *System Initialized*, and the
   i20's *Connection Status* = Connected; action System → *Invoke Macro* `i20 T3`.
5. **Listener, then Build and Upload.** On the PC:

       python experiments/loopback/visca_listener.py --reply ack

   Build in GC (record any build error verbatim), then Upload. When the driver
   connects, the monitor should fire the macro. Stopping and restarting the
   listener drops and restores the connection, which should fire it again;
   whether it does is part of what the first run shows.
6. **Check the capture:**

       python experiments/loopback/visca_listener.py --summarize experiments/loopback/captures/<time>.tsv --expect gc-macro

   All 21 strings, in order, and nothing UNKNOWN. Any extra frame GC sends on its
   own, such as status polls, is listed and decoded rather than failed. There is
   no local twin on this path, so reads are not compared.

## Path A — ControlScript, automated

Extron deploys ControlScript with the **ControlScript Deployment Utility**, not the
VS Code extension. Its help says *a project must be certified in order to be
successfully deployed*: a certified user certifies the project in the Utility,
which adds a `certification.dat`, and anyone can then deploy that project.

1. `python experiments/loopback/controlscript/make_project.py --address <processor>`
   (add `--model "IPCP Pro 360Q xi"` for an xi unit).
2. Open `experiments/loopback/controlscript/build/i20-loopback/` in the Deployment
   Utility, certify it, and deploy.
3. Run a session, then the same against `--reply full`:

       python experiments/loopback/run_loopback.py --processor <processor>
       python experiments/loopback/run_loopback.py --processor <processor> --reply full

Each step prints `wire ok|DIFF` and `read ok|DIFF`, and a DIFF prints both sides.
The report keeps every step's frames, replies, statuses and the module's own
error lines from both sides, and its `processor_info` records the processor's
ControlScript version and Python.

Look at these first:

- **Any `wire DIFF`.** The processor sent bytes the module does not send under
  CPython.
- **Any `read DIFF` against `--reply ack`.** The same reply parsed differently on
  the processor.
- **`--reply full`.** Offline, a runtime that keeps unread data diverges on 12 of
  the 41 reads (`test_run_loopback.py` [4]): each Completion lands on the next
  call. If a processor does the same, every driver built on this template
  misreads a camera that sends both. Worth a finding either way.
- **The edge steps** (`edge, expect -2448`, `edge, expect 5`), which exercise the
  two parser fixes below.

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
