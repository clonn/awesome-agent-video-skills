#!/usr/bin/env python3
"""Validate data/repos.json against the spec.md schema (stdlib only). Exit 1 on any problem."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"Claude Skill", "Codex Skill", "MCP Server", "Agent Tool", "AI Tool"}
BASES = {"Remotion", "HyperFrames", "Manim", "ffmpeg", "After Effects", "Premiere Pro", "HeyGen", "Blender", "p5.js",
         "Lottie", "other"}
TARGETS = {"Frameworks & Toolkits": 29, "Product Promos & Demos": 26, "Explainers & Education": 32,
           "Editing & Post-production": 37, "Short-form & Talking-head": 19, "AI Avatars": 5,
           "Story & Animation": 13, "Motion Graphics & Logos": 11, "Scriptwriting & Film Study": 10, "Music Videos": 2}
FIELDS = ["id", "url", "name", "owner", "category_en", "category_source", "type", "language", "stars", "stars_checked_at",
          "license", "pushed_at", "archived", "render_base", "description_en", "description_zh_source", "install",
          "usage", "safety_upstream", "featured", "notes", "judgments"]


def check(rows):
    errs, seen = [], set()
    for r in rows:
        i = r.get("id", "?")
        for f in FIELDS:
            if f not in r:
                errs.append(f"{i}: missing {f}")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        if r.get("type") not in TYPES:
            errs.append(f"{i}: bad type {r.get('type')}")
        if not set(r.get("render_base", [])) <= BASES:
            errs.append(f"{i}: bad render_base")
        if not isinstance(r.get("stars"), int) or not r.get("stars_checked_at"):
            errs.append(f"{i}: stars/stars_checked_at")
        if len(r.get("description_en", "").split()) > 25 or not r.get("description_en"):
            errs.append(f"{i}: description_en empty or >25 words")
        for k, v in (("install", "command"), ("usage", "snippet")):
            x = r.get(k)
            if x is not None and not (x.get(v) and str(x.get("source_url", "")).startswith("https://")):
                errs.append(f"{i}: {k} without command/source_url")
        if not isinstance(r.get("featured"), bool):
            errs.append(f"{i}: featured not bool")
    return errs


def main():
    rows = json.loads((ROOT / "data/repos.json").read_text())
    errs = check(rows)
    counts = {}
    for r in rows:
        counts[r["category_en"]] = counts.get(r["category_en"], 0) + 1
    if counts != TARGETS:
        errs.append(f"category counts differ from targets: {counts}")
    print(f"{len(rows)} rows, featured={sum(r['featured'] for r in rows)}, errors={len(errs)}")
    for e in errs[:30]:
        print(" ", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
