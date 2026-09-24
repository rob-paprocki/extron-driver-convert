# graph_synthesis — ROADMAP R27 and R28

Both items sit downstream of `findings/18-adding-a-command.md` (same-package
command cloning, positive object ids only) and `findings/12`/`findings/16`
(GC ingests packages this repo produces, gated by resource-hash integrity,
not by graph shape). This directory asks two harder questions than finding
18 did:

- **R27** — can a command be cloned **out of a completely different
  package**, not just within one?
- **R28** — can a package be **assembled from nothing** — object instances
  authored from measured metadata, not copied from any donor's byte stream?

**R27: yes, fully measured, verified through Extron's own loader.**
**R28: the required structure is now measured precisely; a complete
from-scratch build was not finished in this session — see "R28" below for
exactly where it stops and why.**

Tools used: `tools/pkp_build.py`, `tools/pkp_dump.py`, `tools/nrbf_graph.py`,
`tools/pkp_asset.py` (all read as committed at session start — none of these
were being edited by another agent this session, so no snapshot was needed
for them). `tools/pkp_validate.py` **was** being edited concurrently (R38),
so every `pkp_validate` verdict below was produced against a snapshot of
`tools/pkp_validate.py` taken via `git show HEAD:tools/pkp_validate.py` into
this session's private tmp dir, imported with that tmp dir first on
`sys.path` (`PYTHONPATH=tools` was added afterward only so its own
`import pkp_dump` resolves against the unmodified `tools/pkp_dump.py`).
Extron's loader: `experiments/gcp_harness/Load-Package.ps1
-Deserialize -Commands -Protocol`, invoked through 32-bit PowerShell from a
Python subprocess wrapper (the pattern named in the task).

All new code lives in this directory. `tools/pkp_asset.py` was **not**
modified — the cross-package machinery reuses its `CommandGraph` (for the
target side) and `tools/nrbf_graph.py`'s `clone_plan`/`clone_events`
primitives directly, adding what only a cross-package clone needs on top
in `cross_clone.py`.

## R27 — cross-package cloning

**Donor:** `corpus/extron-driver3/pana_19_5702_v1_4_5.pkp` (Panasonic PTZ
camera, built against `Extron.Configuration.{Drivers,Contracts,Core}
13.26.0.15`).
**Target:** the untouched
`samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp` (built
against `1.1.24.402`) — the same donor finding 18 built on, used here
unmodified.
**Command cloned:** `PanTiltAbsolutePosition` (`Pan(Decimal)|Tilt(Decimal)`,
Set-only) — the exact command finding 18 §9 already copied the *shape* of by
hand; this clones the *bytes*.

### Method

`cross_clone.py`'s `clone_command_cross_package()` extends
`tools/pkp_asset.py`'s same-package clone with two things a same-package
clone never has to do (see the module docstring for the full argument):

1. **Class-metadata resolution, schema-verified.** A `ClassWithId`'s
   `metadata_id` is repointed at the target's own matching class definition
   *only if the schema matches exactly* (`_schema_key`: name, `system`
   flag, member names, per-member type shape, all version-stripped);
   otherwise the donor's own class-defining record is imported wholesale
   (fresh id, its own library resolved by version-stripped name reuse or,
   failing that, a new `BinaryLibrary` record).
2. **Closure import of shared objects and class metadata together.**
   `_resolve_graph()` runs one BFS that imports every `MemberReference` the
   cloned subtree points at outside the target's own graph (recursively —
   an imported object can itself point at further shared objects) *and*
   every `ClassWithId.metadata_id` it needs, to a fixpoint, before a single
   event is written out. `AssetBase(+`1)+_parentAsset` references are
   excluded from that closure exactly as `nrbf_graph.owned_subtree` already
   excludes them from ownership — and, measured directly below, that
   exclusion is load-bearing.

### What was measured before writing any code

`probe1_classes.py`-style inspection (kept in the session tmp dir, not
committed — the numbers are recorded here) of the donor's
`PanTiltAbsolutePosition` subtree:

- **15 top-level spans**, **57 ids to renumber**, **12 shared references**
  (10 strings + one command instance + one empty `BinaryArray`) reaching
  outside the subtree.
- **14 distinct class layouts** referenced via `ClassWithId`, every one
  defined **outside** the cloned span (as finding 18 §3 found for
  same-package clones, just now confirmed true across packages too).
- Of those 14, **8 match the target by exact class name** (the enums,
  `DecimalParamAsset`, `DriverCommandAsset`, `System.Guid`) and **6 only
  match after stripping `Version=X.X.X.X`** — the `System.Collections.*`
  generic wrappers (`List`1[[...IParamAsset...]]`,
  `ObservableCollection`1[[...]]`, its `+SimpleMonitor` nested type), whose
  own class name embeds the *type argument's* assembly-qualified name,
  including its version. This is the same assembly-version tolerance
  finding 12 measured at the whole-package level (a package declares
  `13.26.0.15`, GC resolves it against the installed `15.27.0.0`), showing
  up here as a name-matching problem for a tool rather than a loader
  problem for GC.

That reconnaissance under-predicted what the actual build needed, in one
precise way (see attempt 2): name matching alone is not schema matching.

### Attempts, in order, each with the loader/parser's verbatim result

**Attempt 1 — naive closure over every `MemberReference`.**
`pkp_dump.NrbfParseError: ClassWithId references unknown MetadataId 1910
| offset=0x4e992 (321938)`

Cause, found by inspection: the closure followed `AssetBase+_parentAsset`
like any other reference. One `_parentAsset` walk reaches the donor's root
`DriverFileAsset` (object 1) — and from there, ordinary downward
reachability pulls in essentially the **whole 17,645-object donor package**
(`clone_plan(root=1)` renumbered 17,645 ids; `all_tops` grew to 9,007
spans). `nrbf_graph.owned_subtree` already refuses to walk
`AssetBase+_parentAsset` for exactly this reason when deciding what a clone
*owns*; a closure built to decide what a clone must *import* needs the same
refusal, and did not have it yet. Fixed: `_upward_indices_for()` finds these
slots and excludes them from the "must resolve" scan; whichever ones still
point outside the target once the (now-bounded) closure settles get severed
to `ObjectNull` in the output rather than left dangling.

**Attempt 2 — closure bounded correctly, metadata reused by name alone.**
`pkp_dump.NrbfParseError: unhandled/unknown record type while parsing |
record_type=SerializedStreamHeader(0) | offset=0x4e992 (321938)`

A generic "wrong number of bytes somewhere" failure — the kind CLAUDE.md's
methodology notes call the least direct exception this codebase produces.
Bisected by re-emitting successive prefixes of the (now 20-item) top list
and re-parsing each with our own reader (not Extron's — cheaper, and our
own grammar is strict enough to localize this): the third top, a
`DecimalParamAsset` instance, is where it first breaks, and always at the
exact same output offset regardless of what follows. Comparing the class
metadata directly (`Extron.Configuration.Core.Assets.Automation.
DecimalParamAsset`, obj 145 in pana vs obj 124 in the i20 donor) found the
real fault: **pana's build has 29 members, the i20 donor's has 28** — the
i20 donor is missing `_bEnableCustomMinMax` outright, a field that exists
in one library version of `Extron.Configuration.Core` and not the other.
Reusing the i20 donor's metadata id for bytes written against pana's
29-member layout reads every member after the 8th off-by-one-presence -
not a crash where the mismatch happens, a drift that only becomes visible
many records later. **Same class name, different schema, loud failure once
you get far enough to notice - never silent.** Fixed: `_schema_key()`
compares member names *and* per-member type shape (version-stripped) before
trusting a name match; on a mismatch, the donor's own metadata record
(header **and** its own first-instance value events - NRBF has no
schema-only record, `ClassWithMembersAndTypes` always writes a live
instance too) is imported instead, recursively, through the same closure.

**Attempt 3 — metadata resolved via schema, but never applied to the output.**
`pkp_dump.NrbfParseError: ClassWithId references unknown MetadataId -560
| offset=0x4f212 (324114)`

`-560` is `OperatorFlags`, an inline (negative-id) enum instance -
`_resolve_graph()` had correctly worked out where it should point
(`idmap[-560]` was populated), but nothing ever *wrote that mapping into
the emitted `ClassWithId.metadata_id` fields* - `clone_events`/
`_remap_event` deliberately never touches `metadata_id` (same-package
clones never need it touched), and the cross-package path hadn't added the
one pass that does. Fixed: one explicit pass, once `idmap` is complete,
`ev["metadata_id"] = idmap[ev["metadata_id"]]` for every `ClassWithId` in
the output.

**Attempt 4 — metadata correctly applied, one object emitted twice.**
`nrbf_graph.GraphError: object id 1903 encoded twice (at 264244 and
264543)`

`EventWalker`'s own coverage check caught this, not `pkp_dump`'s parser
(`pkp_dump` tolerates a redefinition; `EventWalker` does not, by design -
the safety property `nrbf_graph.py`'s docstring names). Root cause: the
shared string `"seconds"` (donor id 625) was queued and imported on its own
early, as an ordinary shared reference - `clone_plan(root=625)` returned a
one-event span. Later, importing the `DecimalParamAsset` metadata object
(145) - needed because of attempt 2's schema mismatch - `clone_plan(root=
145)` returned 145's **entire instance span**, which **textually contains**
625's own definition (object 145's `_suffix` field happens to be the same
shared `"seconds"` string). Two independent `clone_plan` calls, each
unaware of the other, both correctly claimed to define what turned out to
be an overlapping byte range - `ng.clone_events` has no overlap check of
its own, so it emitted 625's definition twice under the same new id. Fixed:
`_add_claimed()` tracks every claimed `(start, end)` range across the whole
resolve, drops a new span already nested inside one already claimed, and -
the direction that actually fired here - removes an already-claimed
*smaller* span when a later, larger one is found to contain it.

**Attempt 5 — success.** `pkp_validate.py` (HEAD snapshot):

```
Valid         0      experiments/graph_synthesis/out/1bynd_19_r27_cross_clone.pkp
```

`Load-Package.ps1 -Deserialize -Commands -Protocol` (verbatim, trimmed to
the load line, the deserialize line, and the command table):

```
=== 1bynd_19_r27_cross_clone.pkp
  LoadFromFile : DriverFileAsset  name=1bynd_19_4743
  Deserialize  : OK (Extron.Configuration.Drivers.DriverFileAsset)
  ...
  DriverCommands: 16
    ...
    PanTiltAbsolutePosition  Pan Tilt Absolute Position attrs=3   Pan | Tilt
    ...
  model PTZ-IP12  commands=16
  model PTZ-IP20  commands=16

exit 0
```

The Protocol dump (unaffected, printed for the control it provides) still
shows both models' Ethernet and Serial protocol assets rendering their
address, port and compatibility flags correctly - i.e. the command clone
touched nothing else in the graph. `attrs=3` is pana's own bitfield,
carried across unmodified (`ConfigurationVisible | RuntimeVisible`, per
finding 18's decoded table) - not guessed, not reset.

**Cross-package cloning works, all the way through Extron's own
deserializer and object model**, for a subtree whose class metadata differs
in schema between the two packages and whose command shares 12 objects with
the rest of its donor package. `test_cross_clone.py` pins all five findings
above as regression tests (25 checks; run below).

### What this does NOT show

- **One donor pair.** Only `pana_19_5702` -> the i20 donor was tried. A
  donor built against a much older or much newer `Extron.Configuration.*`
  could need class-metadata import for classes this pair resolved by name
  (the mechanism is measured, its FULL reach across the corpus is not).
- **GC's UI was not driven.** Per CLAUDE.md and the task instructions, GC
  was not started and nothing was copied into a GC library folder. Finding
  18 §8 already measured that Extron's *loader* and its *UI* can disagree
  (a package can deserialize and still not render); that gap is not closed
  here, only the loader half is.
- **The parameter widgets are unmeasured**, same caveat finding 18 already
  carries for its own composed shapes - Pan/Tilt's ranges came from pana's
  own bytes, untouched, but nothing here confirms GC's editor shows them
  usably.

## R28 — a graph assembled from scratch

**Goal, restated:** a minimal package - one model, one command, one
`EthernetProtocolAsset` - built from object instances authored from
measured metadata, not copied from any donor's byte stream.

### What was measured

Root `DriverFileAsset` (obj 1 of the i20 donor), full member list via
`pkp_dump`/`EventWalker` (20 members): `_manifest` (nullable, **None** on
this donor - so a minimal package plausibly needs no manifest at all),
`_packageState` (inline enum), `_resourceHashDict`
(`Dictionary<string,byte[]>` - empty is presumably fine if there are no
embedded resources), one shared `_internalChildCollection` referenced from
**three different member slots** (`_internalChildCollection`,
`DriverDescriptorAsset+_internalChildCollection`,
`AssetBase+_internalChildCollection` - all three point at the *same*
object), version triple (`_fileVersion`/`_schemaVersion`/`_minAPIVersion`,
each a `System.Version`), manufacturer/device-type/filename strings, a
`System.Guid`.

**The root's child collection does not hold `SupportedModel` objects
directly.** It holds **six typed pooled-asset containers**, each an
`Extron.Configuration.Core.Assets.AssetBase`1[[T]]` parametrized by a
different asset interface:

| object | `T` |
|---|---|
| 28, 29 | (none - `RevisionHistoryAsset`, not a container) |
| 30 | `IDriverCommandAsset` |
| 31 | `IProtocolAsset` |
| 32 | `IParamAsset` |
| 33 | `IDriverModelAsset` - the actual `SupportedModels` list |
| 34 | `IResourceAsset` |

`AssetBase`1[[T]]`'s own schema is **identical across all five
parametrizations** (8 members: a typed `_internalChildCollection`, an
untyped `AssetBase+_internalChildCollection` - null on every one
inspected - name/defaultName/guid/maxChildCount/disableChildAssetParenting/
parentAsset) - only the generic argument in the class name, and therefore
the metadata id, differs. `DriverCommandAsset` (19 members),
`EthernetProtocolAsset` (22 members) and `DriverModelAsset` (17 members)
were also measured in full (see the tmp-dir probe output; not reproduced
here in full to keep this file short - every number quoted below was read
directly off one of these dumps, not estimated).

**One structural question was directly testable without a from-scratch
build, and was tested:** are all six root-level typed children required?
`probe_minimal_root.py` detaches the two `RevisionHistoryAsset` entries and
the `IParamAsset`/`IResourceAsset` containers from the (real, unmodified)
i20 donor's root, keeping only the `IDriverCommandAsset`,
`IProtocolAsset` and `IDriverModelAsset` containers, and writes the result
to `out/1bynd_19_r28_stripped_root.pkp`.

```
Valid         0      experiments/graph_synthesis/out/1bynd_19_r28_stripped_root.pkp
```

```
=== 1bynd_19_r28_stripped_root.pkp
  LoadFromFile : DriverFileAsset  name=1bynd_19_4743
  Deserialize  : OK (Extron.Configuration.Drivers.DriverFileAsset)
  ...
  DriverCommands: 15
  ...
  model PTZ-IP12  commands=15
  model PTZ-IP20  commands=15

exit 0
```

**Measured, not assumed: `RevisionHistoryAsset` and the top-level
`IParamAsset`/`IResourceAsset` pooled containers are not required** for
`LoadFromFile`, `Deserialize`, the command surface or the protocol surface
to come back correct. A minimal from-scratch package needs at most three
root-level typed children (commands, protocols, models), not six.

### The wall

A complete from-scratch build - every object instance's field values
authored fresh, none copied from a donor's actual command/model/protocol -
was **not completed in this session**. What stands in the way, precisely:

Every non-collection, non-nullable field on every class in this chain
(`DriverCommandAsset._exCmdId`, `CommandAssetBase+_attributes`,
`EthernetProtocolAsset._protocolSubType`/`_compatibility`/
`_httpAuthentication`, ...) is a **value-type enum**, which .NET's
`BinaryFormatter` never writes as a plain `MemberReference` - each one has
to be authored inline, as a `ClassWithId(existing metadata id)` immediately
followed by a `Primitive` carrying the bitfield's numeric value, keyed
correctly to whichever enum type that specific field declares (finding 18
§9's attribute-bitfield table gives the values for `DriverAttributeEnum`;
the other four enum types this chain uses were measured by name here but
not by legal-value table). Every `_internalChildCollection`-shaped member
needs its own three-object wrapper chain
(`ObservableCollection`1` + `List`1` + `+SimpleMonitor`, all confirmed
structurally in R27's closure work) even when it will hold zero or one
item. None of this is unknown any more - the schema for every class in the
chain is measured and recorded above - but authoring dozens of individual
field decisions correctly, each one a candidate for the exact class of
byte-level, loud-failure-many-records-later bug R27's attempts 2-4 hit
repeatedly, is a substantially larger task than R27's clone (which only had
to *retarget references*, never *invent values*), and finishing it was not
attempted here beyond the `IExtronCommandIdEnum`/`DriverAttributeEnum`-style
field survey above.

**What the next session needs, concretely, to finish it:** the measured
member-type tables for `DriverCommandAsset`/`EthernetProtocolAsset`/
`DriverModelAsset`/`AssetBase`1[[T]]` above (all confirmed, not
guessed); the `ObservableCollection`1`/`List`1`/`+SimpleMonitor`/
`BinaryArray` wrapper pattern from R27's closure work
(`cross_clone.py`'s `_resolve_graph`, and `pkp_asset.py`'s own
`_append_child`/`_expand_slots` for growing one); and, per enum field, its
legal value range - only `DriverAttributeEnum`'s is decoded today (finding
18 §9 / ROADMAP R25).

### Reproducing

```
py -3.11 -u experiments/graph_synthesis/build_r27.py
py -3.11 -u experiments/graph_synthesis/probe_minimal_root.py
py -3.11 -u experiments/graph_synthesis/test_cross_clone.py

# then, from the repo root, through 32-bit PowerShell
# (experiments/gcp_harness/README.md says how to launch it):
Load-Package.ps1 -Path experiments/graph_synthesis/out/1bynd_19_r27_cross_clone.pkp -Deserialize -Commands -Protocol
Load-Package.ps1 -Path experiments/graph_synthesis/out/1bynd_19_r28_stripped_root.pkp -Deserialize -Commands -Protocol
```
