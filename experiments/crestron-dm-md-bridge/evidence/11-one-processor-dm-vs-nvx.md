# 11 — One-processor architecture: feasibility across DM-MD-CPU3 vs NVX

**Produced:** 2026-10-10 by workflow `wf_568983fd-5e4` (5 parallel readers → adversarial verify → single-writer synthesis).
**Status:** research-grade. External API claims (NVX REST paths, auth cookie semantics, Pepperdash wrapper interfaces) are from Crestron docs + OSS reads and are not independently re-verified; verify before coding against any specific path or interface.

**Context:** this writeup extends evidence/07 and the three live-chassis captures (evidence/08, 09, 10). Rob's constraint: one control processor (Extron OR Q-Sys), not two. The DM-MD-CPU3 captures proved the OEM program doesn't expose endpoint I/O over CIP. This writeup asks the next question honestly: is there ANY non-SIMPL path to endpoint I/O on this chassis — and does NVX change the answer?

---

# Can we do it with ONE processor on this chassis?

## Path A: Chassis-NAT'd endpoint consoles

**Verdict: Dead end for I/O.**

The :50322 socket exposed through chassis NAT is a CTP/management console — it carries IPTable, HELP, network setup, and the familiar `SETAVROUTE/SETVIDEOROUTE/SETAUDIOROUTE` routing verbs on :41795. It does **not** expose COM/IR/Relay transmit verbs on the RMC. The RMC's physical pins are architecturally tunneled over the DM link and surface in SIMPL# as **slot joins of the parent CPU3 chassis**, not as endpoint-local sockets. PepperDash's `DmRmc4kScalerCController.cs` wrapper confirms this: it implements `IIROutputPorts, IComPorts, IRelayPorts` on the chassis's slot object. The DM-RMC-4K-SCALER-C supplemental guide also states its LAN port is "setup-only when DM IN is connected."

Translation: you can tell the chassis which input goes where, but you cannot tell the chassis to send `PWR ON\r` out of the RMC's COM port without a program running inside the chassis that owns that slot.

## Path B: Core3 ADDMaster slave registration

**Verdict: Theoretically possible for the handshake, practically dead for I/O.**

The CIP handshake on TCP/41794 is reverse-engineered to the byte level (moty66/node-red-contrib-cip, python-cipclient, cresip, CommandFusion/CIP):

1. Master accepts TCP
2. Master sends 0x0F WHOIS (`0f 00 01 02`)
3. Slave sends 0x0A CLIENT_SIGNON with its IPID + 9 device-type bytes
4. Master sends 0x02 CONN_ACCEPTED (`02 00 04 00 00 00 03`)
5. Master sends 0x05 UPDATE_REQUEST, then 0x0D/0x0E ping/pong at 10 s

Both Q-Sys Lua `TcpSocketServer` and Extron `EthernetServerInterface` can host this. Then it dies on three stacked problems:

- **The flat-join model does not apply to DM endpoints.** Every public CIP implementation decodes only the XPanel digital/analog/serial join envelope (joins up to 65535 + Smart Objects). DM-RMC I/O does **not** ride that envelope — it is a slot-addressed proprietary device-message dialect that no public OSS has decoded. The 9 device-type bytes a DM-RMC emits in CLIENT_SIGNON are undocumented, and the port-command messages for COM TX/RX, IR pulse, and Relay close are unmapped.
- **The CPU3 is likely already the endpoint's auto-assigned master**, having provisioned the endpoint IP on the private DM VLAN. `REMMaster` is needed first, and the chassis may re-assert itself on reboot or DM-link renegotiation.
- **Outbound TCP/41794 from endpoint IP through chassis NAT to arbitrary external hosts is unverified.** The chassis may permit, drop, or force-route to its known master only. Newer firmware adds CIPS (TLS on :41796) with device certs — another reverse-engineering layer.

This is a research project with an ongoing firmware-churn maintenance tax, not a deployment path.

## Path C: SIMPL# Pro add-on

**Verdict: Works. Officially supported. But it's a second processor — call it that honestly.**

A used CP3 (~$800) or CP4 (~$2000) running a ~50-line SIMPL# Pro program that (a) owns the DM/RMC device objects as slot devices of the chassis, and (b) exposes signals to Extron via EISC or to Q-Sys via plain TCP/UDP ASCII. This is what shipping integrators do when they need RMC I/O from a non-Crestron brain. Vendor-blessed, Crestron handles firmware churn, Toolbox status stays accurate. The honest framing: you buy a processor, you sign a dealer/AIP agreement to load the program, and you run two codebases on two processors. Calling this "one processor" is a definitional stretch.

**Variant that genuinely eliminates the second processor:** replace each DM-RMC with an Extron DTP3/NAV receiver or Q-Sys I-O Flex at each display. The chassis handles routing only; local I/O moves off the DM-tunneled slot entirely. Cleaner than Path C above about four displays.

## Verdict for this chassis

**On the DM-MD8X8-CPU3-RPS + DM-RMC fleet, true single-processor control from Extron or Q-Sys is not available for endpoint I/O.** Routing-only works fine from either (over :41795 CTP). Endpoint COM/IR/Relay forces either a second Crestron processor (Path C) or an RMC hardware swap.

---

# What changes with NVX?

## NVX endpoints

**NVX endpoints are standalone IP devices with a documented HTTPS REST + WebSocket API. This is the architectural pivot.**

- **Direct API:** HTTPS :443 (CresNext/JSON) + `wss://device/websockify`. Full tree: `https://sdkcon78221.crestron.com/sdk/DM_NVX_REST_API/`
- **Auth:** cookie session via `POST /userlogin.html` (form-urlencoded `login=user&&passwd=pw`, Origin+Referer required). Server returns `AuthByPasswd`, `TRACKID`, `iv`, `tag`, `userid`, `userstr` cookies. **`AuthByPasswd` rotates per response and must be updated.**
- **I/O verbs on `/Device/ControlPorts`:**
  - `Serial.{1}.TransmitData` / `ReceivedData` / `BaudRate` / `DataBits` / `Parity` / `StopBits` / `HardwareHandshake` / `SoftwareHandshake` / `SendBreak` / `ActivateRts` — bidirectional RS-232 up to 115.2k
  - `Infrared.{1,2}.TransmitData` / `TransmitDataFormat` / `DownloadedFile` / `ParsedCommands` — IR TX with driver upload
  - `AudioVideoInputOutput.{...}.TransmitCecMessage` / `ReceiveCecMessage` — CEC send/receive
- **Routing:** `/Device/AvRouting` with L3 + UsbFollowsVideo; `/Device/StreamTransmit`, `/Device/StreamReceive`
- **Standalone operation:** yes, functionally. The spec-sheet phrase "device control via IR and RS-232 requires integration with a Crestron 3-Series or later control system" is boilerplate predating the REST API and refers to the SIMPL path only. Domotz validated the REST path in production against DM-NVX-360.
- **CIP role:** the endpoint is a CIP **client** (Peer-Gateway, outbound-only via `IpTableV2`). It will not accept inbound CIP from an arbitrary master. REST is the integration surface, not CIP.

**Hard caveats:**

- **No NVX endpoint model has a physical relay.** Every model is `com:1, ir:2, relay:0, versi:0`. The schema has a Relay dictionary; no NVX hardware wires it. For relays, pair with CEN-IO-DIGITAL-104 or move relays onto the Extron/Q-Sys processor.
- **Card variants (-C) in a DMF-CI-8 chassis drop both COM and IR** — the manual states "IR and RS-232 are not available on card-based models." CEC-only.
- No native Q-Sys `.qplug` and no shipped Extron `.pkp` for NVX. Integration is custom Lua / custom ControlScript module, ~1–2 weeks.

## NVX Director

**What it is:** a fleet-management appliance for virtual-matrix routing, domain/multicast management, device-map, and diagnostics across 100–1000 endpoints (DIR2 / DIR-160 / DIR-ENT; DIR-80 discontinued). DIR2 is a Dell OptiPlex running AlmaLinux.

**What it provides northbound:** web UI + Crestron CIP for a 3-/4-Series processor. **No publicly documented REST, SOAP, or SNMP on the Director itself.** Adjacent Crestron REST APIs exist for individual NVX endpoints and for VC-4, but neither is the Director's own API. The SDK is dealer/service-provider gated.

**Is it required?** No. For strictly third-party control the per-endpoint REST API bypasses the Director entirely — exactly how Domotz operates.

**Risk if adopted:** CVE-2020-16839 affected DIR/DIR-80/ENT pre-DM-XIO 1.0.3.802 — unauthenticated WebSocket could change the admin password. If you buy a Director, pin current firmware.

## One-processor architecture with NVX

**Extron with NVX (IPCP Pro + NVX fleet, no Crestron brain):** ControlScript already uses the exact pattern. Your own `pkp2cs.py:1502-1540` confirms shipped Extron modules import `urllib.request` + `urllib.error` and call `build_opener(HTTPBasicAuthHandler, HTTPSHandler(context=self._context))` for authenticated HTTPS. Build a cookie-jar wrapper that handles `AuthByPasswd` rotation; wrap `/Device/AvRouting` and `/Device/ControlPorts/Serial/{n}` / `Infrared/{n}`. Long-poll `/Device/Longpoll` or hold a WebSocket on `/websockify` for state events.

**Q-Sys with NVX (Core + NVX fleet, no Crestron brain):** Q-Sys Lua provides `HttpClient` (TLS 1.0–1.3, Basic/Digest/token auth), `WebSocket`, and `TcpSocket` natively. Mirror Domotz: HTTPS REST login, long-poll `/Device/Longpoll` for events, map `AvRouting` + `ControlPorts.Serial.TransmitData` + `Infrared.TransmitData` to Q-Sys controls as a `.qplug`. No native QSC NVX plugin exists; it's custom Lua against the same REST surface.

**Both platforms are architecturally symmetric on NVX.** The barrier that killed one-processor on DM-RMC (chassis-tunneled slot addressing + undocumented CIP device dialect) is gone — NVX endpoints are first-class IP devices.

## Verdict for NVX

**On NVX, true one-processor control from Extron or Q-Sys is viable for everything except physical relays, using Crestron's own documented REST API.** No CIP, no SIMPL, no second Crestron processor. The right SKUs for this plan are standalone 350/351/360/363 (not -C card variants).

---

# The one experiment to run next

**Scope:** 15–30 minutes on a bench NVX-350 or NVX-360 at firmware 7.3.5+. Infrastructure: `curl` + a USB-serial adapter. Self-signed device cert, so skip hostname check (`ssl.create_default_context` + `check_hostname=False`).

**Three requests:**

1. **Login**
   ```
   POST https://<nvx-ip>/userlogin.html
   Content-Type: application/x-www-form-urlencoded
   Origin:  https://<nvx-ip>/
   Referer: https://<nvx-ip>/
   Body: login=admin&&passwd=<pw>
   ```
   Capture cookies: `AuthByPasswd`, `TRACKID`, `iv`, `tag`, `userid`, `userstr`. 403 means auth failed.

2. **Discover the schema**
   ```
   GET https://<nvx-ip>/Device/ControlPorts
   (send all cookies, using the rotated AuthByPasswd from step 1's response)
   ```
   Verify the response JSON contains `Serial` and `Infrared` dictionaries with `TransmitData`, `BaudRate`, `DataBits`.

3. **Drive the COM port**
   ```
   POST https://<nvx-ip>/Device
   Body:
   {"Device":{"ControlPorts":{"Serial":{"1":{
     "BaudRate":9600,"DataBits":8,"Parity":"None","StopBits":1,
     "TransmitData":"PWR ON\r"
   }}}}}
   ```
   Watch the physical 5-pin COM terminal with a USB-serial loopback. Repeat against `/Device/ControlPorts/Infrared/1/TransmitData` with a hex IR frame to resolve IR.

**What this one capture resolves:**

- Definitively kills the "requires 3-Series" spec-sheet claim with primary evidence
- Nails down the cookie-rotation and payload pattern both Extron ControlScript (`urllib.request` + `HTTPSHandler` + cookiejar) and Q-Sys Lua (`HttpClient` with persistent `CookieHeader` concat) will reuse
- Validates the architectural recommendation for the NVX build
- Exposes any undocumented auth quirks (XSRF headers, cert pinning, cookie-rotation gotchas) **before** any custom-module development is sunk

Why this and not a CIP capture against the DM-RMC: the RMC capture would at best tell you which undocumented CIP dialect to spend six months reverse-engineering. The NVX capture validates the actually-deployable path.

---

# Pragmatic recommendation

**Today, with the DM-MD8X8-CPU3-RPS in place:**

1. Keep routing on Extron or Q-Sys via :41795 CTP — this already works at zero cost, no second processor needed for the matrix.
2. For display-local COM/IR/Relay, pick one:
   - **Rip out the RMCs:** replace with Extron DTP3/NAV receivers or Q-Sys I-O Flex at each display. Cleanest. Scales better than the SIMPL# bridge above ~4 displays.
   - **Keep RMCs + add a used CP3** running a 50-line SIMPL# Pro bridge program that exposes RMC I/O to Extron via EISC or Q-Sys via TCP ASCII. Vendor-blessed, two codebases, done in a weekend.
   - **Do not** reverse-engineer CIP + the RMC device dialect. Only pursue if the deliverable is itself a public CIP master implementation. Not a deployment path.

**Future build (NVX):**

- Specify **standalone 350/351/360/363** anywhere you need COM or IR. Card variants give up both.
- **Skip the Director** unless virtual-matrix abstraction across hundreds of endpoints is a hard requirement. The per-endpoint REST path doesn't need it, and the Director itself has no public REST.
- For **relays**, pair NVX with CEN-IO-DIGITAL-104 or wire relays off the Extron/Q-Sys processor directly. No NVX hardware wires relays.
- **Pick the brain (Extron IPCP Pro vs Q-Sys Core) on your UI/room-control story**, not the control plane. Both reach NVX via the same REST surface and both cost roughly the same in custom-integration time.
- **Run the 15-minute experiment above on a bench unit before procurement.** It is cheap, decisive, and the capture becomes the first commit of the integration module.

**One-sentence framing:** The DM-RMC chassis forces two processors (or a hardware swap); NVX ends that forcing. If one-processor flexibility is the goal, NVX is the hardware you buy for the next build, and the bench test above is the thing you run this week.
