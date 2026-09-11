# graph_probes/

The packages that located finding 18's section 6 bug — the one no Python-side
check could see. Every file here was built from the i20 donor
(`samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp`) on
2026-09-10, and every one of them **validates** (`tools/pkp_validate.py`
returns `Valid`). What separates them is whether Extron's own deserializer
accepts them.

Re-run any of them with
`experiments/gcp_harness/Load-Package.ps1 -Deserialize` (32-bit PowerShell).

## The bisection

Built with the **original** id allocator, which mirrored .NET's negative ids
for inline value types. One operation each:

| file | operation | BinaryFormatter |
|---|---|---|
| `probe_A.pkp` | `clone_command` (Backlight → TrackingFraming) | **fails** |
| `probe_B.pkp` | + `text_map` state rename | **fails** |
| `probe_C.pkp` | + description (fresh string object) | **fails** |
| `probe_D.pkp` | + detach an enum state | **fails** |
| `probe_E.pkp` | + compose a parameter (ZoomPosition) | **fails** |
| `probe_F.pkp` | + `rename_asset` on a cloned state | **fails** |
| `probe_G.pkp` | + `set_attributes` | **fails** |

All seven: `SerializationException: An object cannot be registered twice.`

The minimal edits, none of which clone anything:

| file | edit | BinaryFormatter |
|---|---|---|
| `min_P0.pkp` | untouched rebuild | OK |
| `min_P1.pkp` | append one unreferenced string record | OK |
| `min_P2.pkp` | append a string and repoint a member at it | OK |
| `min_P3.pkp` | grow a command `BinaryArray` past its capacity | OK |

And the decisive pair — the same single clone, differing only in id sign:

| file | ids minted for cloned inline value types | BinaryFormatter |
|---|---|---|
| `q_MIX.pkp` | negative, mirroring the original | **fails** |
| `q_POS.pkp` | positive | OK — and `LoadFromFile` enumerates 16 commands |

`compose_test.pkp` is the first ZoomPosition composition test from the same
(negative-id) era; it validates and does not load.

The fix is in `tools/nrbf_graph.py` (`IdAllocator` is always positive) and is
asserted by `tools/test_pkp_asset.py [8]`, because nothing downstream of our
parser can see it.

## eir/

Finding 16 section 5b: Extron's validator exempts any file whose on-disk name
ends in `eir`, without hashing anything.

| file | what it is | `pkp_validate.py` |
|---|---|---|
| `extr_17_17677_v1_0_0.pkp` | unmodified, identical to `samples/DSC_12G-HD/pkp/` | `Valid` |
| `bad_plain.pkp` | the same package with its script digest corrupted | `MismatchHash 80085` |
| `bad_ondisk.eir` | **byte-identical** to `bad_plain.pkp`, renamed | skipped as IR — Extron returns `Valid` |
