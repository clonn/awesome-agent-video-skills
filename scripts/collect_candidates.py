#!/usr/bin/env python3
"""Merge upstream skills.json, the saved live-page cards, and must-feature repos into data/candidates.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIND_EN = {
    "general": "Frameworks & Toolkits",
    "promo": "Product Promos & Demos",
    "explainer": "Explainers & Education",
    "editing": "Editing & Post-production",
    "shorts": "Short-form & Talking-head",
    "avatar": "AI Avatars",
    "story": "Story & Animation",
    "motion": "Motion Graphics & Logos",
    "craft": "Scriptwriting & Film Study",
    "music": "Music Videos",
}
TARGETS = {"general": 29, "promo": 26, "explainer": 32, "editing": 37, "shorts": 19,
           "avatar": 5, "story": 13, "motion": 11, "craft": 10, "music": 2}
MUST = ["YeJe-cpu/SeeCut", "cclank/lanshu-create-ai-presenter-video"]


def main():
    up = json.loads((ROOT / "sources/upstream/skills.json").read_text())["skills"]
    live = json.loads((ROOT / "sources/upstream/live-cards.json").read_text())["cards"]
    rows = {}
    for s in up:
        rows[s["repo_full_name"]] = {
            "id": s["repo_full_name"], "path": s["path"], "category_source": s["kind"],
            "safety_upstream": s["security_grade"], "description_source": s["description"],
            "sources": ["upstream-skills.json"],
        }
    for c in live:
        r = rows.setdefault(c["repo"], {"id": c["repo"], "path": None, "category_source": c["kind"],
                                        "safety_upstream": None, "description_source": None, "sources": []})
        r["sources"].append("live-page")
    for m in MUST:
        rows[m]["must_feature"] = True
    out = sorted(rows.values(), key=lambda r: r["id"].lower())
    counts = {k: sum(1 for r in out if r["category_source"] == k) for k in TARGETS}
    diff = {k: counts[k] - TARGETS[k] for k in TARGETS if counts[k] != TARGETS[k]}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/candidates.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(out), counts, "diff-vs-target:", diff)


if __name__ == "__main__":
    main()
