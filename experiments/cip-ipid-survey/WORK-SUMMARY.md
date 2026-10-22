# Driving Crestron IPID devices from a non-Crestron master

## What this set out to do

The goal was blunt: make something for an Extron processor that can do the
IPID things a Crestron control system does — drive a Crestron DM-MD8X8-CPU3-RPS
chassis, and ideally the wider family of Crestron gear that registers over the
network by IP ID, without a Crestron control brain in the rack.

We got there. The rest of this is how.

## The core result

A Crestron peer device (the DM-MD chassis, an NVX endpoint, an Automate VX2, a
Crestron Connected display) does not sit and wait to be polled. It dials *out*
to whatever control system owns it, on TCP 41794, and the two sides speak
Crestron's CGway peer protocol. The control system is the server; the device is
the client. That inversion was the thing we fought for weeks before it clicked.

Once it clicked, the shape of the solution fell out. An Extron processor can
*be* that control system. It accepts the inbound connection, answers the CGway
handshake (PROGRAM_READY, then the connect response), and from then on the two
exchange join values wrapped in nested slot containers: digital, analog,
serial. Everything the device does and everything you tell it to do rides that
one socket.

We proved it on real hardware. `dm_md_master_v0_0_1.pkp` runs on an Extron box,
the chassis connects to it, and routing works byte-for-byte: send the right
analog leaf to the right output-card slot and the matrix switches. We confirmed
it over SSH against the chassis — `DUMPDMROUTEINFO 33` reports the route change
the instant our write lands.

ComPort passthrough works too, and we know it works because of a jumper. With
RS-232 TX wired to RX on the RMC on output 1, a string we send comes straight
back as a serial feedback event. The bytes left the processor, crossed the DM
link, drove the physical pin, looped through the jumper, and came back.

## What is proven versus what is stubbed

Proven on hardware:

- The master-of-record session: handshake, heartbeat, the lot.
- Matrix routing, every output, byte-exact.
- ComPort send and receive on a DM-RMC endpoint.

Stubbed, and honest about it:

- IR pulse and relay close/open. The chassis stayed silent on every probe we
  threw at it, and without a meter on the relay contacts or a scope on the IR
  emitter we could not tell whether our writes were firing the pins quietly or
  missing entirely. That is a live-hardware question, not a protocol one, and
  it waits for a bench with the right instruments.

The split matters. Routing and RS-232 cover most of what anyone actually asks a
DM-RMC to do: switch video, talk to a projector. IR and relay are the long tail.

## Why the slot architecture took so long to read

The chassis numbers its own guts in a way that is not obvious from outside.
Input cards live at slots 1 through 8. Output cards start at slot 33. For the
longest time we were writing routing commands to slot 1, watching nothing
happen, and assuming the protocol was wrong. The protocol was fine. We were
addressing input card 1 and asking it to behave like a video output.

The endpoints hang off a second tree entirely — an endpoint cluster at slot 1
with the output index underneath it, which is a different slot 1 than the input
card. The ComPort write that worked for output 1 looked like it was doubling up
on slot 1 by coincidence; it was actually two distinct address components that
happened to share a number. That ambiguity hid a real bug for outputs 2 through
8, which we caught and fixed only once the architecture was written down
plainly.

## The survey: what else this unlocks

The DM-MD work produced a reusable thing — the CGway envelope and the
nested-container encoding. Any Crestron device that registers by IP ID speaks
the same envelope. So we read Crestron's own SIMPL symbol library and pulled
the complete join map for the devices worth targeting next:

- Automate VX2 (the camera auto-switcher): 276 named joins.
- DM-NVX encoder/decoder endpoints: around 286 joins covering routing,
  streaming, and HDMI feedback.
- The NVX Director: roughly 6,000 joins, because it carries a 1,000-endpoint
  routing fabric as a flat join surface. It is the giant of the set.
- Crestron Connected displays: 183 joins in the legacy single-symbol form, 161
  in the newer modular form. Power, fifteen source-select slots, volume,
  picture controls, lamp hours, warm-up and cool-down progress, temperature,
  source names, emergency messaging.

That last one is the sleeper. Crestron Connected is a certification a long list
of display vendors carry: Panasonic, Sony, NEC, LG, Samsung, Epson, Christie,
Barco and more. One Extron driver built against that 183-join contract drives
any of them. The contract is already fully declared; no further reverse
engineering stands between us and that driver.

## The honest limit of the survey

The symbol library gives you the declared interface — every named join, its
direction, its type. Paired with the CGway envelope we already derived, that is
enough to build a working driver for the named-join parts of any of these
devices today.

It is not enough for anything the device does *off* the join envelope. The
DM-RMC's ComPort passthrough is the proof: those writes ride the same socket
but use a slot path that appears nowhere in the symbol library. We only found
it by reading the chassis's own behavior on the wire. NVX endpoints almost
certainly hide their COM and IR ports the same way. For those, the symbol
survey tells you nothing and you are back to live capture or driver
decompilation.

So the two approaches are complements, not rivals. Read the driver files once
per protocol family to learn the envelope. After that, the symbol survey is a
fast onramp for every device in that family — until you hit an out-of-band
feature, at which point you read driver files again. Reading every driver cold
would be slower and, for the obfuscated ones, often blocked outright.

## Where everything lives

- `experiments/crestron-dm-md-bridge/` — the DM-MD spike: the master-of-record
  server, the driver, the build scripts, and the evidence trail from first
  handshake to proven routing.
- `experiments/cip-ipid-survey/` — the join maps for VX2, NVX, the Director,
  and Crestron Connected displays, with a README that lays out the shared
  architecture.
- `dm_md_master_v0_0_1.pkp` — the shipping driver. Routing and ComPort proven;
  IR and relay stubbed and marked.

## What a next step looks like

Pick a device from the survey that is worth productizing. The Connected display
is the obvious candidate: it reaches the most hardware, its contract is clean,
and nothing is left to reverse engineer before building. Build its `.pkp`
against the existing harness, point a real display's IP table at the Extron
processor, and watch it come up.
