# Finding 20 — Automate VX, three ways

**Status: measured offline, 2026-09-24. No live Automate VX was reached.** Full report:
`experiments/automate_vx_threeway/REPORT.md`; the 40 discrepancies with evidence and verdicts:
`discrepancies.json` (37 from the first pass, X36–X38 from the third); the calls that settle the
rest: `LIVE_TESTS.md`.

Three sources of truth for one device, compared call by call: Extron's driver (GC package
`1bynd_42_4279` v1.0.11 and ControlScript module v1.0.11.0), Crestron's SIMPL module
(`1Beyond Automate_VX` v1.2) together with native IP ID control, and the live Automate VX API
documentation on Crestron's SDK site.

## What it shows

1. **Extron's two drivers are one wire surface.** Both call the same 33 URIs, byte for byte
   (`surfaces.py extract`; pinned by `test_surfaces.py`): 30 documented calls plus
   `StartISORecord`, `StopISORecord` and `ISORecordStatus`, which have no documentation page.
   Methods, headers, body keys, enumerations and ranges match the documentation.
2. **The documentation is larger than our harvest said.** The site publishes its own table of
   contents (`Data/HelpSystem.xml` → a TOC chunk, built 2026-05-26): 48 API pages, with
   `GetActiveTalkers` live but outside it, so **49 documented calls**. The harvest has 43; six TOC
   pages are missing from it. Finding 08's lesson — use the index the site publishes — applies
   again: the index was there (R43).
3. **Extron covers 30 of the 49.** Missing: `PauseRecord`, layout feedback and every name list,
   `GetActiveTalkers`, `ShotStatus`, `HealthStatus`, storage, copy, import/export, macros, restart.
4. **Crestron's module calls 38 of the 49, read from its decompiled library.** The `.cmc` is a
   readable text module; its `.csp`, found in the installed device database, is a SIMPL+ wrapper
   that forwards every command to a compiled SIMPL# library (REPORT.md §8). The owner had that
   library decompiled for interoperability (§10). Its 3-Series and 4-Series builds post to the same
   42 URIs: 38 documented calls plus the three ISO names and `CopyStatus`. It **defaults to plain
   HTTP on 3579** (HTTPS uses 4443), which Crestron's 6.4.1.8 release notes say new installations
   no longer support. The 1–8 camera and 1–10 scenario limits are not the library's, and A–Y is
   only the wrapper's 25 joins.
5. **Native IP ID is VX2 hardware only** (Automate VX ≥ 6.2.2.27, device database ≥ 200.355.002.00;
   the unit registers with a control system by IP ID on 41794). The join map was not found online.
   It is in the installed device database: the `IV-SAM-VX2` symbol and eight children, 276 named
   joins (REPORT.md §9; the join *numbers* there were corrected in the third pass, because a
   spacer marker in the symbol had been counted as a join). It is the richest of the three
   surfaces: active talkers, health, storage,
   save preset and all name lists. It has no ISO recording, and it is reachable only by acting as
   a Crestron control system. First-generation hardware is told to use the module.
6. **The documentation contradicts itself on value types, and the two vendors took opposite
   sides.** Its prose says Integer for 14 body fields; every example quotes them as strings.
   Extron follows the examples: it sends 10 of them as strings, and `cam` in the pan/tilt/zoom
   calls as a number. Crestron's library follows the prose for `GoToScenario.id`, the
   room-configuration `id`, `ptDir` and `zDir`, sending numbers. It agrees with Extron that the
   camera `address` and preset `cam`/`pre` are strings. The two drivers also differ on the case of
   `StartPT`/`StopPT` (Crestron sends `StartPt`/`StopPt`, X36), on the `Authorization` header
   (Crestron's 3-Series HTTPS path prefixes `Basic `, X37), and on unused keys (Crestron always
   sends all three pan/tilt/zoom integers and an `id` of 0 with a camera switch, X38). If both
   drivers work, the device is lenient on all of these. That is inference, not measurement: live
   tests LT2–LT4 and LT18–LT20 decide it. Finding 08's "driver right, doc wrong" is better read as
   "prose and examples disagree".
7. **The drivers also expect different reply shapes.** For RoomConfigStatus, Crestron reads
   `roomConfig`, one object (the `GetAllStatus` example's shape), where Extron reads `roomConfigs[0]`
   (the page's list). Unless the device sends both, one of them never gets that feedback (X14, LT5).
   Crestron also reads two RecordStatus fields no page documents, `record_state` and
   `pause_enabled` (X09).
8. **Two faults would show on a device.** Extron's ControlScript help sheet documents
   `Set('Scenario', None, {'ID': ...})`, which raises `TypeError` in the shipped v1.0.11.0 code
   (the GC sheet is right); and the Crestron module's HTTP default (above).

## What it does not show

- Which of the two drivers' request forms the device accepts. Both are now known from code, not
  from a capture of either talking to a unit.
- Whether the undocumented ISO calls still work. Both vendors' current shipping code calls them,
  and the feature is in the 6.4.0 release notes.
- How the native VX2 joins travel on the wire (CIP), or what values the analog `Recording` and
  `Streaming` joins take.
- Device behaviour for any of the 16 discrepancies graded "unknown": `LIVE_TESTS.md` names the call
  for each. LT17 needs only the IPCP Pro and a PC (ROADMAP H10).

## Method

Three independent extractions (Extron drivers; Crestron module plus native research; live
documentation), one comparison, and an adversarial verifier that re-checked every discrepancy
against the files and live pages: 37 of 37 confirmed. By hand afterwards, four discrepancies were
re-read at their cited lines and the site's TOC re-counted. A second pass the same day read the
Crestron device database installed on the owner's workstation (REPORT.md §8–9): the module's SIMPL+
source and its library's documentation (`crestron_module.py`), and the native symbol's joins
(`experiments/dm_md/crestron_symbols.py`). Nothing encrypted was opened. A third pass the same day
read the module's SIMPL# library, which the owner had decompiled for interoperability
(`experiments/crestron_decompile/`, ILSpy 11.1). The request bodies, headers and session handling
come from the decompiled C#, and the JSON key names from the IL (REPORT.md §10). Both builds are
pinned by SHA-256.

The second pass said that decompiling the library is what Crestron's development-tools licence
bars. That was wrong. The clause (finding 04) is in the licence for the development tools, and no
term covering this library was found. REPORT.md §10.6 has the correction; ROADMAP D2 keeps the
licence question.
