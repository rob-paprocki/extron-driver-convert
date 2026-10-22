# 15 — Correction: NAV and NVX are AV-over-IP, not HDBaseT; vendors don't interop at that layer either

**Date:** 2026-10-11

Evidence/14 just corrected the HDBaseT story but then conflated Extron **NAV** with Extron's HDBaseT line (DTP3/XTP). **NAV is Extron's AV-over-IP family — same category as Crestron DM NVX, Q-SYS NV, SDVoE, NDI.** Not HDBaseT. Lumping it with DTP3 in a "receiver swap" discussion was wrong.

## Correct taxonomy

| Family | Transport | Vendor-interop? |
|---|---|---|
| **HDBaseT-based** | Copper point-to-point (Valens chip baseline + vendor control layers) | **No.** Each vendor's layer (Crestron DM, Extron DTP3, Extron XTP, AMX HPX, Kramer BT, Lightware) is incompatible with the others' at the control/EDID/HDCP channel. |
| **AV-over-IP** | 1 GbE / 10 GbE (vendor packetization + vendor control plane) | **No.** Crestron DM NVX, Extron NAV, Q-SYS NV, Lightware MMX don't interop with each other. (SDVoE is a shared physical/compression layer that SOME products support, and NDI is a near-standard, but not what most AV-over-IP ecosystems use at their primary layer.) |

## Updated rip-and-replace options

Each ecosystem is a complete all-or-nothing swap because transmitters and receivers only pair with their own:

- **To Extron HDBaseT (DTP3 / XTP):** Extron matrix + DTP3/XTP transmitters + DTP3/XTP receivers. Copper point-to-point.
- **To Extron AV-over-IP (NAV):** Extron NAV encoders + NAV decoders + Extron processor. Ethernet-based. Needs network capacity.
- **To Crestron AV-over-IP (DM NVX):** NVX encoders + NVX decoders + optional NVX Director. Ethernet-based. **Drivable by Extron OR Q-SYS directly via NVX's REST API** (per evidence/11) — the one path that gets Rob his "one processor" without a Crestron processor in the loop.
- **To Q-SYS AV-over-IP (NV):** Q-SYS Core + NV encoders/decoders. Different ecosystem entirely; drives everything through Q-SYS.

## What this changes for Rob's four-options list

Evidence/14's "Full rip-and-replace to Extron DTP3" was listed as option C and "Full rip-and-replace to NVX" as option D. Those are TWO of multiple possible IP migrations; the full matrix is:

| Option | Family | One-processor-Extron? |
|---|---|---|
| **A. SIMPL# Pro on existing chassis** | — | Partially (two codebases on one box) |
| **B. DM for routing + per-room control boxes** | — | Yes |
| **C. Full rip-and-replace to Extron HDBaseT (DTP3/XTP)** | HDBaseT | Yes |
| **D. Full rip-and-replace to Extron NAV** | Extron AV-over-IP | Yes |
| **E. Full rip-and-replace to Crestron NVX** | Crestron AV-over-IP | **Yes, with Extron driving NVX via REST** (unique: this is the one cross-vendor path that works at the ecosystem level, because NVX publishes an open REST API — see evidence/11) |
| **F. Full rip-and-replace to Q-SYS NV** | Q-SYS AV-over-IP | Not Extron-driven (becomes Q-SYS-driven) |

**Option E is uniquely interesting**: it's the only "existing-ecosystem-brand-new-hardware" path where a non-Crestron processor can drive new Crestron hardware without a Crestron processor. The REST API is specific to NVX, not available on DM or DM 8G+.

## No change to prior conclusions

- Existing DM-MD8X8-CPU3-RPS + DM-RMC: still non-redirectable from the RMC side, still either SIMPL program or parallel per-room control if we keep the chassis
- L3 encoder in `cresnet_cip.py`: still correct, still useful for Category A standalone Crestron CIP devices
- NVX REST path from evidence/11: still correct, now re-contextualized as one of several AV-over-IP migration paths
