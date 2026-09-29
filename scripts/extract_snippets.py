#!/usr/bin/env python3
"""Extract install/usage snippets VERBATIM from cached READMEs. Heuristic: first fenced code block under a matching heading.
Anything not found stays null. Writes data/snippets.json."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INSTALL_H = re.compile(r"\b(install|installation|setup|set up|get(ting)? started|quick ?start|add to claude)\b|安装|快速开始|最短安装|インストール|설치", re.I)
USAGE_H = re.compile(r"\b(usage|use|how to use|example|examples|quick ?start|commands?|run)\b|使用|用法|示例|快速开始", re.I)


def slug(h):
    s = re.sub(r"[^\w\- ]", "", h.lower(), flags=re.U).strip().replace(" ", "-")
    return s


def sections(text):
    lines, out, cur, fence = text.split("\n"), [], None, False
    for ln in lines:
        if ln.lstrip().startswith(("```", "~~~")):
            fence = not fence
        m = None if fence else HEAD.match(ln)
        if m:
            cur = {"title": m.group(2), "body": []}
            out.append(cur)
        elif cur is not None:
            cur["body"].append(ln)
    return out


def first_block(body):
    inb, buf = False, []
    for ln in body:
        if ln.lstrip().startswith(("```", "~~~")):
            if inb:
                return "\n".join(buf).strip("\n")
            inb, buf = True, []
        elif inb:
            buf.append(ln)
    return None


def find(secs, pat, exclude=None):
    for s in secs:
        if pat.search(s["title"]) and not (exclude and exclude.search(s["title"])):
            b = first_block(s["body"])
            if b and 1 <= len(b) <= 1500:
                return s["title"], b
    return None


def main():
    enr = json.loads((ROOT / "data/enriched.json").read_text())
    out = {}
    for r in enr:
        p = ROOT / "sources/readmes" / (r["id"].replace("/", "__") + ".md")
        if not p.exists():
            continue
        secs = sections(p.read_text())
        base = r["readme_html_url"]
        ins = find(secs, INSTALL_H)
        use = find(secs, USAGE_H, exclude=INSTALL_H if ins else None)
        if not use:
            use = find(secs, USAGE_H)
        out[r["id"]] = {
            "install": {"command": ins[1], "source_url": f"{base}#{slug(ins[0])}", "section": ins[0]} if ins else None,
            "usage": {"snippet": use[1], "source_url": f"{base}#{slug(use[0])}", "section": use[0]} if use else None,
        }
    (ROOT / "data/snippets.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(out), "install", sum(1 for v in out.values() if v["install"]), "usage", sum(1 for v in out.values() if v["usage"]))


if __name__ == "__main__":
    main()
