export const meta = {
  name: 'nextgen-camera-docs-harvest',
  description: 'Harvest the full Crestron NextGen Cameras documentation set for the i12/i20/p12/p20',
  phases: [
    { title: 'Harvest', detail: 'crawl and save docs.crestron.com area 9440' },
    { title: 'Assess', detail: 'what the full set adds that the VISCA command page alone did not' },
  ],
}

const R = '/Users/robp/GitHub/rob-paprocki/extron-driver-convert'
const ROOT = 'https://docs.crestron.com/en-us/9440/Content/Topics/Home.htm'

const GROUND = `
PROJECT: ${R}. The owner supplied the FULL public documentation set for the Crestron 1 Beyond
NextGen cameras (IV-CAM-I12/I20, IV-CAM-P12/P20): ${ROOT}

WHY THIS MATTERS. We hold two real Crestron driver packages for these cameras:
  "${R}/samples/Crestron 1 Beyond IV-CAM-i12_i20/Crestron/Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg"
  "${R}/samples/Crestron 1 Beyond IV-CAM-p12_p20/Crestron/Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg"
Extract either with 'python3 ${R}/tools/pkg_dump.py <path>' or by importing pkg_dump and calling
process_pkg(path) -> dict with 'driver_definition'.

They are Crestron SDK V2 (Entity Model) drivers whose behaviour is almost entirely declarative
JSON, EXCEPT for a handful of Transformations their own Rules invoke but never define. Those exist
only as compiled IL:
  ViscaAssemble2LowerNibbles (I20 only), ZoomLevelToPosition, ZoomPositionToLevel,
  ApplyZoomPositionStep, FormatRomVersion, ParseDecimal
A separate experiment is trying to reconstruct these from Crestron's VISCA command reference
(already harvested to ${R}/reference/crestron-visca/) WITHOUT decompiling the IL.

The likeliest weak point of that experiment is the ZOOM family: a command reference gives byte
formats, but ZoomLevelToPosition needs the camera's actual zoom POSITION RANGE, its level scale,
optical/digital boundaries, and any step behaviour — data that typically lives in configuration,
specification or web-interface pages rather than in a protocol command list. This harvest exists to
find that data.

RULES:
- Web access ONLY via the Bright Data CLI: 'brightdata scrape <url>', 'brightdata search "q"'.
  Never WebFetch/WebSearch, never curl to target sites — the owner's home IP must not be used for
  crawling. Report failures; do not fall back to another method.
- Do NOT decompile driver IL. Reading metadata names/attributes is fine.
- Cite the URL for every claim. Never fabricate documentation content. If a page is unreachable,
  list it as missing.
- NEVER submit placeholder or test content.
- FILE WRITES: only under ${R}/reference/crestron-nextgen-cameras/. Do NOT write under
  ${R}/tools/ or ${R}/reference/crestron-visca/ — other work owns those.
`

phase('Harvest')
log('Crawling docs.crestron.com area 9440 (NextGen Cameras)')

const harvest = await agent(
  `${GROUND}\n\nYOUR TASK: harvest the complete NextGen Cameras documentation set starting at
${ROOT}, and save it under ${R}/reference/crestron-nextgen-cameras/.

Enumerate pages by scraping the root and following its in-page links, plus
'brightdata search "site:docs.crestron.com 9440 <term>"' with varied terms. MadCap Flare TOC JSON
paths tend to 404 on this host, so do not rely on them. Keep going until repeated searches surface
nothing new, and say what convergence signal you used.

Save each page as markdown, mirroring the site's topic folders, each file starting with a
'Source: <url>' line. Write an INDEX.md listing every page and its URL.

Then write three focused digests, because these are what the rest of the project needs:

1. ZOOM.md — EVERYTHING about zoom: position ranges and their units, zoom level vs zoom position,
   optical vs digital boundaries, field-of-view relationships, step behaviour, any table or
   formula, and any worked example. Quote verbatim with the source URL. This is the highest-value
   output of the whole harvest; if the data exists anywhere in the set, find it.

2. MODELS.md — the model lineup and what differs between I12/I20 and P12/P20: sensor, optical zoom
   range, PTZ vs fixed, auto-tracking features, and anything explaining why the I20 driver has a
   ViscaAssemble2LowerNibbles transformation the P20 driver lacks.

3. CONTROL.md — every control surface documented: VISCA over IP and its port, any REST/HTTP API,
   the web interface, Crestron Home integration, and any authentication or pairing requirement.
   Note anything the cameras expose that a driver could use but the two shipped drivers do not.

Report: pages fetched, pages that failed, whether the set covers the I20 and P20 specifically, and
a blunt assessment of whether ZOOM.md actually contains the numbers needed to pin down
ZoomLevelToPosition — say plainly if it does not.`,
  { label: 'harvest:nextgen-cameras', phase: 'Harvest', model: 'sonnet', effort: 'high' }
)

phase('Assess')
const assessment = await agent(
  `${GROUND}\n\nThe full documentation set has been harvested to ${R}/reference/crestron-nextgen-cameras/.
Harvest report:\n\n${harvest}\n\n---\n\nYOUR TASK: assess what this fuller set adds, and re-attempt
the zoom reconstruction specifically.

1. Read the harvested docs, especially ZOOM.md, MODELS.md and CONTROL.md.
2. Extract both camera drivers' JSON with pkg_dump. Find every Rule and Command that invokes
   ZoomLevelToPosition, ZoomPositionToLevel or ApplyZoomPositionStep. Establish precisely what
   input each receives and what its output feeds into — the surrounding declarative data constrains
   these transformations even though their bodies are compiled.
3. Using ONLY the documentation plus that declarative context, attempt to specify each of the three
   zoom transformations: a precise natural-language definition plus a reference Python
   implementation.
4. TEST each reconstruction against the drivers' own data — if a Command template shows literal
   bytes around the transformation's output, your implementation must produce something consistent
   with them. Show the worked check.
5. Rate each: CONFIDENT (docs plus JSON pin it exactly), PLAUSIBLE (consistent but
   under-determined), or FAILED. Prefer PLAUSIBLE over CONFIDENT wherever an alternative
   implementation would fit the same evidence — actively try to construct such an alternative, and
   if you succeed, that is a downgrade.

A reconstruction that looks right and is wrong would make a driver send subtly incorrect bytes,
which is this project's worst failure mode. An honest FAILED with a clear statement of what would
settle it is a better result than a confident guess.

Also state whether the fuller documentation set changes the earlier finding that documentation
cannot substitute for a shipped driver, or reinforces it.

Prose with headings, cite URLs and JSON paths, no padding.`,
  { label: 'assess:zoom-reconstruction', phase: 'Assess', model: 'opus', effort: 'high' }
)

return { harvest, assessment }
