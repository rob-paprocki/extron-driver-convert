# Finding 12 — GC ingests packages we generate, and the gate is an index, not the file

**Status: measured** on Global Configurator **Pro 3.33.0-b.38** (Windows 11,
`Extron.Configuration.Drivers` **15.27.0.0**), 2026-09-07. Every number below was
read off a running GC or off its own index files.

This closes STATUS.md's open item 2 in the direction it was asked, and largely
dissolves open item 4. It does **not** establish that an invented driver works —
see "What this does not show".

## The driver library is not where the install is

GC reads its catalogue from a **user-writable** directory, not from
`Program Files`:

```
C:\Users\Public\Documents\extron\driver3\
```

| | |
|---|---|
| `.pkp` packages | **6,644** |
| `.eir` IR drivers | 1,745 |
| index files | 2 (`DataFile.dat`, `DriverLookup.dat`) |
| total | 8,391 files, 1.5 GB |
| writable without elevation | **yes** |

`C:\Program Files (x86)\Extron\GCP\devices\drivers` also exists and holds 54
`.pkp`, but that is a bundled subset; it is not what Driver Manager reads.

All 7 of this repo's `samples/*.pkp` are present in `driver3` at **identical byte
sizes**, which is presumably where they came from.

Vendor spread of the 6,644, by filename prefix: `lg` 301, `extr` 260, `smsg` 257,
`pana` 210, `opto` 204, `sony` 196, `shrp` 141, `krmr` 120, `epsn` 110, `view` 105,
`nec` 101, `chri` 94, `benq` 87, `barc` 78, `vadd` 64, `csco` 62 … Extron-authored
packages are **4%** of the library.

## The two index files are NRBF, and our existing reader already opens them

Both `.dat` files carry the same NRBF header as a `.pkp` — they are simply **not
gzipped**:

```
DataFile.dat      00 01 00 00 00 FF FF FF FF ...  "RExtron.Co…"   60.9 MB
DriverLookup.dat  00 01 00 00 00 FF FF FF FF ...  "System.C…"    526 KB
```

`tools/pkp_dump.py` parses both **unmodified** — its `load_bytes` already falls
back to raw NRBF when gzip magic is absent.

`DriverLookup.dat` is a `Dictionary<string,string>` of **8,389 entries** mapping
**filename → last-write timestamp**:

```
'1bynd_19_2858_v1_1_0.pkp'  ->  '7/11/2017 2:29:38 PM'
'extr_17_17677_v1_0_0.pkp'  ->  '8/19/2026 3:14:40 PM'
```

8,389 = 6,644 `.pkp` + 1,745 `.eir` exactly. Measured against the directory:
**0 files unindexed, 0 index entries without a file.** It is a staleness mirror of
the directory, and it is what makes the rest of this finding work.

`DataFile.dat` is the catalogue proper — Driver Manager reports **26,141 models**
from it, far more than the file count, because one package carries many models.

## GC rescans and self-heals — no import UI involved

Dropping a file into `driver3` and starting GC is sufficient. On each start GC
detects the mismatch against `DriverLookup.dat`, **truncates `DataFile.dat` to 0
bytes and rebuilds the whole catalogue** (2–4 minutes, splash reads
"Organizing Driver Manager…"), then appends one lookup entry.

Three tests were run in sequence, each from a clean restart, each a separate
package staged into `driver3`.

| # | staged | what it tests | `DataFile.dat` | `DriverLookup.dat` | models |
|---|---|---|---|---|---|
| — | baseline | — | 63,820,256 | 525,881 (8,389) | 26,141 |
| 1 | byte-identical copy under a new filename | discovery | +3,309 | +65 (8,390) | — |
| 2 | `nrbf_write.py` round-trip of `extr_17_17677` | our writer's bytes | +5,162 | +65 (8,391) | 26,143 |
| 3 | same, with one string mutated | GC read *our* bytes | +5,169 | +65 (8,392) | 26,144 |

**Test 1 — discovery.** `pion_10_555_v1_0_0.pkp` copied to
`pion_10_999555_v1_0_0.pkp`. Index diff after restart was exactly one added key,
nothing changed, nothing removed:

```
ADDED (1):  pion_10_999555_v1_0_0.pkp  ->  '8/6/2014 1:41:34 PM'
REMOVED(0)  CHANGED(0)
```

**Test 2 — our writer's output.** `extr_17_17677_v1_0_0.pkp` (DSC 12G-HD) read
from `driver3`, round-tripped through `experiments/nrbf_writeback/nrbf_write.py`
(629,733 bytes in, byte-identical out, SHA `1e6fcd25cfd52e695e8e`), re-gzipped by
us at `compresslevel=9, mtime=0` — so the **container differs from Extron's** —
and staged as `extr_17_999677_v1_0_0.pkp`.

Model count went 26,141 → 26,143, i.e. **+1 per staged package**, and the split
moved Serial 19,297→19,298 and Ethernet 15,674→15,675. The DSC package landed on
the **Ethernet** side, which is correct for it: GC read transport metadata out of
bytes our writer emitted, and out of a gzip member we produced.

**Test 3 — semantic mutation.** Same package, with object id 540 changed from
`'DSC 12G-HD A'` to `'ZZCLAUDETEST 12G-HD'` via `mutate_string_by_object_id`
(payload 629,733 → 629,740, +7 bytes; the unmutated re-write was re-asserted
byte-identical first as a control). Staged as `extr_17_999678_v1_0_0.pkp`.

Searching Driver Manager for `zzclaudetest` returns **exactly one row**:

| Manufacturer | Model | Model Version | Device Type | File |
|---|---|---|---|---|
| Extron | **ZZCLAUDETEST 12G-HD** | 1.0 | Scaler | `extr_17_999678_v1_0_0.pkp` |

So GC decompressed our gzip, deserialized our NRBF, pulled a string we wrote out
of the object graph, and surfaced it as a searchable catalogue model — while still
deriving Manufacturer, Model Version and Device Type correctly from the rest of
the package.

## No signing, no validation gate observed

Finding 01 established the container is unencrypted and unsigned. This adds that
**nothing downstream checks it either**: GC ingested bytes we produced, in a gzip
member we produced, with no signature prompt, no integrity warning, and no
rejection. The assembly-version skew is also tolerated — the packages declare
`Extron.Configuration.Drivers, Version=13.26.0.15` in their `BinaryLibrary`
records while the installed assembly is **15.27.0.0**.

## What this does not show

Stated plainly, because the tests all started from a real package's byte stream:

- **Not a from-scratch package.** All three staged files descend from an existing
  `.pkp`. A synthesised object graph — assets assembled rather than round-tripped —
  is still untested. What is now known is that the container, the index and the
  catalogue ingest impose no barrier; the remaining question is only whether a
  hand-built graph satisfies the deserializer.
- **Not a working driver.** Appearing in Driver Manager is catalogue acceptance.
  It is not evidence the driver can be placed in a project, built, uploaded, or
  that it controls a device. Per this repo's own standing note, acceptance at one
  layer is necessary and not sufficient.
- **One package, one string.** Test 3 mutated a single model-name string. It does
  not show that arbitrary edits — command tables, parse patterns, transports —
  survive the same path.

## Practical consequences

1. **Open item 4 is largely answered by the machine, not by more sampling.** The
   project had 4 oracle pairs, all Extron-authored. `driver3` holds 6,644 packages
   across hundreds of vendors, 96% of them third-party. That is the "more pairs,
   especially third-party" the item asked for, already on disk.
2. **The acceptance loop is scriptable and cheap.** Stage → start GC → wait for
   rebuild → diff `DriverLookup.dat`. The whole check is one file under 526 KB,
   readable by `pkp_dump.py`; no GUI scraping needed. Model count via UI Automation
   is a useful corroborating signal.
3. **Rebuilds are all-or-nothing.** GC truncates `DataFile.dat` before rebuilding,
   so an interrupted start leaves a 0-byte catalogue. Back both `.dat` files up
   before any experiment — 64 MB, and it is the whole restore.

## Reproducing

Requires Windows with GC installed; nothing else. All staging is in
`C:\Users\Public\Documents\extron\driver3`, which needs no elevation. Back up
`DataFile.dat` and `DriverLookup.dat` first, stage the package, restart GC, wait
for `DataFile.dat` to return to a stable non-zero size, then diff the lookup.

The store used here was left as found: the three test packages were removed and
both index files restored from backup, verified by SHA-256 and by re-parsing the
index (8,389 entries, index == disk == baseline).

## Licence note, recorded because it is time-boxed

The GC Pro licence on this machine reads **"Expires in 30 Days"** as of
2026-09-07. Anything in this direction that needs GC Pro should be done inside
that window or the licence renewed first.
