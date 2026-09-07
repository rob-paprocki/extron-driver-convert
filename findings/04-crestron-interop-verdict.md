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

## Re-run results: the four weak dimensions

Three of the four came back clean (37 confirmed, 6 overstated, 1 refuted).
`modern-targets` returned a placeholder stub twice, so it was researched by hand
instead; those facts are marked below.

### Third parties already do this — publicly

The strongest evidence that "Crestron out" is achievable is that independent
developers ship loadable drivers today, in the open:

- `oznetmaster/TeslaPowerwallCrestronDriver` — builds on `windows-latest` CI
  against the public NuGet packages
- `jbasen/Crestron-Home-Extension-Driver-Template`
- `dberlin/MAK2StarGrillCloudConnected`

None of them is Crestron. All build against the public DevKit. This moves
"can an outsider produce a loadable `.pkg`" from unproven to demonstrated —
though none of these is a resource-swapped shell, which is still untested.

### Testing without hardware — CORRECTED, it is gated

An earlier pass reported VC-4 as a genuine $0, 90-day, software-only trial and
therefore a free route to the decisive load test. **A later pass contradicted
that and is more credible**: VC-4 trial requests require a PO/Sales Order or an
existing dealer relationship, and **Crestron Toolbox itself is restricted to
dealers, CSPs and Authorized Independent Programmers**. The trial exists; getting
one does not appear to be self-service.

Treat the load test as gated behind the same partner relationship as everything
else, not as a free download. This is the correction that matters most for
planning.

A forum report states *"You can upload the pkg file or the dll itself containing
the json"* — consistent with the shell being incidental. REPORTED, not spec.

### The signature does not bite

Both Samsung shell DLLs carry a **self-signed** Authenticode-style PKCS#7
signature — subject equals issuer, `CN=Crestron Electronics Inc, OU=Firmware
Department`. Not CA-chained. A resource swap would break it, but **nothing in
the documented load path ever checks it**, so breaking it has no known
functional consequence.

### V1 is not being retired *(researched by hand)*

SDK **v28 released 2026-04-28**; v27 on 2026-01-30. The release notes update
V1 (RAD Framework) topics — Security System Drivers, AV Switcher Drivers —
alongside V2 topics in the same entry. V2 (Entity Model, from SDK 21.x) is
described as "now available", not as a replacement. December 2025 notes even
added SIMPL *wrapper module* support to the Supported Device Types page.

So `LegacyWrappers` names a hosting layer, not a doomed one. Building on the
JSON-engine form is not building on sand.

### The licence asymmetry is the real constraint

This is where the two vendors diverge sharply, and it shapes what is safe to
build.

**Crestron** — Software Development Tools License Agreement, 13 Feb 2024:

- **§3.1 / §4.2(b) field-of-use:** the tools may be used "only for the purpose of
  Developing software for **Crestron Devices**". A cross-vendor conversion tool
  is not obviously within that field.
- **§4.2(c):** bars discovering "any underlying ideas or algorithms … through
  reverse engineering, de-compilation, or disassembly".
- **§2.11:** requires a written "Underlying Agreement" — Dealer, AIP or Partner.
  Lose it and the licence terminates.
- **§3.2(a):** the user assigns Crestron all rights to modifications, "whether or
  not such modifications are permitted".
- CSP status needs 3+ years professional programming experience, certification,
  a business plan and references.

**Extron** — a free self-service "Extron Insider" account and a lighter EULA:
no resale/redistribution without written consent, no disassembly without written
approval, but **no field-of-use restriction to Extron-only devices and no dealer
contract requirement**.

Neither vendor's public terms address cross-vendor conversion. Reading a file you
were given is not the same as redistributing it or shipping its transformed
output commercially — those five activities carry materially different risk, and
this is a question for a lawyer, not for this document.

`drivers.crestron.io` is login-gated, so the one source that could quantify how
much of Crestron's catalogue uses the JSON-engine form could not be read.

## Still unproven

1. Does a **resource-swapped or outsider-built shell** actually load? The public
   third-party projects prove compiled-from-source works; nobody has shown the
   templating shortcut works.
2. What fraction of Crestron's shipped catalogue uses the JSON-engine form?
   Unmeasurable without portal access. N=2 here.
