# Chassis↔master TLS/SSL analysis

## Short answer

The chassis's choice to initiate TLS vs plain on its outbound master-link
is controlled by a **chassis-side registry setting named `SSL`**
(`HKLM\Crestron\System\SSL`), surfaced via console as
`SECUREGatewaymode`, NOT by the `SSL Certificate` radio in XPanel.

- `SSL = 0 or 1` → `isSSLEnabled = false` → chassis uses
  `ConnectTcpServer(..., 41794)` (plain CIP, what we're already working with).
- `SSL = 2+` → `isSSLEnabled = true` → chassis uses
  `ConnectTcpSecureServer(..., 41796)` (TLS on port 41796).

Source: `ProtoUtil_dotnet/ProtoUtil.decompiled.cs:1857`:

    isSSLEnabled = Convert.ToUInt32(val.GetValue("SSL", (object)num)) > 1;

The chassis's outbound-to-master connect code
(`ProtoTcp_dotnet/ProtoTcp.decompiled.cs:7407-7426` for Ethernet slave,
and `:8892-8966` for TCPGatewayClient) branches entirely on
`InitialParametersClass.isSSLEnabled`, and when true, uses
`SecureCrestronCIPPort` (41796) with `ConnectTcpSecureServer()`.

The port in the IP table (41794) is the UNSECURE port. When isSSLEnabled
is true, the chassis **completely ignores the IP table's port** and uses
41796 for the TLS connect. Confirmed at :7420 and :8933:

    crestronCIPPort = MasterIPTable.Master_IPTable.SecureCrestronCIPPort;
    ...
    flag = ConnectTcpSecureServer(ipaddress, crestronCIPPort, PCSiteName, true);

## Byte-level TLS handshake sequence

1. Chassis TCP-connects to `<master-ip>:41796` (not 41794!).
2. Chassis is the TLS CLIENT. Sends ClientHello.
3. Master responds ServerHello + Certificate + ServerHelloDone.
4. Standard TLS handshake completes (chassis validates master cert per
   its `SSLMode` setting: Self = accept self-signed, CA = require CA).
5. After TLS: same CIP handshake as plain:
   master sends PROGRAM_READY (0x0F 0x00 0x01 0x02) over TLS,
   chassis sends ALTERNATE_CONNECT (op 0x0A), master sends
   CONNECT_RESPONSE (op 0x02).

If SCIP creds are set (`CSAuthenticateUN`+`CSAuthenticatePwd` registry
or `SetCSAuthentication` CLI), the chassis adds a device-router
connect message with embedded `[domain\]user:password` ASCII
(ProtoTcp:8490-8504 for DeviceRouter path).

## Why the 3-minute silent connect you observed

With chassis `isSSLEnabled = true` and master listening on **41794**
(unsecure port) with TLS wrap: the chassis is trying to connect to
**41796** on your host, not 41794. So those "accept from 192.168.6.14"
events on :41794 you logged are NOT the chassis's SSL-enabled
master-link attempts — those are PLAIN connections from some other
chassis-internal service still trying unsecure.

The real SSL chassis-to-master attempt would land on `:41796` where
nothing is listening, chassis gets ECONNREFUSED, retries. Your log
shows no :41796 traffic because `tcp_server_tls.py` had moved to
:41794.

Flipping `SSL Certificate: Self` on the XPanel does NOT set `SSL = 2`
in the registry — that radio controls which SSL cert the chassis
PRESENTS on its own HTTPS/WebUI/XPanel/CTP services (port 443, 41797,
etc.) when THOSE services accept inbound TLS connections. It is a
different setting from the "should I use SSL for my outbound master
connection" `SSL` registry key.

## How to actually enable chassis-to-master TLS

Two parts:

1. **On chassis**: set `HKLM\Crestron\System\SSL = 2` (or use the
   corresponding console command — probably `SSL ON` or `SETSSL`
   — I couldn't find the exact verb in the fragment of HELP ALL we've
   captured; worth asking Toolbox or looking at `SETSSL` in CLI help).
   Reboot. After reboot, isSSLEnabled=true.

2. **On master**: listen on `:41796` with TLS, present a cert. If
   `SCIP Authentication Credentials` are configured on the chassis
   (`SETCSAUTHENTICATION -N:user -P:pw`), master must also validate
   the ASCII `[domain\]user:password` sent in the DEVICEROUTER_CONNECT
   message body — otherwise chassis logs "Reverting to unsecure
   connection" and falls back to plain :41794.

### Minimal `cip_master_server_tls.py` changes

Change the listen port to 41796 (that was the right port we originally
had):

    srv.bind(("0.0.0.0", 41796))

The existing `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)` setup with
self-signed cert and `verify_mode = ssl.CERT_NONE` (we don't require
client cert) should work for `SSLMode = Self` chassis-side acceptance.

For `SSLMode = CA` chassis-side, you'd need a cert chain signed by
a CA the chassis trusts. Easiest: generate a local CA, sign the
server cert with it, import the CA into the chassis's trust store
via Toolbox.

Min TLS version: chassis's `AuthenticationInterface.EnforceMinTlsSslOption`
is called at startup (ProtoUtil:1861). The actual min version depends on
chassis firmware policy — TLSv1.2 is a safe default to accept.

## Role of the IP table entry's Port field

The IP table Port (shown as 41794 in your Toolbox IP Table Setup for
IPID 03) is only consulted by the chassis's TCPGatewayClient when
`isSSLEnabled == false` (ProtoTcp:8962):

    crestronCIPPort = (InDeviceMode) ? m_pGatewayClientIPTableEntry.PortNumber
                                      : MasterIPTable.Master_IPTable.CrestronCIPPort;

When SSL is on, `crestronCIPPort = SecureCrestronCIPPort` (41796)
regardless of what the IP table says. So the greyed-out Port field in
Toolbox is NOT a bug — it's that the field is advisory for the
non-SSL path only, and SSL uses the fixed 41796 constant.

## Role of `OnlyWorkInSecureModeIfSSLIsEnabled`

Per-entry flag on an IP table entry (`ProtoIptable_dotnet:589`).
Default false. When set + isSSLEnabled, the chassis's SERVER-side
dispatcher at `ProtoTcp:2447` DROPS inbound unsecure connections
from this peer. It is auto-set to TRUE for IPID 0x01 (loopback)
when the device is registered via TLDM (ProtoTldm:3608). Rarely user-
controllable; mostly internal.

## 15-line summary

- `SSL Certificate: Off/Self/CA` radio in XPanel = chassis's own
  HTTPS/WebUI cert mode. Does NOT enable TLS on master-link.
- Separate chassis-side registry setting `HKLM\Crestron\System\SSL`
  (0/1 = off, 2+ = on) controls `isSSLEnabled` global flag.
- When `isSSLEnabled=true`, chassis connects to `<master>:41796`
  via `ConnectTcpSecureServer` with TLS. Chassis is TLS CLIENT.
- When `isSSLEnabled=false`, chassis connects to `<master>:41794`
  plain TCP (what we've been doing successfully).
- Port 41796 is a hard-coded constant `SECURE_CIP_PORT`
  (ProtoEngine:1803), used instead of IP table Port when SSL is on.
- The 3-minute silent-connect you saw was NOT a TLS handshake issue
  — it was something else connecting plain to :41794 while we
  thought the chassis was doing SSL there. The real SSL attempts
  would have been on :41796 against nothing (ECONNREFUSED).
- To enable TLS: set the chassis's SSL registry to 2+ (CLI probably
  `SSL ON` or similar — I didn't find the verb in HELP ALL fragment,
  Toolbox GUI likely has a setting too — try chassis's XPanel's
  SSL Certificate = Self + reboot and see if `SSL` registry gets
  auto-bumped, since on InDeviceMode=true the firmware force-sets
  this).
- Server-side: change listen to :41796, SSLContext(PROTOCOL_TLS_SERVER)
  with self-signed cert, chassis expects it in SSLMode=Self.
- If SCIP creds are set, master must parse DEVICEROUTER_CONNECT
  message body for ASCII `[domain\]user:password` and validate.
- Flipping SSLMode=Self on chassis's XPanel without also setting
  `SSL` registry = your WebUI uses self-signed HTTPS, master-link
  stays plain. That matches exactly what you observed.
