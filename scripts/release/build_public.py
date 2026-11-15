#!/usr/bin/python3 -I
"""Build and check the public copy of a release. Fails closed: nothing is
usable unless every check passes.

  build_public.py REF OUTDIR --wordlist FILE [--message TEXT ...]
      (or EDC_WORDLIST env var with the list's lines instead of --wordlist)

Steps:
  1. git archive REF  -> OUTDIR   (only committed files; untracked/ignored can't slip in)
  2. remove private/ and every path listed in private/public-exclude.txt
  3. pattern checks (tools/check_repo.py: emails, IPs, MACs) on the copy
  4. the private word list (regular expressions, one per line) against the
     CONTENT and the PATH of every file, and against the commit/tag messages.
     Missing or empty list = fail. Non-UTF-8 file = fail, except a PNG in
     docs/images/ whose sha256 is in docs/images/approved.sha256 and that has
     no metadata chunks (check_repo.image_problem). Matches are never printed.
  5. relative links in Markdown files must resolve inside the copy
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
import check_repo  # noqa: E402


class PublishError(Exception):
    pass


def load_wordlist(path=None, env_text=None):
    if path:
        if not os.path.exists(path):
            raise PublishError("word list file is missing")
        with open(path, encoding="utf-8") as f:
            text = f.read()
    elif env_text is not None:
        text = env_text
    else:
        raise PublishError("no word list given (--wordlist FILE or EDC_WORDLIST)")
    patterns = []
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line, re.I))
        except re.error:
            raise PublishError("word list line %d is not a valid regular expression" % i)
    if not patterns:
        raise PublishError("the word list is empty")
    return patterns


def archive(ref, out, repo="."):
    if os.path.exists(out) and os.listdir(out):
        raise PublishError("output directory %s is not empty" % out)
    os.makedirs(out, exist_ok=True)
    data = subprocess.run(["git", "-C", repo, "archive", "--format=tar", ref],
                          capture_output=True, check=True).stdout
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            t.extractall(out, filter="data")      # refuses links/paths pointing outside
    except tarfile.TarError:
        raise PublishError("the release contains an unsafe entry (a link or path pointing "
                           "outside the copy); refused, path withheld")


def remove_private(out):
    excl = os.path.join(out, "private", "public-exclude.txt")
    paths = []
    if os.path.exists(excl):
        with open(excl, encoding="utf-8") as f:
            paths = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    for p in paths + ["private"]:
        if p.startswith("/") or ".." in p.split("/"):
            raise PublishError("bad path in public-exclude.txt (line skipped would be unsafe)")
        full = os.path.join(out, p)
        if os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.exists(full):
            os.unlink(full)
    return paths


def all_files(out):
    for d, _dirs, names in os.walk(out):
        for n in names:
            yield os.path.relpath(os.path.join(d, n), out).replace(os.sep, "/")


def wordlist_check(out, patterns, messages):
    problems = []
    for rel in sorted(all_files(out)):
        if any(p.search(rel) for p in patterns):
            # The path itself is the private value: never print it.
            problems.append("a file NAME matches a word-list entry (path withheld)")
            continue
        try:
            with open(os.path.join(out, rel), encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            bad = check_repo.image_problem(out, rel)
            if bad:
                problems.append(bad)
            continue
        if any(p.search(text) for p in patterns):
            problems.append("%s: a word-list entry matches the content" % rel)
    for i, msg in enumerate(messages, 1):
        if any(p.search(msg) for p in patterns):
            problems.append("release message %d: a word-list entry matches" % i)
    return problems


LINK = re.compile(r"\]\(([^)\s]+)\)")


def link_check(out):
    problems = []
    for rel in all_files(out):
        if not rel.lower().endswith(".md"):
            continue
        with open(os.path.join(out, rel), encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                for target in LINK.findall(line):
                    if re.match(r"(https?:|mailto:|#)", target):
                        continue
                    path = target.split("#", 1)[0]
                    if not path:
                        continue
                    full = os.path.normpath(os.path.join(out, os.path.dirname(rel), path))
                    if not full.startswith(os.path.abspath(out)) or not os.path.exists(full):
                        problems.append("%s:%d: link to a file that isn't in the public copy" % (rel, n))
    return problems


def symlinks(out):
    """Symbolic links anywhere in the copy (files or directories)."""
    found = 0
    for d, dirs, names in os.walk(out):
        for n in dirs + names:
            if os.path.islink(os.path.join(d, n)):
                found += 1
    return found


def build(ref, out, patterns, messages=(), repo="."):
    archive(ref, out, repo)
    remove_private(out)
    # A link's target is text no check reads, and following it could read files
    # from outside the copy: refuse links outright (fail closed, path withheld).
    n = symlinks(out)
    if n:
        raise PublishError("the public copy contains %d symbolic link(s); they are not allowed" % n)
    problems = check_repo.check(out)
    problems += wordlist_check(out, patterns, list(messages))
    problems += link_check(out)
    if problems:
        raise PublishError("the public copy failed its checks:\n  " + "\n  ".join(problems))
    return sorted(all_files(out))


def explain(root, wordlist_path):
    """Local diagnosis for the maintainer: which word-list LINE NUMBER matches which
    file:line. Never prints the pattern or the matched text."""
    with open(wordlist_path, encoding="utf-8") as f:
        lines = [(n, l.strip()) for n, l in enumerate(f, 1) if l.strip() and not l.strip().startswith("#")]
    pats = [(n, re.compile(l, re.I)) for n, l in lines]
    hits = 0
    for rel in sorted(check_repo.files_in(root)):
        if rel.startswith("private/"):
            continue
        for n, p in pats:
            if p.search(rel):
                print("word-list line %d matches the NAME of a file (path withheld)" % n)
                hits += 1
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                for ln, text in enumerate(f, 1):
                    for n, p in pats:
                        if p.search(text):
                            print("word-list line %d matches %s:%d" % (n, rel, ln))
                            hits += 1
        except (UnicodeDecodeError, OSError):
            continue
    print("explain: %d match(es)" % hits)
    return 1 if hits else 0


def main(argv):
    args = argv[1:]
    if args[:1] == ["--explain"]:
        if len(args) < 2 or not os.path.isfile(args[1]):
            print("usage: build_public.py --explain WORDLIST_FILE [DIR]", file=sys.stderr)
            return 2
        return explain(args[2] if len(args) > 2 else ".", args[1])
    try:
        ref, out = args[0], args[1]
        wl = args[args.index("--wordlist") + 1] if "--wordlist" in args else None
        msgs = [args[i + 1] for i, a in enumerate(args) if a == "--message"]
        patterns = load_wordlist(wl, os.environ.get("EDC_WORDLIST"))
        files = build(ref, out, patterns, msgs)
    except (PublishError, IndexError, subprocess.CalledProcessError) as e:
        print("build_public: STOPPED, nothing is published.\n%s" % e, file=sys.stderr)
        return 1
    print("build_public: OK, %d files in %s" % (len(files), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
