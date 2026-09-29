#!/usr/bin/env python3
"""Fetch live GitHub facts + README for each candidate via `gh api` (read-only). Writes data/enriched.json and sources/readmes/."""
import base64
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        msg = (r.stdout + r.stderr).strip()
        return None, msg[:200]
    return json.loads(r.stdout), None


def one(c):
    rid = c["id"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d, err = gh(f"repos/{rid}")
    row = {"id": rid, "checked_at": now}
    if d is None:
        row["error"] = err
        return row
    row.update({
        "full_name_live": d["full_name"], "renamed": d["full_name"].lower() != rid.lower(),
        "url": d["html_url"], "stars": d["stargazers_count"], "license": (d.get("license") or {}).get("spdx_id"),
        "license_name": (d.get("license") or {}).get("name"), "language": d.get("language"),
        "pushed_at": d["pushed_at"], "archived": d["archived"], "default_branch": d["default_branch"],
        "gh_description": d.get("description"),
    })
    rd, rerr = gh(f"repos/{d['full_name']}/readme")
    if rd is None:
        row["readme_error"] = rerr
    else:
        text = base64.b64decode(rd["content"]).decode("utf-8", "replace")
        (ROOT / "sources/readmes" / (rid.replace("/", "__") + ".md")).write_text(text)
        row.update({"readme_path": rd["path"], "readme_html_url": rd["html_url"], "readme_bytes": len(text)})
    return row


def main():
    cands = json.loads((ROOT / "data/candidates.json").read_text())
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, cands))
    (ROOT / "data/enriched.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    print("ok", sum(1 for r in rows if "error" not in r), "errors", [(r["id"], r["error"]) for r in rows if "error" in r])
    print("renamed", [(r["id"], r["full_name_live"]) for r in rows if r.get("renamed")])
    print("archived", [r["id"] for r in rows if r.get("archived")])
    print("no readme", [r["id"] for r in rows if "readme_error" in r])


if __name__ == "__main__":
    main()
