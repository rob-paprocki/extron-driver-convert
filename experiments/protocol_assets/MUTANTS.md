# Mutants: edit kinds GC has not yet accepted (ROADMAP R26)

**Status: measured** on this repo's GCP install (`Extron.Configuration.Contracts.dll`
15.45.0.0), 2026-09-23, via `experiments/gcp_harness/Load-Package.ps1`
(`-Deserialize -Commands -Protocol`) and `tools/pkp_validate.py`.

Finding 12 showed GC's catalogue ingests a package our writer produced,
including one with a single mutated `BinaryObjectString` (a model name).
Finding 13 §4b showed the package format carries `_port` and `_compatibility`
as graph fields, and that our tools did not yet read or write them. This
closes the gap between those two: **do edits GC has not yet been shown to
accept survive Extron's own loader?**

## Donor and method

Donor: `samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp`
(same donor as finding 13 §4b and `experiments/skeleton_i20`). Built with
`tools/pkp_build.PackageBuilder`, which round-trip-verifies the donor byte-for-byte
before permitting any mutation (`RoundTripError` otherwise - not hit here).

Three mutants, one change each, in `experiments/protocol_assets/mutants/`:

| mutant | field | before -> after | mechanism |
|---|---|---|---|
| `a_port.pkp` | `EthernetProtocolAsset._port` | 5500 -> 5678 | new code, `mutate_protocol.set_inline_int_member` |
| `b_compatibility.pkp` | `EthernetProtocolAsset._compatibility` | 16 (`Ethernet_Telnet`) -> 32 (`Ethernet_UDP`) | new code, `mutate_protocol.set_enum_ref_member` |
| `c_tag.pkp` | `EnumStateAsset._tag` | `"3"` -> `"3X"` | existing API, `PackageBuilder.replace_string` |

Full detail (object ids, edit log, byte counts) in `mutants/manifest.json`,
written by `experiments/protocol_assets/build_mutants.py`.

### Why `_port`/`_compatibility` needed new code

`tools/pkp_build.PackageBuilder` (unmodified by this task) exposes two
mutation primitives, each keyed by an NRBF object id: `replace_script`
(an `ArraySinglePrimitive` byte payload) and `replace_string` (a
`BinaryObjectString`). `_port` is neither - it is a bare `Int32` written
**inline** as one of `EthernetProtocolAsset`'s own class members, with no
object id of its own. `_compatibility` is a reference to a nested,
single-field enum instance (`ProtocolCompatibilityFlags`, member `value__`,
itself the same "bare inline `Int32`" shape).

`experiments/protocol_assets/mutate_protocol.py` (new file; does not edit
`tools/pkp_build.py` or `experiments/nrbf_writeback/nrbf_write.py`) adds
exactly that: it walks the `TracingPkpParser`'s **nested** (event, children)
trace - `PackageBuilder.parser.trace`, distinct from the **flat**
`PackageBuilder.trace` the writer consumes - to find the class instance by
object id, then indexes into its children list by member position (every
class member, primitive or record, contributes exactly one item to that
list, in declaration order - see the module docstring for the full
argument). Because the flat trace is built by walking the *same* nested
tree and appending the *same* dict objects (not copies), mutating the leaf
dict found this way is immediately reflected in what gets serialized - no
separate flat-list patch is needed. Both fields are fixed-width `Int32`, so
the edit changes no record's length: `a_port.pkp` and `b_compatibility.pkp`
are **byte-identical in length** to the donor (321,697 decompressed bytes),
differing by 2 and 1 bytes respectively (see `manifest.json`).

### A finding made while building the donor's protocol lookup

`tools/pkp2cs.find_protocol_asset`'s own docstring assumes "a
`DriverModelAsset` owns exactly one `ProtocolAsset` child." This donor
violates that: **both `PTZ-IP12` and `PTZ-IP20` carry an
`EthernetProtocolAsset` and a `SerialProtocolAsset` under the same
`AssetBase\`1[[IProtocolAsset]]` wrapper's child collection** (measured by
walking `pkp2cs.child_collection_items` two levels deep). `pkp2cs.unwrap_generic_wrapper`
requires that wrapper to hold exactly one child and returns `None`
otherwise, so `pkp2cs.find_protocol_asset(objs, model)` **silently returns
`None` for both of this donor's models** - this repo's own R14/R26 donor
directly reproduces ROADMAP R17's "resolves to `None`, silently" failure
mode, not just Biamp's. `mutate_protocol.find_protocol_assets_for_model`
(same file) does not share that one-child assumption and finds both assets
correctly. This is incidental to R26 but relevant to R17's fix.

### Item (c): no dedicated "response/match-string asset" class exists

The task named this as an example ("e.g. a response/match-string asset in
the graph") with an explicit fallback ("if the donor has none, say so and
pick another sample package that does, from `samples/`"). Measured, not
assumed: `build_mutants.py`'s `check_no_response_asset_class()` lists every
distinct class name `pkp_dump.py` reads out of all **9** `samples/*.pkp`
files and searches for `Match`/`Response`/`Parse`/`Regex`/`Pattern` in any of
them.

**Result: zero hits, in every sample package** (see `manifest.json`'s
`response_asset_search`, one key per file, every value `[]`). Reply parsing
in a GC package lives entirely in the embedded Python script
(`AddMatchString` calls; GC's `__MatchAllSubscribe` dispatcher, per finding
13) - there is no NRBF-level asset class for it to mutate. The closest
graph-level analog this donor's own graph offers is `EnumStateAsset._tag`,
the per-state string GC's dispatcher keys parsed values against (this donor's
PTZ preset states are tagged `"1"`..`"7"`). Mechanically this is the same
*kind* of edit finding 12 test 3 already made (a `BinaryObjectString`
mutation) - it is included here to record the negative plainly and to test
a *different* asset class (`EnumStateAsset`, not `DriverFileAsset`'s own
model-name string) surviving the same path, not to claim a new edit kind.

## Results

| mutant | `pkp_validate` | hash refresh needed? | `LoadFromFile` | `Deserialize` | `-Protocol` readback |
|---|---|---|---|---|---|
| donor (control) | Valid, 0 | - | `DriverFileAsset` name=`1bynd_19_4743` | OK | `Port=5500 ... Compatibility=Ethernet_Telnet(16)` |
| `a_port.pkp` | Valid, 0 | **No** | `DriverFileAsset` name=`1bynd_19_4743` | OK | `Port=5678 ... Compatibility=Ethernet_Telnet(16)` |
| `b_compatibility.pkp` | Valid, 0 | **No** | `DriverFileAsset` name=`1bynd_19_4743` | OK | `Port=5500 ... Compatibility=Ethernet_UDP(32)` |
| `c_tag.pkp` | Valid, 0 | **No** | `DriverFileAsset` name=`1bynd_19_4743` | OK | unchanged (edit is outside the protocol asset) |

All four (donor + 3 mutants) also pass `experiments/gcp_harness/test_load_package.py`'s
underlying checks by hand: `DriverCommands: 15` on every load, both models
(`PTZ-IP12`, `PTZ-IP20`) carry all 15 commands, byte-identical to the donor's
own command list - the mutations changed exactly the one targeted field and
nothing else Extron's object model surfaces.

**Exact commands and full output** are in the reproduction transcript below;
the short version:

```
=== a_port.pkp
  LoadFromFile : DriverFileAsset  name=1bynd_19_4743
  Deserialize  : OK (Extron.Configuration.Drivers.DriverFileAsset)
  Protocol model=PTZ-IP12 class=EthernetProtocolAsset ... Port=5678 ... Compatibility=Ethernet_Telnet(16) ...
  Protocol model=PTZ-IP20 class=EthernetProtocolAsset ... Port=5678 ... Compatibility=Ethernet_Telnet(16) ...
  DriverCommands: 15
  model PTZ-IP12  commands=15
  model PTZ-IP20  commands=15

=== b_compatibility.pkp
  LoadFromFile : DriverFileAsset  name=1bynd_19_4743
  Deserialize  : OK (Extron.Configuration.Drivers.DriverFileAsset)
  Protocol model=PTZ-IP12 class=EthernetProtocolAsset ... Port=5500 ... Compatibility=Ethernet_UDP(32) ...
  Protocol model=PTZ-IP20 class=EthernetProtocolAsset ... Port=5500 ... Compatibility=Ethernet_UDP(32) ...
  DriverCommands: 15
  model PTZ-IP12  commands=15
  model PTZ-IP20  commands=15

=== c_tag.pkp
  LoadFromFile : DriverFileAsset  name=1bynd_19_4743
  Deserialize  : OK (Extron.Configuration.Drivers.DriverFileAsset)
  DriverCommands: 15
  model PTZ-IP12  commands=15
  model PTZ-IP20  commands=15
```

Exit code of the `Load-Package.ps1` run over all three mutants plus the
donor control: **0** (no `LoadFromFile` failures).

### Hash refresh: measured, not needed for any of the three

`tools/pkp_build.PackageBuilder.refresh_resource_hash` was **not called**
for any of the three mutants. `tools/pkp_validate.py -v` still reports
`Valid` for all three, with **both** packaged resources
(`1bynd_19_4743_v1_0_1.pdf`, `_1bynd_19_4743.py`) showing "sha256 matches
the package's stored digest" - unchanged from the donor:

```
Valid         0      experiments/protocol_assets/mutants/a_port.pkp
  Valid         1bynd_19_4743_v1_0_1.pdf           sha256 matches the package's stored digest
  Valid         _1bynd_19_4743.py                  sha256 matches the package's stored digest
Valid         0      experiments/protocol_assets/mutants/b_compatibility.pkp
  Valid         1bynd_19_4743_v1_0_1.pdf           sha256 matches the package's stored digest
  Valid         _1bynd_19_4743.py                  sha256 matches the package's stored digest
Valid         0      experiments/protocol_assets/mutants/c_tag.pkp
  Valid         1bynd_19_4743_v1_0_1.pdf           sha256 matches the package's stored digest
  Valid         _1bynd_19_4743.py                  sha256 matches the package's stored digest
```

This is expected once the mechanism is understood, but was measured rather
than assumed: `DriverFileAsset._resourceHashDict` covers only the packaged
**resources** (the embedded `.py` script and the comm-sheet `.pdf`), read as
raw byte arrays (`tools/pkp_validate.py`'s own docstring). None of `_port`,
`_compatibility`, or `EnumStateAsset._tag` are resource bytes - they are
graph fields elsewhere in the object tree - so none of these three edit
kinds touches anything the hash dictionary is computed over. A future
edit that changes the embedded script's *text* (as `replace_script` does)
still needs the refresh `pkp_build.py` already performs by default; a
graph-only edit of this kind does not.

## What this shows, and what it does not

- **Measured**: three edit kinds beyond finding 12's single model-name
  string - an inline `Int32` protocol field, an enum-wrapped protocol field,
  and a different asset class's string field - all validate, deserialize
  through `BinaryFormatter`, load through `DriverFileAsset.LoadFromFile`,
  and read back through Extron's own object model (not this repo's parser)
  with exactly the mutated value changed and nothing else disturbed. Command
  tables are unaffected in all three cases (15/15, both models, byte-identical
  to the donor's own command list).
- **Not measured**: whether GC's Driver Manager *catalogues* these three the
  way finding 12 measured for its own mutant (that check needs staging into
  `driver3` and a GC restart, which this task's rules explicitly excluded -
  "do not start Global Configurator"). `LoadFromFile`/`Deserialize` succeeding
  is the same evidence finding 12 relied on before the catalogue check, and
  finding 12 already established that catalogue ingestion imposes no
  additional barrier once `LoadFromFile` succeeds.
- **Not measured**: whether GC's *editor UI* renders the changed port/
  compatibility/preset-label sensibly, whether the package can be placed in
  a project, or whether it drives a device. Per this repo's own standing
  note, loader acceptance is necessary and not sufficient.

## Reproducing

```
py -3.11 -u experiments/protocol_assets/build_mutants.py
py -3.11 -u tools/pkp_validate.py -v \
    "samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp" \
    experiments/protocol_assets/mutants/a_port.pkp \
    experiments/protocol_assets/mutants/b_compatibility.pkp \
    experiments/protocol_assets/mutants/c_tag.pkp

# 32-bit PowerShell, from the repo root:
C:/Windows/SysWOW64/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass \
    -File experiments/gcp_harness/Load-Package.ps1 -Deserialize -Commands -Protocol -Path \
    "samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp,experiments/protocol_assets/mutants/a_port.pkp,experiments/protocol_assets/mutants/b_compatibility.pkp,experiments/protocol_assets/mutants/c_tag.pkp"

# Regression check for the new -Protocol switch (must still pass, unchanged default output):
py -3.11 -u experiments/gcp_harness/test_load_package.py
```

`-Protocol` is new, additive to `experiments/gcp_harness/Load-Package.ps1`
for this task (the only file this task edited rather than created): for
every `SupportedModel` it walks `DriverModelAsset.Protocols` and prints each
protocol asset's simple-valued properties (enum/primitive/string/Guid;
collections, credentials and asset references are filtered out) via
reflection, plus the full `[Enum]::GetNames` mapping of
`ProtocolCompatibilityFlags` (see `experiments/protocol_assets/SURVEY.md`
for what that mapping settles for ROADMAP R16). It does not change any
existing switch's output; `test_load_package.py`'s 66 checks pass unchanged
before and after this task's edits.
