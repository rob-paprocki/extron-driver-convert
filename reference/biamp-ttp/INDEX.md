# Biamp Tesira Text Protocol reference — index

*(2026-09-24: the harvested pages this index lists are the vendor's text and are no longer tracked. This index, its source URLs and our analyses stay, so any page can be fetched again; `vendor-files.manifest.tsv` pins the copies the findings used.)*

## Enumeration method (not keyword search, not filename guessing)

The first source URL supplied,
`https://tesira-software-help.biamp.com/#t=assets%2FTOC%2FSystem_Control%2FTesira_Text_Protocol%2FTTP_Syntax.htm`,
is a MindTouch/Adobe RoboHelp "Responsive HTML5" (RoboHelp 2022, per the page's own
`<meta name="generator">`) frameset app: the `#t=` fragment is a client-side router argument,
never sent to the server, so fetching the URL verbatim only returns the shell page.

Steps actually taken:

1. Fetched `https://tesira-software-help.biamp.com/` and its `whxdata/projectsettings.js` to
   confirm the platform (RoboHelp 2022 responsive WebHelp) and the real per-topic path pattern:
   topics live at `https://tesira-software-help.biamp.com/<relUrl>`, e.g.
   `assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Syntax.htm` — confirming the fragment in
   the supplied URL is exactly the relative topic path RoboHelp uses internally.
2. Grepped the shell's own JS bundles (`template/scripts/{rh,common,layout,layoutwidgets}.min.js`)
   for the data-file URLs the client fetches to build its TOC/search index, rather than guessing.
   `layout.min.js` referenced `whxdata/toc.new.js` (top-level TOC stub only — 4 top books, no
   children, so not useful for full enumeration) and `common.min.js` referenced
   `whxdata/search_topics.js`.
3. `whxdata/search_topics.js` is the project's **published full-text-search metadata index**: a
   JSON blob (wrapped in `rh._.exports("...")`, escaped once) with a `metadata` map keyed `"0"`
   through `"272"`, one entry per topic in the entire help system, each with `title`, `relUrl`
   (the fetchable path) and `relTOCPath` (its full TOC breadcrumb, e.g.
   `["System Control", "Tesira Text Protocol", "TTP Syntax"]`). This is exactly the "published
   index" the task asked to look for — saved at `data/all_topics.json` (273 topics total).
4. Filtered that index for `relTOCPath` containing `"Tesira Text Protocol"` to get the exhaustive
   list of pages in that TOC section — 8 pages, listed below. This is a structural enumeration
   from the site's own manifest, not a keyword search and not an assumption extrapolated from
   one sample filename.
5. For the second supplied URL (the command string calculator at
   `support.biamp.com/Tesira/Control/Tesira_command_string_calculator`), the page is a MindTouch
   article whose interactive body is a single client-side JS widget with no further pages to
   enumerate — fetched directly, one page.

Coverage claim: **complete for the "Tesira Text Protocol" TOC section**, per the site's own
published search-index manifest (`data/all_topics.json`), not by keyword search or filename
inference. The wider "System Control" book also contains a large "Attribute Tables" section
(~180 pages, one per DSP/Service block, e.g. `Standard_Mixer_Block.htm`) — that section was
**not** harvested page-by-page (out of scope: the task asked for TTP grammar/protocol pages, not
the full per-block attribute reference). Two of its pages, `Session.htm` and `Device.htm`, were
fetched anyway because the TTP Syntax page names them as the canonical "Special Addresses"
reference and they are small; the command-string-calculator's embedded `blocks` data object
(`data/calculator_blocks.json`) separately covers the full per-block attribute/verb data for all
92 uniquely-named block types in one shot, without needing to crawl the Attribute Tables book.

## Pages fetched (Tesira Text Protocol TOC section — all 8, per `data/all_topics.json`)

| Local file | Title | Source URL |
|---|---|---|
| `pages/TTP_Security.md` | TTP Security | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Security.htm |
| `pages/SSH.md` | SSH | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/SSH.htm |
| `pages/RS-232.md` | RS-232 | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/RS-232.htm |
| `pages/TTP_Troubleshooting.md` | TTP Troubleshooting | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Troubleshooting.htm |
| `pages/TTP_Responses.md` | TTP Responses | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Responses.htm |
| `pages/TTP_Syntax.md` | TTP Syntax | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Syntax.htm |
| `pages/TTP_Subscriptions.md` | TTP Subscriptions | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Subscriptions.htm |
| `pages/Telnet.md` | Telnet | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/Telnet.htm |

## Supplementary pages fetched (outside the TTP section, cited by the pages above)

| Local file | Title | Source URL |
|---|---|---|
| `pages/Tesira_Software_System_Control_Overview.md` | Tesira Software System Control Overview (parent "System Control" landing page) | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Software_System_Control_Overview.htm |
| `pages/Session.md` | Session (Attribute Table — the `SESSION` special address, referenced by TTP Syntax) | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Attribute_Tables/Service_Addresses/Session.htm |
| `pages/Device.md` | Device (Attribute Table — the `DEVICE` special address, referenced by TTP Syntax) | https://tesira-software-help.biamp.com/assets/TOC/System_Control/Attribute_Tables/Service_Addresses/Device.htm |
| `pages/Command_String_Calculator.md` | Tesira command string calculator | https://support.biamp.com/Tesira/Control/Tesira_command_string_calculator |

## Raw data assets extracted (not pages — machine-readable sources cited from the pages above)

* `data/all_topics.json` — the site's full published search-index manifest (273 topics, title +
  relUrl + relTOCPath each), decoded from `whxdata/search_topics.js`. Used for enumeration
  (method above), and useful for anyone extending this harvest later.
* `data/calculator_blocks.js` — the literal inline JS `blocks` data object from the command
  string calculator page (verbatim, unparsed).
* `data/calculator_blocks.json` — the same data parsed into JSON: 92 uniquely-keyed block types,
  1,062 attribute/service records, each with its valid verbs (`commands`), attribute/service
  code (`commandstring`), index slots, and value type/range/enum.

## Unreachable / not found

Nothing in the "Tesira Text Protocol" TOC section was unreachable — all 8 pages returned HTTP
200 and were fully fetched (fetched as HTML and converted to text locally; see note below).
Two URLs speculatively tried during discovery returned 404 and were abandoned in favor of the
manifest-based method: `whxdata/toc.js`, `whxdata/tocdata.js`, `whxdata/data.js`,
`whxdata/index.js`, `data/toc.js`, `sitemap.xml`, `robots.txt` (this site has none). The Azure
Blob Storage container-listing trick (`?restype=container&comp=list`) also did not work (the
host front-door ignores the query params and serves the normal index page) — not a real
directory listing, just further confirmation the manifest file was the right approach.

Note on fetch method: `brightdata scrape` in default (markdown) format silently truncated every
page from this site mid-sentence at a few hundred to ~2 KB (server-side rendering/conversion
limit, not a real content boundary — confirmed by comparing byte counts and mid-word cutoffs).
All pages here were therefore re-fetched with `-f html` and converted to text locally with a
small stdlib-only HTML-to-text script; every page below was diffed against its raw HTML table
count to confirm no content was dropped in conversion.
