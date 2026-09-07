import subprocess, os, sys, time, re
from urllib.parse import unquote

BASE = "https://docs.crestron.com/en-us/9440/Content/"
MDDIR = "_md_raw"
PAGESDIR = "pages"
os.makedirs(MDDIR, exist_ok=True)

def url_to_relpath(url):
    # strip base, decode percent-encoding, keep folder structure
    rel = url.replace(BASE, "")
    rel = unquote(rel)
    return rel

def fetch_md(url, cache_fn):
    if os.path.exists(cache_fn) and os.path.getsize(cache_fn) > 100:
        with open(cache_fn) as f:
            return f.read()
    for attempt in range(3):
        r = subprocess.run(["brightdata", "scrape", url, "-o", cache_fn],
                            capture_output=True, text=True, timeout=120)
        if os.path.exists(cache_fn) and os.path.getsize(cache_fn) > 50:
            with open(cache_fn) as f:
                return f.read()
        time.sleep(2)
    print("FAILED:", url, r.stdout[-500:] if r else "", r.stderr[-500:] if r else "", file=sys.stderr)
    return None

def strip_boilerplate(md):
    # Remove leading nav/account/logout/filter/search boilerplate up to the first H1
    lines = md.split("\n")
    h1_idx = None
    for i, l in enumerate(lines):
        if l.startswith("# "):
            h1_idx = i
            break
    if h1_idx is not None:
        lines = lines[h1_idx:]
    md = "\n".join(lines)
    # Cut off trailing footer starting at "Have feedback on this document?"
    cut_markers = [
        "Have feedback on this document?",
    ]
    for marker in cut_markers:
        idx = md.find(marker)
        if idx != -1:
            md = md[:idx]
    return md.strip() + "\n"

with open("urls_all.txt") as f:
    urls = [u.strip() for u in f if u.strip()]

index_entries = []
failed = []

for url in urls:
    rel = url_to_relpath(url)
    if rel == "" or rel.startswith("http"):
        # root domain page docs.crestron.com/en-us/9440/
        rel = "root-search-page.md"
        out_path = os.path.join(PAGESDIR, rel)
    else:
        if not rel.endswith(".htm"):
            continue
        out_path = os.path.join(PAGESDIR, rel[:-4] + ".md")
    cache_fn = os.path.join(MDDIR, rel.replace("/", "__") if rel.endswith(".md") else rel.replace("/", "__")[:-4] + ".md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print("Processing:", url, file=sys.stderr)
    md = fetch_md(url, cache_fn)
    if md is None:
        failed.append(url)
        continue
    body = strip_boilerplate(md)
    final = f"Source: {url}\n\n{body}"
    with open(out_path, "w") as f:
        f.write(final)
    # Title = first H1 line if present
    title = None
    for l in body.split("\n"):
        if l.startswith("# "):
            title = l[2:].strip()
            break
    index_entries.append((title or rel, url, out_path))

with open("index_entries.json", "w") as f:
    import json
    json.dump({"entries": index_entries, "failed": failed}, f, indent=2)

print("DONE. pages:", len(index_entries), "failed:", len(failed), file=sys.stderr)
