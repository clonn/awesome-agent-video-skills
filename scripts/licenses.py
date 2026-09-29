#!/usr/bin/env python3
"""For repos whose GitHub license is Other/NOASSERTION/none, read the LICENSE file (gh api, read-only) and classify it.
Writes data/licenses.json: {id: {file, spdx_guess, noncommercial, excerpt_first_line, checked_at}}."""
import base64
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = [  # (regex on lowercased text, spdx-ish, noncommercial)
    (r"polyform noncommercial license 1\.0\.0", "PolyForm-Noncommercial-1.0.0", True),
    (r"polyform.{0,40}(non-?commercial)", "PolyForm-Noncommercial", True),
    (r"creative commons.{0,80}(non-?commercial|by-nc)|cc by-nc", "CC-BY-NC", True),
    (r"apache license.{0,20}version 2\.0", "Apache-2.0", False),
    (r"permission is hereby granted, free of charge", "MIT", False),
    (r"gnu affero general public license", "AGPL-3.0", False),
    (r"gnu general public license", "GPL", False),
    (r"gnu lesser general public license", "LGPL", False),
    (r"mozilla public license", "MPL-2.0", False),
    (r"redistribution and use in source and binary forms", "BSD", False),
    (r"this is free and unencumbered software|unlicense", "Unlicense", False),
    (r"cc0 1\.0|creative commons zero", "CC0-1.0", False),
    (r"non-?commercial|not for commercial|personal use only", "Custom (non-commercial terms)", True),
]


def gh_license(rid):
    r = subprocess.run(["gh", "api", f"repos/{rid}/license"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def one(rid):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d = gh_license(rid)
    if d is None:
        return rid, {"file": None, "spdx_guess": None, "noncommercial": False, "note": "no LICENSE file found", "checked_at": now}
    text = base64.b64decode(d["content"]).decode("utf-8", "replace")
    low = re.sub(r"\s+", " ", text.lower())
    spdx, nc = None, False
    for pat, s, n in RULES:
        if re.search(pat, low):
            spdx, nc = s, n
            break
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return rid, {"file": d["name"], "spdx_guess": spdx, "noncommercial": nc, "first_line": first[:100], "checked_at": now}


def main():
    repos = json.loads((ROOT / "data/repos.json").read_text())
    ids = [r["id"] for r in repos if r["license"] in (None, "Other", "NOASSERTION")]
    with ThreadPoolExecutor(8) as ex:
        out = dict(ex.map(one, ids))
    (ROOT / "data/licenses.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(out), "checked; no file:", sum(1 for v in out.values() if v["file"] is None),
          "; classified:", sum(1 for v in out.values() if v.get("spdx_guess")), "; noncommercial:",
          [k for k, v in out.items() if v["noncommercial"]])
    print("unclassified with file:", [(k, v.get("first_line")) for k, v in out.items() if v["file"] and not v["spdx_guess"]])


if __name__ == "__main__":
    main()
