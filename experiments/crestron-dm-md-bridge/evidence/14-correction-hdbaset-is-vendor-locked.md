# 14 — Correction: vendor-specific HDBaseT implementations don't interop, so "swap DM-RMC for an Extron/Q-SYS receiver" is NOT an option

**Date:** 2026-10-11

Earlier writeups (evidence/07, evidence/11, evidence/13) suggested "replace the DM-RMC with an Extron DTP3/NAV receiver or Q-SYS I-O Flex" as an escape path from the chassis-attached DM endpoint's firmware-locked master. **That suggestion is wrong.** HDBaseT itself is a standard (the Valens chip baseline), but every vendor layers their own control-channel / HDCP / EDID / signaling implementation on top, and those vendor dialects are what fail to interop:

- Crestron **DM** / DM 8G+ — Crestron's HDBaseT implementation. Chassis output cards drive this; only Crestron DM-family receivers (DM-RMC-*) decode it.
- Extron **DTP** / **DTP3** / **XTP** — three successive Extron HDBaseT implementations, Extron-only in each case.
- Q-SYS doesn't ship HDBaseT receivers at all; their room-end A/V is IP-based (Q-SYS NV / NVR / NC family).

Given Rob's existing DM-MD8X8-CPU3-RPS + DM-RMC-4K-SCALER-C hardware, the realistic one-processor-Extron options narrow to:

| Option | What it means | Cost | Hardware waste |
|---|---|---|---|
| **A. SIMPL# Pro program on the chassis** | A user-authored Crestron program instantiates the DM endpoints and bridges their joins to Extron via EISC or TCP. Chassis hardware stays. | Dealer license + ~300 LoC C# + Crestron Toolbox deploy. Weekend of work. | None. |
| **B. Keep DM for routing only; use parallel per-room control** | DM moves video + audio only. Each display's RS-232/IR/relay driven by a separate device at the display location: an Extron IPL (small), a Global Caché IP2SL/iTach-FLEX, or similar. Extron controls both the DM chassis (via CTP/CIP) and the per-room devices. | Hardware at each display: $100-$400 per room. Clean architecturally, scales badly past a few rooms. | None. |
| **C. Full rip-and-replace to Extron DTP3** | New Extron matrix (XTP II or NAV family), new DTP3 transmitters at inputs, new DTP3 receivers at outputs. All Extron. True one-processor. | Expensive. Rebuild the full A/V plant. | DM chassis + endpoints become e-waste. |
| **D. Full rip-and-replace to NVX IP-video (next build)** | Crestron DM NVX endpoints, each with its own IP + REST API. Extron (or Q-SYS) drives them directly via HTTPS. No HDBaseT, no chassis. | Expensive, needs 10 GbE network capacity. Highest future-proofing. | DM chassis + endpoints become e-waste. |

The DM-RMC's "two paths" I kept citing earlier — swap OR SIMPL — only had **one real path** (SIMPL) given interoperability. The other three options above are all rip-and-replace at different scales.

**Where this does NOT affect prior findings:**

- The L3 encoder in `cresnet_cip.py` is still correct and useful — it just has fewer places to deploy within the existing hardware. It's still the right code for a Crestron SIMPL# Pro add-on's EISC-side communications, and still the right code for standalone-mode Crestron CIP devices (Automate VX Series 2, DIN-CEN-CN2, Ethernet keypads, etc.) in future builds.
- The NVX direct-control architecture in evidence/11 is still correct and preferred for next builds.
- The chassis firmware-lock finding in evidence/13 is still correct — that's a Crestron DM architectural truth, not something a hardware swap fixes.

## Memory updated

`memory/extron-dm-md-cpu3-bridge.md` had the same wrong "swap receiver" suggestion; corrected to reflect the four actual options above.
