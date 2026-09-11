export const meta = {
  name: 'pack-up-extron-project',
  description: 'Extract every unfinished/planned item for extron-driver-convert and sweep C: for missed project files',
  phases: [
    { title: 'Backlog', detail: 'parallel readers over findings, status, experiments, transcripts' },
    { title: 'Sweep', detail: 'find project files on C: not already inventoried' },
    { title: 'Critique', detail: 'completeness critic over the merged backlog' },
    { title: 'Synthesize', detail: 'draft ROADMAP.md, verifying each status claim against the repo' },
  ],
}

const REPO_WIN = 'Z:\\GitHub\\rob-paprocki\\extron-driver-convert'
const REPO_SH = '/z/GitHub/rob-paprocki/extron-driver-convert'

const PREAMBLE = `You are helping hand off the research repo at ${REPO_WIN} (Git Bash path ${REPO_SH}).
It converts AV device drivers between Extron .pkp (Global Configurator), Extron ControlScript .py and Crestron .pkg.
Read STATUS.md and CLAUDE.md in that repo first for orientation.

THIS IS A READ-ONLY TASK. Do not edit, create, move or delete any file. Do not run git commands that change state.
Never reproduce any credential, password or token-like string (gho_/ghp_/github_pat_ etc.) in your output - if you see one, say only that it exists and where.

Your job: find every piece of work that was planned, promised, offered, deferred, or left open but NOT completed. That includes:
- explicit open items and "Open" lists
- "What this does NOT show" limitations that imply a concrete next experiment
- anything the user deferred ("another day", "later")
- offers made to the user that were never taken up or answered
- pending hardware tests (build, upload, control, connecting to a camera)
- TODO / FIXME / XXX in code, and anything labelled hypothesis, unmeasured, guess, or untried
- requests the user made that were only partly satisfied
Before calling an item not-started, CHECK THE REPO (grep for the tool, file or command) so you do not report finished work as open.
Be exhaustive: a missed item is worse than a duplicate - the orchestrator dedups.`

const ITEM = {
  type: 'object',
  properties: {
    title: { type: 'string', description: 'short imperative title' },
    area: { type: 'string', description: 'e.g. i20 pkp, p20, ControlScript, validator, IR/.eir, Crestron pkg, oracle pairs, harness, docs' },
    status: { type: 'string', enum: ['not-started', 'partial', 'blocked', 'done-but-unverified'] },
    blocked_by: { type: 'string', enum: ['user-hardware', 'user-decision', 'user-credentials', 'gcp-licence', 'crestron-processor', 'nothing'] },
    evidence: { type: 'string', description: 'file path + line, or a short quote with its source' },
    detail: { type: 'string' },
    next_step: { type: 'string', description: 'the first concrete action someone would take' },
    effort: { type: 'string', enum: ['S', 'M', 'L'] },
  },
  required: ['title', 'area', 'status', 'blocked_by', 'evidence', 'detail', 'next_step', 'effort'],
}
const BACKLOG = { type: 'object', properties: { items: { type: 'array', items: ITEM } }, required: ['items'] }

const FILE = {
  type: 'object',
  properties: {
    path: { type: 'string' },
    size_bytes: { type: 'number' },
    why_related: { type: 'string' },
    recommend: { type: 'string', enum: ['include', 'exclude', 'ask'] },
    reason: { type: 'string' },
    sensitive: { type: 'boolean', description: 'true if it may hold credentials, licence keys, or account data' },
  },
  required: ['path', 'why_related', 'recommend', 'reason', 'sensitive'],
}
const SWEEP = { type: 'object', properties: { files: { type: 'array', items: FILE } }, required: ['files'] }

const known = (args && args.known) ? args.known.join('\n') : ''

const READERS = [
  { key: 'findings-early', scope: `Read findings/01 through findings/09 in full, every file under notes/, and README.md.` },
  { key: 'findings-late', scope: `Read findings/10 through findings/18 in full, and skim tools/out/verdicts/ (multi-agent synthesis documents the findings were written from).` },
  { key: 'code-and-experiments', scope: `Read STATUS.md and CLAUDE.md in full, then every README/PROTOCOL/markdown file and every module docstring under experiments/ and tools/. Grep all .py files for TODO, FIXME, XXX, "not yet", "untested", "unmeasured", "guess", "hypothesis", "What this does NOT". Pay special attention to experiments/skeleton_i20/ (PROTOCOL.md, build_i20*.py) and experiments/oracle_pairs/.` },
  { key: 'transcript-current', scope: `Mine the current session transcript: C:\\Users\\robp\\.claude\\projects\\Z--GitHub-rob-paprocki\\a721b700-8885-4d73-a123-0f6578ca8e4c.jsonl (Git Bash: /c/Users/robp/.claude/projects/Z--GitHub-rob-paprocki/a721b700-8885-4d73-a123-0f6578ca8e4c.jsonl). It is 11 MB of JSONL - DO NOT read it whole. Use grep with context. First extract every genuine USER message (records with "type":"user" whose content is text, not a tool_result) and list what each asked for; then check which were fully satisfied. Then grep assistant text for: "next", "later", "not yet", "TODO", "deferred", "another day", "want me to", "Say the word", "I can", "offer", "still need", "remaining", "untested", "unproven", "p20", "IR", ".eir", "Build", "upload", "licence", "hardware", "Crestron processor", "VC-4".` },
  { key: 'transcript-older', scope: `Mine the older sessions of this project. (a) C:\\Users\\robp\\.claude\\projects\\Z--GitHub-rob-paprocki\\2141be6e-3b63-4e23-acc6-a96522f56910.jsonl (Git Bash /c/Users/robp/.claude/projects/Z--GitHub-rob-paprocki/2141be6e-3b63-4e23-acc6-a96522f56910.jsonl, 2.3 MB). (b) the original session 22114bf1 under Z:\\.claude\\projects - list with: ls /z/.claude/projects/*/22114bf1* and also check /z/.claude/projects/-Users-robp-GitHub-rob-paprocki/22114bf1-2854-52e0-8085-edc584e49feb.jsonl and any subdirectory of that name. Do NOT read whole files; grep with context. Extract every genuine USER request and every plan/offer/deferral, then check against the current repo whether it was since completed.` },
]

const SWEEPERS = [
  { key: 'by-name-content', prompt: `${PREAMBLE}

A different job for you: SWEEP THE C: DRIVE for files belonging to this project that have not already been inventoried. The user wants every project artifact on C: moved into the repo on Z:.

Already inventoried (do not re-report these or anything under them):
${known}

Search C:\\Users\\robp, C:\\Users\\Public and C:\\ProgramData (Git Bash: /c/Users/robp, /c/Users/Public, /c/ProgramData). Skip browser caches, AppData\\Local\\Packages, AppData\\Local\\Temp noise older than 2026-09-06, .vscode extension internals, node_modules, and Windows system files.
Look for: *.pkp, *.eir, *.gcpro, *.gcp, *.pkg (Crestron), *.cmc, *.umc, *.csp, *.clz, *.lpz, *.vsix, *.dat catalogue files, *.py / *.ps1 / *.sh / *.md / *.json / *.txt mentioning extron, crestron, 1bynd, visca, pkp, controlscript, i20 or p20, screenshots of Global Configurator, and zip/7z archives.
For anything inside C:\\Program Files or C:\\Program Files (x86): report it only if it is user-created project data, not part of a vendor application install.
Report each file with a recommendation. Use find with -newermt and -iname; be efficient but thorough.` },
  { key: 'by-time-appdata', prompt: `${PREAMBLE}

A different job for you: SWEEP THE C: DRIVE BY TIME AND BY APPLICATION DATA for files belonging to this project that have not already been inventoried.

Already inventoried (do not re-report these or anything under them):
${known}

1. List files modified between 2026-09-06 and 2026-09-11 under C:\\Users\\robp, C:\\Users\\Public and C:\\ProgramData (Git Bash: find /c/Users/robp /c/Users/Public /c/ProgramData -type f -newermt 2026-09-06 ! -newermt 2026-09-12). Filter out caches, browser data, Windows/Defender noise, .vscode internals and package caches. Keep only what plausibly relates to Extron / Crestron / this repo.
2. Enumerate these application-data locations in full and classify every file: C:\\Users\\robp\\AppData\\Roaming\\Extron, C:\\Users\\robp\\AppData\\Roaming\\@extron, C:\\Users\\robp\\AppData\\Local\\Extron, C:\\ProgramData\\Extron, C:\\Users\\robp\\AppData\\Roaming\\Crestron, C:\\Users\\robp\\AppData\\Local\\Crestron, C:\\ProgramData\\Crestron. Classes: project data / application settings / logs / credential-or-licence material / cache. For credential or licence material: flag sensitive=true and recommend exclude - NEVER print the secret value.
3. Also check C:\\Users\\robp\\.claude for anything else belonging to this project beyond what is inventoried (other job dirs, file-history, todos, plans).` },
]

phase('Backlog')
const readerThunks = READERS.map(r => () => agent(`${PREAMBLE}\n\nYOUR SCOPE (${r.key}): ${r.scope}`, { label: `backlog:${r.key}`, phase: 'Backlog', schema: BACKLOG }))
const sweepThunks = SWEEPERS.map(s => () => agent(s.prompt, { label: `sweep:${s.key}`, phase: 'Sweep', schema: SWEEP }))

const all = await parallel([...readerThunks, ...sweepThunks])
const readerOut = all.slice(0, READERS.length)
const sweepOut = all.slice(READERS.length)

const items = []
readerOut.forEach((r, i) => {
  if (!r) { log(`reader ${READERS[i].key} returned nothing`); return }
  r.items.forEach(it => items.push({ ...it, source_reader: READERS[i].key }))
})
const swept = []
sweepOut.forEach((s, i) => {
  if (!s) { log(`sweeper ${SWEEPERS[i].key} returned nothing`); return }
  s.files.forEach(f => swept.push({ ...f, sweeper: SWEEPERS[i].key }))
})
log(`${items.length} backlog items from ${readerOut.filter(Boolean).length} readers; ${swept.length} candidate files from the C: sweep`)

phase('Critique')
const CRITIC = {
  type: 'object',
  properties: {
    additional: { type: 'array', items: ITEM },
    corrections: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, issue: { type: 'string' }, evidence: { type: 'string' } }, required: ['title', 'issue', 'evidence'] } },
  },
  required: ['additional', 'corrections'],
}
const critique = await agent(`${PREAMBLE}

You are the COMPLETENESS CRITIC. Below is the merged backlog several readers extracted. Your job:
1. Find what is MISSING. Think about the project's whole arc: Crestron .pkg -> ControlScript, .pkp -> ControlScript (pkp2cs), ControlScript -> .pkp (transplant + asset synthesis), the i20 and p20 drivers, the validator, IR/.eir, the oracle-pairs scorecard, finding 10's pending write-up, the Ross/Ultrix natural experiment, the GCP automation harness, Crestron-side loading, licensing questions, the GCP licence expiry, and the hand-off itself (a new machine needs to reproduce the Windows-box setup). Read STATUS.md and findings/18 to check.
2. Find items whose STATUS IS WRONG - marked open but actually done, or vice versa. Verify against the repo with grep before claiming.

Merged backlog (JSON):
${JSON.stringify(items, null, 1)}`, { label: 'critic', phase: 'Critique', schema: CRITIC })

const finalItems = items.concat(critique ? critique.additional.map(a => ({ ...a, source_reader: 'critic' })) : [])

phase('Synthesize')
const roadmap = await agent(`${PREAMBLE}

Write the hand-off ROADMAP.md for this repo from the backlog below. Before writing any status claim, VERIFY it against the repo (grep/ls) - do not trust the backlog blindly; the critic's corrections list flags known problems.

Dedup aggressively: the same item arrives from several readers. Merge them, keep the best evidence.

Structure (markdown, concise, table-heavy where it helps, no fluff):
# Roadmap
One short paragraph: where the project stands and what "done" currently means.
## 1. Needs the user's hardware   (ordered cheapest-failure-first; each with exact steps and what to look for)
## 2. Can be done from the repo, no hardware   (ordered by value)
## 3. Needs a decision or credentials from the user
## 4. Deferred by the user   (e.g. IR/.eir)
## 5. Open research questions and unmeasured claims
## 6. Clocks and machine-bound constraints   (GCP licence expiry ~2026-10-07; what only the Windows box can do; how to rebuild that box)
For every item: what, why it matters, blocked by, first concrete step, evidence (finding number or file path). Mark effort S/M/L.
Do not invent work that has no evidence. Do not include credentials.

Critic corrections:
${JSON.stringify(critique ? critique.corrections : [], null, 1)}

Backlog (JSON):
${JSON.stringify(finalItems, null, 1)}`, { label: 'synthesize-roadmap', phase: 'Synthesize', schema: { type: 'object', properties: { markdown: { type: 'string' } }, required: ['markdown'] } })

return {
  roadmap_markdown: roadmap ? roadmap.markdown : null,
  item_count: finalItems.length,
  corrections: critique ? critique.corrections : [],
  swept_files: swept,
}
