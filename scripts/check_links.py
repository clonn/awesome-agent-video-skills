#!/usr/bin/env python3
"""Check every http(s) URL found in *.md files (stdlib). Usage: check_links.py [--local-only]
Fragments (#anchors) are not verified. Exit 1 if any URL is broken."""
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = re.compile(r"https?://[^\s)>\]\"'`<]+")
SKIP_DIRS = {".git", "readmes", ".claude", "review", "upstream"}


def collect():
    urls = {}
    for p in ROOT.rglob("*.md"):
        if SKIP_DIRS & set(p.relative_to(ROOT).parts):
            continue
        for u in URL.findall(p.read_text(errors="ignore")):
            u = u.rstrip(".,;:*_")
            u = u.split("#")[0]
            if u.startswith(("http://", "https://")) and len(u) > 10:
                urls.setdefault(u, []).append(str(p.relative_to(ROOT)))
    return urls


def probe(u):
    for method in ("HEAD", "GET"):
        for attempt in range(3):
            try:
                req = urllib.request.Request(u, method=method, headers={"User-Agent": "Mozilla/5.0 (link-check)"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    return u, r.status
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503, 504) and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                if method == "HEAD" and e.code in (400, 403, 405, 406, 501):
                    break
                return u, e.code
            except Exception as e:  # noqa: BLE001
                if attempt < 2:
                    time.sleep(1)
                    continue
                return u, type(e).__name__
    return u, "unreachable"


def main():
    urls = collect()
    print(f"{len(urls)} unique URLs")
    if "--local-only" in sys.argv:
        return 0
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(probe, sorted(urls)))
    bad = [(u, c) for u, c in res if c != 200]
    for u, c in bad:
        print(f"BROKEN {c} {u}  <- {urls[u][0]}")
    print(f"checked {len(res)}; ok {len(res) - len(bad)}; not-200 {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
