# Open questions

The questions the sample files need to answer. Each gets an answer with
evidence (a hexdump, a file listing, a quoted field) — not an inference.

## About the `.pkp` container

- [x] What is it? Zip/archive, XML, JSON, SQLite, proprietary binary, or
      an encrypted/signed blob? *(→ finding 01: gzip over .NET NRBF,
      embedding a complete Python driver.)*
- [x] Is it readable without Extron software? If encrypted or signed, that
      likely ends the `.pkp` → `.py` direction on its own. *(→ finding 01;
      `tools/pkp_dump.py` reads it in pure Python, no Extron software
      needed.)*
- [x] Does one `.pkp` hold one device driver or several? *(→ finding 05: the
      Samsung `.pkp` carries a serial driver AND an ethernet driver;
      finding 06: one package can hold 12 `DriverModelAsset`s across six
      physical sizes and two transports.)*
- [ ] Is there a version/schema marker, and do GC Plus and GC Pro differ?
      *(Version marker: yes — `DriverModelAsset._ver`, read and bumped by
      synthesis, findings 15 and 18. GC Plus vs Pro: still open, see
      ROADMAP R33 and STATUS.md's open-questions table.)*

## About the driver content

- [x] How are commands represented — literal strings, templates with
      parameter slots, or something structured? *(→ finding 02: Extron is
      literal Python plus a `self.Commands` dict; finding 03: Crestron is
      composable JSON templates.)*
- [x] How are parameters typed and constrained (ranges, enumerations)?
      *(→ finding 02: `DecimalParamAsset`/`EnumStateAsset` carry ranges and
      wire tokens; finding 18: ranges and enum states written into, and
      read back from, the asset tree.)*
- [x] How is feedback parsing expressed — regex, fixed offsets, delimiters?
      *(→ finding 02: Extron's `AddMatchString` regexes; finding 03:
      Crestron's response decoder tree — `Regex`, `BinaryPacket`, `Json`,
      name-match nodes.)*
- [ ] How are connection settings carried (baud/parity/stop, IP port, IR)?
      *(Crestron: yes — a transport block with full timing, finding 04.
      Extron: the package carries `_port`/`_compatibility`/`_udpOutputPort`
      but no tool reads them yet — open, see ROADMAP R16.)*
- [x] Is there logic beyond the command table (state machines, polling,
      conditionals)? *(→ finding 03: Rules/Conditions/Transformations;
      finding 07: 1 Beyond's compiled async scene/camera-view state
      machine; finding 18: `PollingInterval`, `RequiredPollingCommand`.)*

## About the ControlScript module

- [x] What is the module's actual structure — class layout, command dict
      shape, `Set*`/`Update*`/parse conventions? *(→ finding 02; finding 06:
      the `BaseDriver` API surface generalises — 46 locally-defined
      methods, inherited `AddMatchString`/`Disable`/`Discard`/`Error`.)*
- [x] Is any part obfuscated, minified, or shipped only as bytecode? *(No —
      → finding 01/02: the embedded and shipped ControlScript is plain
      Python source.)*
- [ ] What does a module require from the host system that a `.pkp` has no
      concept of (and vice versa)? *(Partial: embedded scripts call
      runtime-injected globals such as `ExtronTime` — finding 13 §5. Full
      survey still open, see ROADMAP R13, R15, H1.)*

## About the mapping

- [x] Which fields map 1:1? *(→ findings 03 and 05: identical wire frames
      from independently-encoded templates on the same device, checksum
      included.)*
- [x] Which map with loss, and what is lost? *(→ finding 02: version skew,
      hand-edits, a dropped throttle; findings 06/07/09: the IL-only
      Transformation residue — bounded, but not extracted from JSON.)*
- [x] Which have no counterpart at all in either direction? *(→ finding 05:
      Crestron's 8 extra capability families (direct channel, apps,
      transport keys, colour keys, Guide, Art Mode, Ambient); Extron-only
      `AspectRatio` "Custom" and, on IP, `pictureSizeControl`.)*
- [x] Is either direction automatable, or only assistable? *(→ STATUS.md's
      Answers table; findings 02 and 04 — automatable for Extron's own SIS
      drivers and for Crestron-in; Crestron-out is mechanically demonstrated
      but licence-gated, not code-gated.)*
