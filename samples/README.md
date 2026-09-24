# Samples

**Vendor material, not published.** Since
2026-09-24 only this README and the empty folders' `.gitkeep` files are
tracked. The sample packages and modules the tools and tests read are listed,
with their SHA-256s, in `vendor-files.manifest.tsv` at the repo root; put
your copies at those paths and check them with
`python tools/verify_vendor_files.py --only samples/`. Without them the tests
that need a sample skip, naming it. The private archive's earlier commits
still contain them; the public copy's history does not.

Drop files here:

- `pkp/` — `.pkp` drivers from Global Configurator Plus/Pro
- `controlscript/` — ControlScript device modules (`.py`)

Most useful pairing: **the same device in both formats.** That turns the
mapping question from guesswork into a diff. Failing that, any two files
still answer the container and structure questions.

Note the source and version of each file in `notes/sample-provenance.md`
so findings can cite where a format observation came from.
