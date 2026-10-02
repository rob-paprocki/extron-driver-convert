# Crestron SIMPL# libraries, decompiled

`decompile.py` extracts Crestron's SIMPL# libraries from an installed device database
(`<CRESDB>`, see `ENVIRONMENT.md`) and decompiles them with ILSpy's `ilspycmd`, to C# and to IL.
It is the input to two readings:

- `experiments/automate_vx_threeway/REPORT.md` §10: the Automate VX module's requests.
- `experiments/dm_md/DECOMPILE.md`: the DM-MD32X32-CPU3's object model, joins, registration and endpoints.

The owner decided on 2026-09-24 (ROADMAP D2) that these distributed libraries may be decompiled
for interoperability. The output is vendor-derived, so it goes to `out/`, which is git-ignored.
The findings describe the formats the code shows and do not copy it.

```
py -3.11 experiments/crestron_decompile/decompile.py list
py -3.11 experiments/crestron_decompile/decompile.py run          # Automate VX (both builds) + the DM library
py -3.11 experiments/crestron_decompile/decompile.py hash
py -3.11 experiments/crestron_decompile/test_decompile.py
```

`ilspycmd` is the one dependency outside the standard library: `dotnet tool install --global ilspycmd`.
Nothing else in the repo depends on it, and the test uses synthetic packages, so it runs anywhere.

**What the readings were measured against:**

| assembly | where | SHA-256 |
|---|---|---|
| `Automate_VX.dll` | `Automate_VX.clz` in `Modules/crssplus.dat` | `ac6bbcfda23e1be4463bed93aa3145da1e243305c1a3e0157a2850c4185ecdf2` |
| `Automate_Vx_4Series.dll` | `Automate_Vx_4Series.clz` in `Modules/crssplus.dat` | `a7ad416a65dc967d224da90079e7898d1602509fa49641860e2f1b4fd079b55f` |
| `Crestron.SimplSharpPro.DM.dll` | `Programming/Libraries/` (2,185,936 bytes) | `de345091886ecb00798bf3984a8637ccc0f73804d8648bc2a580ca11a9b2be09` |

The decompiler was `ilspycmd` 11.1.0.9782. Line numbers cited in the readings are lines of its
output, so a different version will move them.

**Why IL as well as C#.** ILSpy's C# view prints `[JsonProperty(/*Could not decode attribute
arguments.*/)]` for the Automate VX model classes. Each attribute carries an enum
(`NullValueHandling`) from Crestron's own Newtonsoft build, which the decompiler cannot resolve.
The IL prints each attribute's raw blob, and the JSON key name is the length-prefixed string after
its `01 00` prolog.
