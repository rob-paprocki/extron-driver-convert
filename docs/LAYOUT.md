# Layout, grading and method

## Folder map

```text
STATUS.md  ROADMAP.md
findings/                    numbered research output, 01 to 20
tools/                       the tools in the README, with their tests
gui/                         Driver Studio, the desktop app (the only folder with dependencies)
packaging/                   Windows .exe build for Driver Studio
experiments/
  skeleton_i20/              the IV-CAM-I20 driver, .pkp and ControlScript forms
  oracle_pairs/              the 312-pair translator scorecard (finding 14)
  gcp_harness/               Windows-only: Extron DLL probes and Global Configurator UI automation
  graph_probes/              packages that located finding 18's deserializer bug
  ross_ultrix/               the one oracle pair with a human-written side (finding 17)
  automate_vx_threeway/      Extron vs Crestron vs docs for the Automate VX (finding 20)
  nrbf_writeback/ crestron2cs/ docs_only/ missing_ethernet/ ...
samples/<device>/            vendor packages, not published (README only)
corpus/                      an Extron driver library snapshot, not published (manifests only)
evidence/                    screenshots and logs the findings cite
reference/                   our indexes and analyses of vendor documentation
notes/                       sample provenance and desk research
vendor-files.manifest.tsv    every unpublished vendor file: SHA-256, size, path
```

## Grading a conversion

Six things decide how far a direction gets:

1. Container: can the format be read at all without Extron's tooling?
2. Command table: do commands, parameters and qualifiers map 1:1?
3. Feedback and parse: do match patterns survive translation?
4. Connection model: serial parameters, IP ports, IR, relays, addressing.
5. Logic and events: Global Configurator's event layer against ControlScript's user code.
6. Round-trip loss: what is silently dropped, and does it matter?

## Method

A negative claim needs positive evidence: report "not found by method X", never "does not exist". Acceptance is the wire-string table, not file similarity, and wire correctness is necessary but not sufficient. `Valid` does not mean loadable: finding 18 built a package that passed every local check and that Global Configurator would not list, because every local check shared one wrong model of the format. Deserialize through the vendor's own code before believing an edit.
