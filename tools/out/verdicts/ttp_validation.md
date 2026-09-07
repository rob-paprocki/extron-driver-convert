## 1. Independently re-run metrics, all six pairs

Ran `tools/test_pkp2cs.py` directly: **55 passed, 0 failed** (52 baseline + 3 new). Then independently recomputed both acceptance metrics from scratch (not trusting the report's numbers) using `pkp2cs.translate_job`/`translate_pkp`, `wire_table.extract_table`/`diff_tables`, `find_dangling_self_calls`, `find_invented_wire_strings`, and `compile()`:

| pair | wire-match | dangling | invented | compiles |
|---|---|---|---|---|
| DSC 12G-HD | 28/29 | 0 | 0 | yes |
| DTP3 CP 42 | 27/28 | **2** | 0 | yes |
| Samsung serial | 9/9 | 0 | 0 | yes |
| Automate VX | 17/18 | 0 | 0 | yes |
| Clock Audio 1777 | 4/7 | 0 | 0 | yes |
| Biamp Tesira | 63/74 | **3** | 0 | yes |

This matches the fix report exactly. Confirmed independently: `git status --short` shows only `tools/pkp2cs.py` and `tools/test_pkp2cs.py` modified.

## 2/3. Biamp generated module vs. the TTP spec

Generated the Biamp module fresh (`pkp2cs.translate_job` on `samples/Tesira/pkp/biam_25_150_v1_20_0.pkp`), dumped its wire table with `tools/wire_table.py dump` (77 commands, saved `/tmp/biamp_gen_wt.json`), and did the same for the shipped module (74 commands, `/tmp/biamp_shipped_wt.json`). Checked every SET/UPDATE canonical template against `reference/biamp-ttp/SYNTAX.md`'s attribute/service grammar, quoting rule, and terminator rule. All ~140 templates in the generated module are well-formed `Instance_Tag [set|get] Attribute [Index...] [Value] LF` or Dialer-verb (`dial`/`redial`/`onHook`/`offHook`/…) forms; the subscribe/unsubscribe helper (`/tmp/biamp_generated.py:2158-2172`) matches spec section 6 exactly (`"{tag}" subscribe {attr} "{label}" {interval}\n` / `"{tag}" unsubscribe {attr} "{label}"\n`). `PresetRecall`/`PresetSave`'s `+1000` offset (`/tmp/biamp_generated.py` ~ `DEVICE recallPreset {}1000\n`) is directly confirmed plausible by the spec's own worked example, "Preset | `1001` | An Integer that is the required state" (`reference/biamp-ttp/SYNTAX.md`, Value table, sourced from `pages/TTP_Syntax.md`).

## 4. Diffing generated vs. shipped, spec as referee — the 11 known differences

Computed the diff directly (`wire_table.diff_tables`). It is exactly 11 command names. Categorizing with the spec as referee:

**6 are tool artifacts, not real protocol differences** — `Bluetooth`, `BluetoothDiscovery`, `BluetoothUSBConnectionStatus`, `BluetoothUSBStreamingStatus`, `TILineInUse`, `VoIPLineInUse`. I dumped the full `CommandRecord` for `Bluetooth` from both JSONs: the actual `set_templates[0].canonical` (`'{} set enable {}\n'`) and its `value_maps` (`{"On":"true","Off":"false"}`) are byte-identical between generated and shipped. The only difference is the top-level `value_map` field, which is `{}` in shipped — because shipped implements the On/Off↔true/false mapping inside one giant shared `__MatchAllSubscribe` dispatcher (`samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py:135-270`) that `wire_table.py`'s static per-command-method extraction can't attribute back to each command, while the generated module keeps a separate `__Match<X>` per command. **No spec judgement needed — the wire is identical.**

**5 are real, and here the spec is genuinely useful as a referee:**

- **`PresetRecallName` / `PresetSaveName` — shipped is the buggy one.** The `.pkp`'s own GC script quotes the name: `'DEVICE recallPresetByName "{0}"\n'.format(name)` (confirmed at `.pkp`'s `_cmd_SetPresetRecallName`), and the generated module preserves that. Extron's shipped module drops the quotes: `'DEVICE recallPresetByName {0}\n'.format(name)` (`samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py:1356`). Per `reference/biamp-ttp/SYNTAX.md` §3 ("Values... if it does [have spaces] it can be defined in 'double quotes'", sourced from `pages/TTP_Subscriptions.md`), an unquoted Value containing a space breaks parsing — this is directly demonstrated by the spec's own Instance-Tag example (`"my level 2" get level 1` succeeds, `my level 2 get level 1` fails with `-ERR address not found`). A preset named e.g. "Morning Setup" would fail to recall/save on the shipped module but works on the `.pkp`/generated version. **The translator (and the original GC script) is spec-correct here; Extron's shipped module is not.**

- **`TIHook` / `VoIPHook` — Parameters differ, wire is identical, not spec-adjudicable.** The `.pkp`'s `Dial` branch fetches the number via `self.ReadDialString(...)` (a GC-scratch call that becomes a dangling residual — this is the previously-known, correctly-flagged residual). Extron's shipped version instead requires an explicit `Number` qualifier. I verified both branches produce the exact same wire string, `'{0} dial{1}{2} {3}\n'.format(tag, line, call, number)` — a valid Dialer-verb form per spec §2 (`dial` is in the documented Dialer verb list). This is a Python-API/qualifier-contract difference, not a protocol difference; the spec has nothing to referee here.

- **`DeviceFaultList` — ambiguous on the terminator, real design difference on richness.** Generated sends `'DEVICE get activeFaultList\r\n'` (from the `.pkp`, verbatim); shipped sends `'DEVICE get activeFaultList\n'`. `activeFaultList` is a real, `get`-only Device attribute (`reference/biamp-ttp/pages/Device.md:163`, "Active Faults | activeFaultList | get"), so both commands are grammatically valid attribute-gets. Spec §4 says only "a line feed needs to be sent after each command" — it doesn't explicitly forbid a leading CR, so this one isn't clearly refereeable either way (it's the only command in the entire 140+ template set on either side that uses `\r\n`, suggesting a `.pkp` copy-paste wart the translator correctly preserved rather than "fixed"). Separately, shipped's `Parameters: []` collapses every fault into one generic "Errors in Fault List" status, while the generated module (again following the `.pkp`) parses out individual `Serial Number`s per fault — a richness difference the grammar spec doesn't opine on.

## The wire-diff-invisible bug the spec caught that diffing missed

While reading the quoting logic in the two `NewSpeedDialEntryName/NumberCommand` methods — **not** flagged as one of the 11 differences, because `wire_table`'s diff reported these as fully matching — I found a real bug that is invisible to wire-diffing:

- `.pkp` / generated (`/tmp/biamp_generated.py:1060-1068`): `tag = qualifier['Instance Tag']` (no pre-quoting), then `'"{0}" set speedDialLabel {1} {2} "{3}"\n'.format(tag, ...)`.
- Shipped (`samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py:1181-1195`): adds `if ' ' in tag: tag = '"' + tag + '"'` **before** the same hardcoded-quote format string.

Simulated both with an instance tag containing a space ("My DSP"):
```
shipped  : '""My DSP"" set speedDialLabel 1 3 "Office"\n'
generated: '"My DSP" set speedDialLabel 1 3 "Office"\n'
```
Shipped double-quotes the tag. Per the spec's own worked example of Instance-Tag quoting (`reference/biamp-ttp/SYNTAX.md` §3, `"my level 2" get level 1` — single-quoted, succeeds), `""My DSP""` is not that documented form and, by the stated space-delimited tokenization rule, would parse as a broken/empty leading token — a real regression Extron introduced, present in **both** `NewSpeedDialEntryNameCommand` and `NewSpeedDialEntryNumberCommand` (`samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py:1187-1188` and `1203-1204`). `wire_table.diff_tables` reports these two commands as identical because it only compares the static `.format()` literal, not the runtime value fed into it — so this bug is present in neither the "11 known differences" nor visible in any wire-match/dangling/invented number.

## 5. Well-formed-but-notable observations

- **Semantically confirmed, not implausible**: the `+1000` preset-ID offset in `SetPresetRecall`/`SetPresetSave` looked like an arbitrary magic constant but is directly validated by the spec's own example value (`1001`).
- **Spec constructs neither module ever uses**: the generic `toggle`/`increment`/`decrement` attribute verbs (spec §2, confirmed present in `data/calculator_blocks.json` and the Device/Session attribute-command tables) are never emitted by either module — every level/gain control always does a full `set`, never an increment/decrement, even though Biamp's attribute tables document that support. Also unused by both: quoted numeric Index tokens (`"1""1"` form) and the non-verbose response format (both scripts force `SESSION set verbose true`, so the bare-value non-verbose response shape in spec §5 is never exercised).

## Does spec validation catch anything wire-diffing missed? — Yes.

Two distinct wins, one clear:

1. **It re-adjudicates disagreement.** For the 5 real (non-tool-artifact) differences between generated and shipped, wire-diffing can only say "these differ" — it has no way to say *which side is right*. The spec supplies that: it proves the `.pkp`/generated `PresetRecallName`/`PresetSaveName` quoting is correct and Extron's shipped module is the one with the bug, directly contradicting this project's working assumption that the shipped module is ground truth.
2. **It finds a bug wire-diffing structurally cannot see.** The `NewSpeedDialEntryNameCommand`/`NumberCommand` double-quoting bug in the shipped module produces a *different runtime string* than the generated module for tags containing spaces, but the static `.format()` template literal is identical on both sides, so `wire_table`'s canonical-template comparison reports a match. Only reading the actual quoting logic against the spec's literal quoting example surfaced this. This is exactly the kind of dynamic-value-dependent bug wire-matching (which compares templates, not simulated output for varied inputs) is structurally blind to.

This supports adding spec-based checking as a genuine third metric, distinct from and complementary to wire-matching and runtime-resolvability — not because the spec replaces the shipped module as ground truth, but because it's the only one of the three that can adjudicate disagreements and catch input-dependent quoting/formatting bugs that template-level diffing averages away.

Files/paths referenced: `/Users/robp/GitHub/rob-paprocki/extron-driver-convert/tools/pkp2cs.py`, `tools/wire_table.py`, `tools/test_pkp2cs.py`, `samples/Tesira/pkp/biam_25_150_v1_20_0.pkp`, `samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py`, `reference/biamp-ttp/SYNTAX.md`, `reference/biamp-ttp/pages/Device.md`. Generated module and wire-table dumps used for this review: `/tmp/biamp_generated.py`, `/tmp/biamp_gen_wt.json`, `/tmp/biamp_shipped_wt.json` (scratch, not part of the repo).