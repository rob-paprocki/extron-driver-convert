"""Tests of the release tooling: pattern checks, public-copy builder, changelog, publisher."""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check_repo = load("check_repo", os.path.join(HERE, "check_repo.py"))
build = load("build_public", os.path.join(ROOT, "scripts", "release", "build_public.py"))
changelog = load("changelog", os.path.join(ROOT, "scripts", "release", "changelog.py"))
publish = load("publish_public", os.path.join(ROOT, "scripts", "release", "publish_public.py"))

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def IP(*parts):
    return ".".join(parts)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True,
                          check=True, env=ENV).stdout.strip()


_VIEW = []


def public_view():
    """A temp copy of this working tree as the public repo would get it: tracked files,
    minus private/ and the paths in private/public-exclude.txt."""
    if _VIEW:
        return _VIEW[0]
    exclude_file = os.path.join(ROOT, "private", "public-exclude.txt")
    if not os.path.exists(exclude_file):            # no exclude file: nothing to exclude
        _VIEW.append(ROOT)
        return ROOT
    out = tempfile.mkdtemp()
    with open(exclude_file, encoding="utf-8") as f:
        excl = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    names = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True,
                           check=True).stdout.decode().split(chr(0))
    for rel in names:
        if not rel or rel.startswith("private/") or any(rel == e or rel.startswith(e + "/") for e in excl):
            continue
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), dst)
    _VIEW.append(out)
    return out


def make_repo(files):
    d = tempfile.mkdtemp()
    git(d, "init", "-q", "-b", "main")
    for path, text in files.items():
        p = os.path.join(d, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "init")
    return d


class PatternTests(unittest.TestCase):
    def test_excluded_paths_are_not_checked(self):
        n = "\n"
        d = make_repo({"a.txt": "ok" + n, "lab/log.txt": "x " + IP("10", "20", "30", "40") + n,
                       "private/public-exclude.txt": "lab" + n})
        self.assertEqual(check_repo.check(d), [])

    def kinds(self, text):
        return [k for _, k in check_repo.scan_text(text)]

    def test_allowed_values(self):
        self.assertEqual(self.kinds("gw 192.168.100.1, dns 1.1.1.1, lo 127.0.0.1, doc 203.0.113.9\n"
                                    "mac 00:00:5E:00:53:0a, mail admin@example.com, x@y.invalid, hi@mail.rpaprocki.com\n"
                                    "bcast 255.255.255.255 v6 2001:db8::1 ::1\n"
                                    "time 01:02:52 version 1.2.3 port 8006"), [])

    def test_disallowed_values(self):
        # The "bad" samples are assembled at runtime so that no disallowed value
        # appears literally in this (public) file.
        self.assertEqual(self.kinds(IP("10", "1", "2", "3")), ["IP address"])         # private
        self.assertEqual(self.kinds(IP("100", "64", "1", "2")), ["IP address"])       # CGNAT
        self.assertEqual(self.kinds(IP("8", "8", "4", "5")), ["IP address"])          # public
        self.assertEqual(self.kinds(":".join(["fd12", "3456", "789a", "", "1"])), ["IPv6 address"])
        self.assertEqual(self.kinds(":".join(["e0", "51", "d8", "00", "11", "22"])), ["MAC address"])
        self.assertEqual(self.kinds("me" + "@" + "mail-provider.com"), ["email address"])

    def test_report_never_contains_the_value(self):
        bad = IP("10", "20", "30", "40")
        d = make_repo({"a.txt": "secret %s here\n" % bad, "private/notes.md": bad + "\n"})
        problems = check_repo.check(d)
        self.assertEqual(problems, ["a.txt:1: IP address not allowed in public files"])   # private/ skipped
        self.assertNotIn(bad, "".join(problems))

    def test_this_repo_is_clean(self):
        self.assertEqual(check_repo.check(public_view()), [])


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.wl = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        self.wl.write("SN-ABC123\n")
        self.wl.close()
        self.pat = build.load_wordlist(self.wl.name)

    def out(self):
        return os.path.join(tempfile.mkdtemp(), "copy")

    def test_private_removed_and_excludes_honoured(self):
        d = make_repo({"README.md": "hi [lic](LICENSE)\n", "LICENSE": "GPL\n",
                       "private/plan.md": "mine\n", "private/public-exclude.txt": ".github/workflows/cut.yml\n",
                       ".github/workflows/cut.yml": "private workflow\n"})
        files = build.build("HEAD", self.out(), self.pat, repo=d)
        self.assertEqual(files, ["LICENSE", "README.md"])

    def test_word_in_file_name_fails_without_printing_it(self):
        d = make_repo({"docs/SN-ABC123.md": "nothing\n"})
        with self.assertRaises(build.PublishError) as e:
            build.build("HEAD", self.out(), self.pat, repo=d)
        self.assertNotIn("ABC123", str(e.exception))
        self.assertIn("path withheld", str(e.exception))

    def test_word_in_content_and_message(self):
        d = make_repo({"a.md": "serial sn-abc123\n"})
        with self.assertRaises(build.PublishError):
            build.build("HEAD", self.out(), self.pat, repo=d)
        d2 = make_repo({"a.md": "fine\n"})
        with self.assertRaises(build.PublishError):
            build.build("HEAD", self.out(), self.pat, ["release for SN-ABC123"], repo=d2)

    def test_empty_or_missing_wordlist_fails(self):
        with open(self.wl.name, "w") as f:
            f.write("\n# only a comment\n")
        with self.assertRaises(build.PublishError):
            build.load_wordlist(self.wl.name)
        with self.assertRaises(build.PublishError):
            build.load_wordlist("/nonexistent/wordlist")
        with self.assertRaises(build.PublishError):
            build.load_wordlist(None, None)

    def test_non_utf8_fails(self):
        d = make_repo({"a.md": "x\n"})
        with open(os.path.join(d, "blob.bin"), "wb") as f:
            f.write(b"\xff\xfe\x00bad")
        git(d, "add", "-A")
        git(d, "commit", "-q", "-m", "bin")
        with self.assertRaises(build.PublishError):
            build.build("HEAD", self.out(), self.pat, repo=d)

    def test_link_into_private_fails(self):
        d = make_repo({"README.md": "see [plan](private/plan.md)\n", "private/plan.md": "x\n"})
        with self.assertRaises(build.PublishError) as e:
            build.build("HEAD", self.out(), self.pat, repo=d)
        self.assertIn("link", str(e.exception))

    def _linked_repo(self, target):
        d = make_repo({"a.md": "x\n", "private/secret.md": "mine\n"})
        os.symlink(target, os.path.join(d, "innocent.md"))
        git(d, "add", "-A")
        git(d, "commit", "-q", "-m", "link")
        return d

    def test_relative_symlink_refused(self):
        d = self._linked_repo("private/secret.md")
        with self.assertRaises(build.PublishError) as e:
            build.build("HEAD", self.out(), self.pat, repo=d)
        self.assertIn("symbolic link", str(e.exception))
        self.assertNotIn("secret", str(e.exception))

    def test_absolute_symlink_refused(self):
        d = self._linked_repo("/etc/hosts")
        with self.assertRaises(build.PublishError) as e:
            build.build("HEAD", self.out(), self.pat, repo=d)
        self.assertNotIn("innocent", str(e.exception))

    def test_untracked_files_cannot_slip_in(self):
        d = make_repo({"a.md": "x\n"})
        with open(os.path.join(d, "stray-notes.md"), "w") as f:
            f.write("my %s\n" % IP("10", "9", "8", "7"))
        self.assertEqual(build.build("HEAD", self.out(), self.pat, repo=d), ["a.md"])


CL = """# Changelog

## [Unreleased]

**Upgrading:** nothing to do.

### Fixed
- a bug

## [1.2.3] - 2026-01-01

**Upgrading:** nothing to do.

### Added
- things
"""


def png(*chunks, tail=b""):
    out = b"\x89PNG\r\n\x1a\n"
    for kind, data in (("IHDR", b"\0" * 13),) + chunks + (("IEND", b""),):
        out += len(data).to_bytes(4, "big") + kind.encode() + data + b"\0\0\0\0"
    return out + tail


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "docs", "images"))
        os.makedirs(os.path.join(self.root, "evidence"))

    def put(self, rel, data, approve=True):
        with open(os.path.join(self.root, rel), "wb") as f:
            f.write(data)
        if approve:
            with open(os.path.join(self.root, "docs/images/approved.sha256"), "a") as f:
                f.write("%s  %s\n" % (hashlib.sha256(data).hexdigest(), rel))

    def problems(self):
        return check_repo.check(self.root)

    def test_approved_png_passes(self):
        self.put("docs/images/shot.png", png(("IDAT", b"pixels")))
        self.assertEqual(self.problems(), [])

    def test_unlisted_png_fails(self):
        self.put("docs/images/shot.png", png(("IDAT", b"pixels")), approve=False)
        self.assertTrue(any("not listed" in p for p in self.problems()))

    def test_changed_png_fails(self):
        self.put("docs/images/shot.png", png(("IDAT", b"pixels")))
        with open(os.path.join(self.root, "docs/images/shot.png"), "wb") as f:
            f.write(png(("IDAT", b"other pixels")))
        self.assertTrue(any("not listed" in p for p in self.problems()))

    def test_metadata_chunk_fails_even_if_approved(self):
        self.put("docs/images/shot.png", png(("tEXt", b"Comment\0host secret"), ("IDAT", b"x")))
        self.assertTrue(any("metadata" in p for p in self.problems()))

    def test_data_after_end_fails(self):
        self.put("docs/images/shot.png", png(("IDAT", b"x"), tail=b"hidden"))
        self.assertTrue(any("after its end" in p for p in self.problems()))

    def test_png_outside_images_dir_passes_when_approved(self):
        self.put("evidence/shot.png", png(("IDAT", b"x")))
        self.assertEqual(self.problems(), [])

    def test_non_png_binary_fails(self):
        self.put("tool.exe", b"MZ" + bytes([144, 0, 255, 254]), approve=True)
        self.assertTrue(any("not UTF-8" in p for p in self.problems()))

    def test_approval_is_for_one_name(self):
        data = png(("IDAT", b"x"))
        self.put("docs/images/a.png", data)
        self.put("docs/images/b.png", data, approve=False)
        self.assertTrue(any("b.png" in p and "not listed" in p for p in self.problems()))

    def test_repo_images_pass(self):
        self.assertEqual([p for p in check_repo.check(public_view()) if "approved" in p or "not listed" in p], [])


class ChangelogTests(unittest.TestCase):
    def test_bumps(self):
        self.assertEqual(changelog.plan(CL)["version"], "1.2.4")
        self.assertEqual(changelog.plan(CL.replace("### Fixed", "### Added", 1))["version"], "1.3.0")
        self.assertEqual(changelog.plan(CL.replace("- a bug", "- **Breaking** x", 1))["version"], "2.0.0")
        self.assertEqual(changelog.plan(CL.replace("### Fixed", "### Removed", 1))["version"], "2.0.0")
        self.assertEqual(changelog.plan(CL, bump="minor")["version"], "1.3.0")

    def test_first_release(self):
        first = CL.split("## [1.2.3]")[0]
        self.assertEqual(changelog.plan(first)["version"], "0.1.0")

    def test_upgrading_line_required(self):
        with self.assertRaises(changelog.ChangelogError):
            changelog.plan(CL.replace("**Upgrading:** nothing to do.\n\n### Fixed", "### Fixed", 1))

    def test_finalize(self):
        new = changelog.finalize(CL, "1.2.4", "2026-02-02")
        self.assertIn("## [Unreleased]\n\n## [1.2.4] - 2026-02-02", new)
        self.assertEqual(changelog.notes(new, "1.2.4").splitlines()[0], "**Upgrading:** nothing to do.")
        with self.assertRaises(changelog.ChangelogError):
            changelog.finalize(new, "1.2.3", "2026-02-02")


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.public = make_repo({".github/FUNDING.yml": "github: someone\n"})
        self.copy = tempfile.mkdtemp()
        for path, text in {"README.md": "v1\n", "old.txt": "goes away later\n"}.items():
            with open(os.path.join(self.copy, path), "w") as f:
                f.write(text)

    def test_first_release_then_second_deletes_removed_files(self):
        self.assertEqual(publish.prepare(self.public, self.copy, "1.0.0"), "prepared")
        self.assertEqual(git(self.public, "log", "-1", "--format=%s|%ae"),
                         "extron-driver-convert 1.0.0|41898282+github-actions[bot]@users.noreply.github.com")
        self.assertEqual(git(self.public, "rev-list", "--count", "HEAD"), "2")   # on top of initial
        os.unlink(os.path.join(self.copy, "old.txt"))
        self.assertEqual(publish.prepare(self.public, self.copy, "1.1.0"), "prepared")
        self.assertFalse(os.path.exists(os.path.join(self.public, "old.txt")))
        self.assertEqual(git(self.public, "tag", "--list"), "v1.0.0\nv1.1.0")

    def test_direct_commit_on_public_repo_stops_it(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        with open(os.path.join(self.public, "hotfix.txt"), "w") as f:
            f.write("someone committed here\n")
        git(self.public, "add", "-A")
        git(self.public, "commit", "-q", "-m", "direct")
        with self.assertRaises(publish.PublishError):
            publish.prepare(self.public, self.copy, "1.1.0")

    def test_first_release_refused_if_public_already_has_extra_commits(self):
        with open(os.path.join(self.public, "x.txt"), "w") as f:
            f.write("x\n")
        git(self.public, "add", "-A")
        git(self.public, "commit", "-q", "-m", "extra")
        with self.assertRaises(publish.PublishError):
            publish.prepare(self.public, self.copy, "1.0.0")

    def test_first_release_on_acknowledged_base(self):
        with open(os.path.join(self.public, "x.txt"), "w") as f:
            f.write("maintainer edit\n")
        git(self.public, "add", "-A")
        git(self.public, "commit", "-q", "-m", "maintainer edit")
        head = git(self.public, "rev-parse", "HEAD")
        with self.assertRaises(publish.PublishError):                     # wrong base
            publish.prepare(self.public, self.copy, "1.0.0", first_base="0000000")
        self.assertEqual(publish.prepare(self.public, self.copy, "1.0.0", first_base=head[:7]), "prepared")

    def test_rerun_after_half_done_publish_is_a_no_op(self):
        publish.prepare(self.public, self.copy, "1.0.0")         # tag made, (pretend) push of main failed
        self.assertEqual(publish.prepare(self.public, self.copy, "1.0.0"), "exists")
        with open(os.path.join(self.copy, "README.md"), "w") as f:
            f.write("different\n")
        with self.assertRaises(publish.PublishError):              # same tag, other content
            publish.prepare(self.public, self.copy, "1.0.0")

    def test_older_version_refused(self):
        publish.prepare(self.public, self.copy, "1.1.0")
        with self.assertRaises(publish.PublishError):
            publish.prepare(self.public, self.copy, "1.0.5")

    def _write(self, path, text):
        full = os.path.join(self.copy, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def test_docs_publish_between_releases(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        self._write("README.md", "v1 nicer\n")
        self._write("docs/how.md", "details\n")
        self._write("old.txt", "code change that must NOT go out with docs\n")
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "prepared")
        self.assertEqual(git(self.public, "log", "-1", "--format=%s|%ae"),
                         "extron-driver-convert docs: update|41898282+github-actions[bot]@users.noreply.github.com")
        self.assertEqual(git(self.public, "tag", "--list"), "v1.0.0")          # no tag
        with open(os.path.join(self.public, "old.txt")) as f:
            self.assertEqual(f.read(), "goes away later\n")                   # code untouched
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "unchanged")
        self._write("README.md", "v1 nicer still\n")
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "prepared")  # docs on docs
        self.assertEqual(publish.prepare(self.public, self.copy, "1.0.1"), "prepared")
        self.assertEqual(git(self.public, "tag", "--list"), "v1.0.0\nv1.0.1")

    def test_docs_push_after_rehearsal_still_pushes(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        remote = tempfile.mkdtemp()
        git(remote, "init", "-q", "--bare")
        git(self.public, "remote", "add", "origin", remote)
        git(self.public, "push", "-q", "-u", "origin", "main")
        self._write("README.md", "v1 nicer\n")
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "prepared")   # rehearsal
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "prepared")   # --push run
        git(self.public, "push", "-q", "origin", "HEAD:main")
        git(self.public, "fetch", "-q")
        self.assertEqual(publish.prepare_docs(self.public, self.copy), "unchanged")

    def test_docs_publish_needs_a_release_first(self):
        with self.assertRaises(publish.PublishError):
            publish.prepare_docs(self.public, self.copy)

    def test_hand_commit_after_docs_commit_still_stops_a_release(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        self._write("README.md", "docs\n")
        publish.prepare_docs(self.public, self.copy)
        with open(os.path.join(self.public, "README.md"), "w") as f:
            f.write("maintainer edit\n")
        git(self.public, "commit", "-qam", "extron-driver-convert docs: update")      # right subject, not the bot
        with self.assertRaises(publish.PublishError):
            publish.prepare(self.public, self.copy, "1.0.1")
        with self.assertRaises(publish.PublishError):
            publish.prepare_docs(self.public, self.copy)

    def test_bot_commit_touching_code_is_not_a_docs_commit(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        with open(os.path.join(self.public, "old.txt"), "w") as f:
            f.write("sneaky\n")
        env = dict(os.environ, **publish.BOT)
        subprocess.run(["git", "-C", self.public, "commit", "-qam", publish.DOCS_SUBJECT],
                       env=env, check=True, capture_output=True)
        with self.assertRaises(publish.PublishError):
            publish.prepare(self.public, self.copy, "1.0.1")

    def test_docs_symlink_refused(self):
        publish.prepare(self.public, self.copy, "1.0.0")
        os.symlink("/etc", os.path.join(self.copy, "docs"))
        with self.assertRaises(publish.PublishError):
            publish.prepare_docs(self.public, self.copy)


if __name__ == "__main__":
    unittest.main()
