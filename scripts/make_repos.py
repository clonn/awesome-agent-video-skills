#!/usr/bin/env python3
"""Assemble data/repos.json from candidates, enriched (live GitHub facts), snippets (verbatim), and descriptions_en (our words)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT_EN = {
    "general": "Frameworks & Toolkits", "promo": "Product Promos & Demos", "explainer": "Explainers & Education",
    "editing": "Editing & Post-production", "shorts": "Short-form & Talking-head", "avatar": "AI Avatars",
    "story": "Story & Animation", "motion": "Motion Graphics & Logos", "craft": "Scriptwriting & Film Study",
    "music": "Music Videos",
}
# Featured: top 2 per category by live stars, plus must-feature and article highlights.
EXTRA_FEATURED = {"YeJe-cpu/SeeCut", "cclank/lanshu-create-ai-presenter-video", "Vincentwei1021/video-shotcraft",
                  "calesthio/OpenMontage", "heygen-com/hyperframes", "Vincentwei1021/video-talkcraft"}
CJK = re.compile(r"[㐀-鿿가-힯぀-ヿ]")


def main():
    load = lambda n: json.loads((ROOT / "data" / n).read_text())  # noqa: E731
    cands = {c["id"]: c for c in load("candidates.json")}
    enr = {e["id"]: e for e in load("enriched.json")}
    snip = load("snippets.json")
    desc = {d["id"]: d for d in load("descriptions_en.json")}
    by_cat = {}
    for i, c in cands.items():
        by_cat.setdefault(c["category_source"], []).append(i)
    featured = set(EXTRA_FEATURED)
    for ids in by_cat.values():
        featured |= set(sorted(ids, key=lambda i: -enr[i]["stars"])[:2])
    out = []
    for i in sorted(cands, key=str.lower):
        c, e, d = cands[i], enr[i], desc[i]
        owner, name = i.split("/")
        note = []
        if e.get("renamed"):
            note.append(f"Renamed on GitHub: now {e['full_name_live']}.")
        if c.get("path"):
            note.append(f"Upstream lists a sub-path: {c['path']}.")
        up_desc = c.get("description_source") or ""
        s = snip.get(i, {})
        out.append({
            "id": i, "url": e["url"], "name": name, "owner": owner,
            "category_en": CAT_EN[c["category_source"]], "category_source": c["category_source"],
            "type": d["type"], "language": e.get("language"), "stars": e["stars"], "stars_checked_at": e["checked_at"],
            "license": e.get("license") if e.get("license") not in (None, "NOASSERTION") else (e.get("license_name") or None),
            "pushed_at": e["pushed_at"], "archived": e["archived"], "render_base": d["render_base"],
            "description_en": d["description_en"],
            "description_zh_source": up_desc if CJK.search(up_desc) else None,
            "install": s.get("install") and {"command": s["install"]["command"], "source_url": s["install"]["source_url"]},
            "usage": s.get("usage") and {"snippet": s["usage"]["snippet"], "source_url": s["usage"]["source_url"]},
            "safety_upstream": c["safety_upstream"], "featured": i in featured,
            "notes": " ".join(note) or None, "judgments": {},
        })
    (ROOT / "data/repos.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(out), "featured", sum(r["featured"] for r in out))


if __name__ == "__main__":
    main()
