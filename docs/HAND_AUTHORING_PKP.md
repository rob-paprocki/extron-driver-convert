# Hand-authoring an Extron .pkp

A field guide to producing a working Extron `.pkp` by editing or extending a real donor package, using the tools in `tools/` and the single front door in `tools/convert.py`.


## What this guide gives you, and what it does not

Scope: the proven path for hand-authoring a `.pkp`, which is **donor-transplant** on top of a real Extron package. A ControlScript module becomes the embedded script of a donor whose asset tree you can then extend to add commands. From-scratch synthesis of an NRBF object graph is open work (ROADMAP R28); this guide does not cover it.

Two gates are referenced throughout:

* `convert.py validate` runs the project's Python reimplementation of Extron's hash validator (Finding 16). Local check.
* `convert.py verify --load-package` runs Extron's own deserializer on Windows (Finding 18 gate). The only acceptance check that is not sharing your model of the format.

The names are called out early because every section downstream points back to them. Prefer `verify` over `validate` for anything you intend to upload to a processor.


## What a .pkp actually is

A `.pkp` file is a gzip member wrapping a raw [MS-NRBF] (.NET BinaryFormatter) serialization stream. The stream contains a graph of `Extron.Configuration.*` objects: assets, command collections, string tables, parameter definitions, resource bindings. There is a Python driver inside, serialized as a `StreamResourceAsset` whose bytes are the script source.

Global Configurator reads two sidecar files when it catalogues your drivers: `DataFile.dat` and `DriverLookup.dat`. Both are raw NRBF and parse with `pkp_dump.py`. GC's catalogue is a derived index; the gate between discovery and selection is parsing those files, not reading the `.pkp` itself.

**Finding 18 is the controlling claim here: the asset tree is the command surface.** GC never asks the embedded Python what commands it supports. The commands come from the serialized asset graph. A `.pkp` whose script defines `_cmd_SetZoom` but whose asset tree has no corresponding command node will not render that command in the editor, and a `.pkp` whose asset tree lists `SetZoom` with ranges and enums will render it regardless of whether the script implements it. The script is downstream of the graph.

This is why editing commands means editing the object graph, not the script.


## Why hand-authoring from scratch is not the move yet

ROADMAP R28 is the open item for assembling an NRBF object graph from scratch. Pieces of that work are in `tools/pkp_build.py` and `tools/pkp_asset.py`, but the measured end-to-end path (through to the 20025/20026 run on an IPCP Pro 360, with a panel driving a PC playing a camera) is donor-transplant. Pick a real package. Change what you need. Validate. Verify.


## The donor-transplant method

The mental model behind `cs2pkp` and the `pkp_asset` library:

1. Pick a donor `.pkp` whose shape matches your target (same processor class, closest device family, Extron-published).
2. Replace the embedded script resource with your ControlScript module.
3. Optionally append new commands to the asset tree.
4. Validate (`convert.py validate`).
5. Verify through Extron's deserializer on Windows (`convert.py verify --load-package`).
6. Upload to a processor and bind a transport.

`tools/pkp_build.py` enforces the safety property that makes the method trustworthy. On open, `PackageBuilder.__init__` round-trips the donor against its own decompressed bytes. If the trace does not replay byte-for-byte, it raises `RoundTripError` and refuses every subsequent edit. There is no bypass flag.


## Picking a donor

The donor picks the device descriptor, the resource bindings, the signature, and the GUID table. A wrong donor produces a `.pkp` that validates and loads but behaves incorrectly on-device, and no local gate catches it.

Criteria, in order:

* Same processor class as the target.
* Closest device family (an IV camera donor for an IV camera target).
* Extron-published (so the SHA matches `vendor-files.manifest.tsv` and the signature chain is known-good).
* SHA-verified: `python tools/verify_vendor_files.py --only <path-prefix>` prints each file's hash status.
* Inspected before edit: `python tools/convert.py dump <candidate>` prints the NRBF graph as JSON; `python tools/pkp_asset.py <candidate>` prints the command list directly from the asset tree.

If a field in the dump is a surprise, resolve it before transplant. The donor's shape is the shape your output will have, minus the edits you make.


## The asset tree is the command surface

A command in the asset graph is a `CommandAsset` node (plus owned sub-nodes for parameters, enum states, ranges, descriptions, strings). Appending a command means adding a `CommandAsset` and threading it into every command collection that the parent group holds. The `CommandGraph` class in `tools/pkp_asset.py` is the library interface:

```python
import pkp_build as pb
import pkp_asset as pa

builder = pb.PackageBuilder("corpus/<DONOR>.pkp")   # round-trip gate fires here
graph = pa.CommandGraph(builder)

print("existing commands:", sorted(graph.command_names()))

# clone an existing command and rename it. this is the measured path for
# adding a new command: clone a donor that already has the shape you need,
# then adjust its strings via text_map or set_string_member afterwards.
new_id = graph.clone_command(
    donor_script_name="SetZoom",
    name="SetZoomSlow",
    script_name="SetZoomSlow",
    description="Slow zoom in/out",
    text_map={"SetZoom": "SetZoomSlow"},
)

builder.write("build/i20-authored.pkp")
```

`CommandGraph` exposes the operations that preserve the invariants the stream needs: `clone_asset`, `clone_command`, `attach`, `detach`, `rename_asset`, `set_range`, `set_string_member`, `set_attributes`. Direct NRBF edits sit beneath `PackageBuilder` and are not recommended for authoring.

The `pkp_asset.py` CLI (just `python tools/pkp_asset.py <package.pkp>`) lists commands and their collections. The real work is library-mode.


## The negative-object-id trap

Finding 18 is the most expensive single thing the project paid for, and the trap is specific. **.NET's BinaryFormatter writes inline value types with NEGATIVE object ids.** A negative id is not a free identifier; it is a marker the formatter uses for its own value-type bookkeeping. An early `pkp_asset` allocator mirrored that convention when cloning a subtree, so copies kept their value-type members looking like the original. The resulting stream parsed, round-tripped, validated, and passed every structural test the project could write.

Then GC refused the package. `BinaryFormatter.Deserialize` through 32-bit reflection raised:

```
SerializationException: An object cannot be registered twice.
```

Minting new negative ids collided with the formatter's own bookkeeping during deserialization. The fix was to clone the same subtree with positive ids throughout.

**Invariant to enforce when editing by hand:** never allocate new negative object ids. If you clone an asset, the clone's ids start strictly past the donor's maximum positive id. The current `CommandGraph` allocator does this; a from-scratch graph writer must not reintroduce the trap. `test_pkp_asset.py` asserts the invariant directly, because nothing downstream will.


## String table and reference bookkeeping

The NRBF stream deduplicates strings. Most text you see in a dump is a `BinaryObjectString` record referenced by object id, not an inline string. Editing a label in place by overwriting the text member of one reference leaves the string table out of sync: other references to the same id now point at content that no longer matches, or the referenced record size changes and the stream's size fields drift. The parser still accepts the result; the deserializer does not.

The `CommandGraph.set_string_member(asset_id, member, text)` call is the supported way to change a label on a cloned asset. It allocates a fresh string record and rewrites just the reference, preserving the donor's string table.


## Validating without Global Configurator

`convert.py validate` runs the project's Python reimplementation of Extron's package validator. Finding 16 settled this: the Python implementation agrees with Extron's own code on all 1,853 shipping packages (with the Guid table) and on all 53 deliberate mutants. GC is not needed to check whether a package will catalogue.

```bash
python tools/convert.py validate build/i20-authored.pkp
```

Successful output is `pkp_validate.py`'s per-package status followed by the gate reminder, printed to stderr:

```
note: valid != loadable (Finding 18). Run `convert.py verify --load-package` for the full gate.
```

An `80085`-shaped failure (the Finding 15 and 16 case) is a SHA-256 mismatch between a resource's declared hash and its actual bytes. `pkp_validate.py --verbose` prints a line per resource and names the one that drifted. See `experiments/validator_differential/` for the test corpus and the Guid-table flag.


## Verifying through Extron's own code

The validator shares your model of the format. Finding 18 showed this is not enough. The full gate is Extron's own deserializer, which only runs on Windows with the Extron Configuration DLLs installed. `convert.py verify --load-package` is the one call that clears it.

Off Windows, or without `--load-package`:

```bash
python tools/convert.py verify build/i20-authored.pkp
```

prints the exact command for a Windows session to run:

```
& "$env:SystemRoot\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "experiments/gcp_harness/Load-Package.ps1" "build/i20-authored.pkp"
```

Two things in that command matter. First, the host is **32-bit** PowerShell (`SysWOW64` on a 64-bit OS). Extron's Configuration assemblies are x86; the 64-bit host cannot load them. Second, `Load-Package.ps1` installs an `AssemblyResolve` handler that maps the stream's `Extron.Configuration.* 1.1.24.402` references onto the installed `15.27.0.0` DLLs, then calls `BinaryFormatter.Deserialize`.

`LoadFromFile` on the same package is **not sufficient**: it catches the exception and returns null, which looks exactly like a non-existent file. `BinaryFormatter.Deserialize` with the resolver surfaces the real `SerializationException`.

A cloud session cannot clear verify. The 32-bit assembly load and an installed Extron GC are both required.


## Writing the embedded script side

The script inside a `.pkp` is still a ControlScript module. The constraints are the same as for a standalone module:

* No absolute paths in docstrings or string literals. CLAUDE.md pitfall 6 is specific: a path under `C:\Users` in a non-raw docstring on Windows puts a literal `\U` into the stream and raises `SyntaxError`. Emit repo-relative, forward-slashed paths.
* Repo-relative provenance strings. The pattern used by the Crestron translator in `experiments/crestron2cs/crestron2cs.py:provenance_path()` is a working example, but there is no public helper for script authors to import. The convention is what matters, not the function.
* `pkp2cs.py`'s output is a safe starting template. The emitter raises rather than degrading; whatever it writes resolves at runtime on the dialect it detected.

Finding 14 is worth re-reading before you ship: 54% of mechanically translated modules would raise `AttributeError`, `NameError`, or hit an argument-count mismatch at runtime. Static checks catch some of it. Running the module in `experiments/exec_harness/` catches more. A module that lands on a processor is the only check that catches everything.


## Worked example: wrapping an i20 ControlScript module into a .pkp

The i20 is the best-measured oracle pair in the repo. Findings 09, 13, and 18 all centre on it. The corpus snapshot carries a round-trippable donor; `experiments/skeleton_i20/` carries the module. Every command below is the current CLI; adjust the paths to the files you have.

**Step a. Pick and verify a donor.** The `corpus/` snapshot is where real `.pkp` donors live:

```bash
python tools/verify_vendor_files.py --only corpus/
```

The report prints a line per listed file with its SHA status. Note the donor's path; call it `<DONOR>` below.

**Step b. Inspect the donor's command list.**

```bash
python tools/pkp_asset.py <DONOR>
```

prints the commands and their collections directly from the asset tree. `convert.py dump` is the deeper read:

```bash
python tools/convert.py dump <DONOR> -o build/donor.json
```

Record the embedded script resource KEY from the dump; `convert.py cs2pkp` needs it. The KEY is the name GC uses to refer to the script resource, not the module filename.

**Step c. Transplant the ControlScript.** Replace the donor's embedded script with your i20 ControlScript module:

```bash
python tools/convert.py cs2pkp <DONOR> \
    --script "<KEY>=experiments/skeleton_i20/<i20_module>.py" \
    -o build/i20-authored.pkp
```

Behind the scenes this invokes `pkp_build.py <DONOR> --replace-script KEY=FILE -o OUT`; the output and exit code are `pkp_build.py`'s. If the KEY is wrong, the donor's original script is left in place and the output passes validate (because the hashes are refreshed) and verify (because the stream is clean), but behaves as the donor's device. Confirm the KEY before shipping.

**Step d. Append commands via the `pkp_asset` library.** The script above transplants the Python side. To extend the command surface, write a short authoring script:

```python
# scripts/add_i20_commands.py
import pkp_build as pb
import pkp_asset as pa

builder = pb.PackageBuilder("build/i20-authored.pkp")
graph = pa.CommandGraph(builder)

# clone an existing command and rename it. the donor_script_name is the
# script_name of a command already in the graph; graph.command_names()
# prints the full list.
graph.clone_command(
    donor_script_name="SetZoom",
    name="SetPresetSlow",
    script_name="SetPresetSlow",
    description="Recall a preset at slow speed",
    text_map={"SetZoom": "SetPresetSlow"},
)

builder.write("build/i20-authored.pkp")
print("appended commands:", [c for c, _id in graph.added])
```

Run it:

```bash
python scripts/add_i20_commands.py
```

The `donor_script_name` must already exist in the graph (`clone_command` raises `AssetError` otherwise). Fresh ids come from the allocator with the Finding 18 invariant baked in.

**Step e. Validate.**

```bash
python tools/convert.py validate build/i20-authored.pkp
```

A clean exit prints the gate reminder on stderr. Treat it as a reminder, not a result.

**Step f. Verify through Extron's deserializer.** On Windows with GC installed:

```bash
python tools/convert.py verify --load-package build/i20-authored.pkp
```

Off Windows, run the printed `Load-Package.ps1` command on a Windows session. A pass means the stream deserializes cleanly; a `SerializationException` with "An object cannot be registered twice" means a negative-object-id regression (Finding 18). If verify fails and validate passed, the model you edited through is wrong somewhere, and the invariant is the first thing to re-check.

**Step g. Round-trip against the wire table.** `convert.py pkp2cs` writes the ControlScript back out, and `wire_table.py diff` compares its wire bytes to the module you started from:

```bash
python tools/convert.py pkp2cs build/i20-authored.pkp -o build/i20-roundtrip/
python tools/wire_table.py diff \
    experiments/skeleton_i20/<i20_module>.py \
    build/i20-roundtrip/<generated_module>.py
```

A clean diff is the acceptance signal for the translator half. The command-surface edits you made will show as added commands in the diff; nothing from the donor should drift.


## Loading onto a processor

The measured upload path is in `experiments/skeleton_i20/PROTOCOL.md`. Packages `20025` and `20026` were uploaded from Global Configurator Pro to an IPCP Pro 360 and driven from a TLP Pro 725M panel against a PC playing an i20 camera (2026-09-14 to 09-18 run log). Package `20028` (v1.6) is the current authored version. The upload uses GC Pro's normal project workflow; nothing custom was needed on the processor side.

The one remaining open question is a real camera. Every reply parsed so far came from the documentation. A socket to an actual i20 is the next measurement.


## Pitfalls checklist

Each item is paid for by a finding or methodology note. The guide's full discussion is linked.

* **A negative claim needs positive evidence.** Finding 08 twice asserted an endpoint was undocumented when it was not. Report a negative as "not found by method X," never as "does not exist."
* **Acceptance is the wire-string table.** Line overlap between a package and its shipped module ranges 76% to 38% while command tables stay near-identical. Use `wire_table.py diff`.
* **Wire correctness is necessary but not sufficient.** Finding 14 ran generated modules and 54% raised at runtime. Four static checks catch a lot; some bug classes only surface on execution.
* **Valid is not loadable.** `convert.py validate` reads through this project's Python model of the format. Finding 18 showed the model can agree with itself and still disagree with Extron's deserializer. `convert.py verify --load-package` is the full gate.
* **Unresolvable means opaque, never guessed.** `wire_table.py` emits counted opaque markers rather than plausible-looking fabrications. Preserve that posture when extending the translator.
* **No absolute paths in generated output.** CLAUDE.md pitfall 6 is the specific rule. On Windows a `C:\Users` path in a non-raw docstring puts a literal `\U` into the stream and raises `SyntaxError`.


## Converting instead of authoring

For users who want a direction other than `cs2pkp`:

```bash
python tools/convert.py directions
```

prints the four conversion directions, each with its verification status and the gating finding or ROADMAP item.

* `pkp2cs` is a measured translator. `pkp2cs.py` reports every unresolvable expression as a counted residual rather than guessing (Finding 14's methodology).
* `pkg2cs` dumps the Crestron driver JSON via `pkg_dump.py`. The finish from that JSON to a ControlScript module is a manual step; the dialect patterns live in `pkp2cs.py` and the Crestron-specific translator pieces are under `experiments/`.
* `pkp2pkg` is a resource-swap patch, not a full emit. The Extron object graph and the Crestron driver JSON do not share a schema, so `convert.py pkp2pkg` refuses to auto-chain them. It dumps the Extron graph for inspection and prints the exact `pkg_patch.py` command to run once a conforming Crestron driver JSON is produced. The full-emit gate is STATUS.md D2 (the Crestron licence question).


## What is still gated, and on what

Full from-scratch synthesis of an NRBF object graph (ROADMAP R28) is open work. The donor-transplant method is what has carried a package end-to-end.

Real-device acceptance per family is incomplete. The i20 ran against a PC playing the camera; a socket to an actual i20 is the open measurement. Other device families inherit the same status: wire-correct, runtime-resolvable on the harness, unverified on real hardware.

Open question D2 (the Crestron licence position) is a legal question. Nothing in the tools' output substitutes for it. The patch-only posture of `pkp2pkg` holds until D2 closes.

Catalogue coverage for Crestron drivers is unmeasured. Two data points (Samsung JSON engine, 1 Beyond V2 Entity Model) do not generalise. `drivers.crestron.io` is login-gated.

Donor-transplant produces a `.pkp` that validates and deserializes under Extron's own code; device-side correctness still needs a bench run.


## Tool reference

| `convert.py` verb | underlying tool(s) | notes |
|---|---|---|
| `directions` | this file | prints the conversion matrix |
| `dump` | `tools/pkp_dump.py` / `tools/pkg_dump.py` | dispatches by extension; `-r` resolves back-references on `.pkp` |
| `validate` | `tools/pkp_validate.py` | Python reimplementation of Extron's validator (Finding 16) |
| `verify` | `tools/pkp_validate.py` + `experiments/gcp_harness/Load-Package.ps1` | `--load-package` on Windows invokes the deserializer gate |
| `pkp2cs` | `tools/pkp2cs.py` | translator with counted residuals |
| `cs2pkp` | `tools/pkp_build.py` | donor-transplant; `--script KEY=FILE` and `--set-string ID=VAL` |
| `pkg2cs` | `tools/pkg_dump.py` | dumps driver JSON; translation finish is manual |
| `pkp2pkg` | `tools/pkp_dump.py` + prints `pkg_patch.py` command | refuses to auto-chain (schema mismatch) |

For operations the CLI does not cover (library-mode asset edits, wire-table comparison, catalogue inspection), the underlying tools remain the entry point:

* `python tools/pkp_asset.py <package.pkp>` lists commands; the library is `CommandGraph` on a `PackageBuilder`.
* `python tools/wire_table.py dump <driver_py>` prints the normalised wire table.
* `python tools/wire_table.py diff <a.py> <b.py>` diffs two wire tables.
* `python tools/gc_catalogue.py <DriverLookup.dat>` reads GC's catalogue; `--against <folder>` compares to a driver folder.
