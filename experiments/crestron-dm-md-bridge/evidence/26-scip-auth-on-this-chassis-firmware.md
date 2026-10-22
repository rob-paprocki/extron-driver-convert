# 26 - SCIP authentication on this chassis firmware - configuration path broken

## Short answer

The chassis's SCIP (Secure CIP) authentication **mechanism** is present and
responsive, but the **configuration mechanism** on this specific chassis
firmware (DM-MD-CPU3-RPS v1.8001.5769.27432) is broken in both the Toolbox
GUI and the CLI. Credentials cannot be stored. Plain (unauthenticated)
master-of-record remains the shipping path, as it was before this probe.

## What we proved worked (SCIP mechanism)

- Our master server sends `CONNECT_RESPONSE` with `Mode = 0x60` (0x20 for
  hb-rsp-check + 0x40 for "I require auth"). Chassis receives, acknowledges
  the request, and responds with `op=0x0B AUTHENTICATE` carrying
  `[Handler:2BE][ASCII creds]`.
- So the full challenge-response path is wired on both sides.

## What's broken (SCIP configuration)

- **Toolbox IP Table Setup → SCIP Authentication Credentials section is
  greyed out** on this chassis. The Domain\Username and Password text
  fields can't be edited; the Apply/Erase From Device buttons are inert.
- **CLI `SETCSAUTHENTICATION -N:test -P:test123`** returns the message
  "Success. Please reboot for new parameters to take into effect." - but
  after reboot, querying `SETCSAUTHENTICATION` (no args, shows current)
  reports:
  ```
  Domain Name: Not Set
  User Name:  Not Set
  Password:   Not Set
  ```
  The "Success" message is a lie or references something that doesn't
  survive persistence.
- **CLI `SETCSAUTHENTICATION -D:... -N:... -P:...`** (adding Domain) is
  rejected with "Invalid number of parameters" - -D isn't a valid flag
  on this firmware's SETCSAUTHENTICATION, despite the current-state
  query showing a "Domain Name" field.
- Chassis consequently sends `AUTHENTICATE` with ASCII body `":"` -
  empty user, empty password, just the separator - and our server
  correctly rejects (session churns at ~10s intervals).

## Working theory

Either:
1. This chassis firmware's SCIP CLI/GUI path is bugged/incomplete and
   was never fully wired to the credential store, OR
2. SCIP credentials require some *other* prerequisite setting to be ON
   (SSL in the registry, 802.1X auth, cloud-connect, etc.) that we
   haven't satisfied.

The Toolbox GUI being greyed out across all SCIP controls strongly
suggests (1) - it's a feature gate on this firmware version that
Toolbox detects and visually disables.

## No shipping impact

- The committed one-socket master-of-record design (finding 24) runs on
  plain CIP :41794 with no auth beyond IP-table-based "the connecting
  source IP must match the configured master IP" lookup.
- This is adequate for a trusted control-LAN deployment, which is the
  normal Crestron deployment pattern.
- If SCIP (user:password auth) is ever genuinely required, this chassis
  needs a firmware upgrade to a version where the SCIP config path
  actually works - or Crestron support will have to tell us the exact
  config gate.

## Cleanup done

- `CLEARCSAUTHENTICATION` run (no-op since nothing was stored).
- SCIP demo server stopped. Plain v2 master-of-record server
  (`cip_master_server_v2.py`) relaunched and chassis connected normally.

## Also noted alongside

Found several related CLI verbs we didn't exercise but worth knowing
about:
- `AUTHentication` - global authentication on/off (currently ON)
- `NTLMAUthentication` - NTLM web auth
- `USERPAGEAuth` - user webpage auth
- `SSLVERIFY` - SSL cert verification mode
- `8021XAUthenticate`, `8021XTRUStedcas`, `8021XVALidateserver` -
  802.1X network auth stack (which may be the actual real-world
  auth path for this chassis in enterprise deployments)
- `CERTIFicate` - add/remove/list certificates (would be relevant for
  TLS CA mode)
