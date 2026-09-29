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
EXTRA_FEATURED = {"louisedesadeleer/cut-video", "aijiduonadegou/Paper-Cut", "iart-ai/data-animation-skills", "YeJe-cpu/SeeCut", "cclank/lanshu-create-ai-presenter-video", "Vincentwei1021/video-shotcraft",
                  "calesthio/OpenMontage", "heygen-com/hyperframes", "Vincentwei1021/video-talkcraft"}
CJK = re.compile(r"[㐀-鿿가-힯぀-ヿ]")

CMD_START = re.compile(r"^(\$ |> )?(git|npx|npm|pnpm|yarn|bun|bunx|pip3?|pipx|uv|uvx|python3?|node|cp|mkdir|cd|curl|wget|brew|apt(-get)?|make|sh|bash|zsh|source|export|claude|codex|gemini|sudo|docker|cargo|go|gh|ln|chmod|\./|Copy-Item|iwr|irm|powershell|pwsh|winget|mv|rm|tar|unzip|cat|echo|open|/[A-Za-z][\w:@./-]*)(\s|$)")
CONFIG_START = re.compile(r"^\s*([\[{]|name\s*[:=]|\"mcpServers\"|mcp_servers|command\s*[:=])")


def strip_comments(cmd):
    lines = cmd.split("\n")
    kept = [ln for ln in lines if not ln.lstrip().startswith("#")]
    while kept and not kept[0].strip():
        kept.pop(0)
    return "\n".join(kept).strip("\n"), len(kept) != len(lines)


def install_kind(cmd):
    body, _ = strip_comments(cmd)
    first = next((ln.strip() for ln in body.split("\n") if ln.strip()), "")
    if CONFIG_START.match(first):
        return "config"
    return "shell" if CMD_START.match(first) else "agent_prompt"


def usage_display(u, glosses, rid):
    """Usage with CJK renders as See README unless it is a short command with a hand-written gloss."""
    if not CJK.search(u["snippet"]):
        return {"cjk": False, "gloss": None}
    return {"cjk": True, "gloss": glosses.get(rid, {}).get("usage")}


def main():
    load = lambda n: json.loads((ROOT / "data" / n).read_text())  # noqa: E731
    cands = {c["id"]: c for c in load("candidates.json")}
    enr = {e["id"]: e for e in load("enriched.json")}
    snip = load("snippets.json")
    desc = {d["id"]: d for d in load("descriptions_en.json")}
    lic = load("licenses.json")
    over = load("overrides.json")
    jpath = ROOT / "data/judgments.json"
    judg = json.loads(jpath.read_text()) if jpath.exists() else {}
    dpath = ROOT / "data/review_decisions.json"
    decisions = json.loads(dpath.read_text()) if dpath.exists() else {}
    glosses = load("glosses.json")
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
        ov = {**over.get(i, {}), **decisions.get(i, {})}
        if "install" in ov:
            s = {**s, "install": ov["install"]}
        if "usage" in ov:
            s = {**s, "usage": ov["usage"]}
        jr = judg.get(i, {}).get("render_base")
        rb = ov["render_base"] if "render_base" in ov else (jr["kept"] if jr else d["render_base"])
        judgments = {}
        if jr:
            judgments["render_base"] = {"method": "regex match AND Noul>=%s (TypeSafe Jev; our judgment, not upstream's)" % jr["veto_threshold"],
                                        "model": judg[i].get("model"), "checked_at": judg[i]["checked_at"], "question_version": judg[i]["question_version"],
                                        "regex_hits": jr["regex_hits"], "noul": jr["noul"], "vetoed": jr["vetoed"],
                                        "overridden_by_hand": "render_base" in ov}
        inst = None
        if s.get("install"):
            cmd = s["install"]["command"]
            body, omitted = strip_comments(cmd)
            inst = {"command": cmd, "source_url": s["install"]["source_url"], "kind": install_kind(cmd),
                    "display_command": body, "comments_omitted": omitted, "cjk": bool(CJK.search(body)),
                    "gloss": glosses.get(i, {}).get("install")}
            if s["install"].get("purpose"):
                inst["purpose"] = s["install"]["purpose"]
        usg = None
        if s.get("usage"):
            usg = {"snippet": s["usage"]["snippet"], "source_url": s["usage"]["source_url"], **usage_display(s["usage"], glosses, i)}
        li = lic.get(i)
        license_detail = None
        noncommercial = False
        if li:
            license_detail = li.get("spdx_guess") or ("Custom license (see LICENSE file)" if li.get("file") else "No license file found")
            noncommercial = bool(li.get("noncommercial"))
        out.append({
            "id": i, "url": e["url"], "name": name, "owner": owner,
            "category_en": CAT_EN[c["category_source"]], "category_source": c["category_source"],
            "type": d["type"], "language": e.get("language"), "stars": e["stars"], "stars_checked_at": e["checked_at"],
            "license": e.get("license") if e.get("license") not in (None, "NOASSERTION") else (e.get("license_name") or None),
            "pushed_at": e["pushed_at"], "archived": e["archived"], "render_base": rb,
            "description_en": d["description_en"],
            "description_zh_source": up_desc if CJK.search(up_desc) else None,
            "license_detail": license_detail, "noncommercial": noncommercial,
            "install": inst, "usage": usg,
            "safety_upstream": c["safety_upstream"], "featured": i in featured,
            "notes": " ".join(note + ([ov["notes"]] if ov.get("notes") else [])) or None, "judgments": judgments,
            "entry_kind": ov.get("entry_kind", "tool"),
        })
    (ROOT / "data/repos.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(out), "featured", sum(r["featured"] for r in out))


if __name__ == "__main__":
    main()
