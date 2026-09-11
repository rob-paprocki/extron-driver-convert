export const meta = {
  name: 'crestron-interop-feasibility',
  description: 'Research Crestron module/driver formats and assess whether an Extron-centred converter can ingest and emit them',
  phases: [
    { title: 'Research', detail: '9 parallel dimensions over Crestron SDK docs, forums and prior art via Bright Data' },
    { title: 'Verify', detail: 'adversarial skeptic per dimension, re-checking claims against cited sources' },
    { title: 'Synthesize', detail: 'in/out verdicts, IR architecture recommendation, completeness critic' },
  ],
}

const EXTRON_CONTEXT = `
CONTEXT — what this research serves.

There is an existing research repo investigating conversion between two Extron artifacts:
  (a) .pkp — a Global Configurator Plus/Pro driver package. ESTABLISHED BY DIRECT INSPECTION:
      it is gzip over a .NET BinaryFormatter (NRBF) stream, unencrypted and unsigned, holding
      Extron.Configuration.* assets (DriverModelAsset, DriverCommandAsset, EnumParamAsset,
      DecimalParamAsset, StringParamAsset, EnumStateAsset, EthernetProtocolAsset,
      RevisionHistoryAsset, StreamResourceAsset). Crucially it ALSO embeds a complete ~2,100-line
      Python driver written against the Global Configurator runtime ('from Extron2.BaseDriver
      import BaseDriver').
  (b) the shipped Extron ControlScript module — a ~1,250-line Python file targeting a different
      runtime ('from extronlib.interface import SerialInterface, EthernetClientInterface';
      'class DeviceClass:' with a self.Commands dict of command name ->
      {'Parameters': [...], 'Status': {}}, plus AddMatchString regex response matching and
      transport mixin classes like SSHClass(EthernetClientInterface, DeviceClass)).

So the Extron side of the problem is: two Python dialects over two runtimes, both ultimately
building Extron SIS command strings and regex-matching responses.

THE NEW QUESTION: could such a tool also INGEST and EMIT control modules for another
manufacturer — specifically CRESTRON? The owner is aware this may not be answerable quickly.
Your research must establish the real facts, not a plausible-sounding story.
`

const RULES = `
HARD RULES:
- For ALL web access you MUST use the Bright Data CLI, never WebFetch/WebSearch and never curl to
  target sites. The machine owner's home IP must not be used for agent crawling.
    brightdata search "<query>"          # SERP
    brightdata scrape <url>              # fetch a page as markdown
    brightdata discover "<query>"        # AI intent-ranked search + parsed content
  Run 'brightdata <cmd> --help' if you need options. If a command fails, report the failure;
  do not silently fall back to another fetch method.
- Cite a URL for every factual claim about Crestron. A claim with no citation is an open question.
- Separate VERIFIED (read it in an official Crestron SDK/doc page) from REPORTED (a forum post,
  blog, or vendor page) from INFERRED (your reasoning). Label which is which. Forum and Reddit
  claims are evidence of practice, not of specification — mark them REPORTED even when confident.
- Crestron's developer docs live largely at sdkcon78221.crestron.com and docs.crestron.com.
  Some material is behind a login (drivers.crestron.io, the Crestron SDK downloads). If something
  is gated, SAY SO — "gated, could not verify" is a valuable finding, an invented answer is not.
- Do not assume Crestron works like Extron. Where the models genuinely differ, that difference is
  the finding.
`

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    dimension: { type: 'string' },
    summary: { type: 'string', description: '4-8 sentences: what you established' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          basis: { type: 'string', enum: ['VERIFIED', 'REPORTED', 'INFERRED'] },
          source: { type: 'string', description: 'URL, or "gated"/"not found"' },
          bearing: { type: 'string', enum: ['crestron-in', 'crestron-out', 'both', 'architecture', 'legal', 'neither'] },
          implication: { type: 'string' },
        },
        required: ['claim', 'basis', 'source', 'bearing'],
      },
    },
    gatedOrUnknown: { type: 'array', items: { type: 'string' }, description: 'what you could not reach and why' },
    openQuestions: { type: 'array', items: { type: 'string' } },
  },
  required: ['dimension', 'summary', 'findings'],
}

const VERDICT_SCHEMA = {
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

const DIMENSIONS = [
  {
    key: 'artifact-landscape',
    prompt: `Enumerate EVERY artifact type a Crestron integrator would call a "module" or "driver",
and work out which one is the true analogue of an Extron ControlScript module.

Cover at least: SIMPL Windows programs (.smw), SIMPL+ (.usp/.ush), SIMPL# libraries (.clz),
SIMPL# Pro programs (.cpz), user macros (.umc), Crestron Certified Drivers (.pkg), Crestron Home
drivers, and anything else you find (module archives, .dat files, .cdz, .lpz, plugin formats).

For each: what it IS, what file extension(s), what produces it, what consumes it, whether it is
source or compiled, whether it is declarative data or executable code, and whether it describes
ONE DEVICE (a driver) or PROGRAM LOGIC (an integration).

That last distinction is the crux — an Extron ControlScript module is a per-device command
abstraction, and much of the Crestron world is program logic instead. Rank the candidates by how
closely each matches the per-device-driver concept, and name the single best analogue with reasons.`,
  },
  {
    key: 'ccd-package',
    prompt: `Deep-dive Crestron Certified Drivers (CCD) and the .pkg package, which early searching
suggests is the closest analogue to an Extron driver package.

Establish: what is inside a .pkg (is it a zip? what members?); the role of the JSON/DAT
configuration files reported to live inside; whether a "simple" driver can be purely declarative
JSON or always needs a compiled C# DLL; the driver TYPES supported (display, AVR, cable box,
Blu-ray, switcher, lighting, thermostat, media server...) and whether that taxonomy is fixed;
the transport model (serial/IP/IR/CEC); how commands and their parameters are expressed; how
device responses/feedback are parsed; and what the SDK's base classes and interfaces are.

Crestron's driver SDK documentation is at sdkcon78221.crestron.com. Read the actual pages —
"Load a Driver", "Submit a Driver", the CCD developer microsite generally. Get concrete: names of
JSON keys, class/interface names, file members, anything that lets someone judge whether a
generator could emit a valid package.

Also determine whether a .pkg must be SIGNED or CERTIFIED by Crestron to load on a processor, and
whether side-loading unsigned/third-party packages is supported. That single answer largely decides
whether "spitting out" Crestron drivers is possible at all.`,
  },
  {
    key: 'simpl-ecosystem',
    prompt: `Characterize the SIMPL side: SIMPL Windows, SIMPL+, SIMPL#, SIMPL# Pro.

Establish what a "module" means in each, what the file formats are, whether they are
human-readable/parseable, and what toolchain compiles them. Critically: explain the SIGNAL/JOIN
model — digital, analog and serial joins — and how a device module exposes its capability through
joins rather than through method calls.

Then answer directly: if you had a complete Extron ControlScript module (a Python class with a
command dict, Set/Update methods and regex response matching), what would the equivalent SIMPL+
or SIMPL# module look like, and what information would you need that the Extron module does not
carry? Conversely, if you had a Crestron SIMPL+ device module, what could you recover from it?

Assess whether SIMPL+ source (.usp) is realistically machine-generatable, and whether the
compilation step requires Crestron's proprietary toolchain (and whether that toolchain is
free, licensed, or gated).`,
  },
  {
    key: 'modern-targets',
    prompt: `Determine which Crestron target is worth supporting, by establishing where the platform
actually is in 2026.

Cover: 3-Series vs 4-Series control systems and what changed; Crestron Home (formerly Pyng) and
its driver model; whether CCD is now the recommended path for device control versus SIMPL modules;
the status of SIMPL Windows as a supported/declining authoring environment; Crestron's .AV
Framework; and any newer SDK direction (C# / .NET version supported on 4-Series, containerized
programs, anything post-SIMPL).

Also find out how integrators actually obtain drivers today — the Crestron driver portal
(drivers.crestron.io), what is free vs licensed, and whether third parties (e.g. Ultamation,
Chowmain) sell CCD packages, since a commercial third-party driver market is direct evidence that
non-Crestron parties CAN produce loadable drivers.

Conclude with a ranked recommendation: if a converter supported exactly ONE Crestron output
format, which should it be, and why.`,
  },
  {
    key: 'semantic-gap',
    prompt: `Analyze the IMPEDANCE MISMATCH between the Extron model and the Crestron model. This is
the conceptual heart of the question, so be rigorous rather than diplomatic.

The Extron ControlScript model: a Python class per device; a Commands dict naming capabilities;
per-command Parameters; Set*/Update* methods; regex match strings mapping device responses to
callbacks; a Subscription mechanism; explicit transport objects.

The Crestron model(s): as established by your peers — join-based signals in SIMPL, typed
driver interfaces in CCD.

Produce an honest mapping across the concepts that any device driver must express:
capability/command set, parameters and their types/ranges, addressing (input/output/zone indices),
command string construction, response parsing, state/feedback propagation, polling, connection
lifecycle, error handling, multi-model support within one driver.

For each: 1:1 / mechanical-with-rewrite / needs-human-judgement / no-counterpart. Be specific about
WHERE the models stop being isomorphic — e.g. does Crestron's typed driver taxonomy force a device
into a category that an Extron driver never had to declare? Does the join model require a fixed
capability surface that a free-form command dict does not supply?

Name the top 3 places a naive converter would produce something that looks right and is wrong.`,
  },
  {
    key: 'ir-architecture',
    prompt: `Design the ARCHITECTURE question: should this tool have a manufacturer-neutral
intermediate representation (IR), or do point-to-point converters?

Argue both sides properly. Hub-and-spoke with an IR costs N importers + N exporters and one
carefully-designed core; point-to-point costs N*(N-1) converters but each can be lossless for its
pair and needs no lowest-common-denominator compromise.

Then specify what an IR would actually have to hold to serve Extron ControlScript, Extron .pkp,
and Crestron CCD simultaneously: device identity and models, capability/command set, parameter
types and constraints, wire protocol (command string templates, delimiters, encoding), response
grammar (regex or otherwise), state model, transport/connection config, polling, and metadata
(vendor, version, certification).

Be concrete: sketch the IR schema. Identify precisely where it would LEAK — the things one platform
expresses that the IR would have to either drop or model as an escape hatch. Recommend how to
handle escape hatches (verbatim passthrough? a per-target extension block? refuse to convert?).

Finally: given that the Extron .pkp turned out to EMBED executable Python rather than being purely
declarative, assess whether a declarative IR is even the right centre of gravity, or whether the
tool is really a source-to-source translator with a data sidecar.`,
  },
  {
    key: 'prior-art',
    prompt: `Survey the broader control-system driver landscape and any PRIOR ART in cross-platform
driver conversion — this determines whether the idea is novel, solved, or known-impractical.

Other ecosystems to characterize briefly (format, declarative vs code, openness):
Control4 DriverWorks (.c4z — XML + Lua), AMX NetLinx (.axs/.tko), Q-SYS (Lua plugins),
Savant, Home Assistant integrations, and any open driver-description standards you find
(e.g. anything from AVIXA, or open device-description schemas).

Then search hard for existing attempts: has anyone built a converter between control-system driver
formats? Look for open-source projects, GitHub repos, commercial tools, forum threads where people
asked this exact question, and driver houses (Chowmain, Ultamation, etc.) who ship the same device
driver across multiple platforms — how do THEY do it? Do they maintain a shared internal
representation or hand-write each?

That last question is the most valuable thing you can answer: companies who already ship one device
across Crestron + Control4 + Savant have already solved this problem privately, and how they solved
it is strong evidence about which architecture actually works.`,
  },
  {
    key: 'legal',
    prompt: `Establish the LEGAL and LICENSING constraints on a tool that ingests and emits these
artifacts. Be factual and cite terms; do not give a legal opinion dressed as fact.

Research: Crestron's SDK licence terms and developer agreement; whether the CCD SDK requires
membership in a partner/developer programme; whether Crestron certification is required to
distribute a driver and what that process involves; the terms attached to drivers downloaded from
drivers.crestron.io; whether Crestron module/driver files are themselves licensed artifacts that
may not be reverse-engineered or redistributed.

Do the same, more briefly, for Extron: terms attached to Global Configurator drivers and
ControlScript modules obtained from Extron.

Distinguish clearly between: (a) reading a file you were legitimately given, (b) building a tool
that transforms it, (c) redistributing the input files, (d) distributing the transformed output,
(e) doing any of this commercially. These have materially different risk profiles.

Flag any anti-reverse-engineering clause you actually find, with a quote and URL. If terms are
behind a login and unreadable, say so — that is itself the finding.`,
  },
  {
    key: 'direction-feasibility',
    prompt: `Assess the two directions concretely and separately, and describe what a REAL v1 would do.

CRESTRON-IN (ingest a Crestron module, emit Extron): what would you actually be reading? For a CCD
.pkg, presumably JSON + possibly a compiled DLL — how much of the device's behaviour is recoverable
from the declarative part alone, and what is trapped inside compiled C#? For a SIMPL+ module, is
source usually distributed or only compiled output? Determine how often the useful information is
actually available versus locked in a binary.

CRESTRON-OUT (ingest Extron, emit a Crestron module): what has to be invented that the Extron
source does not supply — driver type/category, join maps, capability declarations, metadata,
certification fields? Can a generated driver be loaded and tested without Crestron's blessing?

For each direction give: a blunt feasible/partly/no verdict, the single hardest blocker, what a
minimum-viable version would actually produce, and how a developer could TEST the output without
owning a processor (emulators, Crestron Toolbox, VirtualControl, any simulator).

Where the answer depends on something gated or unknown, say precisely what file or document would
settle it — the owner may be able to obtain it.`,
  },
]

phase('Research')
log(`Researching ${DIMENSIONS.length} dimensions of the Crestron interop question via Bright Data`)

const researched = await pipeline(
  DIMENSIONS,
  (d) => agent(`${EXTRON_CONTEXT}\n${RULES}\n\nYOUR DIMENSION: ${d.key}\n\n${d.prompt}`, {
    label: `research:${d.key}`,
    phase: 'Research',
    schema: FINDINGS_SCHEMA,
    model: 'sonnet',
    effort: 'high',
  }),
  (result, d) => {
    if (!result) return null
    return agent(
      `${EXTRON_CONTEXT}\n${RULES}\n\nYou are an adversarial verifier for the dimension "${d.key}". ` +
      `Another researcher produced the findings below. Your job is to REFUTE them, not agree.\n\n` +
      `Re-check the cited sources yourself with 'brightdata scrape'. Mark CONFIRMED only if you personally ` +
      `read the claim at the cited URL. Mark REFUTED if the source contradicts it or does not say it. Mark ` +
      `OVERSTATED if it is directionally right but claimed with more certainty than the source supports — ` +
      `pay special attention to forum/blog claims presented as specification, and to claims about signing, ` +
      `certification, gating or licensing, where being wrong is expensive. Mark UNCERTAIN if unreachable.\n\n` +
      `Be especially suspicious of any claim that a format is "open", "documented" or "just JSON" — verify ` +
      `that against a primary source or downgrade it.\n\n` +
      `Also report what the researcher MISSED that changes the picture.\n\n` +
      `Their brief was:\n${d.prompt}\n\nTHEIR FINDINGS:\n${JSON.stringify(result, null, 2)}`,
      { label: `verify:${d.key}`, phase: 'Verify', schema: VERDICT_SCHEMA, model: 'sonnet', effort: 'high' }
    ).then((v) => ({ dimension: d.key, research: result, verification: v }))
  }
)

const dossier = researched.filter(Boolean)
const counts = dossier.reduce((acc, d) => {
  for (const v of (d.verification && d.verification.verified) || []) acc[v.verdict] = (acc[v.verdict] || 0) + 1
  return acc
}, {})
log(`${dossier.length}/${DIMENSIONS.length} dimensions done — ${JSON.stringify(counts)}`)

phase('Synthesize')
const EVIDENCE = JSON.stringify(dossier, null, 2)

const [verdict, critic] = await parallel([
  () => agent(
    `${EXTRON_CONTEXT}\n\nBelow is the verified evidence dossier from 9 research dimensions, each adversarially checked.\n\n` +
    `Write the STRATEGIC ANSWER to: "can this tool take in and spit out Crestron control modules?"\n\n` +
    `Treat REFUTED as false, OVERSTATED as true-but-weaker, UNCERTAIN as unproven. Build only on what survived.\n\n` +
    `Structure:\n` +
    `1. The plain-English answer, up front, in one paragraph. The reader is an AV professional, not a compiler engineer.\n` +
    `2. What a Crestron "module" actually is — because the answer differs sharply by artifact type, and naming the ` +
    `right target is most of the answer.\n` +
    `3. Crestron-IN: verdict, what is recoverable, what is trapped in compiled code.\n` +
    `4. Crestron-OUT: verdict, the hardest blocker, whether output can be loaded and tested at all.\n` +
    `5. The architecture call: intermediate representation or point-to-point, with a firm recommendation and the ` +
    `reasoning. Address whether the embedded-Python discovery on the Extron side changes the centre of gravity.\n` +
    `6. The honest risk list: legal/licensing, gated formats, certification, and effort.\n` +
    `7. What to do NEXT, concretely — including exactly which sample files or documents would most reduce ` +
    `uncertainty, since the owner can likely obtain them.\n\n` +
    `Do not pad. Do not hedge where evidence is clear; do not overclaim where it is not. If the honest answer is ` +
    `"one direction yes, the other probably not worth it", say that plainly. Prose with headings, minimal bullets. ` +
    `Cite URLs inline for load-bearing facts.\n\nDOSSIER:\n${EVIDENCE}`,
    { label: 'verdict:crestron-interop', phase: 'Synthesize', model: 'fable', effort: 'max' }
  ),
  () => agent(
    `${EXTRON_CONTEXT}\n\nBelow is the dossier from 9 research dimensions on Crestron interop.\n\n` +
    `You are the COMPLETENESS CRITIC. Do not summarise. Identify: what remains unanswered; which claims survived ` +
    `only because nobody could check them; which primary sources were never read because they are behind a login; ` +
    `which Crestron artifact types were named but never actually examined; and where two dimensions CONTRADICT ` +
    `each other.\n\n` +
    `Then produce a prioritised acquisition list: the specific files, SDK downloads, documents or accounts that ` +
    `would most change the verdict, ranked by how much uncertainty each removes per unit of effort to obtain.\n\n` +
    `Be blunt. An overconfident verdict here would send the owner down a months-long path.\n\nDOSSIER:\n${EVIDENCE}`,
    { label: 'completeness-critic', phase: 'Synthesize', model: 'sonnet', effort: 'high' }
  ),
])

return {
  dimensionsResearched: dossier.length,
  verdictCounts: counts,
  dossier,
  verdict,
  completenessCritic: critic,
}
