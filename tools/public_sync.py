#!/usr/bin/env python3
"""
public_sync.py - build the public copy's next commit from the private archive, and check it.

The project lives in a private archive; a public copy carries the same work minus what must
stay private (vendor material, the owner's machine details, held-back experiments). Doing that
by hand each time is how things leak, so this tool does it the same way every time:

  build    turn an archive commit into the next commit on the public line: drop the EXCLUDE
           paths, apply the SCRUB rules to text files, check the result, and point a local
           branch at it. The commit's only parent is the public base, so archive history can
           never become part of the public line.
  check    check any commit (for example the live public main) against the same rules.
  rewrite  replay the whole public line through the rules, commit by commit, to purge what
           older public commits still contain. Builds a local branch only.

Nothing here pushes. Publishing stays a deliberate step with the owner's word; the tool prints
the push command. A rewritten history also needs a force-push, which the owner must name.

It works on git objects through a temporary index, so no checkout is touched:

  git fetch https://github.com/<owner>/<public-repo>.git main:public-main
  python tools/public_sync.py build --archive origin/main --public public-main
  python tools/public_sync.py check public-next
  python tools/public_sync.py rewrite --public public-main

Personal patterns that must never be written into a public file - a local username, an email
address - go in private/public-sync-denylist.txt (one regex per line). private/ is git-ignored,
so the patterns are enforced on the owner's machine without being published here.

Standard library only; needs git on PATH.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tempfile

# ---- what stays private -------------------------------------------------------------------
# Repo-relative paths, fnmatch-style. A pattern ending in "/" means everything under that folder.
EXCLUDE = [
    "experiments/dm_md/",                       # held back by the owner (2026-10-02): parked work
    "experiments/validator_differential/*.exe",  # compiled binaries
    "private/",                                 # never published (also git-ignored)
    "*__pycache__/*", "*.pyc",                   # byte code embeds the absolute path it was built from
    # The 2026-10-02 audit of the public copy:
    "tools/out/verdicts/workflows/",            # raw run records: prompts, local paths, third-party names
    "notes/2026-09-pack-up.md",                 # the owner's retired workstation, described
    "evidence/screenshots/GCP_43OeNbeFz0.png",  # GC's status bar shows the licensee's account;
    "evidence/screenshots/GCP_bqttzh6WXR.png",  # most also show lab addresses
    "evidence/screenshots/automation-gcp1.png",
    "evidence/screenshots/automation-gcp2.png",
    "evidence/screenshots/automation-gcp3.png",
    "evidence/screenshots/automation-gcp4.png",
    "evidence/test-logs/corpus_commit.log",     # the vendor corpus being committed and pushed
    "evidence/test-logs/copy_corpus.log",
    "evidence/test-logs/push*.log",             # push transcripts, credential prompts
    "reference/crestron-visca/COMMANDS.md",     # vendor documentation transcribed at length
    "reference/biamp-ttp/SYNTAX.md",
    "reference/crestron-nextgen-cameras/ZOOM.md",
]

# Text rewrites applied to every text file that is published. (pattern, replacement).
_SEP = r"(?:\\+|/)"             # any run of backslashes (JSON escapes nest), or a slash
_NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"   # a user name; never starts with a dot, so `\.noreply` is safe
_SKIP = r"(?!Public\b|Default\b|All Users\b|Shared\b|<user>)"   # shared folders, and done ones
SCRUB = [
    # an absolute path to a checkout of this repository -> <repo> (it says where the owner keeps
    # things, and means nothing in any other checkout). First, before <user> blocks the match.
    (re.compile(r"(?i)\b[A-Z]:(?:\\+|/)(?:[^\s\"'`<>|*?]+?(?:\\+|/))?extron-driver-convert(?:-archive)?\b"),
     "<repo>"),
    (re.compile(r"(?<![\w.:/])/(?:[^\s\"'`<>|*?/]+/)+extron-driver-convert(?:-archive)?\b"), "<repo>"),
    # a Windows home folder other than the shared Public/Default ones -> <user>
    (re.compile(r"(?i)\b([A-Z]):(" + _SEP + r")Users(" + _SEP + r")" + _SKIP + _NAME), r"\1:\2Users\3<user>"),
    # the same in Git Bash form (/c/Users/…)
    (re.compile(r"(?i)/([a-z])/Users/" + _SKIP + _NAME), r"/\1/Users/<user>"),
    # macOS and Linux home folders
    (re.compile(r"/(Users|home)/" + _SKIP + _NAME + r"(?=/)"), r"/\1/<user>"),
    # a home folder flattened into a folder name, as Claude Code names its project folders
    # (C--Users-…-git-…, -Users-…-GitHub-…)
    (re.compile(r"(?i)((?:\b[A-Z]-)?-Users-)(?!<user>)[A-Za-z0-9][A-Za-z0-9._]*(?=-)"), r"\1<user>"),
    # a Windows home folder written without its drive (Users\…\Downloads)
    (re.compile(r"(?i)\b(Users)(\\+)" + _SKIP + _NAME + r"(?=\\)"), r"\1\2<user>"),
    # run instructions for an excluded experiment
    (re.compile(r"(?m)^python[0-9.]* -u experiments/dm_md/\S+\n"), ""),
]

# Binary files that may be published, each one looked at by a person: no text check can see
# into an image, and GC's screenshots carry the licensee's account. A new binary is refused
# until it is reviewed and listed here.
BINARY_OK = [
    "evidence/screenshots/GCP_OJ8lgWOFHo.png",              # Driver Manager list only
    "experiments/skeleton_i20/hardware/80085-invalid-driver.png",  # GC's error dialog only
]

# What the published result must not contain: these refuse a build. (name, pattern)
LEAKS = [
    ("home path", re.compile(r"(?i)\b[A-Z]:" + _SEP + r"Users" + _SEP + _SKIP + _NAME)),
    ("home path", re.compile(r"(?i)/[a-z]/Users/" + _SKIP + _NAME)),
    ("home path", re.compile(r"/(?:Users|home)/" + _SKIP + _NAME + r"/")),
    ("home path", re.compile(r"(?i)-Users-(?!<user>)[A-Za-z0-9][A-Za-z0-9._]*-")),
    ("home path", re.compile(r"(?i)\bUsers\\+" + _SKIP + _NAME + r"\\")),
    ("credential in URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@'\"<>]+:[^/\s@'\"<>]+@[A-Za-z0-9.-]+")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("CIP panel notes", re.compile(r"(?i)\bcipclient\b")),
]

# Worth a look but not refused: the repo legitimately carries factory-default and example
# addresses (192.168.254.254 is Extron's default) and vendor support addresses. The owner's own
# addresses belong in the private denylist, which does refuse.
NOTES = [
    ("private IPv4", re.compile(r"(?<![\d.])(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|"
                                r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|169\.254\.\d{1,3}\.\d{1,3})(?![\d.])")),
]
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_OK = re.compile(r"(?i)^(?:noreply@anthropic\.com|noreply@github\.com|[^@]+@users\.noreply\.github\.com|"
                      r"[^@]+@example\.(?:com|org|net)|[^@]+@yourdomain\.com)$")

DENYLIST_FILE = os.path.join("private", "public-sync-denylist.txt")
# Private rewrites, applied after SCRUB: "regex<TAB>replacement" per line. For what must be
# rewritten rather than refused - chiefly in older commits, which `rewrite` cannot edit by hand -
# without the text being rewritten ever appearing in a tracked file.
REPLACE_FILE = os.path.join("private", "public-sync-replace.tsv")
EXTRA_SCRUB = []
MANIFEST = "vendor-files.manifest.tsv"


# ---- git plumbing ---------------------------------------------------------------------------
class Git:
    def __init__(self, repo):
        self.repo = repo
        self._cat = None
        self._blobs = {}          # blob sha -> bytes
        self._scrubbed = {}       # blob sha -> scrubbed blob sha (or same)

    def run(self, *args, input=None, env=None):
        e = dict(os.environ)
        if env:
            e.update(env)
        p = subprocess.run(["git", "-C", self.repo] + list(args), input=input, capture_output=True, env=e)
        if p.returncode != 0:
            raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace").strip()))
        return p.stdout

    def text(self, *args, **kw):
        return self.run(*args, **kw).decode("utf-8", "replace")

    def rev(self, name):
        return self.text("rev-parse", "--verify", name + "^{commit}").strip()

    def blob(self, sha):
        if sha not in self._blobs:
            if self._cat is None:
                self._cat = subprocess.Popen(["git", "-C", self.repo, "cat-file", "--batch"],
                                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            pipe_in, pipe_out = self._cat.stdin, self._cat.stdout
            assert pipe_in is not None and pipe_out is not None
            pipe_in.write(sha.encode() + b"\n")
            pipe_in.flush()
            header = pipe_out.readline().split()
            size = int(header[2])
            data = pipe_out.read(size)
            pipe_out.read(1)
            self._blobs[sha] = data
        return self._blobs[sha]

    def entries(self, treeish):
        """(mode, type, sha, path) for every file of a tree."""
        out = self.run("ls-tree", "-r", "-z", "--full-tree", treeish)
        rows = []
        for item in out.split(b"\0"):
            if not item:
                continue
            meta, path = item.split(b"\t", 1)
            mode, typ, sha = meta.decode().split()
            rows.append((mode, typ, sha, path.decode("utf-8")))
        return rows

    def close(self):
        if self._cat:
            if self._cat.stdin:
                self._cat.stdin.close()
            self._cat.wait()


def is_binary(data):
    if b"\0" in data[:8192]:
        return True
    try:
        data.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def excluded(path, patterns=EXCLUDE):
    for p in patterns:
        if p.endswith("/"):
            if path.startswith(p):
                return True
        elif fnmatch.fnmatchcase(path, p):
            return True
    return False


def scrub_text(text):
    for rx, rep in SCRUB + EXTRA_SCRUB:
        text = rx.sub(rep, text)
    return text


def load_replacements(repo):
    """The private rewrite rules, or [] when the file is absent."""
    path = os.path.join(repo, REPLACE_FILE)
    rules = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.rstrip("\r\n")
                if not line.strip() or line.startswith("#"):
                    continue
                if "\t" not in line:
                    raise ValueError("%s:%d: expected regex<TAB>replacement" % (REPLACE_FILE, n))
                rx, rep = line.split("\t", 1)
                rules.append((re.compile(rx), rep))
    return rules


def load_denylist(repo):
    path = os.path.join(repo, DENYLIST_FILE)
    pats = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pats.append(("private denylist", re.compile(line)))
    return pats


# ---- transform and check ------------------------------------------------------------------
def transform(git, treeish):
    """The public version of a tree: excluded paths dropped, text scrubbed. Returns a tree sha."""
    lines = []
    for mode, typ, sha, path in git.entries(treeish):
        if excluded(path):
            continue
        if typ == "blob" and mode in ("100644", "100755"):
            if sha not in git._scrubbed:
                data = git.blob(sha)
                new = sha
                if not is_binary(data):
                    text = data.decode("utf-8")
                    out = scrub_text(text)
                    if out != text:
                        new = git.text("hash-object", "-w", "--stdin", input=out.encode("utf-8")).strip()
                git._scrubbed[sha] = new
            sha = git._scrubbed[sha]
        lines.append("%s %s %s\t%s" % (mode, typ, sha, path))
    fd, index = tempfile.mkstemp(prefix="public-sync-index-")
    os.close(fd)
    os.unlink(index)                               # git creates it fresh
    try:
        env = {"GIT_INDEX_FILE": index}
        git.run("update-index", "--index-info", input=("\n".join(lines) + "\n").encode("utf-8"), env=env)
        return git.text("write-tree", env=env).strip()
    finally:
        if os.path.exists(index):
            os.unlink(index)


def check_text(where, text, extra=()):
    """(problems, notes) in one text, each a list of (where, line, kind, excerpt)."""
    problems, notes = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, rx in list(LEAKS) + list(extra):
            m = rx.search(line)
            if m:
                problems.append((where, lineno, kind, _mask(m.group(0))))
        for kind, rx in NOTES:
            m = rx.search(line)
            if m:
                notes.append((where, lineno, kind, _mask(m.group(0))))
        for m in EMAIL.finditer(line):
            if not EMAIL_OK.match(m.group(0)):
                notes.append((where, lineno, "email address", _mask(m.group(0))))
    return problems, notes


def check_tree(git, treeish, manifest_paths=(), extra=(), notes=None):
    """Problems in a tree that is meant to be public: list of (path, line, kind, excerpt).
    Advisory findings are appended to `notes` when a list is given."""
    problems = []
    vendor = set(manifest_paths)
    for mode, typ, sha, path in git.entries(treeish):
        if typ != "blob":
            continue
        if excluded(path):
            problems.append((path, 0, "excluded path present", ""))
            continue
        if path in vendor:
            problems.append((path, 0, "vendor manifest path present", ""))
        data = git.blob(sha)
        if is_binary(data):
            if not any(fnmatch.fnmatchcase(path, g) for g in BINARY_OK):
                problems.append((path, 0, "binary file not reviewed (BINARY_OK)", ""))
            continue
        p, n = check_text(path, data.decode("utf-8"), extra)
        problems += p
        if notes is not None:
            notes += n
    return problems


def check_message(git, commit, extra=()):
    """Blocking problems in a commit's message. Author and committer identity are left to the
    owner's git config and not checked."""
    text = git.text("log", "-1", "--format=%B", commit)
    return [(p[0], p[1], p[2] + " (in %s)" % commit[:7], p[3])
            for p in check_text("<commit message>", text, extra)[0]]


def _mask(s):
    s = s.strip()
    return s if len(s) <= 6 else s[:3] + "***" + s[-2:]


def manifest_paths(git, treeish):
    try:
        text = git.blob(_path_sha(git, treeish, MANIFEST)).decode("utf-8", "replace")
    except (KeyError, RuntimeError):
        return []
    out = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and not line.startswith("#"):
            out.append(parts[2])
    return out


def _path_sha(git, treeish, path):
    for mode, typ, sha, p in git.entries(treeish):
        if p == path:
            return sha
    raise KeyError(path)


def commit_meta(git, rev):
    fmt = "%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%B"
    an, ae, ad, cn, ce, cd, body = git.text("log", "-1", "--format=" + fmt, rev).split("\0", 6)
    env = {"GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae, "GIT_AUTHOR_DATE": ad,
           "GIT_COMMITTER_NAME": cn, "GIT_COMMITTER_EMAIL": ce, "GIT_COMMITTER_DATE": cd}
    return env, body


def report(problems, out=None):
    out = out or sys.stdout
    for path, line, kind, excerpt in problems:
        out.write("  %s:%s  %s  %s\n" % (path, line or "-", kind, excerpt))


def report_notes(notes):
    if notes:
        print("%d note(s), not refused - check that none is the owner's own:" % len(notes))
        report(notes)


# ---- commands -----------------------------------------------------------------------------
def cmd_build(args):
    git = Git(args.repo)
    try:
        archive, public = git.rev(args.archive), git.rev(args.public)
        tree = transform(git, archive)
        notes = []
        problems = check_tree(git, tree, manifest_paths(git, archive), load_denylist(args.repo), notes)
        report_notes(notes)
        if problems:
            print("NOT BUILT: the public tree would contain %d problem(s):" % len(problems))
            report(problems)
            return 1
        if tree == git.text("rev-parse", public + "^{tree}").strip():
            print("Nothing to publish: %s already matches." % args.public)
            return 0
        msg = args.message or ("Public sync from the project's main line\n\nBuilt by tools/public_sync.py: "
                               "private paths excluded and personal paths scrubbed.\n")
        commit = git.text("commit-tree", tree, "-p", public, "-F", "-", input=msg.encode("utf-8")).strip()
        git.run("update-ref", "refs/heads/" + args.branch, commit)
        print("built %s on %s (branch %s). Checked: clean." % (commit[:7], public[:7], args.branch))
        print("To publish (needs the owner's word):  git push <public-repo-url> %s:main" % args.branch)
        return 0
    finally:
        git.close()


def cmd_check(args):
    git = Git(args.repo)
    try:
        rev = git.rev(args.rev)
        deny = load_denylist(args.repo)
        notes = []
        problems = check_tree(git, rev, manifest_paths(git, args.manifest_from or rev), deny, notes)
        if args.history:
            for c in git.text("rev-list", rev).split():
                problems += check_message(git, c, deny)
                if c == rev:
                    continue
                for p in check_tree(git, c, (), deny):
                    problems.append((p[0], p[1], p[2] + " (in %s)" % c[:7], p[3]))
        report_notes(notes)
        if problems:
            print("%d problem(s) in %s:" % (len(problems), args.rev))
            report(problems)
            return 1
        print("clean: %s%s" % (args.rev, " and its history" if args.history else ""))
        return 0
    finally:
        git.close()


def cmd_rewrite(args):
    git = Git(args.repo)
    try:
        public = git.rev(args.public)
        commits = git.text("rev-list", "--reverse", "--topo-order", public).split()
        mapped = {}
        for c in commits:
            parents = git.text("rev-list", "--parents", "-n", "1", c).split()[1:]
            env, body = commit_meta(git, c)
            tree = transform(git, c)
            pargs = []
            for p in parents:
                pargs += ["-p", mapped[p]]
            body = scrub_text(body)
            mapped[c] = git.text("commit-tree", tree, *pargs, "-F", "-", input=body.encode("utf-8"), env=env).strip()
        tip = mapped[public]
        deny = load_denylist(args.repo)
        problems = []
        for c in commits:
            problems += check_message(git, mapped[c], deny)
            for p in check_tree(git, mapped[c], (), deny):
                problems.append((p[0], p[1], p[2] + " (in %s)" % mapped[c][:7], p[3]))
        if problems:
            print("NOT BUILT: the rewritten history would still contain %d problem(s):" % len(problems))
            report(problems)
            return 1
        git.run("update-ref", "refs/heads/" + args.branch, tip)
        print("rewrote %d commit(s): %s -> %s (branch %s). Every commit checked: clean."
              % (len(commits), public[:7], tip[:7], args.branch))
        print("To replace the public history (a force-push; the owner must name it):")
        print("  git push --force <public-repo-url> %s:main" % args.branch)
        return 0
    finally:
        git.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build and check the public copy from the private archive.")
    ap.add_argument("--repo", default=".", help="the repository (default: current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("--archive", required=True, help="archive commit to publish (e.g. origin/main)")
    p.add_argument("--public", required=True, help="tip of the public line (e.g. public-main)")
    p.add_argument("--branch", default="public-next")
    p.add_argument("--message")
    p.set_defaults(fn=cmd_build)
    p = sub.add_parser("check")
    p.add_argument("rev")
    p.add_argument("--history", action="store_true", help="also check every ancestor commit")
    p.add_argument("--manifest-from", help="read the vendor manifest from this commit instead")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("rewrite")
    p.add_argument("--public", required=True)
    p.add_argument("--branch", default="public-rewritten")
    p.set_defaults(fn=cmd_rewrite)
    args = ap.parse_args(argv)
    EXTRA_SCRUB[:] = load_replacements(args.repo)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
