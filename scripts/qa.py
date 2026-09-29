#!/usr/bin/env python3
"""QA run: idempotency, schema, counts, CJK scan, and a spot-check of 10 random cards against their READMEs and live GitHub facts.
Usage: qa.py [--links]  (--links also runs the URL check). Needs cached READMEs in sources/readmes and the gh CLI for the live check."""
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[㐀-鿿가-힯぀-ヿ]")
RENDERED = ["README.md", "CONTRIBUTING.md", "LICENSE"]
RENDERED_DIRS = ["catalog", "skills", "docs", "tour", "examples"]


def files():
    out = [ROOT / f for f in RENDERED if (ROOT / f).exists()]
    for d in RENDERED_DIRS:
        out += sorted((ROOT / d).glob("*.md"))
    return out


def digest():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files()}


def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout + r.stderr).rstrip("\n")


def main():
    ok = True
    repos = json.loads((ROOT / "data/repos.json").read_text())
    print("== 5.3 idempotency, schema, counts")
    before = digest()
    rc1, o1 = sh("python3", "scripts/build.py")
    rc2, o2 = sh("python3", "scripts/build.py")
    after = digest()
    same = before == after
    print(f"build twice: rc={rc1},{rc2}; files unchanged={same} ({len(after)} rendered files)")
    rc, o = sh("python3", "scripts/validate.py")
    print("validate.py:", o.splitlines()[0] if o else rc, "rc=", rc)
    readme = (ROOT / "README.md").read_text()
    rows = len(re.findall(r"^\| \[[^\]]+\]\(https://github.com/", readme, re.M))
    quick = sum(1 for r in repos if r["featured"])
    print(f"README table rows={rows}; expected {len(repos)} + {quick} quick picks = {len(repos) + quick}; header says '{len(repos)} repositories': {f'**{len(repos)} repositories**' in readme}")
    counts = {}
    for r in repos:
        counts[r["category_en"]] = counts.get(r["category_en"], 0) + 1
    print("category counts:", counts)
    ok &= same and rc == 0 and rows == len(repos) + quick
    print("\n== 5.2 CJK scan (rendered files; allowed: code fences, Gloss lines, glossed proper noun 剪映)")
    bad = []
    for p in files():
        fence = False
        for n, ln in enumerate(p.read_text().split("\n"), 1):
            if ln.lstrip().startswith("```"):
                fence = not fence
                continue
            s = ln.lstrip("> ").strip()
            if not fence and CJK.search(ln) and not s.startswith("Gloss:") and "剪映" not in ln:
                bad.append((str(p.relative_to(ROOT)), n, ln[:90]))
    in_fence = sum(1 for p in files() for ln in p.read_text().split("\n") if CJK.search(ln))
    print(f"CJK lines outside allowed places: {len(bad)}; total CJK lines incl. fenced/gloss: {in_fence}")
    for b in bad[:20]:
        print("  ", b)
    ok &= not bad
    print("\n== 5.4 spot-check 10 random cards against README and live GitHub")
    random.seed(20260929)
    feat = [r for r in repos if r["featured"]]
    mism = 0
    for r in random.sample(feat, 10):
        text = (ROOT / "sources/readmes" / (r["id"].replace("/", "__") + ".md")).read_text()
        card = (ROOT / "skills" / (r["id"].replace("/", "__") + ".md")).read_text()
        probs = []
        for key, field in (("install", "command"), ("usage", "snippet")):
            v = r[key]
            if v and v[field] not in text:
                probs.append(f"{key} not verbatim in README")
            if v and not v["cjk"] and key == "install" and v["display_command"].split("\n")[0] not in card:
                probs.append("install missing from card")
        code, out = sh("gh", "api", f"repos/{r['url'].split('github.com/')[1]}", "--jq", "[.license.spdx_id,.archived,.stargazers_count,.pushed_at]|@tsv")
        if code == 0:
            spdx, arch, stars, pushed = out.split("\t")
            if r["license"] not in (None, "Other") and spdx != r["license"] and not (r["license"] and spdx == "NOASSERTION"):
                probs.append(f"license {r['license']} vs live {spdx}")
            if (arch == "true") != r["archived"]:
                probs.append("archived differs")
            if abs(int(stars) - r["stars"]) > max(5, 0.05 * r["stars"]):
                probs.append(f"stars {r['stars']} vs live {stars}")
        else:
            probs.append("live check failed")
        if len(r["description_en"].split()) > 25:
            probs.append("description too long")
        if not r["best_for"]:
            probs.append("no best_for")
        mism += len(probs)
        print(f"  {r['id']}: {'OK' if not probs else '; '.join(probs)}")
    print(f"factual mismatches: {mism}")
    ok &= mism == 0
    if "--links" in sys.argv:
        print("\n== 5.1 link check")
        rc, o = sh("python3", "scripts/check_links.py")
        print(o)
        ok &= rc == 0
    print("\nQA", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
