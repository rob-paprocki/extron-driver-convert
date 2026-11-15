import subprocess, re, os, sys, json, time
from urllib.parse import urljoin, urlparse

BASE = "https://docs.crestron.com/en-us/9440/Content/"
START = BASE + "Topics/Home.htm"
RAWDIR = "_raw"
os.makedirs(RAWDIR, exist_ok=True)

visited = set()
queue = [START]
pages = {}  # url -> html
errors = {}

def url_to_filename(url):
    p = url.replace(BASE, "").replace("/", "__")
    return os.path.join(RAWDIR, p + ".html")

def fetch(url):
    fn = url_to_filename(url)
    if os.path.exists(fn):
        with open(fn) as f:
            return f.read()
    for attempt in range(3):
        r = subprocess.run(["brightdata", "scrape", url, "-f", "html", "-o", fn],
                            capture_output=True, text=True, timeout=120)
        if os.path.exists(fn) and os.path.getsize(fn) > 200:
            with open(fn) as f:
                return f.read()
        time.sleep(2)
    errors[url] = r.stdout + r.stderr
    return None

def extract_links(html, url):
    links = set()
    for m in re.finditer(r'href=[\'"]([^\'"]+)[\'"]', html):
        links.add(m.group(1))
    for m in re.finditer(r"location\.href=[\'\"]([^\'\"]+)[\'\"]", html):
        links.add(m.group(1))
    resolved = set()
    for l in links:
        if l.startswith("#") or l.startswith("mailto:") or l.startswith("javascript:"):
            continue
        full = urljoin(url, l)
        full = full.split("#")[0]
        if full.startswith(BASE) and full.endswith(".htm"):
            resolved.add(full)
    return resolved

while queue:
    url = queue.pop(0)
    if url in visited:
        continue
    visited.add(url)
    print("Fetching:", url, file=sys.stderr)
    html = fetch(url)
    if html is None:
        print("FAILED:", url, file=sys.stderr)
        continue
    pages[url] = True
    for link in extract_links(html, url):
        if link not in visited and link not in queue:
            queue.append(link)

print(json.dumps({"visited": sorted(visited), "errors": errors}, indent=2))
