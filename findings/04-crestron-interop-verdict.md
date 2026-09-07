# Finding 04 — verdict: Crestron interoperability

From a 20-agent research pass with adversarial per-claim verification
(43 confirmed, 9 overstated, 5 refuted), **plus direct inspection of three real
Crestron packages**. See the caveat at the bottom: part of that dossier failed
and is being re-run.

## Answer

**In: yes.** **Out: plausible, unproven, and gated by licence and hardware
rather than by code.**

## What a Crestron "module" is

The word covers five unrelated artifacts, and picking the right one is most of
the answer.

| artifact | what it really is | usable? |
|---|---|---|
| `.umc` user macro | wiring in a graphical dataflow program; numbered joins, no named commands | no |
| `.usp` SIMPL+ | C-like text, also exposes joins; compiles only inside dealer-gated SIMPL Windows | no |
| `.clz` SIMPL# | compiled C#, no source | no |
| `.cpz` SIMPL# Pro | a whole control program, not a device module | no |
| **`.pkg` Crestron Certified Driver** | **a per-device driver** | **yes** |

## Three ways a `.pkg` can be written — and the third is the target

1. **V1 "RAD"** — JSON metadata plus a compiled C# protocol class.
2. **V2 "Entity Model"** — C# methods decorated `[EntityCommand]`, bodies still
   send bytes by hand.
3. **A `DriverDefinition` JSON document interpreted by Crestron's runtime engine,
   with the DLL reduced to a shell.** The tutorials never mention it. The samples
   reveal it.

Both non-IR Samsung packages (dated 2025) use form 3. Their DLLs are, byte for
byte apart from the driver name, the same ~16 KB shell: one class inheriting
`Crestron.DeviceDrivers.Core.LegacyWrappers.DisplayWrapperSerial` (or
`DisplayWrapperTcp`), one `typeof()` call, and the driver JSON as an embedded
resource. The JSON's sections match the public `DriverDefinition` class
property-for-property, and its loader `DriverDefinitionInitialization` is public
too. The wrapper classes ship in the public DevKit's
`Crestron.DeviceDrivers.Core.dll`.

**The name "LegacyWrappers" is a warning** that Crestron may be migrating away
from this form. Whether it is legacy-and-retiring or current-but-undocumented is
being researched — it decides whether building on this format is smart or doomed.

## Crestron-IN

Feasible now, for drivers built the JSON-engine way. Everything is recoverable:
wire bytes as composable templates with checksum and byte-conversion
transformations; response decoders (a tree of `Regex`, `BinaryPacket`, `Json` and
name-match nodes); per-feature polling interval; ack/feedback requirements;
hold-off and retry counts; warm-up/cool-down timers; connector lists; model
lists; transport with timing.

**Trapped:** drivers written the V1/V2 C# way — which is what the public
tutorials teach third parties. Decompiling is technically trivial (plain .NET, no
obfuscation) and legally unattractive. Unknown: what fraction of Crestron's
catalogue uses each form. N=2 non-IR packages here.

## Crestron-OUT

The hardest blocker is not writing the driver — it is being allowed to build it
and proving it loads.

- **Building: technically ungated, contractually gated.** The whole toolchain is
  on public NuGet with no login (`Crestron.DeviceDrivers.DevKit`, `ManifestUtil`,
  `ProgramInterface`, `Program`, all 27.0.24, owner Crestron_Electronics),
  targeting .NET Framework 4.7 and .NET 8. But the bundled Crestron "Software
  Development Tools License Agreement" (13 Feb 2024) §1.2 and §4.1(a) requires a
  separate written agreement — dealer, Authorized Independent Programmer, or
  partner — and §4.2(c) forbids decompiling the tools.
- **Loading: no gate found.** Upload via Toolbox File Manager or SFTP, reference
  by path. No signature, certificate or approval step appears anywhere in the SDK
  docs (11 pages scanned by the verifier). "Certified" is purely a portal-listing
  status for Crestron-authored drivers. The one in-the-wild failure report is a
  .NET version mismatch, not a trust error.
- **Counterweight:** Crestron's own driver DLLs *are* Authenticode-signed with a
  self-signed "Crestron Electronics / Firmware Department" certificate, and the
  wrapper path is undocumented. No verification code is visible in the SDK
  assemblies — consistent with "no gate", but that is an absence, not a proof.

**The decisive test is one afternoon with a 4-Series processor.** Nobody has
shown that an unsigned shell built by an outsider loads.

## Architecture: adopt an IR, modelled on `DriverDefinition`

Firm recommendation: hub-and-spoke IR for the device-protocol layer, with its
concepts modelled on Crestron's `DriverDefinition` (templates + transformations
outgoing, decoder tree incoming, typed state controllers with polling policy,
transport block, connector list). Keep the Extron→Extron path as the AST source
translator from finding 02.

Documentation-only research had recommended point-to-point, believing Crestron's
declarative layer stopped at a whitelist of standard commands. **The samples
refute that**: the whole protocol is data, and it is the most complete
declarative device description either vendor ships.

Do not copy Crestron's JSON as the IR — emit it as one target.

Hand-written Extron code outside the `### BEGIN/END AUTO GENERATION` markers is
the escape hatch: carry it in the IR as an opaque flagged node that the Crestron
emitter reports as manual work, **never silently dropped**.

**There is an offline acceptance test available now**: regenerate the Samsung
Crestron JSON from the Extron module and diff wire bytes per command against
Crestron's own file. No hardware needed.

## Caveat on this finding's basis

Of nine research dimensions, three returned placeholder stubs, one crashed, and
one was never adversarially checked. The verdict above was written by a
synthesist who caught that, discounted those dimensions, and re-verified key
facts first-hand. The four broken dimensions are being re-run —
**artifact-landscape, modern-targets, direction-feasibility and legal above are
the weakest parts of this document** until that completes.
