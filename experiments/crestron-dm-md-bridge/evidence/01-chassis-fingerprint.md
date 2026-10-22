# DM-MD8X8-CPU3-RPS @ 172.16.0.104 — fingerprint

Captured 2026-10-07 via SSH (admin, blank password + Enter past terms).

## VER
```
DM-MD8X8-CPU3-RPS Cntrl Eng [v1.8001.5769.27432 (Oct 18 2024), #8D52016F] @E-00107fda192a
```

## INFO (abridged)
```
Category:          Control System
SIMPL:             Level 1
SIMPL+:            Level 1
Web Server:        Enabled: Level 1
FTP Transfers:     Enabled: Level 1
Ethernet Ports:    2
IP Table:          Yes
IP Table Format:   DIP: Level 2
Max IP Entries:    252
IP Masters:        0
Password:          Yes
Front Panel Slot:  68
Max Programs:      10
Core3UILevel:      1.00
```

## WHOAMI
```
admin  Administrator  Users, Connects, Programmers, Operators, Administrators
```

## IPTABLE
```
CIP_ID  Type    Status     DevID  Port   IP Address/SiteName      RoomId
     1  Gway    OFFLINE           41794  127.000.000.001          Not Specified
```
Only one row. CIP_ID=1 is the local XPanel gateway slot. CIP_IDs 2-FE are free.

## PROGREGISTER
```
No programs are registered
```
No user-authored SIMPL programs; the active behavior is the chassis OEM firmware program at slot 0 (reached via `/cwsprogram0/...` on CWS).

## AUTHENTICATION / SSL
```
AUTHENTICATION: ON.
SSL: Off, Self Signed
Only TLS1.2 is Supported.
```
CIP on 41794 is plain TCP. The web UI serves TLS 1.2 only; current admin cred is blank.

## REPORTDM + CARDS — populated slots

Inputs:
- Slot 1: DMC-4KZ-HD HDMI
- Slot 2: DMC-4KZ-HD HDMI
- Slot 3: DMC-4KZ-HD HDMI
- Slot 4: DMC-4KZ-HD HDMI
- Slot 6: DMC-4KZ-C HDBaseT  <- DM-TX-4K-100-C-1G attached
- Slot 8: DMC-4KZ-C HDBaseT  <- DM-TX-201-C attached
- Slots 5, 7: EMPTY

Outputs:
- Slot 101: DMC-4KZ-CO-HD HDBaseT  <- DM-RMC-4K-SCALER-C "Roombox" attached
- Slot 102: DMC-4KZ-CO-HD HDBaseT (bare)
- Slot 103: DMC-4KZ-CO-HD HDBaseT (bare)
- Slot 104: DMC-4KZ-CO-HD HDBaseT (bare)
- Slot 105: DMC-4KZ-CO-HD HDBaseT (bare)
- Slot 106: DMC-4KZ-CO-HD HDBaseT (bare)
- Slot 107: DMC-4KZ-HDO HDMI (direct output)
- Slot 108: DMC-4KZ-HDO HDMI (direct output)

The only endpoint actually needing pass-through control is **output 101 — DM-RMC-4K-SCALER-C**, plus the two input TXes (6.1, 8.1).

## DUMPDMROUTEINFO
Matrix idle. All outputs show "No Video connection", "No Audio connection", "No USB connection".

## Hardware chassis (SHOWHW)
Processor: DM-MD8X8-CPU3-RPS, slot 68 is C2I-DM-MD8X8-CPU3-RPS-DISPLAY (front LCD).

