# loopback/ — an Extron processor driving the i20 module at a PC

The first way this project runs on Extron hardware without an i20. The i20
ControlScript module runs on a real processor, but the "camera" is a PC. A
PC-side orchestrator sends the module every command through a small console the
processor program serves, plays the camera on TCP 5500, and checks each step two
ways against the same module run on the PC:

| check | on the processor | on the PC |
|---|---|---|
| **wire** | the frames the listener received | the frames the module sends when run locally |
| **read** | what the module on the processor read back | what the same module reads from the same reply bytes |

The local twin replays the processor's calls in the same order, on one module
instance, so a difference on either count is Extron's runtime disagreeing with
CPython about identical code.

## What a session can and cannot settle

| settles | does not settle |
|---|---|
| the exact bytes Extron's runtime sends for every command | how a real i20 answers |
| whether the module imports and runs on the processor's Python (ROADMAP H1) | firmware behaviour: preset 83, lightbar segments, zoom speed |
| what Extron's `SendAndWait` does with an ACK followed by a Completion (`--reply full`) | whether the camera's pan/tilt replies are signed |
| with Path B, Build → Upload → Control for the `.pkp`, everything real but the camera (H4) | |

Every reply the PC sends comes from the documentation. A read that matches proves
the parser behaves the same on a processor, not that the docs match the camera.

## Files

| file | runs on | what it does |
|---|---|---|
| `run_loopback.py` | the PC | starts the listener, drives the console step by step, writes `captures/<time>.tsv` and `captures/<time>-report.json` |
| `visca_listener.py` | the PC | the camera: TCP 5500 listener, frame decoder, documented-reply model; usable alone, with `--summarize` |
| `controlscript/main.py` | the processor | serves the command console on TCP 5600 |
| `controlscript/console_core.py` | the processor | the console protocol; free of extronlib, so the tests run this same code |
| `controlscript/loopback_steps.py` | the PC | the sequence: PROTOCOL T3 and T3b, the composed commands at their range edges, then every `Update()` |
| `controlscript/make_project.py` | the PC | assembles `controlscript/build/i20-loopback/`, a project for the Deployment Utility (git-ignored) |
| `test_visca_listener.py` | anywhere | 50 checks: decoder, framing, reply model, the sequence end to end over TCP |
| `test_run_loopback.py` | anywhere | 19 checks: whole sessions rehearsed against a stand-in processor running `console_core.py` |
| `captures/` | — | captures and reports from real sessions; commit the ones a finding cites |

## What deploying needs

Extron deploys ControlScript with the **ControlScript Deployment Utility**, not the
VS Code extension. Its help says *a project must be certified in order to be
successfully deployed*: a certified user certifies the project in the Utility,
which adds a `certification.dat`, and anyone can then deploy that project. So
Path A needs the Utility, plus a certified account or a certified colleague to
certify `build/i20-loopback/`. Path B needs neither.

## Setup

1. **Network.** Cable the PC to the processor's network. A processor's AV LAN port
   can serve DHCP; for example, a processor at 192.168.254.1 hands the PC an
   address on 192.168.254.x.
2. **Firewall.** Windows blocks inbound connections by default. From an
   **administrator** PowerShell, allow the camera port on the lab adapter only:

       New-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)" -Direction Inbound -Protocol TCP -LocalPort 5500 -InterfaceAlias "<lab adapter>" -Action Allow

   and remove it afterwards with
   `Remove-NetFirewallRule -DisplayName "i20 loopback (TCP 5500)"`.

## Path A — ControlScript, automated

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
  call. If a processor does the same, every driver built on this template misreads
  a camera that sends both. Worth a finding either way.
- **The edge steps** (`edge, expect -2448`, `edge, expect 5`), which exercise the
  two parser fixes below.

## Path B — Global Configurator, by hand

Use the GCP project from ROADMAP H0, with the device on Ethernet Port 1 addressed
to the PC. GC drives commands from a touch panel, so it needs a GUI Designer
layout with a button per PROTOCOL T3 step. Run
`python experiments/loopback/visca_listener.py --reply ack` while pressing them,
then check the capture:

    python experiments/loopback/visca_listener.py --summarize experiments/loopback/captures/<time>.tsv

There is no local twin on this path. The check is the decoder and the T3
checklist: every wire string arrived, in order, and nothing UNKNOWN. An UNKNOWN
frame means GC's runtime sent something the module does not.

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
