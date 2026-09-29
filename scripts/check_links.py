#!/usr/bin/env python3
"""Check every http(s) URL found in *.md files. Stdlib only. Usage: check_links.py [--local-only]"""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = re.compile(r"https?://[^\s)>\]\"'`]+")


def main():
    local_only = "--local-only" in sys.argv
    urls = {}
    for p in ROOT.rglob("*.md"):
        if any(part in (".git", "readmes", ".claude") for part in p.parts):
            continue
        for u in URL.findall(p.read_text(errors="ignore")):
            urls.setdefault(u.rstrip(".,;"), p.relative_to(ROOT))
    print(f"{len(urls)} unique URLs")
    if local_only:
        return 0
    bad = 0
    for u, src in sorted(urls.items()):
        try:
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "link-check"})
            code = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "code", str(e))
        if code != 200:
            bad += 1
            print(f"BROKEN {code} {u} ({src})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
