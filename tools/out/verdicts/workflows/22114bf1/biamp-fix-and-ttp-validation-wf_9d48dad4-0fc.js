export const meta = {
  name: 'biamp-fix-and-ttp-validation',
  description: 'Fix the Emulated pre-write guard-shape rule generally, harvest Biamp TTP docs, and validate generated wire strings against the protocol spec',
  phases: [
    { title: 'Work', detail: 'fix the rewrite rule; harvest Tesira Text Protocol documentation' },
    { title: 'Validate', detail: 'check generated Biamp wire strings against TTP syntax' },
    { title: 'Review', detail: 'adversarial review of the fix' },
  ],
}

const R = '/Users/robp/GitHub/rob-paprocki/extron-driver-convert'

const GROUND = `
PROJECT: ${R}. A .pkp -> ControlScript translator with two acceptance metrics.

CURRENT STATE, all six pairs, rules unchanged:

  pair              wire-match   dangling  invented  compiles
  DSC 12G-HD        28/29        0         0         yes
  DTP3 CP 42        27/28        4         0         yes
  Samsung serial     9/9         0         0         yes
  Automate VX       17/18        0         0         yes
  Clock Audio 1777   4/7         0         0         yes
  Biamp Tesira      63/74       51         0         yes

tools/test_pkp2cs.py: 52 passed. THE BASELINE ABOVE MUST NOT REGRESS.

THE BUG TO FIX — diagnosed precisely, not yet fixed.
GC scripts write an "Emulated" status value before performing a Set, e.g.:
    if self.__SafeToSet('X'):
        self.WriteX(value, qualifier, 'Emulated')
        ...
The translator deletes the per-command Write<X>/Read<X> wrapper DEFINITIONS (correct — shipped
modules define only the generic WriteStatus/ReadStatus), and separately strips the Emulated
pre-write CALLS. But the call-stripping predicate is gated on the __SafeToSet guard SHAPE
(tools/pkp2cs.py, GenericBodyRewriter.visit_If). Biamp's Tesira generator never emits
__SafeToSet -- 0 occurrences in its 4,618-line script -- it gates on plain parameter validation
instead, e.g.:
    if 0 <= len(value) <= 30:
        self.WriteMatrixIONameString(value, qualifier, 'Emulated')
So 48 Emulated pre-write calls survive while their target definitions are deleted -> dangling
references -> AttributeError at runtime.

THIS WAS ALREADY LEAKING IN-SAMPLE. DTP3's SetMatrixIONameString / SetMatrixIONumberSelect have
exactly that shape and account for 4 of the in-sample dangling. A correct general fix should
reduce BOTH Biamp's 51 and DTP3's 4.

Judge the fix by that: if it fixes Biamp but leaves DTP3 at 4, it is shape-matching a second
special case rather than fixing the rule.

TOOLS (import as libraries):
  tools/pkp_dump.py, tools/pkg_dump.py
  tools/wire_table.py   extract_table(src) -> WireTable; diff_tables(a,b) -> {"differences": ...}
  tools/pkp2cs.py       translate_pkp(path); discover_jobs(path);
                        find_dangling_self_calls(module_src) -> undefined self.X() names
                        find_invented_wire_strings(module_src, origin_src) -> literals sent but
                          absent from the source package. MUST STAY AT 0 FOR ALL SIX.

THE SIX PAIRS:
  "${R}/samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp"
    -> "${R}/samples/DSC_12G-HD/controlscript/extr_scaler_DSC_12G_HD_A_v1_0_0_0.py"
  "${R}/samples/DTP3 CP 42/pkp/extr_15_17578_v1_3_0.pkp"
    -> "${R}/samples/DTP3 CP 42/controlscript/extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py"
  "${R}/samples/Samsung QNxxLS03DAFXZA/pkp/smsg_10_6738_v1_0_0.pkp"
    -> "${R}/samples/Samsung QNxxLS03DAFXZA/controlscript/smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py"
  "${R}/samples/Automate VX/pkp/1bynd_42_4279_v1_0_11.pkp"
    -> "${R}/samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py"
  "${R}/samples/ClockAudio/pkp/clau_25_1777_v1_3_0.pkp"
    -> "${R}/samples/ClockAudio/controlscript/clau_dsp_CDT100_v1_0_3_0.py"
  "${R}/samples/Tesira/pkp/biam_25_150_v1_20_0.pkp"
    -> "${R}/samples/Tesira/controlscript/biam_dsp_TesiraSeries_v1_18_3_0.py"

RULES:
- Work test-first. Report ACTUAL command output; never assert that tests pass.
- Python 3 standard library only; pytest is NOT installed.
- Report BOTH metrics for ALL SIX pairs after every change. A fix that improves one device and
  regresses another is not a fix.
- Never fabricate wire content. find_invented_wire_strings must stay 0 everywhere.
- Cite path:line. Never submit placeholder or test content.
- Web access ONLY via the Bright Data CLI ('brightdata scrape <url>' / 'brightdata search "q"').
  Never WebFetch/WebSearch and never curl to target sites.
`

phase('Work')
log('Fixing the Emulated pre-write guard-shape rule; harvesting Biamp TTP documentation')

const harvestP = agent(
  `${GROUND}\n\nYOUR TASK: harvest Biamp's Tesira Text Protocol documentation into
${R}/reference/biamp-ttp/. You are the only agent writing there; do NOT write under ${R}/tools/.

Two sources the repo owner supplied:
  https://tesira-software-help.biamp.com/#t=assets%2FTOC%2FSystem_Control%2FTesira_Text_Protocol%2FTTP_Syntax.htm
  https://support.biamp.com/Tesira/Control/Tesira_command_string_calculator

The first is a frameset-style help system, so the '#t=' fragment will not fetch directly — the real
page is likely at a path like .../assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Syntax.htm or
a flattened equivalent. Work out the real URL pattern and enumerate the Tesira Text Protocol
section.

IMPORTANT — a lesson this project learned expensively: do NOT enumerate by keyword search alone
and do NOT infer a filename convention from one sample and assume it is exhaustive. Both failed
here before. Look for a published index (TOC data file, sitemap, navigation JSON) and use it. If
you cannot find one, report coverage as "found by method X" rather than claiming completeness.

Save each page as markdown with a 'Source: <url>' first line, plus INDEX.md.

Then write SYNTAX.md capturing precisely: the TTP command grammar (verb, instance tag, attribute,
index, value), the full verb set (get/set/subscribe/unsubscribe/toggle/increment/decrement/
recallPreset...), token quoting rules, the line terminator, the response/acknowledgement formats
including error responses, and the subscription mechanism. Quote verbatim with URLs.

Also capture what the command string calculator page documents about how strings are assembled --
it is a tool for building valid TTP strings, so it likely states the grammar concretely.

Report pages fetched, anything unreachable, and how you enumerated.`,
  { label: 'harvest:biamp-ttp', phase: 'Work', model: 'sonnet', effort: 'high' }
)

const fix = await agent(
  `${GROUND}\n\nYOUR TASK: fix the Emulated pre-write rule GENERALLY, in ${R}/tools/pkp2cs.py.
Work test-first.

The current predicate only recognises the pre-write when it sits inside a __SafeToSet guard. The
real invariant has nothing to do with the guard: a call of the form
    self.Write<Command>(<args>, 'Emulated')
is GC dual-status bookkeeping with no ControlScript counterpart, and should be dropped wherever it
appears, because the shipped modules contain no per-command Write<X> at all. Verify that claim
against the shipped modules before relying on it.

Be careful about what you do NOT drop:
- a Write<X> call whose last argument is 'Live' (or absent) is NOT the Emulated pre-write.
- a Read<X>(..., 'Emulated') call is a different construct: it READS GC-only scratch state and its
  value is consumed. Those are the 5 known residuals that Extron restructured by hand into
  qualifier['Number'] / qualifier['Name']. Do not guess at them; leave them reported.
- do not delete a statement that has other effects.

After the change, report for ALL SIX pairs: wire-match, dangling, invented (must be 0), and whether
the module compiles. DTP3 should improve from 4 as well as Biamp from 51; if DTP3 does not move,
you have shape-matched a second special case instead of fixing the rule — say so rather than
declaring success.

If some of Biamp's 51 have a different root cause, fix what is genuinely the same bug and report
the remainder separately with its own diagnosis. Partial progress honestly described beats an
overclaimed total.`,
  { label: 'fix:emulated-prewrite', phase: 'Work', model: 'sonnet', effort: 'high' }
)

const harvest = await harvestP

phase('Validate')
const validation = await agent(
  `${GROUND}\n\nFix report:\n${fix}\n\nTTP harvest report:\n${harvest}\n\n---\n\nYOUR TASK: validate
the generated Biamp module against Biamp's OWN protocol specification — a third source, independent
of both Extron's shipped module and the .pkp.

1. Re-run all six pairs yourself. Do not trust the fix report. Report both metrics for each.
2. Extract every command string the generated Biamp module builds (use wire_table.py).
3. Check each against the TTP grammar in ${R}/reference/biamp-ttp/SYNTAX.md: is it well-formed
   TTP? Correct verb, instance tag, attribute, index placement, quoting, terminator?
4. Do the same for Extron's SHIPPED Biamp module. Where the two differ (there are 11 known wire
   differences), use the TTP spec as referee: which one is right? This is the interesting result —
   the project has assumed Extron's shipped module is ground truth, and the spec can test that.
5. Note any generated string that is well-formed TTP but semantically implausible, and any place
   the spec shows a construct neither module uses.

Then answer: does validating against a protocol SPEC catch anything that diffing against another
implementation did not? That bears directly on whether the project should add spec-based checking
as a third metric alongside wire-matching and runtime resolvability.

Be careful with the known TTP subtleties: quoting of string values, the difference between get and
subscribe responses, and index/attribute ordering. Cite the spec by URL for each judgement.`,
  { label: 'validate:ttp-spec', phase: 'Validate', model: 'sonnet', effort: 'high' }
)

phase('Review')
const review = await agent(
  `${GROUND}\n\nFix report:\n${fix}\n\nValidation:\n${validation}\n\n---\n\nYOU ARE AN ADVERSARIAL
REVIEWER. Read ${R}/tools/pkp2cs.py and ${R}/tools/test_pkp2cs.py as they stand on disk. Ignore what
the reports claim.

Check specifically:
 - Is the new Emulated-pre-write predicate genuinely general, or does it pattern-match a second
   special case? Construct a plausible fifth guard shape and see whether it would be handled.
 - Does it delete anything it should not? Look for Write<X> calls with a 'Live' argument, calls with
   side effects, and Read<X>(..., 'Emulated') reads whose value is consumed.
 - Re-run all six pairs and both metrics yourself. Confirm the baseline did not regress and that
   find_invented_wire_strings is 0 everywhere.
 - Are the new tests meaningful, or would they pass against a broken implementation?
 - Did anything get added to EXTRONLIB_PROVIDED or otherwise allowlisted to make a number look
   better? That would be silencing a bug rather than fixing it.

Report findings ranked by severity with file:line and a concrete failure scenario. Do NOT fix
anything — report only.`,
  { label: 'review:adversarial', phase: 'Review', model: 'sonnet', effort: 'high' }
)

return { fix, harvest, validation, review }
