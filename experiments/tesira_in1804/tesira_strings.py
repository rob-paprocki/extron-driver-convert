#!/usr/bin/env python3
"""
tesira_strings.py - device command strings written the way a Biamp Tesira Command String block
takes them, and the Extron IN1804 command set in that form.

Tesira's "Edit Command String" dialog takes printable ASCII as-is and any other byte as a tilde
plus two hex digits: ~0D is CR, ~0A is LF, and a literal tilde is ~7E. Expected Response patterns
(Network Command String block, Tesira 3.15+) use the same syntax, except that "?" (one printable
character) and "*" (zero or more printable characters, matched minimally) are wildcards, so a
literal "?" or "*" in a device reply has to be written ~3F or ~2A. A wildcard never spans CR or
LF, a pattern must not end in "*", and Biamp advises starting with a definite character and
ending with the reply's terminator. Sources: MAP.md section 2.

The IN1804 strings are the bytes Extron's own ControlScript module for the series sends and
matches (extr_scaler_IN1804_Series_v1_3_0_0.py, vendor material, not in this repo; MAP.md section 3).

    python experiments/tesira_in1804/tesira_strings.py            # the paste-ready table
    python experiments/tesira_in1804/tesira_strings.py --serial   # strings for the RS-232 block

Standard library only.
"""
import argparse
import sys

TILDE = 0x7E
WILDCARDS = (0x2A, 0x3F)            # '*' and '?' in Expected Response patterns


def _escape(data, extra=()):
    out = []
    for b in data:
        if 0x20 <= b < 0x7F and b != TILDE and b not in extra:
            out.append(chr(b))
        else:
            out.append("~%02X" % b)
    return "".join(out)


def command(data):
    """A command string as typed into Tesira's Edit Command String dialog."""
    return _escape(data)


def pattern(data):
    """A device reply as a literal Tesira Expected Response pattern (no wildcards)."""
    return _escape(data, extra=WILDCARDS)


def problems(pat):
    """Biamp's rules a response pattern breaks, as short notes (empty when it is fine)."""
    notes = []
    if pat.endswith("*"):
        notes.append("ends in '*'")
    if pat[:1] in ("*", "?"):
        notes.append("starts with a wildcard")
    if not (pat.endswith("~0A") or pat.endswith("~0D")):
        notes.append("no CR/LF terminator")
    return notes


def for_serial(data):
    """Biamp's serial block transmits only strings that end in CR and/or LF: add a CR if missing."""
    return data if data.endswith((b"\r", b"\n")) else data + b"\r"


# (Command ID, label, bytes sent, reply bytes to match or None, note)
# Replies are in Extron's verbose mode 3, which command 1 turns on.
IN1804 = [
    (1, "Verbose mode 3 (tagged replies)", b"w3cv\r\n", b"Vrb3\r\n", "send once per connection, first"),
    (2, "Auto-switch off", b"w0AUSW\r", b"Ausw0\r\n", "stops auto-switching overriding a manual select"),
    (3, "Input 1", b"1!", b"In1 All\r\n", "audio and video together; no breakaway"),
    (4, "Input 2", b"2!", b"In2 All\r\n", ""),
    (5, "Input 3", b"3!", b"In3 All\r\n", ""),
    (6, "Input 4", b"4!", b"In4 All\r\n", ""),
    (7, "Input query", b"!", None, "answered by the In1-In4 patterns above"),
    (8, "Video blank all, on", b"1B", b"Vmt1\r\n", "reply form not confirmed (MAP.md H-T5)"),
    (9, "Video blank all, off", b"0B", b"Vmt0\r\n", "reply form not confirmed (MAP.md H-T5)"),
    (10, "Video blank query", b"B", b"Vmt1 1\r\n", "both outputs blanked; 'Vmt0 0' = neither"),
    (11, "Audio mute all, on", b"1Z", b"Amt1\r\n", "reply form not confirmed (MAP.md H-T5)"),
    (12, "Audio mute all, off", b"0Z", b"Amt0\r\n", "reply form not confirmed (MAP.md H-T5)"),
    (13, "Audio mute query", b"Z", b"Amt1 1\r\n", "both outputs muted; 'Amt0 0' = neither"),
    (14, "Front-panel lock, mode 1", b"1X", b"Exe1\r\n", "Extron executive mode"),
    (15, "Front-panel lock off", b"0X", b"Exe0\r\n", ""),
    (16, "Video blank output 1A, on", b"1*1B", b"Vmt1*1\r\n", "per output: 1 = 1A, 2 = 1B"),
    (17, "Video blank output 1A, off", b"1*0B", b"Vmt1*0\r\n", ""),
    (18, "Signal present query", b"w0LS\r", None, "reply 'In00 a*b*c*d', one 0/1 per input; see MAP.md section 5"),
    (19, "Volume -40", b"-40V", None, "fixed levels; range -100..0 (MAP.md section 4)"),
    (20, "Volume -20", b"-20V", None, ""),
    (21, "Volume 0 (maximum)", b"0V", None, ""),
]

ERROR_REPLY = "E??~0D~0A"            # Extron error codes E01..E33; one pattern catches them all


def table(serial=False):
    head = ["ID", "Label", "Command string", "Expected response", "Note"]
    rows = []
    for cid, label, sent, reply, note in IN1804:
        sent = for_serial(sent) if serial else sent
        rows.append([str(cid), label, command(sent), pattern(reply) if reply and not serial else "", note])
    width = [max(len(r[i]) for r in rows + [head]) for i in range(len(head))]
    fmt = "| " + " | ".join("%%-%ds" % w for w in width) + " |"
    lines = [fmt % tuple(head), "|" + "|".join("-" * (w + 2) for w in width) + "|"]
    lines += [fmt % tuple(r) for r in rows]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="IN1804 command strings for a Biamp Tesira Command String block.")
    ap.add_argument("--serial", action="store_true",
                    help="strings for the Serial Command String block (CR added; it matches no replies)")
    args = ap.parse_args(argv)
    print(table(serial=args.serial))
    if not args.serial:
        print("\nError replies: match %s on one logic output." % ERROR_REPLY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
