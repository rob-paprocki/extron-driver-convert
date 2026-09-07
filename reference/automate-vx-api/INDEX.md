# Automate VX API Documentation — Harvest Index

Harvested from `https://sdkcon78221.crestron.com/sdk/Automate-VX-API/` (a MadCap Flare site). Fetched via
`brightdata scrape` on 2026-09-07. Page enumeration relied entirely on `brightdata search "site:sdkcon78221.crestron.com Automate-VX-API <term>"`
plus links harvested from within fetched pages (the `Data/Tocs` JSON TOC endpoints return 404, and the
site's HTML has no visible sidebar TOC in the scraped DOM — the definitive endpoint list came from
in-page relative links inside `Whats-New/Whats-New.htm`, which names every API call added/changed across
firmware releases). 40 pages found and fetched; 0 pages failed. No 404s encountered among the URLs listed
below — all links tried against the live site resolved.

Local layout mirrors the site's own topic folders under this directory (`Quick-Start/`, `API-Reference/`,
`Whats-New/`, `Support/`, plus `Home.md` at the root). Every local file's first line is `Source: <url>`.

## Home

| Local file | Source URL |
|---|---|
| `Home.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Home.htm |

## Quick Start

| Local file | Source URL |
|---|---|
| `Quick-Start/Quick-Start.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Quick-Start/Quick-Start.htm |
| `Quick-Start/Prerequisites-and-Assumptions.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Quick-Start/Prerequisites-and-Assumptions.htm |
| `Quick-Start/Authentication.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Quick-Start/Authentication.htm |
| `Quick-Start/Make-API-Calls.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Quick-Start/Make-API-Calls.htm |

## API Reference (index + 32 endpoint pages)

| Local file | Source URL |
|---|---|
| `API-Reference/API-Reference.md` (index) | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/API-Reference.htm |
| `API-Reference/Get-Token-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Get-Token-API.htm |
| `API-Reference/CallCameraPreset-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CallCameraPreset-API.htm |
| `API-Reference/CameraStatus-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CameraStatus-API.htm |
| `API-Reference/ChangeLayout-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ChangeLayout-API.htm |
| `API-Reference/CopyFiles-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CopyFiles-API.htm |
| `API-Reference/ForceChangeRoomConfig-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ForceChangeRoomConfig-API.htm |
| `API-Reference/GetActiveTalkers-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetActiveTalkers-API.htm |
| `API-Reference/GetAllStatus-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetAllStatus-API.htm |
| `API-Reference/GetCameras-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetCameras-API.htm |
| `API-Reference/GetScenarios-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GetScenarios-API.htm |
| `API-Reference/GoHome-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GoHome-API.htm |
| `API-Reference/GoToScenario-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/GoToScenario-API.htm |
| `API-Reference/ImportCameraPresets-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ImportCameraPresets-API.htm |
| `API-Reference/Macro-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Macro-API.htm |
| `API-Reference/ManualSwitchCamera-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ManualSwitchCamera-API.htm |
| `API-Reference/RecordingSpaceAvail-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/RecordingSpaceAvail-API.htm |
| `API-Reference/Restart-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Restart-API.htm |
| `API-Reference/SaveCameraPreset-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/SaveCameraPreset-API.htm |
| `API-Reference/ScenarioStatus-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ScenarioStatus-API.htm |
| `API-Reference/ShotStatus-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ShotStatus-API.htm |
| `API-Reference/Sleep-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/Sleep-API.htm |
| `API-Reference/StartOutput-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartOutput-API.htm |
| `API-Reference/StartPT-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartPT-API.htm |
| `API-Reference/StartRecord-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartRecord-API.htm |
| `API-Reference/StartStream-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartStream-API.htm |
| `API-Reference/StartZ-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartZ-API.htm |
| `API-Reference/StopOutput-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopOutput-API.htm |
| `API-Reference/StopPT-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopPT-API.htm |
| `API-Reference/StopRecord-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopRecord-API.htm |
| `API-Reference/StopStream-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopStream-API.htm |
| `API-Reference/StopZ-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopZ-API.htm |
| `API-Reference/StreamStatus-API.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StreamStatus-API.htm |

## What's New

| Local file | Source URL |
|---|---|
| `Whats-New/Whats-New.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Whats-New/Whats-New.htm |

## Support

| Local file | Source URL |
|---|---|
| `Support/Support.md` | https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Support/Support.htm |

## Enumeration method and confidence

1. Started at `Home.htm`; confirmed `Data/Tocs/*.json` returns 404 (per task brief) — not re-tested here.
2. `brightdata search "site:sdkcon78221.crestron.com Automate-VX-API"` (paged) surfaced ~25 distinct URLs.
3. Targeted `brightdata search "site:sdkcon78221.crestron.com Automate-VX-API <CandidateName>"` queries for
   plausible endpoint names (guessing from Start/Stop, Get/Set pairing conventions already observed)
   surfaced the remainder: `StartPT`, `StartRecord`, `StopOutput`, `StopRecord`, `StopStream`, `StopZ`,
   `CopyFiles`.
4. The decisive source was `Whats-New/Whats-New.htm`'s version history, which contains **relative links to
   every API page it mentions** (unlike any other page on the site, whose in-body links are sparse). That
   page's links surfaced `CameraStatus-API.htm`, `ManualSwitchCamera-API.htm`, `GetAllStatus-API.htm`,
   `ShotStatus-API.htm`, and `Quick-Start/Authentication.htm` — none of which had appeared in step 2/3 search
   results.
5. Convergence check: after step 4, ten additional plausible-name search queries (`RecordStatus`,
   `GetRoomConfig`, `DeleteCameraPreset`, `GetVersion`, `Snapshot`, `Ping`, etc.) returned **zero** new
   pages — all hits were pages already known. Combined with the fact that the resulting 32-endpoint count
   exactly matches the 32 identical endpoint strings independently observed shared between the Extron
   ControlScript module and the Extron .pkp (findings/07), this is treated as strong (not absolute)
   evidence the API-Reference page set is complete.
6. Confidence caveat: this is search-engine + in-page-link enumeration of a site with no accessible
   sitemap, TOC JSON, or robots.txt (all three checked and 404). A page that is orphaned (no in-page link
   to it and not indexed by Google) would not be found by this method. The `GetAllStatus` example response
   names 8 further sub-API call names with no page of their own at all (see `ENDPOINTS.md`, "Undocumented
   sub-APIs") — these are documented evidence that server-side APIs can exist with zero dedicated page, which
   is the one concrete reason to hold the "32 is complete" conclusion as strong rather than certain.

## Deprecated endpoint noted but not fetched

`CallPlugin` — referenced only in `Whats-New/Whats-New.htm` ("Removed support for depreciated CallPlugin
API call," May 9, 2025). No `CallPlugin-API.htm` page exists on the site (searched directly, zero results);
it predates the currently-published 6.4.1 documentation and was not captured as a standalone page here.
