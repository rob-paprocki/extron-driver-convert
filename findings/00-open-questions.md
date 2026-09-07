# Open questions

The questions the sample files need to answer. Each gets an answer with
evidence (a hexdump, a file listing, a quoted field) — not an inference.

## About the `.pkp` container

- [ ] What is it? Zip/archive, XML, JSON, SQLite, proprietary binary, or
      an encrypted/signed blob?
- [ ] Is it readable without Extron software? If encrypted or signed, that
      likely ends the `.pkp` → `.py` direction on its own.
- [ ] Does one `.pkp` hold one device driver or several?
- [ ] Is there a version/schema marker, and do GC Plus and GC Pro differ?

## About the driver content

- [ ] How are commands represented — literal strings, templates with
      parameter slots, or something structured?
- [ ] How are parameters typed and constrained (ranges, enumerations)?
- [ ] How is feedback parsing expressed — regex, fixed offsets, delimiters?
- [ ] How are connection settings carried (baud/parity/stop, IP port, IR)?
- [ ] Is there logic beyond the command table (state machines, polling,
      conditionals)?

## About the ControlScript module

- [ ] What is the module's actual structure — class layout, command dict
      shape, `Set*`/`Update*`/parse conventions?
- [ ] Is any part obfuscated, minified, or shipped only as bytecode?
- [ ] What does a module require from the host system that a `.pkp` has no
      concept of (and vice versa)?

## About the mapping

- [ ] Which fields map 1:1?
- [ ] Which map with loss, and what is lost?
- [ ] Which have no counterpart at all in either direction?
- [ ] Is either direction automatable, or only assistable?
