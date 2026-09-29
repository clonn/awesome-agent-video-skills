#!/usr/bin/env python3
"""TypeSafe experiments E1-E5 over the curation data. Usage: run.py pilot|full  (stdlib only; key from env, never printed).
Raw answers -> experiments/typesafe/results/<mode>_raw.json (no README text stored). Metrics -> evaluate.py."""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import client  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/typesafe/results"

CATS = {
    "general": ("Frameworks & Toolkits", "General-purpose video toolkits, rendering frameworks and multi-pipeline production systems.", "A tool for one specific video style or goal."),
    "promo": ("Product Promos & Demos", "Product launch films, ads, feature demos and app walkthrough videos.", "Explainers about concepts, or editing of existing footage."),
    "explainer": ("Explainers & Education", "Knowledge videos, tutorials, lectures and narrated lessons.", "Product marketing videos."),
    "editing": ("Editing & Post-production", "Cutting, captions, B-roll, silence removal and recaps of existing footage.", "Videos generated from scratch without source footage."),
    "shorts": ("Short-form & Talking-head", "Vertical short video and talking-head (spoken to camera) production for social platforms.", "Long-form or product promo videos."),
    "avatar": ("AI Avatars", "Digital humans, virtual presenters and lip-sync videos.", "Tools that only edit real recorded people."),
    "story": ("Story & Animation", "Animated tales, short dramas, comics-to-video and cinematic scenes.", "Product or educational videos."),
    "motion": ("Motion Graphics & Logos", "Animated logos, titles, kinetic typography, UI motion and GIFs.", "Full narrated videos."),
    "craft": ("Scriptwriting & Film Study", "What comes before the video: screenwriting, shot analysis, learning from existing videos. Does not produce video itself.", "Tools that render or edit video."),
    "music": ("Music Videos", "Music videos made in code.", "Other video types."),
}
BASES = {
    "Remotion": "Remotion (React video framework)", "HyperFrames": "HyperFrames (HTML/GSAP video composition)",
    "Manim": "Manim (math animation library)", "ffmpeg": "ffmpeg (used to cut, encode or render output video)",
    "After Effects": "Adobe After Effects", "Premiere Pro": "Adobe Premiere Pro", "HeyGen": "HeyGen (avatar video service)",
    "Blender": "Blender", "p5.js": "p5.js", "Lottie": "the Lottie animation format/tools",
}
KEYWORDS = {"Remotion": r"remotion", "HyperFrames": r"hyperframes", "Manim": r"manim", "ffmpeg": r"ffmpeg",
            "After Effects": r"after effects", "Premiere Pro": r"premiere", "HeyGen": r"heygen", "Blender": r"blender",
            "p5.js": r"p5\.?js|\bp5\b", "Lottie": r"lottie"}


def readme(rid):
    t = (ROOT / "sources/readmes" / (rid.replace("/", "__") + ".md")).read_text(errors="replace")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[\]\([^)]*\)", "", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def candidates(text, limit=25):
    """Code-generated candidates: fenced blocks and inline commands (candidate generation stays in code)."""
    out, inb, buf = [], False, []
    for ln in text.split("\n"):
        if ln.lstrip().startswith(("```", "~~~")):
            if inb and buf:
                out.append("\n".join(buf).strip())
            inb, buf = not inb, []
        elif inb:
            buf.append(ln)
    for m in re.finditer(r"`([^`\n]{8,200})`", text):
        s = m.group(1)
        if re.match(r"(git |npx |npm |pip |pipx |cp |curl |/plugin|claude |codex |brew |make |sh |bash |uv )", s):
            out.append(s)
    seen, res = set(), []
    for c in out:
        c = c[:600]
        if c and c not in seen:
            seen.add(c)
            res.append(c)
    return res[:limit]


def heuristic_install(cands):
    for c in cands:
        if re.search(r"install|clone|npx|cp ", c, re.I):
            return c
    return None


def questions_for(rid, desc, txt, exp):
    if exp == "E1":
        crit = {k: {"what": v[1], "not_for": v[2]} for k, v in CATS.items()}
        crit["out_of_scope"] = {"what": "Not a tool for making, editing or planning video/motion graphics (e.g. a general agent framework, 3D web page, prompt collection).", "not_for": "Anything that fits a listed category."}
        return txt[:3000], {"category": {"type": "choice", "instructions": "Which category best describes what this repository is for?", "criteria": crit}}
    if exp == "E2":
        qs = {b: {"type": "noul", "instructions": f"Does this project actually use {d} to build, render or encode its videos (not just mention it, compare against it, or list it as an alternative)?"} for b, d in BASES.items()}
        return txt[:8000], qs
    if exp == "E4":
        qs = {
            "makes_video": {"type": "noul", "instructions": "Does this repository make video, edit video, or make motion graphics? (3D web pages and prompt collections do not count.)"},
            "agent_oriented": {"type": "noul", "instructions": "Is it built for coding agents: a skill, plugin, MCP server, or toolkit written for an AI agent to operate?"},
            "shows_output": {"type": "noul", "instructions": "Does the README show finished output, such as demo videos, screenshots or sample results?"},
            "one_command_start": {"type": "noul", "instructions": "Can a user get started with a single command or a single short instruction, as shown in the README?"},
        }
        return txt[:6000], qs
    if exp == "E5":
        return txt[:6000], {"beginner": {"type": "score", "instructions": "How easy is this README for a complete beginner to understand and start using?",
            "criteria": ["Hard: assumes deep expertise, no clear start, or missing setup steps",
                         "Difficult: has setup steps but they are incomplete or assume prior tooling knowledge",
                         "Moderate: clear purpose and install steps, but requires several prerequisites or manual configuration",
                         "Easy: clear purpose, concise install and a first-use example that works with few prerequisites",
                         "Very easy: one-command or one-sentence start, shows expected output, explains prerequisites"]}}
    raise ValueError(exp)


def run_one(rid, exp, cache):
    txt = readme(rid)
    desc = cache["desc"].get(rid, "")
    if exp == "E3":
        cands = candidates(txt)
        if not cands:
            return {"skipped": "no candidates", "n_cands": 0}
        crit = {f"c{i+1}": c for i, c in enumerate(cands)}
        crit["none"] = "None of the candidates is an installation command for this project."
        qs = {"install": {"type": "choice", "instructions": "Which candidate is the command or instruction to install this project as a skill/plugin/tool?", "criteria": {k: v for k, v in crit.items()}}}
        state = {"repository": rid, "readme_start": txt[:1500]}
        r = client.call(state, qs)
        a = r["answers"]["install"]
        return {"n_cands": len(cands), "choice": a["choice"], "confidence": a.get("confidence"), "probabilities": a.get("probabilities"),
                "chosen_text": crit.get(a["choice"]), "usage": r.get("usage", {}), "latency": r["_latency_s"]}
    state_txt, qs = questions_for(rid, desc, txt, exp)
    r = client.call({"repository": rid, "description": desc, "readme_excerpt": state_txt}, qs)
    return {"answers": r["answers"], "usage": r.get("usage", {}), "latency": r["_latency_s"]}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    gold = json.loads((ROOT / "experiments/typesafe/gold.json").read_text())
    repos = json.loads((ROOT / "data/repos.json").read_text())
    cache = {"desc": {r["id"]: r["description_en"] for r in repos}}
    if mode == "pilot":
        ids = [g["id"] for g in gold][::3][:10] + [g["id"] for g in gold][1::3][:10]
    elif mode == "gold":
        ids = [g["id"] for g in gold]
    else:
        ids = [r["id"] for r in repos]
    exps = ["E1", "E2", "E3", "E4", "E5"]
    jobs = [(i, e) for i in ids for e in exps]
    workers = 1 if mode == "pilot" else 6
    t0 = time.time()

    def go(job):
        try:
            return job, run_one(job[0], job[1], cache)
        except Exception as ex:  # noqa: BLE001
            return job, {"error": str(ex)[:300]}

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(go, jobs))
    raw = {}
    for (i, e), v in res:
        raw.setdefault(i, {})[e] = v
    OUT.mkdir(exist_ok=True)
    (OUT / f"{mode}_raw.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False))
    lat = [v["latency"] for _, v in res if "latency" in v]
    tok = sum(v["usage"].get("input_tokens", 0) for _, v in res if "usage" in v)
    errs = [(j, v["error"]) for j, v in res if "error" in v]
    print(f"mode={mode} repos={len(ids)} calls={len(jobs)} errors={len(errs)} wall={time.time()-t0:.1f}s")
    if lat:
        s = sorted(lat)
        print(f"latency p50={s[len(s)//2]}s p95={s[int(len(s)*0.95)-1]}s max={s[-1]}s; input_tokens={tok}; cost=${tok*client.PRICE_PER_INPUT_TOKEN:.5f}")
    for j, e in errs[:5]:
        print("ERR", j, e)


if __name__ == "__main__":
    main()
