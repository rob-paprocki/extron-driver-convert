# 17 - DM-RMC endpoint-side peering attempt: BLOCKED BY TOPOLOGY

## Scope correction (2026-10-16)

The original title and conclusions of this finding over-reached. This
experiment tested exactly ONE of two possible paths to the DM
proprietary dialect's L1 handshake, and I conflated them in the first
draft:

- **Endpoint-side peering** (this experiment): try to make the RMC
  initiate a sign-on to our host so we can observe its handshake bytes
  as it registers. **This path is blocked** by DM-link topology and the
  reason is captured below.
- **Master-side peering** (NOT tested here): us initiating a sign-on
  TO the chassis on `chassis:41794` as a "proprietary device peer" (the
  role a native Crestron master processor plays). This is a different
  handshake, lives inside `TLDMInterfaceDLL.dll`, and is NOT ruled out
  by anything in this evidence. See "What this does NOT close" below.

The original phrasing implied both paths were structurally dead. Only
the first one is.

## Goal (as originally run)

Finding 12 flagged two remaining pieces of the DM proprietary CIP
dialect as "two pcaps away" from being fully specified: the L1 TCP
handshake and the L4 heartbeat byte layouts. One way to collect those
pcaps is to make an endpoint call home to a listener we control. This
experiment pursued that direction: put a stub CIP master listener on
our host (0.0.0.0:41794), redirect the DM-RMC-4K-SCALER-C at output
101 to call home to us via `ADDMASTER <host-ip>`, let it register, and
capture the bytes.

## What the capture attempt showed

The attempt failed, and the failure revealed a hard topology
constraint on this specific path.

**The RMC is on an isolated DM-link link-local subnet, not the IP LAN.**

RMC ESTATUS output:

    MAC Address: 00.10.7f.c4.53.cb
    DHCP:        Disabled
    IP Address:  169.254.1.66
    Subnet Mask: 255.255.0.0
    Def Router : 169.254.0.1       <- chassis-as-gateway on DM-link
    IP Table:
    CIP_ID  Type    Status     DevID  Port   IP Address/SiteName
       183  Gway    ONLINE            41794  169.254.0.1

The RMC lives on 169.254.0.0/16. The only path OUT of that subnet is
the chassis itself at 169.254.0.1, which does NOT route to the
192.168.6.0/24 IP LAN - the RMC has no path to any host we can run a
listener on.

`ADDMASTER 192.168.6.114` returns `ERROR: Console command returned
error code -1` whether `AUTODISCOVERY` is ON or OFF, and whether we
try rebooting the CIP client or bouncing the Ethernet ports (bare
`PORTDISABLE` / `PORTENABLE` with no args turn into no-ops that just
print port state). The -1 almost certainly means "address not
reachable from any of my interfaces" - the RMC refuses to add a master
it cannot route to.

## Why this is structural (for the endpoint-side path)

The DM-link bus is not Ethernet. It is a proprietary HDBaseT-adjacent
transport, carried as a pseudo-NIC inside the chassis so the RMC own
IP stack can speak CIP to the chassis "DM master" process. The
169.254.x.x addresses are not visible outside the chassis - the
chassis does NOT act as an IP router between its DM-link segment and
the 192.168.6.0/24 LAN. That bridge is one-way: the chassis OWNS the
DM-link master role; it does not forward RMC-originated traffic to
arbitrary external masters.

For a stub listener on 192.168.6.114 to ever see RMC sign-on bytes,
one of the following would have to be true, and none are:

1. The chassis forwards TCP from 169.254.1.66 to 192.168.6.114 (it
   does not - no IP forwarding verb exists in the Crestron CLI, and
   the NAT table at ports :50002..:50322 is management-only, inbound).
2. We can put our host on 169.254.0.0/16 AND physically land on the
   DM-link segment (we cannot - DM-link is not a standard Ethernet
   port; it needs a DM-TX or RMC to bridge, which puts us right back
   on the restricted side of the same problem).
3. The RMC accepts an unreachable master and attempts out anyway (it
   does not - the -1 error is the enforcement).

## What this closes

- The **endpoint-side** path to the L1 handshake. The RMC will not
  initiate a sign-on to any host we control, because every host we
  can control sits on an IP subnet the RMC cannot route to.

That is it. That is the only thing this closes.

## What this does NOT close

- **The master-side L1 handshake path.** A real Crestron master
  processor opens one TCP session to `chassis:41794` and over that
  one socket carries BOTH chassis-local joins AND slot-addressed
  messages to/from endpoints (RMC ComPort writes, IR pulses, relay
  sets, COM RX feedback). The chassis internally bridges
  slot-addressed messages onto its DM-link master process and down
  to the endpoints. The endpoints never need to be reachable from
  the master subnet - the chassis IS the bridge. This is how a
  Crestron processor achieves one-socket control of the whole fleet.

  The byte-level L3 encoding for those slot-addressed messages is
  specified in finding 12 and implemented in `cresnet_cip.py`. The
  gap is NOT a reachability problem - the chassis is on 192.168.6.14,
  trivially reachable from our host. The gap is the L1 registration
  handshake that gets us accepted as a "proprietary device peer"
  rather than as an IPID 1 XPanel masquerade. That handshake lives
  inside the native `TLDMInterfaceDLL.dll`. Finding 12 touched the
  managed-side P/Invoke stub at `SimplSharpPro_exe.cs:176006` and the
  IPC struct `TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT` at
  `:167437`, but did NOT disassemble the DLL itself.

- **The L4 heartbeat.** Same story - lives in the same native DLL.

## Why "IPID 1 masquerade for endpoint I/O" would never have worked

Related clarification worth capturing while we are here. IPID 1 is
XPanel-space - flat digitals/analogs/serials. The chassis OEM program
publishes routing-adjacent joins there and that is what the
CIP-feedback half of the committed driver reads. **Slot-addressed
endpoint I/O does NOT ride on IPID 1 joins and never will.** Endpoint
I/O requires the chassis to accept us as a proprietary peer, not as a
touchpanel.

So the single-socket design never had a shortcut via IPID 1 even if
every finding above had gone the other way. The real path to
one-socket endpoint I/O is the master-side proprietary-peer
handshake, and that handshake is a native-DLL reverse engineering
project of days-to-weeks, deferred by choice (not blocked by physics).

## What this does NOT change

- The committed shipping design is unaffected. CTP :41795
  (authenticated) for routing commands + CIP IPID 1 masquerade for
  routing feedback is the dual-transport design in the unified `.pkp`.
  Endpoint I/O is NOT in that design regardless of socket count - see
  memory `extron-dm-md-cpu3-bridge` for the four honest deployment
  choices for display-local control.
- Finding 12 byte-level L3 payload specification is still the full
  deal for anything you would actually encode or decode on the client
  side, and remains the correct foundation if someone later tackles
  the DLL RE work for the master-side handshake.

## Chassis state verification

Pre-attempt and post-attempt ESTATUS captures match exactly (same IP,
same subnet, same IP Table with only the chassis-as-gateway entry at
CIP_ID 183, ONLINE). AUTODISCOVERY was turned back ON before close.
No lingering host-as-master entry (because the ADD never took effect).

## Artifacts

- `evidence/17-stub-handshake-capture-NEGATIVE.log` - full session
  transcript including before/after ESTATUS, all attempted verbs, every
  response, and the empty stub listener log.
