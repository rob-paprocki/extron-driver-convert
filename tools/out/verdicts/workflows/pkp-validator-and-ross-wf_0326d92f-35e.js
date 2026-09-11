export const meta = {
  name: 'pkp-validator-and-ross',
  description: 'Reimplement Extron\'s driver validator in pure Python and analyse a hand-authored ControlScript module set',
  phases: [
    { title: 'Decode' },
    { title: 'Ross' },
    { title: 'Implement' },
    { title: 'Verify' },
  ],
}

const REPO = 'Z:\\GitHub\\rob-paprocki\\extron-driver-convert'
const GCP = 'C:\\Program Files (x86)\\Extron\\GCP'

const CONTEXT = `
CONTEXT — repo: ${REPO} (read CLAUDE.md and STATUS.md first; standard-library Python only, no deps).

Extron Global Configurator validates a .pkp before use:
  Extron.Configuration.Drivers.DriverAssetValidator.Validate(IDriverFileAsset) -> ErrorCode
  enum ErrorCode { Valid = 0, MismatchHash = 80085, NoHash_NoGuid = 80086 }
GC shows "Invalid Driver ... Error Code: 80085" when it fails.

Already MEASURED by the main session (do not re-derive, but DO challenge if you find contradicting evidence):
 - DriverFileAsset._resourceHashDict is Dictionary<string, byte[]>: resource key -> 32-byte digest.
   Its NRBF shape is {Version, Comparer, HashSize, KeyValuePairs}; KeyValuePairs is a BinaryArray of
   KeyValuePair<string,byte[]> entries with members "key" and "value".
 - The digest is plain SHA-256 over the resource bytes. Verified: sha256(donor script utf-8 bytes)
   == the stored digest cc80101d367ad0d13162ed0daee29b580155543d2fcd22449fa583a0d0505eb3.
 - ComputeHash's IL constructs SHA256CryptoServiceProvider and calls ComputeHash(stream).
 - Packages carry a hash per resource: the embedded .py AND the comm-sheet .pdf.
 - The .pdf hash cannot currently be checked from the object graph alone (the pdf is a separate
   resource) - determine whether it is embedded in the package or external. This matters.

Tools already in the repo:
 - tools/pkp_dump.py     NRBF reader (PkpParser, load_bytes). Parses all 1853 shipping packages, 0 errors.
 - tools/pkp_build.py    transplant builder; has resource_hashes() and refresh_resource_hash().
 - experiments/nrbf_writeback/nrbf_write.py  NRBF writer.
Run python as: python (it is on PATH).
`

const IL = `
DriverAssetValidator.Validate — IL 234 bytes, maxstack 3, locals:
  local[0] IEnumerator\`1   local[1] IResourceAsset   local[2] Byte[]   local[3] ErrorCode
IL bytes (hex):
03 3A B8 00 00 00 38 A8 00 00 00 38 86 00 00 00 02 7B 23 00 00 04 07 6F F4 00 00 0A 6F FB 00 00 0A
08 28 1B 00 00 2B 2D 6D 2B 5B 06 6F F6 00 00 0A 0B 07 6F 99 00 00 0A 0C 03 6F FD 00 00 0A 07 6F 85
00 00 0A 6F 97 00 00 0A 2C 25 2B 00 03 6F FD 00 00 0A 07 6F 85 00 00 0A 6F FE 00 00 0A 08 28 1B 00
00 2B 2D 2F 2B 00 20 D5 38 01 00 0D DE 77 02 7B 23 00 00 04 07 6F F4 00 00 0A 6F F7 00 00 0A 2C 0A
2B 8A 20 D5 38 01 00 0D DE 5A 20 D6 38 01 00 0D DE 52 06 6F 60 00 00 0A 3A 8A FF FF FF 2B 00 DE 41
06 2C 0A 2B 00 06 6F 2E 00 00 0A 2B 00 DC 72 5C 06 00 70 73 FF 00 00 0A 7A 03 6F 86 00 00 0A 72 9C
06 00 70 19 6F 00 01 00 0A 2C 04 2B 00 16 2A 03 6F 8B 00 00 0A 6F F3 00 00 0A 0A 38 25 FF FF FF 16 2A 09 2A

ComputeHash — IL 49 bytes, locals: local[0] Byte[]  local[1] SHA256CryptoServiceProvider
14 0A 2B 00 73 F8 00 00 0A 0B 2B 00 07 03 6F F9 00 00 0A 0A 07 6F FA 00 00 0A DE 0E 07 2C 0A 2B 00
07 6F 2E 00 00 0A 2B 00 DC DE 03 26 FE 1A 06 2A

Note 0x000138D5 = 80085 and 0x000138D6 = 80086 appear as ldc.i4 operands.
You may inspect the assembly yourself with 32-bit Windows PowerShell:
  & "C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -File <script.ps1>
loading ${GCP}\\Extron.Configuration.Drivers.dll via [Reflection.Assembly]::LoadFrom.
Resolve metadata tokens (0x0A000xxx = MemberRef, 0x04000023 = Field) via Module.ResolveMember to name
the actual calls rather than guessing. That is the difference between a spec and a story.
`

const SPEC_SCHEMA = {
  type: 'object',
  properties: {
    pseudocode: { type: 'string', description: 'Faithful pseudocode of Validate(), control flow exact' },
    resolved_calls: { type: 'array', items: { type: 'string' },
      description: 'metadata token -> resolved member name, one per line, for every call site you resolved' },
    returns_valid_when: { type: 'string' },
    returns_mismatchhash_when: { type: 'string' },
    returns_nohash_noguid_when: { type: 'string' },
    which_resources_are_hashed: { type: 'string',
      description: 'Exactly which resources are iterated and hashed, and any filtering (e.g. extension checks)' },
    string_literals: { type: 'array', items: { type: 'string' },
      description: 'ldstr literals referenced by the method, resolved' },
    uncertainties: { type: 'array', items: { type: 'string' },
      description: 'Anything you could NOT resolve. Be explicit; do not paper over.' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['pseudocode', 'returns_valid_when', 'returns_mismatchhash_when',
             'returns_nohash_noguid_when', 'which_resources_are_hashed', 'uncertainties', 'confidence'],
}

phase('Decode')
const decodes = await parallel([0, 1, 2].map(i => () => agent(
  `${CONTEXT}\n${IL}\n\nTASK: decode DriverAssetValidator.Validate into faithful pseudocode.\n` +
  `Resolve the metadata tokens to real member names using reflection (Module.ResolveMember /\n` +
  `ResolveString) rather than inferring from opcode shape. State precisely under which conditions\n` +
  `each of the three ErrorCode values is returned, and exactly which resources get hashed —\n` +
  `note the ldstr + EndsWith-looking sequence near the end, it may filter by file extension.\n` +
  `Attempt ${i + 1} of 3, independent — do not assume the other attempts exist.\n` +
  `Report what you could not resolve in 'uncertainties'. An honest gap beats a confident guess.`,
  { label: `decode-il-${i + 1}`, phase: 'Decode', schema: SPEC_SCHEMA, effort: 'high' })))

const ROSS_FILES = [
  { f: 'mod_ross_matrix_RossTalk_v1_1_0_0.py', what: 'hand-authored ControlScript device module (RossTalk protocol)' },
  { f: 'mod_ross_matrix_tsl_3_1_v1_1_0_0.py', what: 'hand-authored ControlScript device module (TSL 3.1 protocol)' },
  { f: 'plugin_ross_ultrix.py', what: 'a plugin/translation layer above the two device modules' },
  { f: 'tools.py', what: 'a ~398KB shared framework the programmer wrote (36 top-level classes/functions)' },
]

phase('Ross')
const ross = await parallel(ROSS_FILES.map(r => () => agent(
  `${CONTEXT}\n\nTASK: analyse samples/Custom Module/${r.f} — ${r.what}.\n\n` +
  `This material is NEW to the repo: modules a third-party programmer hand-wrote for Ross Ultrix,\n` +
  `a device Extron does not ship a driver for. Every other ControlScript module in this repo was\n` +
  `generated by Extron's own tooling. So this is the first evidence of what a HUMAN writes when\n` +
  `targeting an unsupported API, and the project's live question is exactly that: how to author a\n` +
  `driver for hardware the vendor does not support (see findings/13, the Crestron 1 Beyond i20).\n\n` +
  `Answer concretely, with line references:\n` +
  ` 1. Structure vs Extron's generated modules (DeviceClass, self.Commands, __SetHelper/__UpdateHelper,\n` +
  `    SubscribeStatus/NewStatus/WriteStatus/ReadStatus, the three transport classes). What conforms,\n` +
  `    what deviates, and does any deviation look deliberate rather than sloppy?\n` +
  ` 2. What does the author do that Extron's generator does NOT, and vice versa?\n` +
  ` 3. Does tools/wire_table.py extract a wire table from it? RUN IT:\n` +
  `      python -c "import sys; sys.path.insert(0,'tools'); import wire_table; ` +
  `t=wire_table.extract_table(open(r'samples/Custom Module/${r.f}',encoding='utf-8').read(),'${r.f}'); ` +
  `print(len(t.commands), sorted(t.commands))"\n` +
  `    If it fails or under-extracts, say exactly how. Our oracle has only ever been run on\n` +
  `    machine-generated modules; this is its first hand-written input.\n` +
  ` 4. Anything reusable for authoring the i20 driver, or that contradicts our assumptions.\n` +
  `For tools.py, do NOT read all 398KB — map its top-level classes and report what the framework\n` +
  `provides, then read only what matters.\n\n` +
  `Return prose with concrete file:line citations. No summary padding.`,
  { label: `ross:${r.f.replace(/\.py$/, '')}`, phase: 'Ross', effort: 'high' })))

phase('Implement')
const spec = decodes.filter(Boolean)
const implementation = await agent(
  `${CONTEXT}\n\nThree independent decodes of DriverAssetValidator.Validate:\n\n` +
  spec.map((s, i) => `--- decode ${i + 1} (confidence: ${s.confidence}) ---\n` +
    `pseudocode:\n${s.pseudocode}\n` +
    `Valid when: ${s.returns_valid_when}\n` +
    `MismatchHash when: ${s.returns_mismatchhash_when}\n` +
    `NoHash_NoGuid when: ${s.returns_nohash_noguid_when}\n` +
    `resources hashed: ${s.which_resources_are_hashed}\n` +
    `uncertainties: ${(s.uncertainties || []).join('; ')}\n`).join('\n') +
  `\n\nTASK: write tools/pkp_validate.py — a PURE PYTHON (standard library only) reimplementation of\n` +
  `Extron's validator, so this repo can check a package on any machine WITHOUT Global Configurator\n` +
  `installed. That is the whole point: GC is Windows-only and licensed; the repo is cloud-first.\n\n` +
  `Requirements:\n` +
  ` - Reuse tools/pkp_dump.py to parse; do not write a second NRBF reader.\n` +
  ` - Public API: validate(path_or_bytes) -> Result with .code (int), .name (str), .details.\n` +
  `   Mirror Extron's enum exactly: Valid=0, MismatchHash=80085, NoHash_NoGuid=80086.\n` +
  ` - CLI: python tools/pkp_validate.py FILE... printing one line per package, non-zero exit if any invalid.\n` +
  ` - Where the three decodes DISAGREE, or a decode listed an uncertainty, implement the behaviour you\n` +
  `   can justify from evidence and record the disagreement in a module-level comment. Do NOT silently\n` +
  `   pick one. This repo's standing rule: a plausible guess is worse than a recorded gap.\n` +
  ` - Handle the .pdf resource honestly: if its bytes are not in the package, you cannot verify its\n` +
  `   hash — say so in the Result rather than pretending it passed.\n\n` +
  `Also write tools/test_pkp_validate.py in the SAME style as tools/test_pkp_build.py (plain script,\n` +
  `no pytest, prints "N passed, M failed"). It must cover: every sample package validates Valid;\n` +
  `a script mutated WITHOUT a hash refresh returns MismatchHash; the same mutation WITH\n` +
  `pkp_build.refresh_resource_hash returns Valid; and a truncated/garbage input fails loudly rather\n` +
  `than returning Valid.\n\n` +
  `Run both files before you finish. Report the final test output verbatim.`,
  { label: 'write-pkp-validate', phase: 'Implement', effort: 'high' })

phase('Verify')
const checks = [
  ['differential', `Differentially test tools/pkp_validate.py against Extron's REAL validator over a large sample.\n` +
    `Extron's validator, via 32-bit Windows PowerShell (the DLL is x86 .NET Framework):\n` +
    `  [Reflection.Assembly]::LoadFrom("${GCP}\\Extron.Configuration.Contracts.dll")\n` +
    `  [Reflection.Assembly]::LoadFrom("${GCP}\\Extron.Configuration.Core.dll")\n` +
    `  $asm=[Reflection.Assembly]::LoadFrom("${GCP}\\Extron.Configuration.Drivers.dll")\n` +
    `  DriverFileAsset.LoadFromFile(string) then DriverAssetValidator.Instance.Validate(asset)\n` +
    `  (marshal args as explicit object[] with [string] casts, or PowerShell boxes them and Invoke throws)\n` +
    `Run BOTH validators over at least 300 packages from C:\\Users\\Public\\Documents\\extron\\Driver3\n` +
    `plus every .pkp under ${REPO}\\samples and ${REPO}\\experiments\\skeleton_i20\\out.\n` +
    `Report: total compared, exact agreements, and EVERY disagreement with the package name and both\n` +
    `verdicts. A disagreement is the most valuable thing you can find - hunt for one.`],
  ['adversarial', `Adversarially review tools/pkp_validate.py. Try to REFUTE that it faithfully reimplements\n` +
    `Extron's validator. Specifically hunt for: a package it calls Valid that Extron would reject;\n` +
    `reliance on a field that is absent in some real packages; mishandling of the .pdf resource;\n` +
    `an exception path that returns Valid by accident; and any case where it silently guesses rather\n` +
    `than recording a gap. Construct concrete counterexample packages with tools/pkp_build.py and\n` +
    `TEST them against both validators. Report each attempted refutation and whether it succeeded.`],
  ['integration', `Check that tools/pkp_validate.py is genuinely usable without Global Configurator, which is\n` +
    `its entire purpose. Verify: standard library only (no imports outside stdlib + repo modules);\n` +
    `no path under "Program Files" or any GC-installed file referenced at runtime; works from a\n` +
    `different working directory; the CLI exits non-zero on an invalid package. Then run the repo's\n` +
    `whole existing suite (tools/test_pkp2cs.py, test_wire_table.py, test_pkg_dump.py,\n` +
    `test_pkp_build.py, experiments/nrbf_writeback/test_nrbf_write.py,\n` +
    `experiments/crestron2cs/test_crestron2cs.py, experiments/skeleton_i20/test_i20_wire.py,\n` +
    `experiments/skeleton_i20/test_i20_cs_wire.py) and confirm nothing regressed. Report each\n` +
    `suite's final line verbatim.`],
]
const verdicts = await parallel(checks.map(([label, task]) => () => agent(
  `${CONTEXT}\n\nThe implementer reported:\n${String(implementation).slice(0, 3000)}\n\nTASK: ${task}`,
  { label: `verify:${label}`, phase: 'Verify', effort: 'high' })))

return {
  decodes: spec.map(s => ({ confidence: s.confidence, uncertainties: s.uncertainties })),
  implementation: String(implementation).slice(0, 4000),
  verdicts: verdicts.filter(Boolean).map(String),
  ross: ross.filter(Boolean).map(String),
}
