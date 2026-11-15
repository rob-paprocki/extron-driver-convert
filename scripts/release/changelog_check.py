#!/usr/bin/python3 -I
"""Flag commits that change user-visible files without touching CHANGELOG.md.

  changelog_check.py [BASE]     commits in BASE..HEAD (default: since the last
                                v* tag, or since CHANGELOG.md was added)

A commit can opt out with "[no changelog]" in its message (typos, tests,
invisible refactors). Exit 1 if any commit is flagged.
"""
import subprocess
import sys

VISIBLE = ("tools/", "gui/", "packaging/", "findings/", "docs/", "STATUS.md", "ROADMAP.md",
           "README.md", "LICENSE")


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, check=True).stdout


def default_base():
    tags = git("tag", "--list", "v*", "--sort=-v:refname").split()
    if tags:
        return tags[0]
    added = git("log", "--diff-filter=A", "--format=%H", "--", "CHANGELOG.md").split()
    return added[-1] if added else None


def flagged(base):
    rng = "%s..HEAD" % base if base else "HEAD"
    out = []
    for sha in git("rev-list", "--no-merges", rng).split():
        msg = git("log", "-1", "--format=%B", sha)
        if "[no changelog]" in msg:
            continue
        files = git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).split()
        if "CHANGELOG.md" in files:
            continue
        visible = [f for f in files if not f.startswith("private/") and
                   any(f == v or f.startswith(v) for v in VISIBLE)]
        if visible:
            out.append((sha[:10], msg.splitlines()[0] if msg else "", visible))
    return out


def main(argv):
    base = argv[1] if len(argv) > 1 else default_base()
    bad = flagged(base)
    for sha, subject, files in bad:
        print("%s %s\n    changes %s but not CHANGELOG.md (add a line, or put "
              "[no changelog] in the message)" % (sha, subject, ", ".join(files[:5])))
    print("changelog check: %s" % ("%d commit(s) need a changelog line" % len(bad) if bad else "OK"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
