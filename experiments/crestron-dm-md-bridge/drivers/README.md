# DM-MD CPU3/CPU4 chassis drivers for Extron ControlScript and Q-SYS Lua

Three source-code deliverables for driving the routing surface of a Crestron
DM-MD CPU3/CPU4 chassis from a non-Crestron processor. Endpoint RS-232 / IR /
Relay is NOT supported — those are firmware-locked on the chassis (see
`experiments/crestron-dm-md-bridge/evidence/13-encoder-and-chassis-lockin.md`).

## Files

| File | Platform | Transport | Scope | Prerequisite |
|---|---|---|---|---|
| `cs_dm_md_ctp.py` | Extron ControlScript | TCP :41795 CTP | Routing commands + feedback (polled) | **Chassis must have CTP enabled.** Also requires `AUTHentication OFF` on this firmware (`TELNETport ON` is gated behind auth-off on CPU3). Standard on many Crestron installations. |
| `cs_dm_md_cip_feedback.py` | Extron ControlScript | TCP :41794 CIP | **Real-time feedback only** (receive) — route changes, endpoint online state, system info | None — IPID 1 slot (stock XPanel) is auth'd by presence in the chassis IP table, which is already configured by the OEM firmware. Works on Rob's current chassis as-is. |
| `qsys_dm_md_ctp.lua` | Q-SYS Designer (Script Component or `.qplug`) | TCP :41795 CTP | Routing commands + feedback (polled) | Same as `cs_dm_md_ctp.py` — CTP must be enabled. |

## Verification status

**All three** have unit tests that pass against fixture bytes derived from
live chassis captures:

- `cs_dm_md_ctp.py` — DUMPDMROUTEINFO parser verified against a known-good
  response sample. Command-surface builders callable (`route_video`,
  `route_audio`, `route_av`, `route_usb`, `route_avu`, `route_all`,
  `break_output`, `poll_routes`).

- `cs_dm_md_cip_feedback.py` — frame peeler, digital decoder, analog decoder,
  and serial decoder all verified against bytes observed in
  `experiments/crestron-dm-md-bridge/evidence/08-dmresetslot-101-capture.log`
  and `evidence/09-poe-cycle-capture.log`. Parse logic is identical to the
  live-verified `cip_proof_of_connect.py` reference implementation that
  completed real CIP handshakes against the chassis.

- `qsys_dm_md_ctp.lua` — mirror of the Python CTP driver's command and parse
  logic in Lua against Q-SYS Designer's `TcpSocket` + `Timer` + `Controls`
  APIs.

**NOT yet verified**: end-to-end live operation on real Extron / Q-SYS
hardware. These are source-code modules; packaging into `.pkp` or `.qplug`
is the next step and requires:

- For Extron `.pkp`: a donor package of similar shape (candidates in
  `corpus/extron-driver3/`) + a build script in the pattern of
  `experiments/skeleton_i20/build_i20.py` that applies named, verifiable
  edits to transplant our driver code into the donor's NRBF object graph
  and `DriverCommandAsset` list. The project's `tools/pkp_build.py` and
  `tools/pkp_asset.py` are the right primitives.

- For Q-SYS `.qplug`: use the `qsys_dm_md_ctp.lua` as the runtime script in
  a plugin manifest built in Q-SYS Designer. The `PluginInfo` /
  `GetProperties` / `GetControls` skeleton is included at the bottom of
  the Lua file for the plugin path; the file is immediately usable in a
  Script Component without `.qplug` packaging.

## Suggested deployment pattern (Extron)

For Rob's current chassis (CTP disabled, CIP available):

1. Deploy `cs_dm_md_cip_feedback.py` as a background component in the
   ControlScript project — provides real-time route and online-state
   feedback.
2. Issue routing COMMANDS via one of:
   - The chassis's SSH console using paramiko (if available on your Extron
     model) with `SETVIDEOROUTE` / `SETAVROUTE` text commands.
   - A chassis-side SIMPL# Pro program that bridges Extron EISC joins to
     chassis routing (same program slot that would be needed for endpoint
     I/O — "two codebases on one box" tradeoff).
   - Enable CTP on the chassis (`AUTHentication OFF` + `TELNETport ON` is
     the current firmware path; may change the security surface of the
     chassis — review before enabling) and use `cs_dm_md_ctp.py`.

For future installations with CTP enabled, `cs_dm_md_ctp.py` is the
drop-in driver.

## Scope reminder

These drivers do not and cannot address DM endpoint RS-232 / IR / Relay. The
chassis firmware owns that control plane via DM-link, and no console or CIP
path from outside can override it. See the four options enumerated in
`memory/extron-dm-md-cpu3-bridge.md`:

- Load a chassis-side SIMPL# Pro program (= two codebases on one box)
- Keep DM for routing only + add per-room-local control hardware
- Full rip-and-replace to Extron DTP3 / XTP (HDBaseT) or Extron NAV (AV-over-IP)
- Full rip-and-replace to Crestron DM NVX (IP, drivable directly via REST API —
  see `memory/nvx-direct-control-api.md` and
  `experiments/crestron-dm-md-bridge/evidence/11-one-processor-dm-vs-nvx.md`)

## File line counts

```
cs_dm_md_ctp.py           ~260 LoC
cs_dm_md_cip_feedback.py  ~280 LoC
qsys_dm_md_ctp.lua        ~220 LoC
```

Combined: ~760 LoC of driver code. All tests pass. Live chassis end-to-end
validation requires a real Extron processor or Q-SYS Core.
