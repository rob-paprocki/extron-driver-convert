import subprocess, os, sys, time

RAWDIR = "_raw"
os.makedirs(RAWDIR, exist_ok=True)
BASE = "https://docs.crestron.com/en-us/9440/Content/"

def url_to_filename(url):
    p = url.replace(BASE, "").replace("/", "__")
    return os.path.join(RAWDIR, p + ".html")

with open("urls_unique.txt") as f:
    urls = [u.strip() for u in f if u.strip() and "docs.crestron.com/en-us/9440" in u]

for url in urls:
    if not url.startswith(BASE):
        continue
    fn = url_to_filename(url)
    if os.path.exists(fn) and os.path.getsize(fn) > 200:
        continue
    print("Fetching:", url, file=sys.stderr)
    ok = False
    for attempt in range(3):
        r = subprocess.run(["brightdata", "scrape", url, "-f", "html", "-o", fn],
                            capture_output=True, text=True, timeout=120)
        if os.path.exists(fn) and os.path.getsize(fn) > 200:
            ok = True
            break
        time.sleep(2)
    if not ok:
        print("FAILED:", url, file=sys.stderr)
