#!/usr/bin/python3 -I
"""Fail if a published file contains a personal-looking value.

Checks every git-tracked file (or every file under a directory), except
anything in private/ and the paths listed in private/public-exclude.txt:

  * email addresses: only placeholders (example.com and its subdomains,
    .invalid), the project's public domain (rpaprocki.com and its subdomains)
    and a few service addresses are allowed;
  * IPv4/IPv6 addresses: only the example network 192.168.100.0/24, loopback,
    0.0.0.0 / 255.255.255.255, the documentation ranges and a few well-known
    public resolvers;
  * MAC addresses: only the documentation range 00:00:5E:00:53:xx;
  * home-folder paths (a drive, "Users", then a name; or /Users/<name>, /home/<name>): only
    placeholders such as <user>, and the shared Public/Default folders;
  * credentials: tokens, private keys and passwords inside URLs.

Everything else fails. This is an allow-list on purpose: it catches real
values without them ever being written down here (this file is public).
Messages name the file, line and KIND of value, never the value itself.

usage: check_repo.py [DIR]      (default: the git checkout this file is in)
"""
import hashlib
import ipaddress
import os
import re
import subprocess
import sys

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.]*\d)")
IPV6 = re.compile(r"(?<![\w:.])([0-9A-Fa-f]{0,4}(?::[0-9A-Fa-f]{0,4}){2,7})(?![\w:])")
HOME = re.compile(r"(?i)(?:\b[A-Z]:(?:\\+|/)Users(?:\\+|/)|/(?:Users|home)/)(?!(?:Public|Default|All Users|Shared)\b)(?!<)[A-Za-z0-9][A-Za-z0-9._-]*")
SECRETS = [
    ("credential in URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@'\"<>]+:[^/\s@'\"<>]+@[A-Za-z0-9.-]+")),
    ("access token", re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|xox[abprs]-[A-Za-z0-9-]{10,})")),
    ("cloud access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
MAC = re.compile(r"(?<![0-9A-Fa-f:-])[0-9A-Fa-f]{2}([:-])[0-9A-Fa-f]{2}(?:\1[0-9A-Fa-f]{2}){4}(?![0-9A-Fa-f:-])")

ALLOWED_EMAILS = {"git@github.com", "noreply@github.com", "noreply@anthropic.com",
                  "41898282+github-actions[bot]@users.noreply.github.com"}
EXAMPLE_NET = ipaddress.ip_network("192.168.100.0/24")
ALLOWED_NETS = [ipaddress.ip_network(n) for n in (
    "127.0.0.0/8", "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")]
ALLOWED_IPS = {ipaddress.ip_address(a) for a in (
    "0.0.0.0", "255.255.255.255", "1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4", "9.9.9.9",
    "::", "::1",
    "192.168.254.254")}        # Extron's documented factory-default address


def _load_quads():
    """Software version numbers that look like IPv4 addresses (for example 3.33.0.38),
    one per line in tools/check_repo_allow.txt. They are not addresses and not personal."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_repo_allow.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return {l.split("#")[0].strip() for l in f if l.split("#")[0].strip()}
    except OSError:
        return set()


ALLOWED_QUADS = _load_quads()


def email_ok(addr):
    a = addr.lower()
    domain = a.split("@", 1)[1]
    return (a in ALLOWED_EMAILS or domain.endswith(".invalid")
            or any(domain == d or domain.endswith("." + d) for d in ("example.com", "example.org", "example.net", "rpaprocki.com")))


def ip_ok(ip):
    if ip.version == 4 and ip in EXAMPLE_NET:
        return True
    if ip.is_multicast or str(ip) in ALLOWED_QUADS:
        return True
    return ip in ALLOWED_IPS or any(ip in n for n in ALLOWED_NETS if n.version == ip.version)


def scan_text(text):
    """Yield (line_number, kind) for every disallowed value."""
    for n, line in enumerate(text.splitlines(), 1):
        for m in EMAIL.finditer(line):
            if not email_ok(m.group(0)):
                yield n, "email address"
        for m in IPV4.finditer(line):
            try:
                ip = ipaddress.ip_address(m.group(1))
            except ValueError:
                continue
            if not ip_ok(ip):
                yield n, "IP address"
        for m in IPV6.finditer(line):
            try:
                ip = ipaddress.ip_address(m.group(1))
            except ValueError:
                continue
            if not ip_ok(ip):
                yield n, "IPv6 address"
        for m in HOME.finditer(line):
            yield n, "home-folder path"
        for kind, rx in SECRETS:
            if rx.search(line):
                yield n, kind
        for m in MAC.finditer(line):
            if not m.group(0).upper().replace("-", ":").startswith("00:00:5E:00:53:"):
                yield n, "MAC address"


def files_in(root):
    if os.path.isdir(os.path.join(root, ".git")) or os.path.isfile(os.path.join(root, ".git")):
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True,
                             check=True).stdout.decode()
        return [f for f in out.split("\0") if f]
    found = []
    for d, _dirs, names in os.walk(root):
        for name in names:
            found.append(os.path.relpath(os.path.join(d, name), root).replace(os.sep, "/"))
    return found


# Screenshots are the one exception to "public files are UTF-8 text". A word-list
# or pattern scan can't read pixels, so an image is allowed only if a person has
# looked at it: its SHA-256 must be listed in docs/images/approved.sha256 (a text
# file, scanned like any other). It must also be a plain PNG with no chunk that
# can carry text (comments, EXIF, timestamps...).
IMAGE_DIR = "docs/images/"
IMAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./-]*\.png$")
APPROVED = IMAGE_DIR + "approved.sha256"
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_CHUNKS_OK = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"sRGB", b"gAMA", b"cHRM", b"pHYs", b"tRNS", b"bKGD"}
IMAGE_MAX = 2 * 1024 * 1024


def approved_images(root):
    """{sha256: repo-relative path} from docs/images/approved.sha256 ("<sha256>  <path>" lines)."""
    found = {}
    try:
        with open(os.path.join(root, APPROVED), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    digest, name = line.split(None, 1)
                    found[digest.lower()] = name.strip()
    except (OSError, ValueError):
        pass
    return found


def image_problem(root, rel, approved=None):
    """None if REL is an approved, metadata-free PNG; otherwise why not."""
    if not IMAGE_NAME.match(rel):
        return "%s: not UTF-8 text" % rel
    path = os.path.join(root, rel)
    if os.path.islink(path):
        return "%s: image is a symlink" % rel
    with open(path, "rb") as f:
        data = f.read(IMAGE_MAX + 1)
    if len(data) > IMAGE_MAX:
        return "%s: image is larger than 2 MB" % rel
    if not data.startswith(PNG_SIG):
        return "%s: not a PNG" % rel
    pos, ended = len(PNG_SIG), False
    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        kind = data[pos + 4:pos + 8]
        if kind not in PNG_CHUNKS_OK:
            return "%s: PNG has a %r chunk (metadata is not allowed)" % (rel, kind.decode("latin-1"))
        pos += 12 + length
        if kind == b"IEND":
            ended = True
            break
    if not ended or pos != len(data):
        return "%s: PNG is malformed or has data after its end" % rel
    approved = approved_images(root) if approved is None else approved
    if approved.get(hashlib.sha256(data).hexdigest()) != rel:
        return "%s: image is not listed in %s (look at it, then add its sha256 and path)" % (rel, APPROVED)
    return None


def excluded(root):
    """Paths listed in private/public-exclude.txt. They never reach a release, so they
    are not checked. Returns an empty list when the file doesn't exist."""
    try:
        with open(os.path.join(root, "private", "public-exclude.txt"), encoding="utf-8") as f:
            return [l.strip().rstrip("/") for l in f if l.strip() and not l.startswith("#")]
    except OSError:
        return []


def check(root):
    problems = []
    skip = excluded(root)
    for rel in sorted(files_in(root)):
        if rel == "private" or rel.startswith("private/") or rel.startswith(".git/"):
            continue
        if any(rel == e or rel.startswith(e + "/") for e in skip):
            continue
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            bad = image_problem(root, rel)
            if bad:
                problems.append(bad)
            for _line, kind in scan_text(rel):            # the image's name still counts
                problems.append("%s: %s in the file name" % (rel, kind))
            continue
        except OSError:
            continue
        for line, kind in scan_text(text):
            problems.append("%s:%d: %s not allowed in public files" % (rel, line, kind))
        for _line, kind in scan_text(rel):                # file names too
            problems.append("%s: %s in the file name" % (rel, kind))
    return problems


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems = check(root)
    for p in problems:
        print(p)
    print("check_repo: %s" % ("%d problem(s)" % len(problems) if problems else "OK"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
