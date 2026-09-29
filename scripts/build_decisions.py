#!/usr/bin/env python3
"""Turn the PM's review-queue decisions into data/review_decisions.json (reproducible; needs cached READMEs in sources/readmes).
Accepted install candidates are expanded to the whole fenced block in the README that contains them, verbatim."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
judg = json.loads((ROOT / "data/judgments.json").read_text())
enr = {e["id"]: e for e in json.loads((ROOT / "data/enriched.json").read_text())}
snip = json.loads((ROOT / "data/snippets.json").read_text())

ACCEPT = {  # id -> extra install fields
    "BusyBee3333/animated-explainer-skills": {}, "JimLiu/baocut": {}, "Maartenlouis/remotion-ads": {},
    "bangtutorial/bang-motion": {}, "heygen-com/hyperframes": {},
    "hahadu4520/vlog-cut": {"gloss": "The trailing Chinese comment 字幕默认字体 means \"default subtitle font\"."},
    "inematds/skill-video-plan-editor": {}, "jtydhr88/screenwriting-skills": {}, "kangarooking/promo-creator-skills": {},
    "misbahsy/tiktok-ig-shorts": {}, "molkex/mcp-flow-google": {"note": "Connects to a third-party hosted MCP server (openflowmcp.com)."},
    "remotion-dev/skills": {}, "santmun/video-vox": {}, "vibe-motion/remotion-code-motion-explainer": {},
    "jinjin1/scenewright": {"gloss": "Korean comments: 로컬 TTS용 Python 환경 means \"Python environment for local TTS\"; (선택) 스톡 API 키 입력 means \"(optional) enter stock-footage API keys\"."},
    "liyue-aigc/xianxia-cinematic-video-director": {"note": "Windows PowerShell commands."},
    "magichourhq/skills": {"note": "Installs one of several skills (image-to-video shown)."},
    "JUNKDOGE-JOE/after-effects-mcp": {"kind": "agent_prompt"},
    "toufuim/personal-ip-brand-intro-skill": {"kind": "agent_prompt", "gloss": "Prompt (translated from the README): use $skill-installer to install personal-ip-brand-intro from the repo URL; the skill path is personal-ip-brand-intro."},
    "Monet-AI-Editor/Monet": {},
}
SAFETY = {
    "Monet-AI-Editor/Monet": ["Install pipes a remote script into bash (curl ... | bash); read install.sh first."],
    "molkex/mcp-flow-google": ["Connects to a third-party hosted MCP server (openflowmcp.com); review what data it receives."],
}
NOTES = {
    "EverMind-AI/Raven": "The entry is the git-story-film skill path inside the larger Raven repository, not Raven as a whole.",
}
NULL_INSTALL = ["Anil-matcha/vox-ai-motion-graphics-generator"]
INSTALL_NOTE = {"davidcervinka/vibe-editing": "Sets up the dependency browser-use/video-use."}
SHOWCASE = ["JimLiu/taohuayuan", "JohnHeibel/PDoomVideo", "ledbetterljoshua/functional-emotions-video"]


def expand(text, cand):
    """Return the raw fenced block in text that contains cand's first line (verbatim; the judged candidate came from
    HTML-stripped text, so we re-read the raw README), else the inline candidate if it is a raw substring."""
    first = cand.split("\n")[0].strip()
    pos = text.find(first)
    if pos < 0:
        raise AssertionError("candidate not found in raw README")
    start = text.rfind("```", 0, pos)
    end = text.find("```", pos)
    if start >= 0 and end > pos:
        nl = text.find("\n", start)
        block = text[nl + 1:end].strip("\n")
        if first in block and len(block) <= 4000:
            return block
    return first


def main():
    out = {}
    for rid, extra in ACCEPT.items():
        cand = judg[rid]["install_choice"]["candidate"]
        text = (ROOT / "sources/readmes" / (rid.replace("/", "__") + ".md")).read_text()
        cmd = expand(text, cand)
        assert cmd in text, rid
        inst = {"command": cmd, "source_url": enr[rid]["readme_html_url"], **extra}
        out.setdefault(rid, {})["install"] = inst
    for rid in NULL_INSTALL:
        out.setdefault(rid, {})["install"] = None
    first = "pip install -r requirements.txt   # ffmpeg must be on PATH (brew install ffmpeg)"
    text = (ROOT / "sources/readmes/ZiadAbdelkarim__beat-synced-edit.md").read_text()
    assert first in text
    src = snip["ZiadAbdelkarim/beat-synced-edit"]["install"]["source_url"]
    out.setdefault("ZiadAbdelkarim/beat-synced-edit", {})["install"] = {"command": first, "source_url": src}
    for rid, n in INSTALL_NOTE.items():
        s = snip[rid]["install"]
        out.setdefault(rid, {})["install"] = {"command": s["command"], "source_url": s["source_url"], "note": n}
    for rid, s in SAFETY.items():
        out.setdefault(rid, {})["safety_notes"] = s
    for rid, n in NOTES.items():
        out.setdefault(rid, {})["notes"] = n
    for rid in SHOWCASE:
        out.setdefault(rid, {})["entry_kind"] = "showcase"
    (ROOT / "data/review_decisions.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(len(out), "rows with decisions")


if __name__ == "__main__":
    main()
