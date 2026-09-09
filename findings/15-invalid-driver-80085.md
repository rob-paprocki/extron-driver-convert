# Finding 15 — the asset tree is the contract, not the script

**Status: measured on hardware** 2026-09-08, Global Configurator Pro, on a
system this repo has no access to. First hardware test of a package this
project built.

This is the answer to STATUS.md open items 4 and 5, and it splits them apart:
a transplanted package is **discovered, parsed and catalogued**, and then
**rejected at selection** — with a specific error — the moment the embedded
script declares commands the package's asset tree does not.

## The result

Four packages, each differing from the previous by one thing:

| package | change | outcome |
|---|---|---|
| `1bynd_19_20020` | none (byte-identical copy, new filename) | **loads** |
| `1bynd_19_20021` | two model strings renamed to `IV-CAM-I12`/`I20` | **loads** |
| `1bynd_19_20022` | embedded script substituted | **rejected** |
| `1bynd_19_20023` | renamed + script substituted | **rejected** |

The rejection, verbatim:

> **Invalid Driver**
> There seems to be something wrong with the driver selected. Try downloading
> the driver again from www.extron.com or call for an Extron representative
> for support.
> 1 Beyond - Camera (1bynd_19_20023_v1_0_0.pkp)
> **Error Code: 80085**

`80085` appears nowhere in the GCP install or in the harvested vendor
documentation; it is undecoded.

## Catalogue acceptance really is not driver acceptance

Finding 12 warned that getting listed in Driver Manager proves nothing about
use. That was a caution; this measures it.

The index files, before staging and after GC's rebuild:

| | `DataFile.dat` | `DriverLookup.dat` | our packages indexed |
|---|---|---|---|
| before | 18,591 | 1,409 | 0 |
| after | **51,695** | **1,669** | **all 4** |

`DriverLookup.dat` lists all four including the two that fail, and
`DataFile.dat` grew by 33 KB absorbing them. So GC **discovered** them,
**parsed** them into its catalogue, and presented them in the UI as
"1 Beyond - Camera". Rejection happens later, when the driver is selected for
use.

Three separate gates, and they fail differently:

1. **discovery** — filename vs internal id mismatch is tolerated (`20020`
   carries the internal identity `1bynd_19_4743` under a different filename)
2. **catalogue parse** — passes even for the packages that will be refused
3. **selection** — where `80085` is raised

## Why the script substitution fails

A `.pkp` declares its command surface **as assets in the NRBF object graph**,
not in the embedded Python. The donor carries:

| asset | count |
|---|---|
| `DriverCommandAsset` | 27 (15 distinct device commands) |
| `EnumStateAsset` | 56 |
| `DecimalParamAsset` | 43 |
| `EnumParamAsset` | 14 |
| `ExtronCommandIdEnum` | 15 |
| `DriverAttributeEnum` | 15 |
| `ParamAttributeFlags` | 58 |
| `DriverConditionTypeFlags` | 58 |
| `OperatorFlags` | 346 |

The 15 named commands — Auto Exposure, Auto Focus, Backlight, Connection
Status, Focus, Gain, Iris, Pan Tilt, Power, Preset, Shutter, User Defined
Command, User Defined String, White Balance, Zoom — are exactly the script's
`self.Commands` table.

Finding 13's `build_i20.py` added ten commands to the **script's** table
(`[PATCH E3]`) and **zero assets** to the graph. GC builds its UI and its
validation from the asset tree, so the package promises a command surface it
does not declare. That is the most likely cause of `80085`.

**It is a hypothesis, not a measurement.** `experiments/skeleton_i20/build_ladder.py`
emits three packages that test it, each differing by one thing and all leaving
the `Commands` table untouched:

| package | change | what a failure would mean |
|---|---|---|
| `1bynd_19_20030` | provenance comment only | the script is hashed or signed; substitution is dead in this form |
| `1bynd_19_20031` | + the E2 zoom fix | content is validated beyond a byte compare |
| `1bynd_19_20032` | + every i20 method, `Commands` untouched | added methods are themselves the problem |

If `20032` loads, the script side is unconstrained, the i20 command
implementations are already sitting on the processor as dead code, and the
only remaining work is synthesising `DriverCommandAsset` subtrees.

## What this changes

- **Open item 4 is answered in part.** A *round-tripped* package loads. A
  package whose script was replaced does not, unless the asset tree agrees.
  The NRBF writer is not the gate; the object graph is.
- **The transplant approach has a ceiling.** Substituting a script is enough
  to change *behaviour* of existing commands (pending `20031`), and not enough
  to add commands. Adding commands means constructing a `DriverCommandAsset`
  plus its `ExtronCommandIdEnum`, `DriverAttributeEnum`, parameter and state
  assets, and flag objects — from scratch, into an existing graph.
- **The ControlScript module is unaffected.** It has no asset tree; commands
  are declared in the module's own `Commands` dict, which is why the same
  command set works there. For the i20 specifically, that remains the shortest
  path to a working driver.

## What this does NOT show

- **`80085` is undecoded.** The command/asset mismatch is the leading
  hypothesis because it is the one structural inconsistency we introduced, but
  the code has not been traced to a cause in Extron's code.
- **Nothing has driven a camera.** All four packages were tested through GC
  only; gates beyond selection (place, build, upload, control) remain
  untouched.
- **The ladder is unrun.** `20030`/`20031`/`20032` are built and await
  hardware.
