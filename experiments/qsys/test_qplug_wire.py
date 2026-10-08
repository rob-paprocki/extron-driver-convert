#!/usr/bin/env python3
"""
test_qplug_wire.py - the Lua parser and the Q-SYS plugin wire-table reader.

[1]-[2] run anywhere on synthetic Lua. [3] needs the plain plugins listed in
vendor-files.manifest.tsv under samples/qsys/, and the Extron modules under corpus/; it
skips, naming them, when they are absent.
Plain test_* functions + asserts, run by the __main__ block; no pytest.
Run: python -u experiments/qsys/test_qplug_wire.py
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools"))

import lua_parse as lp            # noqa: E402
import qplug_wire as qw           # noqa: E402
import vendor_inputs              # noqa: E402


def _ev(src):
    """The value of the chunk's last `return` expression, as rendered templates."""
    prog = qw.Program(lp.parse(src))
    ev = qw.Evaluator(prog)
    ret = prog.main.returns[-1].exprs[0]
    return sorted(qw.render(a.val, a.label).canonical for a in ev.ev(ret, ev.open_ctx(prog.main, 0)))


def _sends(src):
    t = qw.extract(src)
    return sorted({(tm.canonical, tm.label) for s in t.sends for tm in s.templates})


# ---- [1] the parser -----------------------------------------------------------------------------
def test_precedence_follows_lua():
    def top(src):
        return lp.parse("return " + src)[0].exprs[0]
    e = top("1 + 2 * 3")
    assert e.op == "+" and e.right.op == "*"
    e = top("-x ^ 2")                      # unary binds looser than ^
    assert e.kind == "Unop" and e.operand.op == "^"
    e = top("2 ^ 3 ^ 2")                   # ^ is right associative
    assert e.op == "^" and e.right.op == "^"
    e = top("a .. b .. c")                 # .. is right associative
    assert e.op == ".." and e.right.op == ".."
    e = top("not a == b")                  # not binds tighter than ==
    assert e.op == "==" and e.left.kind == "Unop"
    e = top("a or b and c")
    assert e.op == "or" and e.right.op == "and"
    e = top("1 << 2 + 3")                  # shifts below arithmetic
    assert e.op == "<<" and e.right.op == "+"


def test_strings_numbers_and_comments():
    body = lp.parse(
        "a = '\\x41\\65\\z\n    B\\u{48}\\n'\n"
        "b = [==[\nraw ]] still]==]\n"
        "--[[ a long\ncomment ]] c = 0x10 + 1e2 + 0x1p4 + 3.\n"
        "-- a line comment\n"
        "d = \"tab\\tq\\\"\"\n")
    vals = {st.targets[0].name: st.exprs[0] for st in body}
    assert vals["a"].value == b"AAB" + "H".encode() + b"\n"
    assert vals["b"].value == b"raw ]] still"
    c = vals["c"]
    assert c.left.left.left.value == 16 and c.left.left.right.value == 100.0
    assert c.left.right.value == 16.0 and c.right.value == 3.0
    assert vals["d"].value == b'tab\tq"'


def test_statements_and_sugar():
    body = lp.parse(
        "local function f(a, ...) return a end\n"
        "function obj.m:meth(x) goto done ::done:: end\n"
        "for i = 1, 10, 2 do end for k, v in pairs(t) do end\n"
        "repeat local z = 1 until z\n"
        "if a then elseif b then else end\n"
        "x, y = s:upper(), f{1, 2; k = 3, [4] = 5}\n"
        "print'hi'\n")
    kinds = [st.kind for st in body]
    assert kinds == ["LocalFunc", "FuncStat", "NumFor", "GenFor", "Repeat", "If", "Assign", "CallStat"], kinds
    assert body[1].method == "meth" and body[1].func.params == ["self", "x"]
    tbl = body[6].exprs[1].args[0]
    assert [f.key is None for f in tbl.fields] == [True, True, False, False]


def test_syntax_errors_name_the_line():
    for src, line in (("x = 1\ny = = 2", 2), ("if a then\n", 2), ("s = 'open\n", 1), ("f(", 1)):
        try:
            lp.parse(src)
        except lp.LuaSyntaxError as e:
            assert e.line == line, (src, e.line)
        else:
            raise AssertionError("no error for %r" % src)


# ---- [2] the reader -----------------------------------------------------------------------------
def test_concat_format_char_and_tostring():
    assert _ev('return "PWR" .. tostring(1) .. "\\r"') == ["PWR1\r"]
    assert _ev('return string.format("%s%02d*%X", "V", 7, 255)') == ["V07*FF"]
    assert _ev('return ("A%dB"):format(3)') == ["A3B"]
    assert _ev('return string.char(0xAA, 0x11, 1) .. "\\x05"') == ["AA 11 01 05"]
    assert _ev('return "VOL" .. Controls.Volume.Value') == ["VOL{}"]


def test_and_or_follows_the_condition():
    src = ('function Q(cmd, ext) return cmd .. (ext and " " .. ext or "") .. "\\r" end\n'
           'return Q("ARM", "1")')
    assert _ev(src) == ["ARM 1\r"]
    src = ('function Q(cmd, ext) return cmd .. (ext and " " .. ext or "") .. "\\r" end\n'
           'return Q("GET")')
    assert _ev(src) == ["GET\r"]
    assert _ev('return (Controls.Mute.Boolean and "1" or "0")') == ["0", "1"]


def test_parameters_resolve_through_call_sites_without_mixing_calls():
    src = """
    sock = TcpSocket.New()
    function Send(cmd, arg) sock:Write(cmd .. " " .. arg .. "\\r") end
    Controls.Power.EventHandler = function(ctl) Send("PWR", "1") end
    function Poll() Send("VOL", "?") end
    """
    assert _sends(src) == [("PWR 1\r", "Controls.Power.EventHandler"), ("VOL ?\r", "Poll")]


def test_queue_tables_keep_items_together():
    src = """
    udp = UdpSocket.New()
    Q = {}
    function ToQueue(cmd, ext) table.insert(Q, {cmd, ext}) end
    function Pump()
      local item = table.remove(Q, 1)
      udp:Send(ip, 49494, item[1] .. " " .. item[2] .. "\\r")
    end
    function A() ToQueue("SARMC", "1") end
    function B() ToQueue("LOAD", "0") end
    """
    assert _sends(src) == [("LOAD 0\r", "B"), ("SARMC 1\r", "A")]
    src = """
    s = TcpSocket.New()
    CmdQ = {}
    function SendQ(cmd, kind) table.insert(CmdQ, {cmd, kind}) end
    function Send() s:Write(CmdQ[1][1] .. "|\\r") end
    function Poll() for i = 1, 4 do SendQ("W7*" .. i .. "PNAM", "Name") end end
    """
    sends = qw.extract(src).sends
    assert [(t.canonical, t.typed) for t in sends[0].templates] == [("W7*{}PNAM|\r", "W7*{#}PNAM|\r")]


def test_tables_as_value_maps_and_constants():
    src = """
    sock = TcpSocket.New()
    Inputs = {HDMI = "1", DP = "2"}
    function Set(name) sock:Write("IN" .. Inputs[name] .. "\\r") end
    Controls.In.EventHandler = function(c) Set(c.String) end
    function Fixed() sock:Write("IN" .. Inputs.DP .. "\\r") end
    """
    t = qw.extract(src)
    by = {tm.canonical: tm for s in t.sends for tm in s.templates}
    assert set(by) == {"IN{}\r", "IN2\r"}
    assert by["IN{}\r"].value_maps == {"table[?]": {"HDMI": "1", "DP": "2"}}


def test_what_cannot_be_known_is_opaque_and_counted():
    src = """
    sock = TcpSocket.New()
    function Frame(data)
      local v = "\\xAA"
      for i = 1, #data do v = v .. string.char(data[i]) end
      sock:Write(v)
    end
    """
    t = qw.extract(src)
    tm = t.sends[0].templates[0]
    assert tm.opaque == 1 and t.stats["opaque_templates"] == 1


def test_http_requests_and_reply_patterns():
    src = """
    function Get(path)
      HttpClient.Download{Url = "https://" .. ip .. ":4003/v2/" .. path, EventHandler = Done}
    end
    function Poll() Get("status") end
    sock = TcpSocket.New()
    sock.EventHandler = function(s, evt)
      local line = s:ReadLine(TcpSocket.EOL.Any)
      local a, b = line:match("^Vol(%d+)$")
      if line == "ACK" then end
    end
    """
    t = qw.extract(src)
    assert [tm.canonical for tm in t.sends[0].templates] == ["GET https://{}:4003/v2/status"]
    assert {r.get("pattern") or r.get("equals") for r in t.responses} == {"^Vol(%d+)$", "ACK"}


def test_wire_comparison_primitives():
    T = qw.tokens
    assert qw.intersects(T("text", "SCH32 {} {}={}\r"), T("text", "SCH32 1 R=1\r"))
    assert not qw.intersects(T("text", "LOAD 0\r"), T("text", "LOAD 3\r"))
    assert not qw.intersects(T("text", "WM{#}AU|"), T("text", "WM4000*1AU|"))   # a number holds no '*'
    assert qw.intersects(T("text", "WM{}AU|"), T("text", "WM4000*1AU|"))
    assert qw.intersects(T("bytes", "AA 11 ?? 01 CHK"), T("bytes", "AA 11 FE 01 12"))
    assert qw.sis_normal("WBRCDR|\r") == qw.sis_normal("wBRCDR\r") == "\x1bBRCDR\r"
    assert qw.sis_normal("1*2!\r") == "1*2!\r"
    assert qw.http_path("url=v2/x/{} body={}") == "v2/x/{}"
    assert qw.http_path("GET https://{}:4003/v2/x/{}") == "v2/x/{}"


# ---- [3] the owner's plugins and the four Extron pairs ------------------------------------------
QSYS_DIR = os.path.join(REPO, "samples", "qsys")
CLOCK = os.path.join(QSYS_DIR, "library", "ClockAudio_CDT100.3.6.0", "ClockAudioCDT100.qplug")
CLOCK_EXTRON = os.path.join(REPO, "corpus", "extron-gs-modules", "09062026", "clau_dsp_CDT100_v1_0_3_0.py")


def test_every_plain_plugin_parses():
    vendor_inputs.require(CLOCK)
    files = sorted(glob.glob(os.path.join(QSYS_DIR, "**", "*.qplug"), recursive=True))
    assert len(files) == 27, len(files)
    for f in files:
        with open(f, encoding="utf-8", errors="surrogateescape") as fh:
            lp.parse(fh.read())


def test_clock_audio_against_extrons_module():
    vendor_inputs.require(CLOCK, CLOCK_EXTRON)
    with open(CLOCK, encoding="utf-8") as f:
        table = qw.extract(f.read(), CLOCK)
    assert table.stats["send_sites"] == 1 and table.stats["opaque_templates"] == 0
    with open(CLOCK_EXTRON, encoding="utf-8") as f:
        cmp = qw.compare(table, f.read(), CLOCK_EXTRON)
    rows = {r["template"]: r for r in cmp["rows"]}
    assert cmp["summary"] == {"exact": 5, "full": 1, "partial": 2}, cmp["summary"]
    assert rows["SCH32 {} {}{}\r"]["covered"] == 20 == rows["SCH32 {} {}{}\r"]["strings"]
    assert (rows["LOAD {}\r"]["covered"], rows["LOAD {}\r"]["strings"]) == (1, 10)   # the plugin loads preset 0 only


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items(), key=lambda kv: kv[1].__code__.co_firstlineno
                                       if callable(kv[1]) and hasattr(kv[1], "__code__") else 0)
             if n.startswith("test_") and callable(f)]
    passed = failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except vendor_inputs.VendorInputMissing as e:
            skipped += 1
            print("SKIP", name, "-", e)
        except Exception as e:                       # noqa: BLE001
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d skipped (vendor input absent), %d total" % (passed, failed, skipped, len(tests)))
    sys.exit(1 if failed else 0)
