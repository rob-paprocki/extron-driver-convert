# REMEASURE.md — ROADMAP R32: re-measuring docs-only generation for Automate VX

Re-does the docs-only-generation experiment (`experiments/docs_only/`, finding
19 section 3) against a completed harvest, and computes the "~84% (27/32)"
headline `STATUS.md` currently quotes the way finding 08 actually computed it.

Scope of this pass: 9 new pages under `reference/automate-vx-api/API-Reference/`,
plus `experiments/docs_only/generator.py`, `analyze_endpoints.py`,
`endpoint_crossref.txt`, and the new `test_generator.py`. Nothing outside
that was touched; `ENDPOINTS.md`, `INDEX.md`, `STATUS.md`, `ROADMAP.md` and
`findings/` are the orchestrator's — see "What this leaves stale" at the
bottom.

## 1. The harvest gap, closed

Finding 08's correction header (2026-09-07) named 9 pages its original
harvest missed by keyword search alone: `Wake-API.htm`, plus
`AutoSwitchStatus`, `StartAutoSwitch`, `OutputStatus`, `RecordStatus`,
`RoomConfigStatus`, `GetLayouts`, `LayoutStatus`, `GetRoomConfigs` (all
`<Name>-API.htm`). Two more pages the header also named —
`StopAutoSwitch.htm` (no `-API` suffix) and `ChangeRoomConfig-API.htm`
(shortened, documents `ChangeRoomConfiguration`) — were already present in
this repo's `API-Reference/` from an earlier session; the other 9 were not.

All 9 were fetched today (2026-09-23, via `WebFetch`) from
`https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/<Name>-API.htm`
and saved in the same per-page markdown format as the rest of the harvest
(`Source:` line, `# <Name> API` heading, Syntax/Parameters/Responses
sections), each also carrying a `Fetched:` line:

```
reference/automate-vx-api/API-Reference/Wake-API.md
reference/automate-vx-api/API-Reference/AutoSwitchStatus-API.md
reference/automate-vx-api/API-Reference/StartAutoSwitch-API.md
reference/automate-vx-api/API-Reference/OutputStatus-API.md
reference/automate-vx-api/API-Reference/RecordStatus-API.md
reference/automate-vx-api/API-Reference/RoomConfigStatus-API.md
reference/automate-vx-api/API-Reference/GetLayouts-API.md
reference/automate-vx-api/API-Reference/LayoutStatus-API.md
reference/automate-vx-api/API-Reference/GetRoomConfigs-API.md
```

`API-Reference/` now holds 44 files: 43 endpoint pages (each with its own
`Base URI` line) + the `API-Reference.md` index page. 32 original + 2
already-fetched (`StopAutoSwitch`, `ChangeRoomConfiguration`) + these 9 = 43.

**Two discrepancies worth recording while reading these pages:**

- `OutputStatus-API.md`'s fetched content has no Error response block at
  all, unlike every sibling status page (`RecordStatus`, `RoomConfigStatus`,
  `AutoSwitchStatus`, `LayoutStatus` all document one). Recorded in the file
  itself as "not found by method WebFetch (2026-09-23)" rather than invented.
- `RoomConfigStatus-API.md`'s own page gives the success field as plural
  `"roomConfigs": [...]` (a list), while `GetAllStatus-API.md`'s embedded
  example for the same sub-API (`api_call_12`) shows a *singular*
  `"roomConfig": {...}` object instead. Both are cited verbatim, not
  reconciled — the generator (below) trusts the endpoint's own dedicated
  page over `GetAllStatus`'s example, per the same type-precedence policy
  `generator.py`'s docstring already states for prose vs. example bodies.

**Confirmed still absent, re-checked live today** (not just cited from the
2026-09-07 correction): `StartISORecord-API.htm`, `StopISORecord-API.htm`,
`ISORecordStatus-API.htm` and `CopyStatus-API.htm` all return HTTP 404 via
WebFetch, 2026-09-23. Not found by method WebFetch direct probe — the same
method finding 08 used, re-run rather than assumed still true.

## 2. Coverage, re-run

`analyze_endpoints.py` no longer hardcodes which endpoints are
"documented" (that hardcoded set is exactly the kind of staleness finding 08
tripped on once already). It now scans every `*.md` under `API-Reference/`
for its own `Base URI` line at run time — see `build_documented_uris()` —
so "has a dedicated page" is answered by the corpus on disk, not by a
frozen Python set. The 9 sub-APIs `ENDPOINTS.md`'s "Undocumented sub-APIs"
section names are still hand-transcribed (a scan can prove a page *exists*,
not enumerate names that have none), but any name the scan finds now DOES
have a page is dropped from the example-only bucket automatically.

Full output: `experiments/docs_only/endpoint_crossref.txt` (regenerated
2026-09-23 with `py -3.11 experiments/docs_only/analyze_endpoints.py >
experiments/docs_only/endpoint_crossref.txt`).

| | before (6 DOC_GAP, stale harvest) | after (this pass) |
|---|---|---|
| documented-endpoint pool size | 32 (frozen `OFFICIAL_32`) | 43 (scanned) |
| official coverage, both generated+shipped | 22 | **26** |
| official, shipped-only (generator never built it) | 0 | **4** |
| official, generated-only (Extron chose not to build it) | 10 | 13 |
| sub-API (example-only) coverage, both | 5 | **1** |
| sub-API, generated-only | 4 | 1 |
| DOC_GAP (Extron calls it, appears nowhere in the corpus) | 6 | **2** |

The DOC_GAP set shrank from `{ChangeRoomConfiguration, StartAutoSwitch,
StopAutoSwitch, StartISORecord, StopISORecord, Wake}` to `{StartISORecord,
StopISORecord}` — exactly the 4 endpoints whose pages this pass fetched and
that Extron also calls. Those 4 didn't just move buckets silently: they
surface as the new **"official, shipped-only (4)"** row above, i.e. *now
documented, but the generator's endpoint spec (written before this harvest
existed) never had a contract for them and so never built
`SetWake`/`SetAutoSwitch`-via-`StartAutoSwitch`/etc. That's a live follow-up
this pass did not take (see "What this doesn't do" below) — the R32 task
asked to fix the two response-handling defects and re-measure, not extend
the endpoint set.

`api/ISORecordStatus` (the query-side of the ISO-record family) still has no
dedicated page, but stays classified `EXAMPLE_ONLY` rather than `DOC_GAP`
because it *is* named with a response shape inside `GetAllStatus-API.md`'s
example — "documented by example but not by page," in finding 08's phrase.
Only the two Start/Stop ISO-record commands, which appear nowhere in the
corpus at all (not even inside an example), are `DOC_GAP`.

## 3. Generator defects fixed

Finding 19 recorded two defects in `generator.py`, both confirmed present
before this pass:

- `grep -c "self.WriteStatus(.*res, qualifier)" automate_vx_docs_only.py`
  returned **15** (of the module's 33 commands) — every `Update<Cmd>` built
  through `gen_simple_update()` handed `WriteStatus` the raw, undecoded HTTP
  response dict (envelope keys `status`/`message` and all), where
  `WriteStatus`/downstream consumers expect a scalar.
- `GetAllStatus-API.md`'s own NOTE — "Each individual response body is of
  type string and must be deserialized by the client" — was never acted on:
  each of the 13 nested `api_call_N.response_body` values stayed an
  undecoded JSON-in-JSON string.

**Fix, from documentation only (never from Extron's module):**

- `gen_simple_update()` now takes `result_field` (a single JSON field name)
  or `result_fields` (a list, for responses with more than one
  status-bearing field), cited from each endpoint's own doc page, and
  extracts that value(s) before calling `WriteStatus`. All 15 call sites in
  `build_module()` now pass one or the other — see the field-by-field
  citations inline (e.g. `CameraStatus` → `address`; `RecordingSpaceAvail` →
  `available_gigabytes`/`total_gigabytes`; `RoomConfigStatus` →
  `roomConfigs`, with the plural-vs-singular discrepancy noted above spelled
  out in its own `doc_note`).
- A new `gen_get_all_status()` replaces the generic `gen_simple_update()`
  call for `GetAllStatus`: it loops `api_call_0..12`, `json.loads()`s each
  `response_body`, and writes a dict keyed by `request_api` name (e.g.
  `'AutoSwitchStatus': {...}, 'StreamStatus': {...}, ...`) — real nested
  objects, not opaque strings — into `GetAllStatus`'s own `Status`.

After the fix: `grep -c "self.WriteStatus(.*res, qualifier)"
automate_vx_docs_only.py` → **0**. `"json.loads(call['response_body'])"` is
present once, inside `UpdateGetAllStatus`.

**Re-measured against Extron's shipped module with `tools/wire_table.py`.**
Because `tools/wire_table.py` is itself under concurrent, in-progress edit
elsewhere in this tree (ROADMAP R36 — confirmed via `git diff --stat HEAD --
tools/wire_table.py`, 192 changed lines uncommitted at measurement time),
this measurement used a **snapshot of `tools/wire_table.py` taken from
`HEAD`** (saved to this session's private tmp dir, run as a standalone
script), not the live in-progress file, so the numbers below don't depend on
another agent's half-finished edit:

- `wire_table.py diff <regenerated-module> <Extron-shipped-module>` is
  **byte-identical** to the diff recorded before the fix
  (`experiments/docs_only/diff.json`, unchanged — confirmed by re-running
  and diffing against the file on disk). Same for `wire_table.py dump
  <regenerated-module>` against `wire_table.generated.json`.
- This is expected, not a null result: `wire_table`'s `Template` extraction
  for an `Update` method looks only at the arguments of its
  `__UpdateHelper(...)` call (`_extract_template_from_helper_call`); nothing
  the method does with the *returned* value — raw passthrough, field
  extraction, or a `json.loads()` loop — is visible to it. Finding 19 said
  exactly this ("wire_table only cares about the request side"); this pass
  is a direct, reproduced confirmation of that limit, not just a repetition
  of the claim.

`experiments/docs_only/test_generator.py` (new) pins this down as a
permanent regression test rather than a one-off observation: section 4
asserts the extracted `update_template.source` for `GetAllStatus` and
`CameraStatus` is *exactly* their `__UpdateHelper(...)` call, structurally
proving the response-side fix can't move wire_table's numbers, rather than
comparing two snapshots (a snapshot-equality test would have spuriously
failed here today, precisely because of R36's unrelated concurrent edit —
see "Test results" below).

## 4. The "~84% (27/32)" headline, recomputed

`STATUS.md` currently reads: *"~84% (27 of 32) of what a real driver
calls."* That is **a different, simpler metric** than either coverage table
above: not "does the generator build it," but **"of the endpoint URIs
Extron's shipped module actually calls, how many have a dedicated
documentation page at all"** — an upper bound on what docs-only generation
could ever achieve here, not what `generator.py` achieves.

Computed the way finding 08 computed it (its final corrected tally, from
its correction header): take every distinct endpoint URI Extron's shipped
module references, exclude `get-token` (the auth handshake, not a "driver
call" in the sense either write-up means), and classify each by whether a
dedicated page exists in the harvest today:

```
Extron calls 33 endpoint URIs total (32 api/... + get-token).
Excluding get-token: 32.
  documented with a dedicated page: 29
  no dedicated page:                 3   (StartISORecord, StopISORecord, ISORecordStatus)
29/32 = 90.6% ≈ 91%
```

This **reproduces finding 08's already-corrected final tally exactly**
("documented with dedicated page: 29, no dedicated page: 3" — the ISO-record
family, all of it). Before this pass, that 29/32 rested on finding 08's own
direct-probe evidence that the 9 missing pages existed, without the pages
themselves being saved to this repo; `endpoint_crossref.txt` and
`analyze_endpoints.py`'s hardcoded set still reflected the older,
incomplete harvest (hence the still-6 `DOC_GAP` entries `ROADMAP.md` R32
pointed at). This pass makes 29/32 reproducible **from the repository
alone** — the pages are now on disk, and `analyze_endpoints.py` computes
the number by scanning them, not by trusting a hand-maintained set.

**`STATUS.md`'s "~84% (27/32)" is stale on both counts**: the denominator's
correct answer was already 29/32 (91%) as of finding 08's 2026-09-07
correction, and it stays 29/32 now — this pass changes *how reproducible*
that number is, not its value. (`ROADMAP.md`'s own R4/R32 rows already flag
27/32 as stale; this section is the re-measurement R32 asked for. Updating
`STATUS.md` itself is out of this pass's scope — see below.)

## What this pass does NOT do

- **Does not add `SetWake`/`SetChangeRoomConfiguration`/an `AutoSwitch`
  toggle command etc. to the generator**, even though 4 endpoints
  (`Wake`, `ChangeRoomConfiguration`, `StartAutoSwitch`, `StopAutoSwitch`)
  are now documented and Extron calls them. R32's brief was "fix the
  generator's [two response-handling] defects... and re-measure," not
  extend its endpoint coverage; the new "official, shipped-only: 4" row
  above is exactly the measurement of that remaining gap, left for whoever
  picks it up next.
- **Does not touch `ENDPOINTS.md`**, which still asserts (in its
  "Undocumented sub-APIs" section) that 8 of the 9 sub-APIs are "confirmed
  absent... by repeated brightdata search queries" — a claim this pass's
  harvest disproves for 7 of those 8. `ENDPOINTS.md` sits directly under
  `reference/automate-vx-api/`, not under `API-Reference/`, so it's outside
  this pass's stated scope (new files under `API-Reference/` only). Flagged
  for the orchestrator in the hand-off notes.
- **Does not touch `reference/automate-vx-api/INDEX.md`**, whose harvest
  table and "40 pages found... 0 pages failed" summary line are now stale
  by 9 pages (49 total, not 40; this pass's `Wake` etc. did fail on the
  original 2026-09-07 sweep and were found by a second, more direct method).
  Also out of scope; also flagged below.

## Test results

`py -3.11 experiments/docs_only/test_generator.py` (as committed, against
whatever `tools/wire_table.py` is on disk when it's run) — **at the moment
this pass was written, 9 passed, 2 failed, 11 total.** Both failures are in
section 4 ("GetAllStatus/CameraStatus has exactly one update_template") and
are **not** a defect in this pass's work: `tools/wire_table.py` is mid-edit
under ROADMAP R36 right now (`git diff --stat HEAD -- tools/wire_table.py`:
192 lines changed, uncommitted), and the in-progress version on disk
currently returns `update_templates: []` for both commands where the
HEAD-committed version correctly returns 1. Verified directly:

```
# current (mid-edit) tools/wire_table.py:
GetAllStatus.update_templates -> []
# HEAD-committed tools/wire_table.py (snapshotted to this session's tmp dir):
GetAllStatus.update_templates -> ["self.__UpdateHelper('GetAllStatus', value, qualifier, url='api/GetAllStatus')"]
```

Against the HEAD snapshot, all 11 checks pass. The test is written to run
against whatever `tools/wire_table.py` is current (correct for its life as a
permanent regression test once R36 lands); this note exists so today's 9/11
isn't misread as this pass's own defect.

`py -3.11 experiments/docs_only/analyze_endpoints.py` and `py -3.11
experiments/docs_only/generator.py` both run clean (exit 0); `ast.parse()`
on the regenerated `automate_vx_docs_only.py` succeeds;
`py_compile.compile(..., doraise=True)` succeeds for `generator.py`,
`analyze_endpoints.py` and `test_generator.py`.

## Files touched

- `reference/automate-vx-api/API-Reference/{Wake,AutoSwitchStatus,StartAutoSwitch,OutputStatus,RecordStatus,RoomConfigStatus,GetLayouts,LayoutStatus,GetRoomConfigs}-API.md` — new, fetched 2026-09-23.
- `experiments/docs_only/analyze_endpoints.py` — rewritten to scan the harvest instead of hardcoding it.
- `experiments/docs_only/generator.py` — the two WriteStatus/GetAllStatus fixes.
- `experiments/docs_only/automate_vx_docs_only.py` — regenerated.
- `experiments/docs_only/endpoint_crossref.txt` — regenerated.
- `experiments/docs_only/test_generator.py` — new regression test.
- `experiments/docs_only/diff.json`, `wire_table.generated.json`,
  `wire_table.extron_shipped.json` — unchanged (verified byte-identical
  after the fix; not rewritten).
