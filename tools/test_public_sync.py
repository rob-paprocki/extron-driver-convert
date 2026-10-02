#!/usr/bin/env python3
"""
test_public_sync.py - the public-copy builder against throwaway git repositories.

Each test builds a repository with two unrelated histories, an "archive" and a "public" line,
and runs tools/public_sync.py on them. No vendor input; needs git on PATH.
Plain test_* functions + asserts, run by the __main__ block; no pytest.
Run: python -u tools/test_public_sync.py
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import public_sync as ps   # noqa: E402

os.environ.update({"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "noreply@example.com",
                   "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "noreply@example.com",
                   "GIT_CONFIG_NOSYSTEM": "1"})

# The fixtures' user and repository names are filled in at run time: this file is itself
# published through the tool, and a literal fixture path would arrive already scrubbed.
U, U2, RD = "ali" + "ce", "bo" + "b", "extron-driver-" + "convert"


def fill(text):
    return text.replace("{u}", U).replace("{u2}", U2).replace("{r}", RD)


ARCHIVE = {
    "README.md": "# Project\n",
    "keep/a.txt": "plain\n",
    "experiments/dm_md/DESIGN.md": "held back\n",
    "experiments/validator_differential/tool.exe": b"MZ\x90\x00\x03\x00binary",
    "evidence/screenshots/GCP_OJ8lgWOFHo.png": b"\x89PNG\r\n\x1a\n\x00\x00binary",
    "tools/__pycache__/x.cpython-314.pyc": b"\xcb\r\r\n\x00\x00compiled",
    "notes/paths.md": fill("raw C:\\Users\\{u}\\proj\\x.py and C:/Users/{u}/y\n"
                           "json \"C:\\\\Users\\\\{u}\\\\z\"\n"
                           "nested C:\\\\\\\\Users\\\\\\\\{u}\\\\\\\\n\n"
                           "bash /c/Users/{u}/w and mac /Users/{u}/repo/q\n"
                           "slugs C--Users-{u}-git-proj and -Users-{u}-GitHub-proj\n"
                           "repo Z:\\GitHub\\someone\\{r}\\tools and "
                           "/Users/{u}/GitHub/someone/{r}/experiments\n"
                           "url https://github.com/someone/{r} stays\n"
                           "shared C:\\Users\\Public\\Documents\\extron stays\n"),
    "ENVIRONMENT.md": ("python -u tools/test_a.py\n"
                       "python -u experiments/dm_md/test_x.py\n"
                       "python -u tools/test_b.py\n"),
    "vendor-files.manifest.tsv": "# sha\tsize\tpath\nabc\t1\tsamples/v.pkp\n",
}


def _git(repo, *args, input=None):
    p = subprocess.run(["git", "-C", repo] + list(args), input=input, capture_output=True)
    assert p.returncode == 0, p.stderr.decode("utf-8", "replace")
    return p.stdout.decode("utf-8", "replace").strip()


def _commit(repo, branch, files, message, parent_branch=None):
    """Commit `files` (path -> str/bytes, None = delete) on `branch`, as an orphan unless parent_branch."""
    if parent_branch is None:
        _git(repo, "checkout", "-q", "--orphan", branch)
        _git(repo, "rm", "-r", "-q", "--cached", "--ignore-unmatch", ".")
        for name in os.listdir(repo):
            if name != ".git":
                p = os.path.join(repo, name)
                shutil.rmtree(p) if os.path.isdir(p) else os.unlink(p)
    else:
        _git(repo, "checkout", "-q", parent_branch)
        _git(repo, "checkout", "-q", "-B", branch)
    for path, data in files.items():
        full = os.path.join(repo, path)
        if data is None:
            _git(repo, "rm", "-q", path)
            continue
        os.makedirs(os.path.dirname(full) or repo, exist_ok=True)
        with open(full, "wb") as f:
            f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        _git(repo, "add", path)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _repo(archive=None):
    repo = tempfile.mkdtemp(prefix="public-sync-test-")
    _git(repo, "init", "-q")
    _git(repo, "config", "commit.gpgsign", "false")
    pub = _commit(repo, "public", {"README.md": "# Project (public)\n"}, "public start")
    arc = _commit(repo, "archive", archive or ARCHIVE, "archive work")
    return repo, arc, pub


def _run(repo, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ps.main(["--repo", repo] + list(argv))
    return code, out.getvalue()


def _show(repo, rev, path):
    return _git(repo, "show", "%s:%s" % (rev, path))


def _files(repo, rev):
    return set(_git(repo, "ls-tree", "-r", "--name-only", rev).splitlines())


def test_build_excludes_scrubs_and_keeps_public_ancestry():
    repo, arc, pub = _repo()
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 0, out
    files = _files(repo, "public-next")
    assert "experiments/dm_md/DESIGN.md" not in files
    assert "experiments/validator_differential/tool.exe" not in files
    assert "tools/__pycache__/x.cpython-314.pyc" not in files
    assert {"README.md", "keep/a.txt", "evidence/screenshots/GCP_OJ8lgWOFHo.png", "notes/paths.md"} <= files
    assert _git(repo, "rev-parse", "public-next^") == pub
    p = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", arc, "public-next"])
    assert p.returncode != 0, "archive history reached the public line"


def test_personal_paths_are_scrubbed_in_every_form_and_shared_paths_kept():
    repo, arc, pub = _repo()
    _run(repo, "build", "--archive", "archive", "--public", "public")
    text = _show(repo, "public-next", "notes/paths.md")
    assert U not in text, text
    assert "C:\\Users\\<user>\\proj" in text and "C:/Users/<user>/y" in text
    assert "C:\\\\Users\\\\<user>\\\\z" in text and "C:\\\\\\\\Users\\\\\\\\<user>\\\\\\\\n" in text
    assert "/c/Users/<user>/w" in text and "/Users/<user>/repo" in text
    assert "C--Users-<user>-git-proj" in text and "-Users-<user>-GitHub-proj" in text
    assert "repo <repo>\\tools and <repo>/experiments" in text, text
    assert fill("https://github.com/someone/{r} stays") in text
    assert "C:\\Users\\Public\\Documents" in text


def test_run_lines_for_an_excluded_experiment_are_dropped():
    repo, arc, pub = _repo()
    _run(repo, "build", "--archive", "archive", "--public", "public")
    assert _show(repo, "public-next", "ENVIRONMENT.md").splitlines() == \
        ["python -u tools/test_a.py", "python -u tools/test_b.py"]


def test_build_refuses_a_leak_it_cannot_scrub():
    # assembled at run time, so this file does not itself carry what the tool refuses
    for name, text in (("url", "https://user:" + "hunter2@github.com/x\n"), ("cip", "see python-cip" + "client\n"),
                       ("key", "-----BEGIN RSA PRIVATE " + "KEY-----\n")):
        repo, arc, pub = _repo(dict(ARCHIVE, **{"keep/leak.md": text}))
        code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
        assert code == 1 and "NOT BUILT" in out, (name, out)
        assert subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", "public-next"],
                              capture_output=True).returncode != 0, name


def test_addresses_and_emails_are_noted_not_refused():
    repo, arc, pub = _repo(dict(ARCHIVE, **{"keep/n.md": "default 192.168.254.254, mail support@vendor.example.net\n"
                                                         "Co-Authored-By: X <noreply@anthropic.com>\n"}))
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 0, out
    assert "2 note(s)" in out and "private IPv4" in out and "email address" in out, out


def test_build_refuses_a_tracked_vendor_file_and_an_unlisted_binary():
    repo, arc, pub = _repo(dict(ARCHIVE, **{"samples/v.pkp": "vendor\n"}))
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 1 and "vendor manifest path present" in out, out
    repo, arc, pub = _repo(dict(ARCHIVE, **{"keep/blob.bin": b"\x00\x01\x02"}))
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 1 and "binary file" in out, out
    # an image no one has looked at is refused like any other binary
    repo, arc, pub = _repo(dict(ARCHIVE, **{"evidence/screenshots/new.png": b"\x89PNG\r\n\x1a\n\x00"}))
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 1 and "evidence/screenshots/new.png" in out and "not reviewed" in out, out


def test_audit_exclusions_hold():
    extra = {"tools/out/verdicts/workflows/wf_1.result.json": "{}\n",
             "tools/out/verdicts/synthesis.md": "kept\n",
             "evidence/test-logs/push3.log": "auth failed\n",
             "evidence/screenshots/automation-gcp1.png": b"\x89PNG\r\n\x1a\n\x00"}
    repo, arc, pub = _repo(dict(ARCHIVE, **extra))
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 0, out
    files = _files(repo, "public-next")
    assert "tools/out/verdicts/synthesis.md" in files
    for path in ("tools/out/verdicts/workflows/wf_1.result.json", "evidence/test-logs/push3.log",
                 "evidence/screenshots/automation-gcp1.png"):
        assert path not in files, path


def test_private_denylist_is_enforced_without_being_published():
    repo, arc, pub = _repo(dict(ARCHIVE, **{"keep/d.md": "made by quinlan\n"}))
    os.makedirs(os.path.join(repo, "private"))
    with open(os.path.join(repo, "private", "public-sync-denylist.txt"), "w") as f:
        f.write("# local names\n\\bquinlan\\b\n")
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    assert code == 1 and "private denylist" in out, out


def test_private_replacements_rewrite_text_and_bare_home_folders():
    repo, arc, pub = _repo(dict(ARCHIVE, **{"keep/r.md": "written by Quinn Example at Acme AV\n",
                                            "keep/t.md": fill("| `Users\\{u}\\Downloads\\x.vsix` |\n")}))
    os.makedirs(os.path.join(repo, "private"))
    with open(os.path.join(repo, "private", "public-sync-replace.tsv"), "w") as f:
        f.write("# test\nQuinn Example at Acme AV\tan integrator\n")
    try:
        code, out = _run(repo, "build", "--archive", "archive", "--public", "public")
    finally:
        ps.EXTRA_SCRUB[:] = []
    assert code == 0, out
    assert _show(repo, "public-next", "keep/r.md") == "written by an integrator"
    assert _show(repo, "public-next", "keep/t.md") == "| `Users\\<user>\\Downloads\\x.vsix` |"


def test_check_reports_what_build_removes():
    repo, arc, pub = _repo()
    code, out = _run(repo, "check", "archive")
    assert code == 1
    for kind in ("excluded path present", "home path"):
        assert kind in out, (kind, out)
    _run(repo, "build", "--archive", "archive", "--public", "public")
    code, out = _run(repo, "check", "public-next")
    assert code == 0, out


def test_nothing_to_publish_when_already_current():
    repo, arc, pub = _repo()
    _run(repo, "build", "--archive", "archive", "--public", "public")
    code, out = _run(repo, "build", "--archive", "archive", "--public", "public-next", "--branch", "again")
    assert code == 0 and "Nothing to publish" in out, out


def test_rewrite_cleans_every_commit_and_keeps_metadata():
    repo = tempfile.mkdtemp(prefix="public-sync-test-")
    _git(repo, "init", "-q")
    _git(repo, "config", "commit.gpgsign", "false")
    _commit(repo, "public", {"a.md": fill("path C:\\Users\\{u2}\\x\n"), "bin/t.exe": b"MZ\x00\x01"}, "first")
    _commit(repo, "public", {"a.md": "clean now\n", "bin/t.exe": None, "b.md": "two\n"},
            fill("second, from C:\\Users\\{u2}\\repo"), parent_branch="public")
    old = _git(repo, "rev-list", "--reverse", "public").splitlines()
    ps.EXCLUDE.append("bin/*.exe")
    try:
        code, out = _run(repo, "rewrite", "--public", "public")
    finally:
        ps.EXCLUDE.remove("bin/*.exe")
    assert code == 0, out
    new = _git(repo, "rev-list", "--reverse", "public-rewritten").splitlines()
    assert len(new) == len(old) == 2
    assert U2 not in _show(repo, new[0], "a.md")
    assert "bin/t.exe" not in _files(repo, new[0])
    for o, n in zip(old, new):
        assert _git(repo, "log", "-1", "--format=%an %ae %aI", o) == _git(repo, "log", "-1", "--format=%an %ae %aI", n)
    assert _git(repo, "log", "-1", "--format=%B", new[0]) == "first"
    assert _git(repo, "log", "-1", "--format=%B", new[1]) == "second, from C:\\Users\\<user>\\repo"
    assert _git(repo, "rev-parse", "public-rewritten^{tree}") == _git(repo, "rev-parse", "public^{tree}")
    code, out = _run(repo, "check", "--history", "public")
    assert code == 1 and "<commit message>" in out, out
    code, out = _run(repo, "check", "--history", "public-rewritten")
    assert code == 0, out


def test_the_tool_and_its_tests_pass_through_their_own_scrub_unchanged():
    # Both are published through the tool; a fixture the scrub rewrote would leave the
    # public copy's tests with nothing to detect.
    for name in ("public_sync.py", "test_public_sync.py"):
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            src = f.read()
        assert ps.scrub_text(src) == src, name
        problems, _ = ps.check_text(name, src)
        assert not problems, (name, problems)


def test_the_tool_publishes_no_personal_names_itself():
    with open(os.path.join(HERE, "public_sync.py"), encoding="utf-8") as f:
        src = f.read()
    for rx in ps.LEAKS:
        assert not rx[1].search(src.replace("<user>", "")) or rx[0] in ("home path",), rx[0]
    assert not ps.EMAIL.search(src.replace("noreply@anthropic.com", "").replace("noreply@github.com", "")
                               .replace("@users.noreply.github.com", "").replace("@example.", "")), "email in tool"


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
