# ROADMAP R8 — is `build_index.match_models`'s join rule right?

**Verdict: keep today's committed rule.** Both alternatives tried here were
built to fix a real risk — "first same-vendor substring match, in directory
order" has no reason to be the *right* same-vendor module when several
qualify — and both do catch real instances of it. But on a pair-by-pair
inspection, neither is a net improvement over the committed rule: "longest
match" is right in 4 of the 10 packages it changes and wrong in 6; "exact
token match" is right in essentially 1 of its 7 reassignments and throws away
121 correct pairs outright. What *is* worth carrying forward is five specific,
confirmed mis-pairs in the current 314-package set (§4) and one structural
observation (§5) — not a rule change.

This is a scratch, read-only experiment: `experiments/oracle_pairs/scratch/
join_rule_experiment.py` imports `build_index.py` and `pkp_dump.py` without
editing either. Nothing under `experiments/oracle_pairs/out/` changed, and
`match_models` in the committed script is untouched.

## 1. Method

Ran the same corpus finding 14 used — `corpus/extron-driver3` (1,854 `.pkp`
packages) against `corpus/extron-gs-modules/09062026` (2,235 ControlScript
modules) — parsing every package once and computing matches for a model name
under three rules in the same pass:

1. **current** — `build_index.match_models`, called unmodified. Same-vendor,
   substring containment on the fully-normalised (alnum-only) strings, first
   module in directory-sorted order.
2. **longest** — same substring/vendor gate, but among the same-vendor
   modules that contain the model name, picks the *tightest fit*: the
   module whose normalised filename is closest in length to the normalised
   model name (least leftover characters), ties broken by filename. Reads
   "longest match" as "the model name should occupy the largest share of the
   matched filename," which should stop a short model name from preferring
   whichever unrelated module happens to sort first.
3. **exact-token** — same vendor gate, but instead of raw substring
   containment, splits the model name on whitespace and the module filename
   on `_`, normalises each piece, and requires the model's words to appear
   as a contiguous, *exact* run of the module's tokens. This is the rule
   that would have killed the two false positives documented in
   `build_index.py`'s own docstring (`absn` "C110" inside "DMBC110"; `acer`
   "K750" inside a Digital Projection module) — neither is an exact token,
   only a raw substring.

Self-test: rule 1, called through this script, reproduces
`out/pairs_strict.json` exactly — **314 packages, 352 pairs, 0 packages
different** — confirming the harness matches build_index.py's own behaviour
before trusting its diffs of the other two rules.

Run: `py -3.11 -u experiments/oracle_pairs/scratch/join_rule_experiment.py`
(≈12 minutes: parsing all 1,854 packages dominates; matching under all three
rules is comparatively instant). Corpus provenance: `corpus/extron-driver3`
and `corpus/extron-gs-modules/09062026`, the same snapshot finding 14 used.

## 2. Where Clock Audio 5940 itself lands

Checked first, since it is the motivating example. `clau_25_5940_v1_1_1.pkp`
declares one model, `CDT100 MK3`. The corpus ships exactly one Clock Audio
GS module, `clau_dsp_CDT100_v1_0_3_0.py`. Normalised, `cdt100mk3` is **not**
a substring of `claudspcdt100v1030` at all (nothing after `cdt100` in the
filename spells `mk3`) — so under all three rules, 5940 matches **nothing**,
exactly as the committed pair set already shows
(`"clau_25_5940_v1_1_1.pkp": {"models": ["CDT100 MK3"], "matches": []}` in
`out/pair_index.json`). The historical mis-pairing finding 10 describes
(5940 scored against the 1777 module) did not happen through this join at
all — it happened in finding 10's own, separate, four/six-pair held-out
harness. **The specific instance is not live in the committed 314-package
set.** The general risk it illustrates is — see §4.

## 3. Counts

| rule | packages paired | pairs | packages differing from committed |
|---|---|---|---|
| committed (`out/pairs_strict.json`) | 314 | 352 | — |
| current (self-test) | 314 | 352 | 0 |
| longest | 314 | 352 | 10 |
| exact-token | 196 | 220 | 128 (121 lost outright, 7 reassigned) |

## 4. Every changed pair, inspected

For each, the model's declared internal `.pkp` version (read with
`pkp_dump.py` off the package's own `System.Version` object, e.g.
`extr_25_5_v1_5_12.pkp` really does carry `{Major:1, Minor:5, Build:12}` —
checked directly, not assumed from the filename) is compared against the
`vMajor_Minor_Build` suffix GS modules carry in their own filenames. A close
or exact version match is strong, independently-checkable evidence for which
module is the real counterpart, on top of which models a module's filename
declares.

### 4a. "longest" — all 10 changed packages

| # | package | model(s) | committed pick | candidate pick | verdict |
|---|---|---|---|---|---|
| 1 | `absn_10_6675_v1_0_4` | X108, X136, X163 | `..._X108_X136_X163_v1_0_4_0.py` — **exact version match** (1.0.4), lists all 3 declared models | X136/X163 moved to `..._X136_X163_V2_v1_0_0_0.py` (v1.0.0, only 2 models) | **committed correct.** The tighter-fitting module is a different (V2, 2-model) SKU revision at a different version; the package's own version and full 3-model declaration both point at the module current already picked. |
| 2 | `away_18_5688_v1_3_0` | AQL-C+ | `..._AQL_C_Series_v1_3_0_0.py` — **exact version match** (1.3.0) | `..._AQL_C_v1_0_0_0.py` (v1.0.0) | **committed correct.** Version mismatch on the candidate. |
| 3 | `barc_1_2536_v1_3_0` | F80-Q9, F90-4K13, F90-W13 | F80-Q9 & F90-4K13 → `..._F80Q9_F90_4K13_W13_v1_1_0_0.py`, which names **all 3** declared models; F90-W13 → the other module (only place `f90w13` is contiguous) | F90-4K13 moved to the 2-model module | **committed correct.** The package declares 3 sibling models; only one module's filename covers all 3, and it is v1.1.0 vs. the alternative's v1.0.3 — no version evidence favours splitting the family. |
| 4 | `extr_17_15_v1_7_1` | IN1606, IN1608 | `..._IN1606_IN1608_Series_v1_7_0_0.py` — close version (1.7.0 vs. pkg 1.7.1), names both declared models exactly | IN1608 moved to `..._IN1608xi_Series_v1_2_4_0.py` | **committed correct.** "IN1608xi" is a different SKU (an "xi" variant) the package never declares; "longest" prefers it only because it's a shorter filename. |
| 5 | `extr_18_39_v1_1_1` | Annotator (bare) | `..._Annotator300_v1_2_1_0.py` | `..._annotator_v1_0_0_1.py` (bare name) | **candidate correct.** Confirmed by a collision: a *different* package in the same corpus explicitly declares model `"Annotator 300"` and is *also* paired to `Annotator300_v1_2_1_0.py` (`out/pair_index.json`). Extron ships a plain "Annotator" and an "Annotator 300" as separate products with separate modules; the bare-model package belongs on the bare module. Today's rule collides two distinct packages onto one module. |
| 6 | `extr_20_14_v1_1_0` | MLA VC10, MLA VC10 Plus | both → `..._MLAVC10Plus_v1_0_2_0.py` | MLA VC10 (base) moved to `..._MLAVC10_v1_0_2_0.py`, same version | **candidate correct.** ASCII sort puts `MLAVC10Plus_...` before `MLAVC10_...` (`P` < `_`), so "first in directory order" always prefers the Plus-suffixed module for any name that's a prefix of it — even though a same-version, correctly-named base module exists. A directory-order artifact, not a content judgement. |
| 7 | `extr_25_5_v1_5_12` | DMP 128 | `..._DMP128_FlexPlus_v1_0_9_0.py` (v1.0.9 — different minor from the package's 1.5.12) | `..._DMP128_Series_v1_5_11_0.py` (v1.5.11 — **same minor**, off by one build) | **candidate correct.** The version-appropriate module (`DMP128_Series`) is claimed by *no other package* in the 314-set — it sits unused while the wrong-generation `FlexPlus` module gets grabbed. (Exact-token's pick for the same package, `DMP_128_Plus_Series_v1_10_14_0.py`, is a third option and also wrong — see §4b row 7.) |
| 8 | `extr_42_1339_v1_11_10` | SMD 101, SMD 202 | `..._SMD101_SMD202_v1_11_10_0.py` — **exact version match** (1.11.10) | `..._SMD101_SMD202_v1_11_9_0.py` (v1.11.9, one patch older) | **committed correct.** "longest" picks the older patch purely because the string `"9"` is one character shorter than `"10"` — a version-digit-width artifact of the tightest-fit heuristic, not a real signal. |
| 9 | `nec_1_2710_v1_0_6` | NP-PA653U, NP-PA803U | NP-PA653U → `..._NPPA_653U_803U_853W_903X_v1_0_1_0.py`, which spells the model's own bare suffix `653U` exactly | moved to `..._NP_PA_653UL_803UL_v1_0_0_0.py`, suffix `653UL` (an extra "L" the package never declares) | **committed correct.** `653U` is a substring of `653UL` too, so both match, but only the committed pick's *own* declared token is an exact match; the candidate substitutes a different NEC SKU suffix. |
| 10 | `wolf_44_2101_v1_18_4` | Cynap (bare) | `..._Cynap_Core_Pure_Pro_v1_1_1_0.py` (v1.1.1) | `..._cynap_v1_18_4_0.py` (bare name, v1.18.4) | **candidate correct.** Package's own internal version, read directly off its `System.Version` object, is **exactly** `{1, 18, 4}` — an exact, verified match to the bare module; `Core_Pure_Pro` is seventeen minor versions stale. |

Tally: committed right in 6/10 (rows 1–4, 8, 9); the alternative right in
4/10 (rows 5–7, 10). **Not a net win for "longest."**

### 4b. "exact-token" — the 7 reassigned packages (of 128 changed; 121 of the
128 are pure drops, covered in §4c)

Three of these seven are the same packages as §4a rows 3, 5 and 7
(`barc_1_2536`, `extr_18_39`, `extr_25_5`) — same verdicts apply, with one
addition for `extr_25_5`: exact-token's own pick differs again from
"longest"'s (`DMP_128_Plus_Series_v1_10_14_0.py`, v1.10.14 — a *third*,
still-wrong option, chosen only because that filename happens to spell
`DMP` and `128` as separate underscore tokens while the correct
(`DMP128_Series`) module glues them into one — a formatting coincidence, not
a specificity signal).

| # | package | model(s) | committed pick | candidate pick | verdict |
|---|---|---|---|---|---|
| 1 | `blkmd_37_382_v1_4_0` | HyperDeck Studio | `..._HyperDeckStudio_Series_v1_3_4_0.py` (glues "HyperDeck"+"Studio" into one token, so exact-token can't even see it) | `..._HyperDeck_Studio_4K_Pro_HD_Plusv1110.py` — itself a malformed filename (version digits fused onto "Plus", no separator) | **uncertain, lean committed.** exact-token wins here only because this one filename happens to use an underscore between "HyperDeck" and "Studio"; the candidate's own filename is garbled enough (`Plusv1110`) to distrust on its own. |
| 2 | `entt_13_2531_v1_3_1` | DIN-ODE, DIN-ODE POE Mk2, Ethergate MK3 | Ethergate MK3 → a v1.1.1.2 module | Ethergate MK3 → `..._DIN_ODE_POE_Mk2_Ethergate_MK3_v1_3_1_0.py`, **exact version match** (1.3.1) | **candidate correct for Ethergate MK3** — a genuine, confirmed live instance of the Clock-Audio-class risk. But exact-token *simultaneously drops* "DIN-ODE POE Mk2" from this same, correct, version-matched module, because the tokeniser splits `"DIN-ODE POE Mk2"` on whitespace only, and the hyphen inside "DIN-ODE" makes it one word that never equals the module's separate `DIN`/`ODE` tokens. Net: the real fix (all three names → the 1.3.1.0 module) is achieved by **neither** rule as implemented. |
| 3 | `extr_25_2146_v1_0_1` | MVC 121 | `..._MVC121_v1_0_2_2.py` (v1.0.2, close to pkg's 1.0.1, bare) | `..._MVC_121_xi_v1_0_0_0.py` — a different "xi" SKU (v1.0.0) | **committed correct.** Same glued-vs-split-token artifact as row 5 of §4a, but here it points at the *wrong* module, because the bare/correct module is the one that glues `MVC121` into one token. |
| 4 | `extr_25_2441_v1_2_1` | DMP 64 | `..._DMP64_v1_2_0_0.py` (v1.2.0, near-exact match to pkg's 1.2.1, bare) | `..._DMP_64_Plus_Series_v1_4_2_0.py` — different SKU, v1.4.2 | **committed correct.** Same artifact again. |

Tally: 1 clear win (Annotator, shared with §4a), 1 partial/wash (Ethergate),
1 uncertain lean-committed, and 4 clear losses (barc, MVC121, DMP64, and a
third-wrong pick for DMP128). **Not a net win for "exact-token"** even before
counting its coverage collapse.

### 4c. "exact-token"'s 121 pure drops (recall loss, not disagreement)

Sampled and categorised all 131 removed `(model, module)` pairs across the
121 packages that lost their match outright (a package can carry >1 model):

| cause | pairs | example |
|---|---|---|
| model name has a hyphen the tokeniser doesn't split on (`"-"` only breaks module filenames, via `_`, not model names, via whitespace) | 86 | `AVL-1050-D` vs. module tokens `avl`, `1050`, `d` |
| model name has a space but the module glues the words into one token | 45 | `Annotator 300` (two words) vs. module token `annotator300` (one token) |
| module filename has fewer than 3 usable `_`-tokens (can't be evaluated at all) | 0 | — (none of the 35 such modules happened to be a committed pick) |

Neither cause is evidence the underlying (dropped) pairing was wrong — both
are just Extron's own filenames being inconsistent about where they put
separators, sometimes for the very same product family (`DMP128` glued in
one module, `DMP_128_Plus_Series` split in a sibling). A literal
"exact-token" rule is not usable without a materially smarter tokeniser
(hyphens, camelCase, digit/letter boundaries), and even a smarter one would
still face the glued-vs-split inconsistency in §4b rows 3–4, where the
*correct* module is the one that glues its tokens. That is why this
experiment does not recommend iterating further on exact-token rather than
just reporting the result.

## 5. Recommendation

**Keep `build_index.match_models` as committed.** Neither "same vendor,
longest match" nor "same vendor, exact token match" is a net improvement on
inspection — the first trades 4 real fixes for 6 new regressions, the second
trades ~1 real fix for several regressions plus a two-thirds coverage
collapse driven by filename formatting, not genuine ambiguity.

What this experiment does deliver: **five confirmed mis-pairs** in the
current, committed 314-package / 352-pair set, all the same shape as the
Clock Audio 5940 caution (a model name is a genuine, vendor-consistent
substring of more than one module, and "first in directory order" — an
ASCII-sort accident, not a correctness signal — picks the wrong one):

- `extr_18_39_v1_1_1.pkp` ("Annotator") → should be `extr_sp_annotator_v1_0_0_1.py`, not `extr_sp_Annotator300_v1_2_1_0.py`
- `extr_20_14_v1_1_0.pkp` ("MLA VC10" only; "MLA VC10 Plus" is already right) → should be `extr_controller_MLAVC10_v1_0_2_0.py`, not `..._MLAVC10Plus_...`
- `extr_25_5_v1_5_12.pkp` ("DMP 128") → should be `extr_dsp_DMP128_Series_v1_5_11_0.py`, not `..._FlexPlus_...`
- `wolf_44_2101_v1_18_4.pkp` ("Cynap") → should be `wolf_cs_cynap_v1_18_4_0.py`, not `..._Core_Pure_Pro_...`
- `entt_13_2531_v1_3_1.pkp` ("Ethergate MK3" sub-pair only) → should be `entt_lc_DIN_ODE_POE_Mk2_Ethergate_MK3_v1_3_1_0.py`, not the v1.1.1.2 module

That's 5 of 314 packages (~1.6%), all Extron except one (Entertech) — small,
but real, and now identified with a stated reason for each rather than
guessed. Hand-correcting these (or excluding them) the next time finding
14's scorecard is touched is cheaper and more targeted than a blanket rule
change, since a blanket change was shown above to break more than it fixes.

**Structural note for a possible future item, not implemented here:** in at
least 2 of the 5 confirmed mis-pairs (DMP 128, Cynap), the version-correct
module is claimed by *no other package* in the 314-set — it sits unused
while a stale sibling gets grabbed instead. `match_models` has no
cross-package consistency check (nothing stops one module being claimed by
an earlier-sorting package when a better home for it exists elsewhere) and
no version-awareness at all (nothing prefers a module whose own filename
version is close to the package's internal version, verified via
`pkp_dump.py`'s `System.Version` read, over one that is not). Either would
be a more targeted fix than resorting on string length or token exactness,
and cheaper to get right — worth a future ROADMAP item if finding 14's
precision is revisited, but out of scope for this comparison.

## Provenance

- Corpus: `corpus/extron-driver3` (1,854 packages) and
  `corpus/extron-gs-modules/09062026` (2,235 modules) — the snapshot finding
  14 used, read-only.
- Baseline: `experiments/oracle_pairs/out/pairs_strict.json` (314 packages,
  352 pairs), reproduced exactly by this script's "current" rule before its
  diffs of the other two rules are trusted.
- Script: `experiments/oracle_pairs/scratch/join_rule_experiment.py`. Does
  not modify `build_index.py`, `test_build_index.py`, or anything under
  `experiments/oracle_pairs/out/`. Writes its own JSON report outside the
  repo (OS temp dir by default, `--outdir` to change it).
- Version numbers quoted above for `.pkp` packages are read directly from
  each package's own `System.Version` object via `pkp_dump.py`, not assumed
  from the filename (checked for `wolf_44_2101`, `extr_25_5`, `extr_18_39`,
  `nec_1_2710`, `extr_42_1339`, all of which matched their filename's
  version suffix exactly).
