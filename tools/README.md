# tools/

Standard-library Python 3.11 or later, so there is nothing to install. Run
everything from the repo root.

## Start here

| file | what it is |
|---|---|
| `convert.py` | One command line for every conversion. `python tools/convert.py directions` prints what each direction can and cannot do. |
| `convert_gui.py` | The same verbs in a desktop window (tkinter). |

`convert.py` verbs:

| verb | does |
|---|---|
| `directions` | the status of each conversion direction |
| `dump` | a `.pkp` or `.pkg` to JSON |
| `validate` | checks a `.pkp` with this project's own copy of Extron's validator |
| `verify` | `validate`, plus, with `--load-package` on Windows, Extron's own loader |
| `pkp2cs` | Extron `.pkp` to a ControlScript module |
| `cs2pkp` | a ControlScript module into a donor `.pkp` |
| `pkg2cs` | Crestron `.pkg` to driver JSON; writing the module from it is still manual |
| `pkp2pkg` | prints the patch command for a Crestron `.pkg` (patch only) |

You need a driver to feed it. None ship here (see `samples/README.md`), so use
a `.pkp` from your own Global Configurator driver library or a `.pkg` you are
licensed to hold. For example:

```bash
python tools/convert.py pkp2cs path/to/driver.pkp -o out/
python tools/convert.py dump path/to/driver.pkp -o driver.json
python tools/convert.py validate path/to/driver.pkp
```

Each verb takes `--help`.

`validate` uses our model of the format, and finding 18 shows that model can
pass a package Extron's code rejects. Before trusting an edited `.pkp`, run
`verify --load-package` on a Windows machine with Global Configurator.

## The rest, by job

`convert.py` calls these. Each runs on its own too.

| job | files |
|---|---|
| read a package | `pkp_dump.py` (`.pkp` to an object graph), `pkg_dump.py` (Crestron `.pkg` to manifest and driver JSON), `gc_catalogue.py` (what Global Configurator actually catalogued) |
| translate | `pkp2cs.py` (raises on anything it cannot translate) |
| build or edit a package | `pkp_build.py` (transplant into a donor; refuses unless the donor round-trips byte for byte), `pkp_asset.py` (add commands to a `.pkp`), `nrbf_graph.py` (object-id to record-span map that `pkp_asset.py` edits through), `pkg_patch.py` (swap the driver definition inside a `.pkg`'s DLL) |
| check a result | `wire_table.py` (the acceptance test: the bytes each command sends, from either Python dialect), `pkp_validate.py` (Extron's driver validator rewritten in Python) |
| repo upkeep | `verify_vendor_files.py` and `vendor_inputs.py` (check and locate the unpublished vendor files), `public_sync.py` (builds the public copy from the private archive) |

## Tests

`test_<tool>.py` pairs with `<tool>.py`. There is no pytest; run a file
directly, for example `python tools/test_wire_table.py`. Tests that need a
vendor file skip and name it. With the vendor files in place the full set
walks every sample package and takes about 20 minutes. The commands for every
suite are in `ENVIRONMENT.md`.

## out/verdicts/

Raw output of the multi-agent runs the numbered findings were written from,
kept as provenance. You do not need it to use anything above.
