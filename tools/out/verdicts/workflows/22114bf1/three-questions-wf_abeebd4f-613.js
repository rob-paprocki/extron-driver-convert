export const meta = {
  name: 'three-questions',
  description: 'Settle three questions by experiment: Crestron IP to Extron, filling a missing Ethernet path, and generating a driver from API docs alone',
  phases: [
    { title: 'Experiments', detail: 'NRBF round-trip, Crestron-to-Extron emitter, missing-Ethernet generation, docs-only generation' },
    { title: 'Verify', detail: 'adversarial check per experiment' },
    { title: 'Synthesize', detail: 'answer the three questions with measured evidence' },
  ],
}

const R = '/Users/robp/GitHub/rob-paprocki/extron-driver-convert'

const GROUND = `
PROJECT: ${R}. The owner asked three concrete questions. Each is now TESTABLE with the tools and
samples on disk, so answer them by measurement, not by argument.

TOOLS (all working, all with passing test suites — import them as libraries, do not shell out):
- tools/pkp_dump.py   — Extron .pkp (gzip + .NET NRBF) -> JSON object graph. Parses every sample
                        with every byte accounted for. 23 tests.
- tools/pkg_dump.py   — Crestron .pkg (zip + CLR ManifestResource) -> manifest + driver JSON.
                        process_pkg(path) -> dict with 'driver_definition'. 23 tests.
- tools/wire_table.py — THE ACCEPTANCE ORACLE. extract_table(source) returns a normalised
                        per-command table (parameters, command-string templates with slots and
                        slot sources, response patterns, value maps) from EITHER Python dialect
                        (shipped ControlScript over extronlib, or the GC-runtime script embedded in
                        a .pkp). diff_tables(a, b) reports commands only in A / only in B, and per
                        shared command any difference in template, slots, response or value map.
                        Unresolvable expressions become COUNTED opaque markers, never guesses.
                        34 tests.
- tools/pkp2cs.py     — .pkp -> ControlScript translator. discover_jobs(path) yields one job per
                        transport by grouping DriverModelAssets on _scriptFileName. Raises
                        UntranslatableDriver rather than degrading. 25 tests.

MEASURED BASELINE for the translator (independently validated, every difference traced to source):
  DSC 12G-HD 28/29 commands matching, DTP3 27/28, Samsung serial 9/9 exact, Automate VX 17/18.
  All outputs compile. Remaining differences are Extron's own bugs, version skew, or package gaps.

KEY SAMPLES AND WHAT MAKES THEM USEFUL:
- Samsung QN43LS03DAFXZA — the crown jewel: the SAME display encoded by BOTH vendors.
    Extron .pkp: "${R}/samples/Samsung QNxxLS03DAFXZA/pkp/smsg_10_6738_v1_0_0.pkp"
      contains TWO embedded scripts: a serial one, and an ethernet one that subclasses
      Extron2.HTTPDriver and speaks JSON-RPC 2.0 over HTTPS to port 1516 with a createAccessToken
      handshake. 12 DriverModelAssets = 6 sizes x 2 transports.
    Extron shipped ControlScript: only the SERIAL module exists —
      "${R}/samples/Samsung QNxxLS03DAFXZA/controlscript/smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py"
      EXTRON NEVER SHIPPED AN IP CONTROLSCRIPT MODULE FOR THIS DEVICE.
    Crestron packages (Serial / IP / IR):
      "${R}/samples/Samsung QNxxLS03DAFXZA/Crestron/IP/FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg"
      The IP one is a LegacyWrappers JSON-engine driver — fully declarative, no meaningful IL —
      targeting the SAME port 1516 with the SAME createAccessToken handshake, and 8 of its 16
      methods carry exactly Extron's method names.
    For 6 of 8 capability families the two vendors' SERIAL drivers produce byte-identical frames
    including checksum, and both encode the same undocumented firmware-bug workaround
    (0D 00 00 02 for power-on rather than the documented 00 00 00 02).
- Automate VX — an HTTP/REST device whose vendor API is fully documented and harvested:
    "${R}/reference/automate-vx-api/ENDPOINTS.md" (32 endpoints, 40 pages)
    Extron shipped ControlScript (HTTP dialect, a working template for HTTP ControlScript):
      "${R}/samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py"
    Extron .pkp: "${R}/samples/Automate VX/pkp/1bynd_42_4279_v1_0_11.pkp"
    ESTABLISHED (findings/08): Extron implements 22 of the 32 documented endpoints, ALSO calls 5
    sub-APIs visible only inside GetAllStatus's example body, and 5 endpoints with NO trace in the
    docs at all (StartAutoSwitch, StopAutoSwitch, StartISORecord, StopISORecord, Wake — note Sleep
    IS documented and Wake is NOT), and sends three parameters as JSON strings where the spec says
    int.

ESTABLISHED CONSTRAINTS:
- Crestron's load path has no signing/certification gate, but its SDK licence restricts the tools
  to "Developing software for Crestron Devices" and requires a dealer/AIP/partner agreement.
- Extron -> .pkp (writing a package) was judged impractical earlier, but that judgement was made
  BEFORE a complete NRBF parser existed. It has never actually been attempted.
- Do NOT decompile driver IL. Read metadata (names, attributes) freely; that is not decompilation.

RULES:
- Work test-first where you write code. Report ACTUAL command output, never a claim.
- Python 3 standard library only.
- Cite path:line, JSON path or byte offset for every claim. No citation, no finding.
- NEVER submit placeholder or test content. An honest failure is a valid, valuable result here —
  a fabricated success is not.
- Web access only via the Bright Data CLI ('brightdata search' / 'brightdata scrape').
- FILE WRITES: each experiment writes ONLY inside its own directory, named below. Do not write
  under ${R}/tools/ or into any other experiment's directory.
`

const FIND = {
  type: 'object',
  properties: {
    dimension: { type: 'string' },
    summary: { type: 'string' },
    verdict: { type: 'string', enum: ['YES', 'YES_WITH_CAVEATS', 'PARTIAL', 'NO', 'UNPROVEN'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          evidence: { type: 'string' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['claim', 'evidence', 'confidence'],
      },
    },
    openQuestions: { type: 'array', items: { type: 'string' } },
  },
  required: ['dimension', 'summary', 'verdict', 'findings'],
}

const VERD = {
  type: 'object',
  properties: {
    dimension: { type: 'string' },
    verified: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          verdict: { type: 'string', enum: ['CONFIRMED', 'REFUTED', 'UNCERTAIN', 'OVERSTATED'] },
          note: { type: 'string' },
        },
        required: ['claim', 'verdict'],
      },
    },
    missedOrWrong: { type: 'array', items: { type: 'string' } },
  },
  required: ['dimension', 'verified'],
}

const EXPERIMENTS = [
  {
    key: 'q1a-nrbf-writeback',
    prompt: `QUESTION 1, HALF A: can we WRITE a .pkp at all? This has never been attempted and the
earlier "impractical" judgement predates the complete parser.

The cheap decisive test is a ROUND TRIP. Write ${R}/experiments/nrbf_writeback/nrbf_write.py: an
NRBF SERIALIZER that consumes the object graph pkp_dump produces and emits a .NET BinaryFormatter
stream. Then, for each of the four sample .pkp files, do: gunzip -> parse -> re-serialize -> compare
against the original decompressed bytes.

Byte-identical round-trip is the goal because it proves the serializer models every record type,
every reference, and the exact layout the format requires. If you cannot reach byte-identity,
report precisely where the streams first diverge and why — that residue IS the finding, and it
tells the owner exactly what stands between here and a writable package.

Then attempt a MUTATION test: parse a .pkp, change something small and semantically safe (a
revision-history string, or a command's description), re-serialize, and re-parse with pkp_dump.
Confirm the mutation survives and the rest of the graph is intact.

Write tests first, in the style of ${R}/tools/test_pkg_dump.py (plain asserts, no pytest).

Be honest about scope: byte-identical round-trip proves the FORMAT is writable. It does NOT prove
Global Configurator will accept a package assembled from scratch — that needs GC and is out of
reach here. State that boundary clearly rather than overclaiming.`,
  },
  {
    key: 'q1b-crestron-to-controlscript',
    prompt: `QUESTION 1, HALF B: can a Crestron IP driver be turned into an Extron ControlScript
module? Build it and MEASURE it, because for this device the ground truth exists.

Write ${R}/experiments/crestron2cs/crestron2cs.py: read a Crestron .pkg via pkg_dump, and emit an
Extron ControlScript module.

Use the Samsung IP package as the subject:
  "${R}/samples/Samsung QNxxLS03DAFXZA/Crestron/IP/FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg"
It is a LegacyWrappers JSON-engine driver, so its whole protocol is declarative: resolve the
Template chains bottom-up (running each level's Transformations BEFORE substituting into the
parent), apply send-rewriting Rules before recording what reaches the wire, and flatten the
Responses decoder tree into (outstanding command, pattern, captures) tuples.

For the ControlScript output shape, you have a working HTTP-dialect template to copy:
  "${R}/samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py"
and a working serial-dialect one in the Samsung shipped module.

THEN MEASURE, which is the point. The Extron .pkp for this same display contains an ETHERNET
embedded script (Extron2.HTTPDriver, JSON-RPC over HTTPS:1516) that is Extron's own encoding of the
same IP protocol. Extract it with pkp_dump, run wire_table.py over BOTH your generated module and
that Extron script, and diff them.

Report: how many commands your Crestron-derived module produces, how many the Extron script has,
how many match on wire content, and classify every difference. This is a genuine cross-vendor
conversion measured against an independent implementation of the same protocol — the strongest
validation available anywhere in this project.

Be rigorous about what "match" means: same endpoint/method, same parameters, same JSON body shape.`,
  },
  {
    key: 'q2-missing-ethernet',
    prompt: `QUESTION 2: an Extron .pkp contains an Ethernet element the shipped ControlScript
module does not have. Can the Ethernet control be written into a .py from the .pkp?

The Samsung display is exactly this case, and it is real rather than contrived: the .pkp carries
BOTH a serial and an ethernet embedded script, and Extron shipped ONLY the serial ControlScript
module. The IP module does not exist. Generate it.

  Package: "${R}/samples/Samsung QNxxLS03DAFXZA/pkp/smsg_10_6738_v1_0_0.pkp"
  pkp2cs.discover_jobs() already returns 2 jobs for it (serial and ethernet) — confirm that, then
  drive the ethernet job through to a complete ControlScript module.

Write your work under ${R}/experiments/missing_ethernet/. You may import pkp2cs and extend it in
your own directory, but do NOT modify anything under ${R}/tools/.

The gap to close is the transport template: the shipped Samsung module is serial, so pkp2cs's
serial template does not fit an HTTP driver. The Automate VX shipped module
("${R}/samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py") is a working
HTTP-dialect ControlScript module and is your template. Derive it from that file rather than
inventing it.

VALIDATE: run wire_table.py over your generated IP module and over the .pkp's embedded ethernet
script, and diff. Every command in the embedded script should appear in your module with matching
wire content. Report the scorecard and classify every difference. Confirm the output compiles with
'python3 -m py_compile'.

Also state clearly what a human would still need to check before putting this on a real system,
since nobody can test it against hardware here. Do not imply it is verified working.`,
  },
  {
    key: 'q3-docs-only-generation',
    prompt: `QUESTION 3: can a working driver be generated from API documentation alone? MEASURE
it, do not opine — this project has an oracle and a ground-truth driver for exactly this device.

THE PROTOCOL, and you must follow it honestly for the result to mean anything: generate an Extron
ControlScript module for the Automate VX using ONLY the harvested API documentation at
${R}/reference/automate-vx-api/ (ENDPOINTS.md and the API-Reference pages) plus a ControlScript
HTTP-dialect template. You may look at Extron's shipped Automate VX module ONLY for its
STRUCTURAL/BOILERPLATE shape — the class scaffold, helper methods, transport classes. You must NOT
look at which endpoints it calls, its parameter handling, or its command table while generating.
Write the generator and the generated module under ${R}/experiments/docs_only/.

THEN, and only then, diff your docs-only module against Extron's real shipped module using
wire_table.py.

Report the full scorecard: commands in yours, commands in Extron's, matching, and every difference
classified as one of —
  (a) DOC GAP — Extron has it, the docs never mention it (expect StartAutoSwitch, StopAutoSwitch,
      StartISORecord, StopISORecord, Wake)
  (b) EXAMPLE-ONLY — Extron has it, documented only inside GetAllStatus's example body
  (c) UNIMPLEMENTED — documented, Extron chose not to implement it
  (d) TYPE MISMATCH — both have it but the docs' declared type differs from what Extron sends
  (e) GENUINE GENERATOR ERROR — you got something wrong that the docs actually specified correctly

Category (e) is the honest measure of how good doc-driven generation is; (a)-(d) measure the
documentation's own limits. Keep them strictly separate.

Then answer the practical question the owner actually cares about: WOULD THE DOCS-ONLY MODULE WORK?
Not "does it match Extron's" but "would it control the device". A module missing Wake still controls
most of the device. Give an honest functional assessment of what works, what silently does not, and
whether a human reviewing the generated module could TELL that anything was missing without owning
the hardware. That last point is the crux: undetectable incompleteness is far more dangerous than
visible incompleteness.`,
  },
]

phase('Experiments')
log('Four experiments to settle the three questions')

const done = await pipeline(
  EXPERIMENTS,
  (e) => agent(`${GROUND}\n\nYOUR EXPERIMENT: ${e.key}\n\n${e.prompt}`, {
    label: `exp:${e.key}`, phase: 'Experiments', schema: FIND, model: 'sonnet', effort: 'high',
  }),
  (res, e) => {
    if (!res) return null
    return agent(
      `${GROUND}\n\nYou are an adversarial verifier for experiment "${e.key}". REFUTE the findings ` +
      `below rather than agreeing. RUN THE CODE YOURSELF — do not trust reported output. Re-run the ` +
      `wire_table diffs, recount every scorecard number, and re-verify any claim of a byte-identical ` +
      `round trip.\n\nBe most skeptical of: any generated module claimed to "match" (check the wire ` +
      `CONTENT, not just command names); any claim of round-trip fidelity (re-run the comparison); and ` +
      `in the docs-only experiment, whether the generator actually avoided looking at Extron's command ` +
      `table — look for suspicious exactness that documentation alone could not have produced, ` +
      `especially any of the five undocumented endpoints appearing in the docs-only output.\n\n` +
      `CONFIRMED only if you personally reproduced it. REFUTED if contradicted. OVERSTATED if ` +
      `directionally right but claimed too strongly. UNCERTAIN if uncheckable.\n\n` +
      `If placeholder or test content was submitted, say so explicitly in missedOrWrong.\n\n` +
      `Their brief:\n${e.prompt}\n\nFINDINGS:\n${JSON.stringify(res, null, 2)}`,
      { label: `verify:${e.key}`, phase: 'Verify', schema: VERD, model: 'sonnet', effort: 'high' }
    ).then((v) => ({ dimension: e.key, analysis: res, verification: v }))
  }
)

const dossier = done.filter(Boolean)
const counts = dossier.reduce((a, d) => {
  for (const v of (d.verification && d.verification.verified) || []) a[v.verdict] = (a[v.verdict] || 0) + 1
  return a
}, {})
log(`Experiments done: ${dossier.length}/${EXPERIMENTS.length} — ${JSON.stringify(counts)}`)

phase('Synthesize')
const synthesis = await agent(
  `${GROUND}\n\nVerified dossier follows. Treat REFUTED as false, OVERSTATED as weaker, UNCERTAIN ` +
  `as unproven.\n\nThe owner asked three questions. Answer each one DIRECTLY and FIRST, in one ` +
  `sentence, before any elaboration. He is an AV professional who writes code and wants to know ` +
  `what he can actually build.\n\n` +
  `1. Can we ingest a Crestron IP device driver and generate a matching Extron .pkp AND ` +
  `ControlScript .py? Treat the two outputs separately — the evidence differs sharply between them.\n` +
  `2. Can we take an Extron .pkp that has an Ethernet element the ControlScript .py lacks, and ` +
  `write that Ethernet control into the .py? Say whether it is done, demonstrated, or blocked.\n` +
  `3. Can a .pkp / .py / .pkg be generated from a set of API docs handed to an LLM? Give the ` +
  `measured number, separate the documentation's limits from the generator's, and answer the ` +
  `practical question: would the result actually control the device, and could a reviewer TELL what ` +
  `was missing without the hardware?\n\n` +
  `Then: for each of the three, what is the remaining work and the single hardest obstacle. Be ` +
  `concrete about which parts are demonstrated, which are plausible, and which are unproven. Where ` +
  `an experiment failed, say what was learned — a failed experiment that maps the obstacle is a ` +
  `real result.\n\n` +
  `Prose with headings, minimal bullets, cite evidence, no padding, no hedging where the evidence ` +
  `is clear.\n\nDOSSIER:\n${JSON.stringify(dossier, null, 2)}`,
  { label: 'synthesis:three-questions', phase: 'Synthesize', model: 'opus', effort: 'high' }
)

return { experiments: dossier.length, verdictCounts: counts, dossier, synthesis }
