# gcp_harness/

Windows-only PowerShell that asks Extron's **own code** about a package, and
drives Global Configurator over UI Automation. This is how finding 18 turned
hardware round trips into seconds.

**Why PowerShell in a standard-library Python repo.** Every tool and test in
`tools/` still runs anywhere Python 3 does. This folder is the exception
because it has to load Extron's x86 .NET assemblies, which Python cannot do
without a third-party bridge (pythonnet) — and the repo's no-dependency rule
excludes that. So the harness is PowerShell, and machine-bound, like the GC
experiments it supports.

## Requirements (measured on the 2026-09 Windows box)

| | |
|---|---|
| Global Configurator Pro | 3.33.0.38, at `C:\Program Files (x86)\Extron\GCP` |
| `Extron.Configuration.*.dll` | 15.27.0.0 (x86) |
| PowerShell | **32-bit** 5.1: `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe` |
| .NET Framework | 4.8 |

`Get-FileHash` is missing from that 32-bit PowerShell; hash with Python
(`hashlib`) instead.

## Load-Package.ps1 — tested

The check `CLAUDE.md` requires before believing any object-graph edit.

```powershell
$ps32 = 'C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe'
& $ps32 -ExecutionPolicy Bypass -File .\Load-Package.ps1 -Path PKG.pkp              # will GC load it?
& $ps32 -ExecutionPolicy Bypass -File .\Load-Package.ps1 -Path PKG.pkp -Deserialize # if not, why?
& $ps32 -ExecutionPolicy Bypass -File .\Load-Package.ps1 -Path PKG.pkp -Commands    # what does GC see inside?
```

Verified 2026-09-11 against the finding 18 probes: `q_POS.pkp` loads and
deserializes; `q_MIX.pkp` returns `NULL` from `LoadFromFile` and
`An object cannot be registered twice.` from `BinaryFormatter`;
`1bynd_19_20024` enumerates all 34 commands. Exit code is 1 if any package
fails to load.

`lib/Extron.ps1` holds the two things that make this work: the 32-bit check,
and an `AssemblyResolve` handler that maps the assembly versions named inside a
`.pkp` stream (`Extron.Configuration.* 1.1.24.402`) onto the installed ones.

Pair it with `tools/gc_catalogue.py`, which answers *did GC catalogue it?* from
`DriverLookup.dat` — portable Python, no Windows needed.

## scratch/ — the UI Automation chain, verbatim

The 39 scripts that drove GCP on 2026-09-10, exactly as run. Each step was
verified individually; **they have not been consolidated into one end-to-end
script** (an open item in `ROADMAP.md`). They dot-source `uia_lib.ps1`,
`uia_act.ps1` and `mouse.ps1` from their own folder, so run them in place.

The verified sequence, in order:

| step | script | what it does |
|---|---|---|
| 1 | *(back up `DataFile.dat` + `DriverLookup.dat`)* | GC truncates both on start |
| 2 | `launch.ps1` | start GCP, wait for the main window (~48 s) |
| 3 | *(wait for `DataFile.dat` to stop growing)* | the catalogue rebuild |
| 4 | `open_drvmgr.ps1` → `dm_search.ps1` → `dm_rows.ps1` | Driver Manager: search, read the grid |
| 5 | `dm_close.ps1` | close it |
| 6 | `newproj.ps1` | File → New Project (Pro) |
| 7 | `add_device.ps1`, then `click_named.ps1 "Add Controller" "Add"` | add the controller |
| 8 | `palette.ps1 "Communication Ports"` | open the port list |
| 9 | `dblclick_item.ps1 "Ethernet Port 1"` | opens the driver picker |
| 10 | `pick_driver.ps1 "IV-CAM" "IV-CAM-I20"` | assign the driver |
| 11 | `inspect_cmd.ps1`, `inspect2.ps1 CMD PARAM`, `enum_states.ps1 CMD PARAM` | read the property editor |
| 12 | `shot.ps1 OUT.png` | screenshot |

Everything else in `scratch/` is an earlier probe of the same steps
(`uia_probe.ps1`, `tree_deep.ps1`, `dump_all.ps1`, …) or the failed save
attempts described below.

## Traps — each one cost real time

1. **Icon-font buttons read as `?`.** GCP is WPF with good `AutomationId`s,
   but the **+** (add controller) and hamburger buttons render from an icon
   font and appear as unnamed `MenuItem`s. Find them by bounding rectangle.
2. **Driver Manager opens slowly** — well over three seconds. Wait for the
   window by name rather than sleeping a fixed time.
3. **Assigning a driver needs a real double-click.** `SelectionItemPattern`
   selects the row but does not commit it.
4. **Do not drive the native Save As dialog.** Its Save button has no
   `InvokePattern`, `ValuePattern.SetValue` on the filename box does not stick,
   `SendKeys` cannot reach the foreground from a non-interactive session — and
   the filename box doubles as *rename* for whatever is selected. It renamed a
   folder in this repo (fixed in commit `064098f`). Project saving was left
   undone.
5. **Never press Verify, Build or Upload.** The Add Controller dialog is
   pre-filled with the real processor's address and credentials.
6. **Launching GCP rebuilds the catalogue.** Back it up first (step 1).
7. **`mouse.ps1` moves the real cursor.** Do not run the chain while someone
   is using the machine.

## askpass.sh

The workaround for Git Credential Manager hanging on an invisible prompt when
pushing from this box. Point `GIT_ASKPASS` at it and it answers with
`gh auth token` — the `rob-paprocki` keyring login — so the token never
appears in argv or the process table:

```sh
GIT_ASKPASS="$PWD/experiments/gcp_harness/askpass.sh" GIT_TERMINAL_PROMPT=0 git push origin main
```
