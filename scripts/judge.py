#!/usr/bin/env python3
"""Run our TypeSafe judgments and cache them in data/judgments.json. The ONLY script that needs TYPESAFE_API_KEY (env, never printed).
build.py / make_repos.py read the cache and never call the API. Method + numbers: docs/methodology.md, experiments/typesafe/REPORT.md.
Judgments are OURS (Jev via api.typesafe.ai), not upstream's."""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments/typesafe"))
import client  # noqa: E402
import run  # noqa: E402

QUESTION_VERSION = "2026-09-29.v1"
NOUL_VETO = 0.3


def judge(rid, desc=""):
    txt = run.readme(rid)
    low = txt.lower()
    out = {"question_version": QUESTION_VERSION, "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    common = {"repository": rid, "description": desc}
    # E1 category suggestion (never auto-applied)
    _, qs = run.questions_for(rid, desc, txt, "E1")
    r = client.call({**common, "readme_excerpt": txt[:3000]}, qs)
    a = r["answers"]["category"]
    out["model"] = r.get("model")
    out["category_suggestion"] = {"choice": a["choice"], "confidence": round(a["confidence"], 3)}
    # E2 render base: regex proposes, Noul vetoes below threshold
    _, qs = run.questions_for(rid, desc, txt, "E2")
    r = client.call({**common, "readme_excerpt": txt[:8000]}, qs)
    hits = [b for b in run.BASES if re.search(run.KEYWORDS[b], low)]
    noul = {b: round(r["answers"][b]["noul"], 3) for b in run.BASES}
    out["render_base"] = {"regex_hits": hits, "noul": {b: noul[b] for b in hits}, "kept": [b for b in hits if noul[b] >= NOUL_VETO],
                          "vetoed": [b for b in hits if noul[b] < NOUL_VETO], "veto_threshold": NOUL_VETO}
    # E3 install candidate pick (review queue only)
    cands = run.candidates(txt)
    if cands:
        crit = {f"c{i+1}": c for i, c in enumerate(cands)}
        crit["none"] = "None of the candidates is an installation command for this project."
        q = {"install": {"type": "choice", "instructions": "Which candidate is the command or instruction to install this project as a skill/plugin/tool?", "criteria": crit}}
        r = client.call({"repository": rid, "readme_start": txt[:1500]}, q)
        a = r["answers"]["install"]
        out["install_choice"] = {"choice": a["choice"], "confidence": round(a["confidence"], 3),
                                 "candidate": crit[a["choice"]] if a["choice"] != "none" else None, "n_candidates": len(cands)}
    else:
        out["install_choice"] = None
    # E4 inclusion flags (review queue only)
    _, qs = run.questions_for(rid, desc, txt, "E4")
    r = client.call({**common, "readme_excerpt": txt[:6000]}, qs)
    out["inclusion"] = {k: round(r["answers"][k]["noul"], 3) for k in ("makes_video", "agent_oriented")}
    return rid, out


def main():
    repos = json.loads((ROOT / "data/repos.json").read_text())
    with ThreadPoolExecutor(6) as ex:
        res = dict(ex.map(lambda r: judge(r["id"], r["description_en"]), repos))
    (ROOT / "data/judgments.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(len(res), "rows judged; model:", next(iter(res.values())).get("model"))


if __name__ == "__main__":
    main()
