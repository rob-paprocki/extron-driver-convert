#!/usr/bin/env python3
"""
test_tesira_strings.py - Tesira string escaping and the IN1804 table.

No vendor input. Plain test_* functions + asserts, run by the __main__ block; no pytest.
Run: python -u experiments/tesira_in1804/test_tesira_strings.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tesira_strings as ts   # noqa: E402


def _unescape(s):
    return bytes(int(m.group(1), 16) if m.group(1) else ord(m.group(2))
                 for m in re.finditer(r"~([0-9A-F]{2})|(.)", s, re.S))


def test_control_bytes_and_tilde_are_escaped():
    assert ts.command(b"w3cv\r\n") == "w3cv~0D~0A"
    assert ts.command(b"a~b") == "a~7Eb"
    assert ts.command(b"\x1b0AUSW\r") == "~1B0AUSW~0D"


def test_command_strings_keep_star_and_question_mark_literal():
    assert ts.command(b"1*1B") == "1*1B"
    assert ts.command(b"2*\\") == "2*\\"


def test_patterns_escape_the_wildcards():
    assert ts.pattern(b"Amt1*1\r\n") == "Amt1~2A1~0D~0A"
    assert ts.pattern(b"Why?\r\n") == "Why~3F~0D~0A"


def test_escaping_round_trips():
    for data in (b"In2 All\r\n", b"wE1*3LOGO\r", b"x~*?\x00\xff"):
        assert _unescape(ts.command(data)) == data
        assert _unescape(ts.pattern(data)) == data


def test_problem_rules():
    assert ts.problems("In1 All~0D~0A") == []
    assert "ends in '*'" in ts.problems("Vol*")
    assert "starts with a wildcard" in ts.problems("?mt~0D~0A")
    assert "no CR/LF terminator" in ts.problems("Exe1")


def test_every_expected_response_obeys_biamps_rules():
    for cid, label, sent, reply, note in ts.IN1804:
        if reply:
            assert ts.problems(ts.pattern(reply)) == [], (cid, label)
    assert ts.problems(ts.ERROR_REPLY) == []


def test_ids_fit_one_block():
    ids = [row[0] for row in ts.IN1804]
    assert ids == list(range(1, len(ids) + 1)) and len(ids) <= 32


def test_serial_variant_adds_cr_only_where_missing():
    assert ts.for_serial(b"1!") == b"1!\r"
    assert ts.for_serial(b"w0AUSW\r") == b"w0AUSW\r"
    assert ts.for_serial(b"w3cv\r\n") == b"w3cv\r\n"


def test_input_rows_match_extrons_strings():
    rows = {label: (sent, reply) for cid, label, sent, reply, note in ts.IN1804}
    for n in range(1, 5):
        assert rows["Input %d" % n] == (b"%d!" % n, b"In%d All\r\n" % n)


def test_table_renders_every_row():
    out = ts.table()
    assert out.count("\n") == len(ts.IN1804) + 1
    assert "| 3  | Input 1" in out and "In1 All~0D~0A" in out
    assert "1!~0D" in ts.table(serial=True)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d total" % (passed, failed, len(tests)))
    sys.exit(1 if failed else 0)
