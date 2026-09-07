## Adversarial review results

**Independently reproduced, all six pairs (matches the report exactly):**

| pair | wire-match numerator | dangling | invented | compiles |
|---|---|---|---|---|
| DSC 12G-HD | 28 (of 29) | 0 | 0 | yes |
| DTP3 CP 42 | 27 | 2 (`ReadMatrixIONameString`, `ReadMatrixIONumberSelect`) | 0 | yes |
| Samsung serial | 9 | 0 | 0 | yes |
| Automate VX | 17 | 0 | 0 | yes |
| Clock Audio 1777 | 4 | 0 | 0 | yes |
| Biamp Tesira | 63 | 3 (`ReadDialString`, `ReadNewSpeedDialEntryNameString`, `ReadNewSpeedDialEntryNumberString`) | 0 | yes |

`tools/test_pkp2cs.py` independently run: 55 passed, 0 failed. `git diff --stat` confirms only `tools/pkp2cs.py` and `tools/test_pkp2cs.py` touched — no changes to `EXTRONLIB_PROVIDED` or any dangling/invented-detection allowlist (`tools/pkp2cs.py:1660`, `1769` unchanged in diff).

**Meaningfulness of new tests:** verified directly by checking out the pre-fix `tools/pkp2cs.py` (`git show HEAD:tools/pkp2cs.py`) and rerunning the suite — exactly the 3 new tests fail (52 passed, 3 failed), confirming they are real regression tests against the actual bug, not vacuous.

**Genuine generality, checked with two independently-constructed fifth guard shapes** (not in any test or the report): (1) the pre-write nested two levels deep inside `for`/`try` gated by an arbitrarily-named `self._validate(...)` guard, and (2) an early-return guard where the pre-write sits completely outside any `if` at all. Both were correctly stripped by `transform_method`, confirming the fix generalizes across guard *shape*, as claimed.

**Deletion safety:** dumped all 122 distinct `Write<X>` wrapper-definition bodies across all six `.pkp` sources — every one is a single-line `self.WriteStatusHelper(name, value, qualifier, context)` call with no other side effects, so dropping the pre-write call never discards real behavior. Confirmed `'Live'` writes and `Read<X>(..., 'Emulated')` reads (whose return values are consumed) are structurally excluded and untouched, both by the guardrail test and by grepping all 144 real `'Emulated'`-suffixed call sites in the six packages (zero exceptions to the Write-is-bare-Expr / Read-is-Assign split the fix relies on).

**One finding reported** (PLAUSIBLE, not currently triggering on any of the six pairs): the rule keys on the call being a bare top-level `Expr(Call)` statement with `'Emulated'` as the last *positional* argument (`tools/pkp2cs.py:405-407`). A hypothetical seventh device whose GC generator emits the pre-write as `self.WriteFoo(value, qualifier, context='Emulated')` (keyword arg) or embedded in a larger expression (e.g. a `BoolOp`) would not be caught — verified by constructing both synthetically and confirming the call survives while its definition is still deleted, reproducing the same dangling-reference bug class. This is a real boundary on the "call shape" framing in the code's own comment, though grepping all 144 real `'Emulated'` occurrences across the six packages found zero instances of either form, so no currently-scored pair is affected.

Files reviewed: `/Users/robp/GitHub/rob-paprocki/extron-driver-convert/tools/pkp2cs.py` (esp. lines 257-521), `/Users/robp/GitHub/rob-paprocki/extron-driver-convert/tools/test_pkp2cs.py` (esp. lines 301-419, 1021-1035).