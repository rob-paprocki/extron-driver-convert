#!/usr/bin/env python3
"""
lua_parse.py - a Lua 5.3 lexer and parser, standard library only.

Q-SYS plugins are Lua 5.3 source. This turns one into a tree of `Node`s that
qplug_wire.py walks. It is a full parser of the language (goto, integer division
and the bitwise operators included), not a pattern scan, so a string or a comment
can never be mistaken for code.

    from lua_parse import parse
    tree = parse(open("x.qplug", encoding="utf-8").read())

Every node has `.kind`, `.line` and the fields its kind names (see the table at
the end of this docstring). String literals are kept as `bytes`, as Lua keeps
them, after every escape is decoded; numbers as int or float.

    expressions  Nil True False Vararg Number(value) String(value)
                 Function(params, vararg, body, name)  Table(fields)
                 Binop(op, left, right)  Unop(op, operand)  Paren(expr)
                 Name(name)  Index(obj, key)  Call(func, args)  Method(obj, name, args)
    table fields Field(key, value)  key is None for a positional field
    statements   Local(names, attribs, exprs)  Assign(targets, exprs)  CallStat(call)
                 Do(body)  While(cond, body)  Repeat(body, cond)
                 If(clauses, orelse)  clauses = [(cond, body)]
                 NumFor(var, start, stop, step, body)  GenFor(names, exprs, body)
                 FuncStat(target, method, func)  LocalFunc(name, func)
                 Return(exprs)  Break  Goto(label)  Label(name)
    a body is a list of statements

Run as a script to parse files and report the first syntax error in each:
    python experiments/qsys/lua_parse.py FILE...
"""
import sys

KEYWORDS = {
    "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if", "in",
    "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while",
}
# longest first, so '...' wins over '..' and '//' over '/'
OPERATORS = sorted([
    "+", "-", "*", "/", "//", "%", "^", "#", "&", "~", "|", "<<", ">>", "==", "~=", "<=", ">=",
    "<", ">", "=", "(", ")", "{", "}", "[", "]", "::", ";", ":", ",", ".", "..", "...",
], key=len, reverse=True)

# Lua 5.3 operator priorities (lparser.c): left, right
BINARY_PRIORITY = {
    "or": (1, 1), "and": (2, 2),
    "<": (3, 3), ">": (3, 3), "<=": (3, 3), ">=": (3, 3), "~=": (3, 3), "==": (3, 3),
    "|": (4, 4), "~": (5, 5), "&": (6, 6), "<<": (7, 7), ">>": (7, 7),
    "..": (9, 8), "+": (10, 10), "-": (10, 10),
    "*": (11, 11), "/": (11, 11), "//": (11, 11), "%": (11, 11),
    "^": (14, 13),
}
UNARY_PRIORITY = 12


class LuaSyntaxError(Exception):
    def __init__(self, msg, line):
        super().__init__("line %d: %s" % (line, msg))
        self.line = line


class Node:
    """One syntax-tree node: `kind`, `line`, and the fields its kind names."""
    __slots__ = ("kind", "line", "f")

    def __init__(self, kind, line, **fields):
        self.kind = kind
        self.line = line
        self.f = fields

    def __getattr__(self, name):
        try:
            return self.f[name]
        except KeyError:
            raise AttributeError("%s node has no field %r" % (self.kind, name)) from None

    def __repr__(self):
        return "%s@%d(%s)" % (self.kind, self.line, ", ".join("%s=%r" % kv for kv in self.f.items()))


# ---- lexer ------------------------------------------------------------------------------------
class Token:
    __slots__ = ("type", "value", "line")

    def __init__(self, type_, value, line):
        self.type = type_       # 'name' 'kw' 'num' 'str' 'op' 'eof'
        self.value = value
        self.line = line

    def __repr__(self):
        return "%s:%r@%d" % (self.type, self.value, self.line)


def _long_bracket_level(src, i):
    """At src[i] == '[': the level of a long bracket opening here, or -1."""
    j = i + 1
    while j < len(src) and src[j] == "=":
        j += 1
    if j < len(src) and src[j] == "[":
        return j - i - 1
    return -1


def tokenize(src):
    toks = []
    i, n, line = 0, len(src), 1
    if src.startswith("#"):                     # a shebang line
        while i < n and src[i] != "\n":
            i += 1
    while True:
        # whitespace and comments
        while i < n:
            c = src[i]
            if c == "\n":
                line += 1
                i += 1
            elif c in " \t\r\f\v":
                i += 1
            elif src.startswith("--", i):
                i += 2
                if i < n and src[i] == "[":
                    level = _long_bracket_level(src, i)
                    if level >= 0:
                        close = "]" + "=" * level + "]"
                        end = src.find(close, i)
                        if end < 0:
                            raise LuaSyntaxError("unfinished long comment", line)
                        line += src.count("\n", i, end)
                        i = end + len(close)
                        continue
                while i < n and src[i] != "\n":
                    i += 1
            else:
                break
        if i >= n:
            toks.append(Token("eof", None, line))
            return toks
        c = src[i]
        start_line = line
        if c.isalpha() or c == "_":
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            toks.append(Token("kw" if word in KEYWORDS else "name", word, line))
            i = j
        elif c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            j, value = _number(src, i, line)
            toks.append(Token("num", value, line))
            i = j
        elif c in "\"'":
            j, value, line = _short_string(src, i, line)
            toks.append(Token("str", value, start_line))
            i = j
        elif c == "[" and _long_bracket_level(src, i) >= 0:
            level = _long_bracket_level(src, i)
            open_end = i + level + 2
            close = "]" + "=" * level + "]"
            end = src.find(close, open_end)
            if end < 0:
                raise LuaSyntaxError("unfinished long string", line)
            body = src[open_end:end]
            if body.startswith("\r\n") or body.startswith("\n\r"):
                body = body[2:]
            elif body.startswith("\n") or body.startswith("\r"):
                body = body[1:]
            line += src.count("\n", i, end)
            toks.append(Token("str", body.encode("utf-8"), start_line))
            i = end + len(close)
        else:
            for op in OPERATORS:
                if src.startswith(op, i):
                    toks.append(Token("op", op, line))
                    i += len(op)
                    break
            else:
                raise LuaSyntaxError("unexpected character %r" % c, line)


def _number(src, i, line):
    n = len(src)
    if src.startswith(("0x", "0X"), i):
        j = i + 2
        mant, frac, exp, seen = 0, 0, 0, False
        while j < n and src[j] in "0123456789abcdefABCDEF":
            mant = mant * 16 + int(src[j], 16)
            j += 1
            seen = True
        is_float = False
        if j < n and src[j] == ".":
            is_float = True
            j += 1
            while j < n and src[j] in "0123456789abcdefABCDEF":
                mant = mant * 16 + int(src[j], 16)
                frac += 1
                j += 1
                seen = True
        if j < n and src[j] in "pP":
            is_float = True
            j += 1
            sign = 1
            if j < n and src[j] in "+-":
                sign = -1 if src[j] == "-" else 1
                j += 1
            k = j
            while j < n and src[j].isdigit():
                j += 1
            if k == j:
                raise LuaSyntaxError("malformed number", line)
            exp = sign * int(src[k:j])
        if not seen:
            raise LuaSyntaxError("malformed number", line)
        if is_float:
            return j, mant * 2.0 ** (exp - 4 * frac)
        return j, mant & 0xFFFFFFFFFFFFFFFF if mant >= 2 ** 64 else mant
    j = i
    while j < n and src[j].isdigit():
        j += 1
    is_float = False
    if j < n and src[j] == ".":
        is_float = True
        j += 1
        while j < n and src[j].isdigit():
            j += 1
    if j < n and src[j] in "eE":
        is_float = True
        j += 1
        if j < n and src[j] in "+-":
            j += 1
        k = j
        while j < n and src[j].isdigit():
            j += 1
        if k == j:
            raise LuaSyntaxError("malformed number", line)
    text = src[i:j]
    if j < n and (src[j].isalpha() or src[j] == "_"):
        raise LuaSyntaxError("malformed number near %r" % src[i:j + 1], line)
    return j, float(text) if is_float else int(text)


_SIMPLE_ESCAPES = {"a": 7, "b": 8, "f": 12, "n": 10, "r": 13, "t": 9, "v": 11,
                   "\\": 92, '"': 34, "'": 39}


def _short_string(src, i, line):
    quote = src[i]
    j, n = i + 1, len(src)
    out = bytearray()
    while True:
        if j >= n:
            raise LuaSyntaxError("unfinished string", line)
        c = src[j]
        if c == quote:
            return j + 1, bytes(out), line
        if c == "\n":
            raise LuaSyntaxError("unfinished string", line)
        if c != "\\":
            out += c.encode("utf-8")
            j += 1
            continue
        j += 1
        if j >= n:
            raise LuaSyntaxError("unfinished string", line)
        e = src[j]
        if e in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[e])
            j += 1
        elif e == "\n" or e == "\r":
            out.append(10)
            line += 1
            j += 1
            if j < n and src[j] in "\r\n" and src[j] != e:
                j += 1
        elif e == "x":
            hx = src[j + 1:j + 3]
            if len(hx) != 2 or any(h not in "0123456789abcdefABCDEF" for h in hx):
                raise LuaSyntaxError("hexadecimal digit expected", line)
            out.append(int(hx, 16))
            j += 3
        elif e == "z":
            j += 1
            while j < n and src[j] in " \t\r\n\f\v":
                if src[j] == "\n":
                    line += 1
                j += 1
        elif e.isdigit():
            k = j
            while k < n and k < j + 3 and src[k].isdigit():
                k += 1
            v = int(src[j:k])
            if v > 255:
                raise LuaSyntaxError("decimal escape too large", line)
            out.append(v)
            j = k
        elif e == "u":
            if j + 1 >= n or src[j + 1] != "{":
                raise LuaSyntaxError("missing '{' in \\u{xxxx}", line)
            k = src.find("}", j + 2)
            if k < 0:
                raise LuaSyntaxError("missing '}' in \\u{xxxx}", line)
            out += chr(int(src[j + 2:k], 16)).encode("utf-8", "surrogatepass")
            j = k + 1
        else:
            raise LuaSyntaxError("invalid escape sequence '\\%s'" % e, line)


# ---- parser -----------------------------------------------------------------------------------
class Parser:
    def __init__(self, src):
        self.toks = tokenize(src)
        self.p = 0

    # token helpers
    @property
    def tok(self):
        return self.toks[self.p]

    def peek(self, k=1):
        return self.toks[min(self.p + k, len(self.toks) - 1)]

    def next(self):
        t = self.toks[self.p]
        self.p += 1
        return t

    def check(self, value, type_=None):
        t = self.tok
        return t.value == value and t.type in ((type_,) if type_ else ("op", "kw"))

    def accept(self, value):
        if self.check(value):
            return self.next()
        return None

    def expect(self, value, opener=None, open_line=None):
        if self.check(value):
            return self.next()
        if opener and open_line != self.tok.line:
            raise LuaSyntaxError("'%s' expected (to close '%s' at line %d) near %s"
                                 % (value, opener, open_line, self._near()), self.tok.line)
        raise LuaSyntaxError("'%s' expected near %s" % (value, self._near()), self.tok.line)

    def name(self):
        t = self.tok
        if t.type != "name":
            raise LuaSyntaxError("name expected near %s" % self._near(), t.line)
        self.p += 1
        return t.value

    def _near(self):
        t = self.tok
        return "<eof>" if t.type == "eof" else repr(t.value)

    # blocks
    def chunk(self):
        body = self.block()
        if self.tok.type != "eof":
            raise LuaSyntaxError("'<eof>' expected near %s" % self._near(), self.tok.line)
        return body

    def _block_follow(self, with_until=True):
        t = self.tok
        if t.type == "eof":
            return True
        if t.type == "kw" and t.value in ("else", "elseif", "end"):
            return True
        return with_until and t.type == "kw" and t.value == "until"

    def block(self):
        body = []
        while not self._block_follow():
            if self.check("return"):
                body.append(self.retstat())
                break
            st = self.statement()
            if st is not None:
                body.append(st)
        return body

    def retstat(self):
        line = self.next().line
        exprs = []
        if not self._block_follow() and not self.check(";"):
            exprs = self.exprlist()
        self.accept(";")
        return Node("Return", line, exprs=exprs)

    def statement(self):
        t = self.tok
        line = t.line
        if t.type == "op":
            if t.value == ";":
                self.next()
                return None
            if t.value == "::":
                self.next()
                label = self.name()
                self.expect("::")
                return Node("Label", line, name=label)
        if t.type == "kw":
            v = t.value
            if v == "if":
                return self.ifstat()
            if v == "while":
                self.next()
                cond = self.expr()
                self.expect("do")
                body = self.block()
                self.expect("end", "while", line)
                return Node("While", line, cond=cond, body=body)
            if v == "do":
                self.next()
                body = self.block()
                self.expect("end", "do", line)
                return Node("Do", line, body=body)
            if v == "for":
                return self.forstat()
            if v == "repeat":
                self.next()
                body = self.block()
                self.expect("until", "repeat", line)
                return Node("Repeat", line, body=body, cond=self.expr())
            if v == "function":
                return self.funcstat()
            if v == "local":
                self.next()
                if self.accept("function"):
                    name = self.name()
                    return Node("LocalFunc", line, name=name, func=self.funcbody(line, name))
                names, attribs = [self.name()], [self._attrib()]
                while self.accept(","):
                    names.append(self.name())
                    attribs.append(self._attrib())
                exprs = self.exprlist() if self.accept("=") else []
                return Node("Local", line, names=names, attribs=attribs, exprs=exprs)
            if v == "goto":
                self.next()
                return Node("Goto", line, label=self.name())
            if v == "break":
                self.next()
                return Node("Break", line)
        return self.exprstat()

    def _attrib(self):
        # Lua 5.4's <const>/<close>; harmless to accept
        if self.check("<") and self.peek().type == "name" and self.peek(2).value == ">":
            self.next()
            a = self.name()
            self.next()
            return a
        return None

    def ifstat(self):
        line = self.next().line
        clauses = []
        cond = self.expr()
        self.expect("then")
        clauses.append((cond, self.block()))
        orelse = None
        while True:
            if self.accept("elseif"):
                cond = self.expr()
                self.expect("then")
                clauses.append((cond, self.block()))
            elif self.accept("else"):
                orelse = self.block()
                self.expect("end", "if", line)
                break
            else:
                self.expect("end", "if", line)
                break
        return Node("If", line, clauses=clauses, orelse=orelse)

    def forstat(self):
        line = self.next().line
        first = self.name()
        if self.accept("="):
            start = self.expr()
            self.expect(",")
            stop = self.expr()
            step = self.expr() if self.accept(",") else None
            self.expect("do")
            body = self.block()
            self.expect("end", "for", line)
            return Node("NumFor", line, var=first, start=start, stop=stop, step=step, body=body)
        names = [first]
        while self.accept(","):
            names.append(self.name())
        self.expect("in")
        exprs = self.exprlist()
        self.expect("do")
        body = self.block()
        self.expect("end", "for", line)
        return Node("GenFor", line, names=names, exprs=exprs, body=body)

    def funcstat(self):
        line = self.next().line
        n = self.name()
        target = Node("Name", line, name=n)
        full = n
        method = None
        while self.check("."):
            self.next()
            key = self.name()
            target = Node("Index", line, obj=target, key=Node("String", line, value=key.encode()))
            full += "." + key
        if self.accept(":"):
            method = self.name()
            full += ":" + method
        func = self.funcbody(line, full, is_method=method is not None)
        return Node("FuncStat", line, target=target, method=method, func=func)

    def funcbody(self, line, name=None, is_method=False):
        self.expect("(")
        params, vararg = (["self"] if is_method else []), False
        if not self.check(")"):
            while True:
                if self.accept("..."):
                    vararg = True
                    break
                params.append(self.name())
                if not self.accept(","):
                    break
        self.expect(")")
        body = self.block()
        self.expect("end", "function", line)
        return Node("Function", line, params=params, vararg=vararg, body=body, name=name)

    def exprstat(self):
        line = self.tok.line
        e = self.suffixedexp()
        if self.check("=") or self.check(","):
            targets = [e]
            while self.accept(","):
                targets.append(self.suffixedexp())
            self.expect("=")
            for t in targets:
                if t.kind not in ("Name", "Index"):
                    raise LuaSyntaxError("syntax error near '='", line)
            return Node("Assign", line, targets=targets, exprs=self.exprlist())
        if e.kind not in ("Call", "Method"):
            raise LuaSyntaxError("syntax error near %s" % self._near(), self.tok.line)
        return Node("CallStat", line, call=e)

    # expressions
    def exprlist(self):
        out = [self.expr()]
        while self.accept(","):
            out.append(self.expr())
        return out

    def expr(self, limit=0):
        t = self.tok
        if (t.type == "kw" and t.value == "not") or (t.type == "op" and t.value in ("-", "#", "~")):
            self.next()
            operand = self.expr(UNARY_PRIORITY)
            left = Node("Unop", t.line, op=t.value, operand=operand)
        else:
            left = self.simpleexp()
        while True:
            t = self.tok
            op = t.value if t.type in ("op", "kw") else ""
            prio = BINARY_PRIORITY.get(op)
            if prio is None or prio[0] <= limit:
                return left
            self.next()
            right = self.expr(prio[1])
            left = Node("Binop", t.line, op=op, left=left, right=right)

    def simpleexp(self):
        t = self.tok
        line = t.line
        if t.type == "num":
            self.next()
            return Node("Number", line, value=t.value)
        if t.type == "str":
            self.next()
            return Node("String", line, value=t.value)
        if t.type == "kw":
            if t.value == "nil":
                self.next()
                return Node("Nil", line)
            if t.value == "true":
                self.next()
                return Node("True", line)
            if t.value == "false":
                self.next()
                return Node("False", line)
            if t.value == "function":
                self.next()
                return self.funcbody(line)
        if t.type == "op":
            if t.value == "...":
                self.next()
                return Node("Vararg", line)
            if t.value == "{":
                return self.table()
        return self.suffixedexp()

    def primaryexp(self):
        t = self.tok
        if t.type == "name":
            self.next()
            return Node("Name", t.line, name=t.value)
        if t.type == "op" and t.value == "(":
            self.next()
            e = self.expr()
            self.expect(")", "(", t.line)
            return Node("Paren", t.line, expr=e)
        raise LuaSyntaxError("unexpected symbol near %s" % self._near(), t.line)

    def suffixedexp(self):
        e = self.primaryexp()
        while True:
            t = self.tok
            if t.type == "op" and t.value == ".":
                self.next()
                key = self.name()
                e = Node("Index", t.line, obj=e, key=Node("String", t.line, value=key.encode()))
            elif t.type == "op" and t.value == "[":
                self.next()
                key = self.expr()
                self.expect("]")
                e = Node("Index", t.line, obj=e, key=key)
            elif t.type == "op" and t.value == ":":
                self.next()
                name = self.name()
                e = Node("Method", t.line, obj=e, name=name, args=self.callargs())
            elif (t.type == "op" and t.value in ("(", "{")) or t.type == "str":
                e = Node("Call", t.line, func=e, args=self.callargs())
            else:
                return e

    def callargs(self):
        t = self.tok
        if t.type == "str":
            self.next()
            return [Node("String", t.line, value=t.value)]
        if t.type == "op" and t.value == "{":
            return [self.table()]
        self.expect("(")
        if self.accept(")"):
            return []
        args = self.exprlist()
        self.expect(")", "(", t.line)
        return args

    def table(self):
        line = self.expect("{").line
        fields = []
        while not self.check("}"):
            t = self.tok
            if t.type == "op" and t.value == "[":
                self.next()
                key = self.expr()
                self.expect("]")
                self.expect("=")
                fields.append(Node("Field", t.line, key=key, value=self.expr()))
            elif t.type == "name" and self.peek().type == "op" and self.peek().value == "=":
                self.next()
                self.next()
                fields.append(Node("Field", t.line, key=Node("String", t.line, value=t.value.encode()),
                                   value=self.expr()))
            else:
                fields.append(Node("Field", t.line, key=None, value=self.expr()))
            if not (self.accept(",") or self.accept(";")):
                break
        self.expect("}", "{", line)
        return Node("Table", line, fields=fields)


def parse(src):
    """The body (a list of statements) of a Lua chunk."""
    return Parser(src).chunk()


def walk(node):
    """Every Node under (and including) `node`, or under every node of a list, depth first."""
    stack = [node]
    while stack:
        n = stack.pop()
        if isinstance(n, Node):
            yield n
            stack.extend(reversed(list(_children(n))))
        elif isinstance(n, (list, tuple)):
            stack.extend(reversed(n))


def _children(n):
    for v in n.f.values():
        if isinstance(v, Node):
            yield v
        elif isinstance(v, (list, tuple)):
            for item in v:
                if isinstance(item, (Node, list, tuple)):
                    yield item


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    bad = 0
    for path in argv:
        with open(path, encoding="utf-8", errors="surrogateescape") as f:
            src = f.read()
        try:
            parse(src)
            print("ok   %s" % path)
        except LuaSyntaxError as e:
            bad += 1
            print("FAIL %s: %s" % (path, e))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
