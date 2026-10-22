# XPanel project — DM-CPU3_2.000.0013.c3p

Container is a plain .zip (deflate) renamed .c3p.

Panel type: `XPANEL Core 3 UI` built from `DMC-CPU3_V1.0_desktop.vtz` with
VTPro-e 6.20.00 on 2020-09-21. Smart Graphics platform (Flash/AIR).

## Key config: swf/Environment.xml

```xml
<CNXConnection>
  <Host>172.16.0.104</Host>
  <IPID>1</IPID>
  <Port>41794</Port>
  <EnableSSL>false</EnableSSL>
  <ProgramInstanceId><![CDATA[]]></ProgramInstanceId>
</CNXConnection>
```

So the XPanel is hard-wired to IP-ID 1 on the chassis, plain CIP, no SSL.
That matches the single "Gway" row in the chassis's IPTABLE output.

## Where the join map lives

The user panel pages compile into the SWF theme files:
- swf/BaseObjectsRSL.swf (5.4 MB) — SmartGraphics object library
- swf/BaseObjectsRSL_AIR.swf (8.4 MB) — same for AIR runtime
- swf/container.swf — the host runtime
- swf/themes/Black Glass for DM 2.0.swf (2.3 MB) — the theme + UI logic

The .vtx is a binary project header. .vtpage files are page definitions (also
binary). No joins.xml / joins.json sidecar in this package.

To recover the join map we need one of:
1. Crestron's OEM Programmer's Reference for DM-MD-CPU3 (research workflow is
   hunting; may be dealer-gated).
2. SWF decompile (JPEXS/FFDec on BaseObjectsRSL.swf + Black Glass theme).
3. Wireshark capture of this XPanel talking to the chassis after the user
   runs it and clicks route buttons.

Option 3 is the authoritative answer source. Options 1 and 2 can corroborate.

## Annotation.ini — not real joins

Annotation.ini has a `[DIGITAL]` section with joins 21817-21880 — these are
VTPro-e internal joins for font/color/size style registration, not user UI
controls. Ignore.

