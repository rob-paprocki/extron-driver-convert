# Finding 16 — `80085` is a hash mismatch, and the validator is now ours

**Status: measured** 2026-09-09, against `Extron.Configuration.Drivers` 15.27.0.0
running locally. **Supersedes finding 15's hypothesis.**

Finding 15 recorded the hardware failure correctly and then guessed wrong about
its cause. This one decodes it, reimplements Extron's check in pure Python, and
differential-tests that reimplementation against Extron's own code on **1,919
packages**.

## 1. The error code, exactly

`DriverAssetValidator.Validate(IDriverFileAsset)` returns an enum with three
values, read straight off the assembly:

```
Valid         = 0
MismatchHash  = 80085
NoHash_NoGuid = 80086
```

**`80085` is a hash mismatch.** Finding 15 proposed that the failure came from
the embedded script declaring commands the package's asset tree does not — a
tidy story that fit every observation and was wrong. The asset tree is not
consulted. What fails is integrity.

Why the story fit: the only packages we had modified were ones whose script we
had rewritten, and rewriting the script is exactly what breaks the digest. Every
observation was consistent with both explanations. **A hypothesis that explains
all the data is not thereby correct** — it needed one experiment that could
separate the two, and the local validator provided it in seconds.

## 2. What is actually hashed

`DriverFileAsset._resourceHashDict` is a `Dictionary<string, byte[]>`: resource
key → **SHA-256 of that resource's bytes**. Confirmed two ways — `ComputeHash`'s
IL constructs a `SHA256CryptoServiceProvider`, and `sha256(donor script)`
reproduces the stored digest byte for byte.

Both packaged resources are covered:

| resource | hashed? |
|---|---|
| the embedded `.py` driver | yes |
| the comm-sheet `.pdf` | **yes** — embedded in the package, not external |

The `.pdf` was an open question in finding 15 and is now closed: appending bytes
to the PDF without refreshing its digest returns `80085`, measured on three
donors.

## 3. The ladder was answered without hardware

`build_ladder.py` staged three packages to find out whether *any* script edit is
refused or only one that adds undeclared commands. Run against the local
validator, all three answer at once:

| package | change | verdict |
|---|---|---|
| `20030` | **a comment only** | `MismatchHash` |
| `20031` | + the zoom fix | `MismatchHash` |
| `20032` | + i20 methods, `Commands` untouched | `MismatchHash` |

A comment is enough. There is no "content validation" subtlety to find — the
digest covers the bytes. The ladder was built to cost a trip to a system this
repo cannot reach; it cost three seconds instead.

## 4. The fix, and that it is genuinely correct

`pkp_build.refresh_resource_hash()` recomputes and rewrites the stored digest;
`replace_script()` now calls it by default. `--no-refresh-hash` exists only to
reproduce the failure deliberately.

Validated against **Extron's own validator**, not merely against ourselves:

```
_02_refreshed_script  (script replaced + hash refreshed)  ->  Valid
```
on all three donors. The i20 deliverables `20020`–`20023` all return `Valid`.

## 5. A pure-Python validator, and what differential testing found

`tools/pkp_validate.py` reimplements `Validate` using only the standard library
and `pkp_dump.py`, so a package can be checked on any machine — GC is Windows-
only and licensed, and this repo is cloud-first.

Differentially tested against the real validator over **1,919 packages** (1,853
shipping + 13 built + 53 deliberate mutants): **1,900 exact agreements, 19
disagreements**, and three of those were real bugs in the reimplementation. Both
are fixed and re-verified; the third class is Extron's own behaviour.

*(Re-run in full after the fixes, 2026-09-23 —
`experiments/validator_differential/POSTFIX.md`. Shipping: **1,850 of 1,853**;
the 3 are the pre-13.x packages of §5a, now reported as `80086` instead of a
blind `Valid`, and all three agree once the Guid table is supplied
(`--guid-table`, §5c) — so 1,853 of 1,853. Mutants: **45 of 53**, up from 37;
the 8 left are files Extron's `LoadFromFile` refuses before `Validate` runs
(corrupt gzip, truncations, non-`.pkp`/`.eir` extensions), which this tool
scores instead of refusing. The Extron verdicts for the "13 built" packages
were not found in the repo, so those 13 were not re-run.)*

### 5a. It failed open on 3 shipping packages

`extr_10_397_v1_0_4`, `extr_1_789_v1_0_2`, `extr_8_89_v1_0_0` are built against
`Extron.Configuration.Contracts` **1.0.0.0**, where the layout is the reverse of
every other package: the serialized `_manifest` field **holds** the manifest and
there is no `Manifest` child asset. The first implementation looked only for the
child, found none, and returned **`Valid` having verified zero resources**.

It reported success because it had not looked. That is the worst available
failure mode for a validator, and it is the same shape as the four harness bugs
in finding 14 — a wrong assumption yielding a clean-looking result rather than a
crash.

**The 126-case local suite passed while this was true**, because it contained no
pre-13.x package. Only the differential run caught it. Those three packages are
now a regression test.

### 5b. Extron exempts anything named `*eir`

`Validate` returns `Valid` **without hashing anything** when the file's on-disk
name ends in the three characters `eir`, case-insensitively. Eight packages with
deliberately corrupted digests, renamed to `.eir`, pass Extron's own validator.

Two clarifications, both measured:

- It is the **on-disk** name that counts. `LoadFromFile` overwrites `Filename`
  with `Path.GetFileName()`, so the serialized `_filename` has no effect — a
  `.pkp` whose `_filename` was rewritten to end in `.eir` still returns `80085`.
- The reach is bounded. `LoadFromFile` accepts only `.pkp` and `.eir` and
  returns **null** otherwise, so `foo.weir` or a bare `xxxeir` never reaches
  `Validate` at all.

This is presumably deliberate — `.eir` IR drivers carry no embedded script — but
it means integrity is keyed to a filename. Not attacker-controlled through
package content.

### 5c. The Guid fallback is live

`DriverAssetValidator.Instance`'s Guid table is empty on a fresh instance;
`LoadDefaultFromResource()` fills it from an embedded `ExtronDH.dat` with
**4,775 entries**. Loading it turns the three pre-13.x packages from `80086` to
`Valid` and changes **nothing else** across the corpus. Those packages ship with
an empty `_resourceHashDict` and are vouched for entirely by GUID.

`pkp_validate.py` takes an optional `guid_hash_table` and, when it is absent,
labels an `80086` as a prediction rather than a measurement.

## 6. What this changes

- **GC's validator is now a local unit test.** Any package this repo builds can
  be checked in seconds, on any machine, with no hardware and no round trip
  through a person.
- **Finding 15's three gates still stand** — discovery, catalogue parse,
  selection — but the third one's cause is integrity, not declaration.
- **STATUS.md open item 4 narrows again.** A transplanted package with a
  refreshed digest is `Valid` to Extron's own code. What remains untested is a
  package whose object graph was assembled from scratch. *(STATUS has since
  been renumbered; that question is now ROADMAP R28.)*

## What this does NOT show

- **Nothing has run on a processor.** `Valid` means GC will accept the file for
  use; place, build, upload and control are still untouched. *(Since done,
  2026-09-14 to 09-18: `20025`/`20026` placed, built, uploaded to an IPCP Pro
  360 and controlled from a panel, against a PC playing the camera —
  `experiments/skeleton_i20/PROTOCOL.md`.)*
- **The Guid table's contents are not decoded.** 4,775 entries were counted and
  membership tested for the three packages that need it; what else it covers is
  unknown.
- **`ComputeHash(Stream)` is not on `Validate`'s path.** Nothing in
  `Extron.Configuration.Drivers.dll` calls it; the digest comparison uses
  `GetContentHashCode()`. It may be dead code. Only that one assembly was
  scanned for callers.
- **A resource whose content is not `byte[]`** would make Extron throw
  `ArgumentNullException` out of `SequenceEqual` rather than return a code. Read
  from IL, never observed — every resource in every package measured is `byte[]`.
