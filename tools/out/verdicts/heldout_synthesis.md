## 1. The honest generalisation verdict

**Corrected held-out score: 67 of 81 shared commands wire-match a shipped module — 82.7%, against 96.4% in-sample (81/84). The project's "~95%" is an in-sample number and does not survive out of sample.** Rules were unchanged for every number below; `tools/test_pkp2cs.py` reports `47 passed, 0 failed, 47 total`.

| pair | shared | wire-match | differ | dangling |
|---|---|---|---|---|
| DSC 12G-HD (in-sample) | 29 | 28 | 1 | 0 |
| DTP3 CP 42 (in-sample) | 28 | 27 | 1 | 4 |
| Samsung serial (in-sample) | 9 | 9 | 0 | 0 |
| Automate VX (in-sample) | 18 | 17 | 1 | 0 |
| Clock Audio 1777 (held-out, **valid pairing**) | 7 | 4 | 3 | 0 |
| Biamp Tesira (held-out) | 74 | 63 | 11 | 51 |
| *Samsung ethernet (no shipped oracle)* | *9* | *1* | *8* | *1* |
| *Clock Audio 5940 / MK3 (no shipped oracle)* | *6* | *1* | *5* | *0* |

**The Clock Audio caveat resolves as a mis-pairing, and it is 100% of that device's apparent failure.** The shipped `clau_dsp_CDT100_v1_0_3_0.py` belongs to package **1777**, not 5940: it implements `LEDLightControl` on the 4-channel `ACK GCH32 0 CH1R=…CH4…` family (`samples/ClockAudio/controlscript/clau_dsp_CDT100_v1_0_3_0.py:38`), which is byte-identical to 1777's own `AddMatchString` and is entirely absent from 5940; 5940 instead hardcodes `LOAD 0\r`/`SAVE 0\r`, matching `MAN_CDT100_MK3.pdf` lines 958/960 ("LOAD x (x = 0)"), and uses a 12-channel `BSTATUS B(\d|1[012])` scheme matching the manual's lines 1181-1211. Scoring 5940 against a MK I/II module was an unfair test; it must be dropped, exactly as Samsung's ethernet module already is (no shipped ethernet oracle exists either — the project has been quietly carrying that same asymmetry in-sample).

**On the valid pairing the translator has zero faults.** All three "differences" are byte-faithful carries of the .pkp source: `/tmp/ca1777_emb.py:150` `ACK (SARMC|GARMC) (0|1)\r`, `:155` `PP1=(0|1|ON|OFF)…`, `:156` `BSTATUS B(1|2|3|4|6|8|10|12)`. And Clock Audio's *own* Crestron library sides with the translator against Extron's shipped module on all three (see §5). The corrected held-out Clock Audio result is **7 shared, 7 correct, 0 translator faults, 0 dangling**.

**Biamp's 11 wire differences are likewise not mistranslations.** Each traces to a post-generation human edit in Extron's shipped module: `DEVICE recallPresetByName "{0}"\n` in the source (`/tmp/biamp_emb.py:2487`) vs unquoted in shipped (`biam_dsp_TesiraSeries_v1_18_3_0.py:1356`); `activeFaultList\r\n` (`/tmp/biamp_emb.py:1478`) vs `\n` (`:817`); six `value_map` diffs caused by Extron collapsing per-command matchers into `__MatchAllSubscribe` (`:135`); the `Number` qualifier on TIHook/VoIPHook (`:1886`, `:2071`) that exists nowhere in the .pkp.

**So the two metrics diverge sharply, and both are true:**
- **Fidelity to source: 81/81 held-out (100%).** No held-out difference is a translation error.
- **Agreement with a shipped module: 67/81 (83%).** The 17% gap is Extron's hand-editing, which no converter can predict.
- **Runtime resolvability: collapsed. 51 dangling on Biamp vs 5 across four in-sample modules** — and that *is* real overfitting.

## 2. Which rules are general, which were fitted

**Genuinely general — re-validated out of sample:**
- NRBF extraction and job discovery (`tools/pkp2cs.py:160`): handled a 5.6 MB gzip/16 MB graph with 23 models and a 4,618-line script unchanged.
- Verbatim carry of wire strings and response regexes. This is the core value and it held at 100% on both new families.
- Deletion of per-command `Write<X>`/`Read<X>` wrappers (`pkp2cs.py:694`) — vindicated by the shipped modules, which contain no per-command wrappers at all, only the generic `WriteStatus` (`biam_dsp_TesiraSeries_v1_18_3_0.py:2421`, `extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py:1229`).
- Dropping `UserDefinedCommand`/`UserDefinedString` (`pkp2cs.py:218`) and GC config-parsing boilerplate (`:668`): 10 drops on Biamp, no fallout.
- Synthesising `ConnectionStatus` (`pkp2cs.py:1356`): present in both new shipped modules.
- The Emulated-pre-write *predicate* itself (`_strip_emulated_prewrites`, `pkp2cs.py:346`).

**Fitted to the original four:**
1. **The guard-shape gate on that predicate** (`visit_If`, `pkp2cs.py:271-320`). It fires only from the two `__SafeToSet` branches. Tesira's generator never emits `__SafeToSet` (0 hits in 4,618 lines) — it gates on plain parameter validation — so 48 dead calls survive while their targets are deleted. **This was already leaking in-sample:** DTP3's `SetMatrixIONameString`/`SetMatrixIONumberSelect` have exactly Tesira's shape (`if 0 <= len(value) <= 30: self.WriteMatrixIONameString(value, qualifier, 'Emulated')`, generated lines 313-320) and account for 2 of the baseline's 5 dangling. The bug was always there; Biamp only made it big.
2. **The `__SafeToSet`-BoolOp else-handling rule** (`pkp2cs.py:290-310`), explicitly derived by diffing Automate VX's five `Set*` methods. No out-of-sample evidence either way — untested, not validated.
3. **`FIXED_SET_UPDATE_HELPER`** (`pkp2cs.py:1214`, substituted at `:842-865`). Two keys only, and the `sis_ethernet` template is Extron SIS boilerplate lifted from the DSC module. **This is the worst finding in this review:** the generated Biamp and Clock Audio modules both emit `self.Send('w0echo\r\n')` and `self.Send('w3cv\r\n')` (generated `biam_25_150.py:2222+`, generated `clau_25_1777.py` `__SetHelper`). Those are Extron SIS commands. Neither string appears anywhere in either source .pkp (grep count 0 on all three embedded scripts); they appear in `extr_scaler_DSC_12G_HD_A_v1_0_0_0.py:1000,1004`. The shipped modules send the device's real equivalent — `SESSION set verbose true\n` for Tesira (`:2270`) and `SASIP {0}:{1}\r` for Clock Audio (`clau_dsp_CDT100_v1_0_3_0.py:249`). **The translator is currently inventing wire content for third-party devices**, which is the failure mode this project says it exists to prevent, and `wire_table` cannot see it because it extracts per-command tables, not helper bodies.
4. **`find_protocol_asset`'s "exactly one ProtocolAsset child" invariant** (`pkp2cs.py:95`, sourced to findings/06). False out of sample: 20 of Biamp's 23 models resolve to `None`. The package contains a `SerialProtocolAsset` (1 occurrence in the decompressed graph) that is never seen; the dialect silently defaults through the Ethernet branch with **no residual raised** (`dialect` residual list is empty), and the shipped module's `SerialClass` and `SerialOverEthernetClass` (`:2489`, `:2508`) have no generated counterpart. Clock Audio 1777 declares a `CDT 100-UDP` model that likewise gets a TCP class.
5. **Transport class naming**: always `SSHClass`; Clock Audio's shipped module names it `EthernetClass` (`:419`).

## 3. Mechanically fixable vs. real limitation

**Mechanically fixable (no guessing, justified by shipped-module behaviour):**
- **The 50 Emulated pre-writes** (48 Biamp + 2 DTP3, i.e. 50 of the 56 dangling across all six pairs). The fix is smaller than a new `if` branch: run the existing `_strip_emulated_prewrites` predicate at statement level anywhere inside a `_cmd_Set<X>` body, independent of the enclosing conditional. Justification is the shipped modules' own content, not a desire to pass — they contain no `Write<X>` wrappers and no calls to them. Predicted post-fix: in-sample dangling 5 → 3, Biamp 51 → 3, wire tables untouched (no wire strings involved). Anything less than that measured outcome means the fix is wrong.
- **The SIS boilerplate injection.** Substituting DSC's `w0echo`/`w3cv` into a non-SIS device is strictly worse than emitting nothing. Correct behaviour: substitute the fixed template only when the source script itself evidences SIS (`w0echo`/`w3cv`/`Verbose` SIS idioms), otherwise carry GC's own `__SetHelper`/`__UpdateHelper` body through the generic rewriter and raise a residual. The `sis_ethernet` dialect name is doing double duty as "Extron SIS" and "anything over TCP"; those must be separated.
- **Protocol-asset resolution.** Resolve per-model protocol assets robustly, and when a model resolves to none, raise a residual instead of silently defaulting. A package declaring Serial + Ethernet assets should produce the transports it declares or say loudly that it did not.
- **Scorecard hygiene**: excluding unpaired packages (5940, Samsung ethernet) is a reporting fix, not a rule change.

**Real limitations — a converter cannot infer these, and must not try:**
- The `Number` qualifier on TIHook/VoIPHook. It is a new API surface invented by a human to replace a staged companion command; it exists in no bit of the .pkp. The three remaining `Read*` dangling calls (Biamp) plus DTP3's 2 and Samsung's 1 are the correct, honest surfacing of this: `DialString`, `NewSpeedDialEntryNameString`, `NewSpeedDialEntryNumberString` are `Live=False/Emulated=True` scratch commands with no ControlScript store. Leave them dangling and reported.
- The many-matchers-to-one-`__MatchAllSubscribe` refactor (`:135`) — an architectural choice, with the label-parsing convention invented by the author.
- The preset-name unquoting and the `\r\n`→`\n` change. These are protocol corrections that required a device or a manual. Note the shipped module is not even self-consistent here: it uses `\r\n` for 49 command strings and bare `\n` for two, while Biamp's own library uses `\n` throughout. A converter that "fixed" this would be guessing.
- Firmware/version skew between a .pkp capture and a module vintage (Clock Audio's three diffs). Unknowable from the package.

The boundary is clean: **fixable = the translator dropped, mangled or invented something with no basis in the source; limitation = the shipped module contains information the source does not.** All 14 held-out wire differences fall on the limitation side. All 50 emulated pre-writes and the SIS injection fall on the fixable side.

## 4. The SIMPL answer — correcting finding 07

Finding 07 (`findings/07-1beyond-and-simpl.md`) says of the Automate VX macro: *"it is an I/O contract plus a pointer to logic that is absent"*, and *"the protocol logic lives in a companion `.usp`/`.csp` shipped alongside."*

**The first half is confirmed and now generalises; the second half is wrong.** With real `.usp` source in hand for two vendors, the companion module is *not* where the protocol lives. Every `.usp` in both suites is a second dispatcher: `Clock Audio Device v3.4.1.usp:80` declares `#USER_SIMPLSHARP_LIBRARY "Clock Audio"` and calls `device.SetLedState(...)`; `Biamp Tesira Comm v3.3.usp:52` declares `#USER_SIMPLSHARP_LIBRARY "BiampTesiraLib3"` and calls `tesira.Connect()`. Neither contains a single literal wire token. The chain is `.umc → .usp → compiled SimplSharp .NET assembly`. So finding 07's structural claim should read: *a Crestron module is an I/O contract plus a pointer to logic in a compiled assembly, and the `.usp` is part of the contract, not the logic.*

**Its other conclusion — "Extron vs Crestron: untestable, not refuted" — is now testable, and it was tested. Wire strings are fully recoverable** from the assembly's ECMA-335 `#US` heap. `BiampTesiraLib3.clz` is a ZIP containing `BiampTesiraLib3.dll`; `Clock Audio.dll` sits uncompressed under `SPlsWork/`.

**Does the Samsung two-vendor convergence result reproduce?**
- **Clock Audio: yes, strongly.** 19 of the 20 command tokens Extron's 1777 driver uses appear in Clock Audio's own library (the one miss is `ON`, a value, not a verb): `GARMC`, `SARMC`, `PP`, `QUERY`, `GCH32`, `SCH32`, `SRGB`, `STS`, `STSB`, `LOAD`, `SAVE`, `BSTATUS`, `SASIP`, `VERSION`, `NACK`. Response formats are structurally identical modulo named-vs-anonymous capture groups (`Clock Audio.dll` @0x14b1d `ACK QUERY PP1=(?<state1>\w+) … ID=\w+` vs the .pkp's `ACK QUERY PP1=(0|1|ON|OFF) …`).
- **Biamp: partially — convergence at the grammar level, not byte level.** Both sides speak the same TTP: `DEVICE get version\n` (@0x267ac), `SESSION set verbose true` (@0x25cfe), `SESSION get alias "{0}"\n` (@0x2680a), `(set|get|subscribe)` (@0x265fc), instance-tag-first templates. Two systematic divergences: Biamp's library always quotes the instance tag (`"{0}" {1} {2}\n` @0x268c6 and six arity variants — no unquoted counterexample) while Extron never does (`biam_dsp_TesiraSeries_v1_18_3_0.py:513`); and Biamp terminates with bare `\n` (verified in the raw bytes) while Extron mostly uses `\r\n`. Extron's driver PDF (`biam_25_150_v1_20_0.pdf` lines 521-524) lists only `/` and `&` as illegal instance-tag characters and states no quoting rule, so both forms are defensible.

So Samsung's verbatim-string convergence is **not** the general case. Clock Audio reproduces it at the token/format level; Biamp reproduces it at the grammar level only. Cross-vendor corroboration is strong enough to *adjudicate* a disputed string, and not strong enough to *generate* one.

## 5. What Clock Audio's own module adds that vendor-vs-vendor could not

Biamp's library is still a second integrator's reading of Biamp's protocol. Clock Audio's is the **manufacturer's own implementation of its own device** — as close to ground truth as a static artifact gets. It does three things no Extron-vs-Crestron comparison could:

**It reverses the direction of two of the three "differences."** On all three commands where the translator's output "differs" from Extron's shipped module, Clock Audio's own module agrees with the *translator*: `ACK [SG]ARMC (?<state>\d)` (@0x14a92) accepts the Set-ack with a digit, exactly as the .pkp does and the shipped module does not; `PP1=(?<state1>\w+)` accepts textual ON/OFF, as the .pkp does and the shipped module does not; `BSTATUS B(?<button>\d*)=` accepts unbounded channels, where the shipped module accepts only `B(1|2|3|4)`. **The shipped module is the stale artifact, and the wire-match metric was penalising the translator for being more correct than its oracle.** It also weakens the "1777 wrongly assumes SARMC carries a digit" reading — two independent implementations agree it does.

**It caught a real defect in Extron's source driver.** The 5940/MK3 package emits `'SRBG {} {} {} {}\r'` (`/tmp/ca5940_emb.py:352`). The verb is `SRGB` — per Clock Audio's own module (@0x1711e), per Extron's own 1777 package (`/tmp/ca1777_emb.py:578`), and per the manufacturer's manual (`MAN_CDT100_MK3.pdf:1005,1341,1343`). Extron's MK3 driver has a transposed-letter typo that will never set an RGB LED. The translator carries it verbatim, which is correct behaviour — but only a manufacturer oracle could tell us the source was wrong rather than the translator.

**It confirms the family split independently.** The single `Clock Audio.dll` implements both the 4-channel `GCH32` family (@0x15afb) and the 15-channel `GTS`/`GRGB` family (@0x14c10, @0x16828), and the suite ships separate mkI/mkII/**mkIII** `.umc` wrappers over one `.usp`. The manufacturer treats MK3 as a distinct protocol generation — the same split Extron expresses as two packages, and the reason the 5940 comparison was invalid.

The general lesson: a manufacturer artifact is an **adjudicator**, not just a third opinion. It should be the tiebreaker whenever the generated output and a shipped module disagree.

## 6. Ranked next steps — fix these before pulling more samples

More data cannot fix an overfitted rule set; it can only re-measure it. Everything above the line is a rule fix validated across all six pairs, reporting wire-match *and* dangling every time.

1. **Stop injecting SIS wire strings into non-SIS devices.** `w0echo`/`w3cv` in a Biamp Tesira and a Clock Audio DSP driver is wire-content invention — the failure mode the project is built to avoid — and it is shipping today in two of six outputs. Gate `FIXED_SET_UPDATE_HELPER_SIS_ETHERNET` on SIS evidence in the source script; otherwise carry GC's own helper through the rewriter and raise a residual. Test-first, non-negotiable, highest priority.
2. **Generalise the Emulated pre-write strip** to statement level regardless of guard shape. Expected: dangling 5 → 3 in-sample, 51 → 3 on Biamp, zero wire-table movement. Justified by the shipped modules, and it fixes a latent in-sample bug, not just Biamp's.
3. **Make `wire_table` cover the helper bodies and transport classes**, or add a second metric that does. Both #1 and #4 were invisible to the current scorecard while it reported 85% for Biamp. A metric that cannot see invented wire strings is the most dangerous artifact in the repo.
4. **Fix protocol-asset resolution and fail loudly.** 20 of 23 Biamp models resolve to no protocol asset, a declared `SerialProtocolAsset` is never seen, two of three shipped transport classes are never emitted, and *no residual is raised*. Silence is the bug; emitting the missing transports is the follow-on.
5. **Fix the scorecard's pairing policy.** Report Clock Audio 5940 and Samsung ethernet as "no shipped oracle — unscored", not as percentages. Report in-sample and held-out separately, and report fidelity-to-source alongside agreement-with-shipped, because those are 100% and 83% and conflating them is what produced the "~95%" claim.
6. **Add manufacturer artifacts as a formal adjudication tier.** When generated and shipped disagree, check the vendor's own module before labelling anything. It flipped all three Clock Audio verdicts and found the `SRBG` typo.
7. **Only then pull more samples** — and pull them as *matched pairs* (a .pkp whose model set is confirmed against the shipped module's command set before scoring), ideally with a manufacturer module. A genuine MK3 ControlScript module would make 5940 a real seventh data point.

Not worth doing: chasing the 14 held-out wire differences. Every one is a human edit that postdates generation. Closing them requires guessing, and guessing is worse than the 83%.