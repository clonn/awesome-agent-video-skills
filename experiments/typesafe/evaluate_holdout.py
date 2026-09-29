#!/usr/bin/env python3
"""Score the preregistered holdout (holdout_prereg.json + holdout_gold.json) with thresholds fixed in advance."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "experiments/typesafe"
pre = json.loads((D / "holdout_prereg.json").read_text())
gold = {g["id"]: g for g in json.loads((D / "holdout_gold.json").read_text())}
raw = json.loads((D / "results/full_raw.json").read_text())
cand = {c["id"]: c for c in json.loads((ROOT / "data/candidates.json").read_text())}
ids = pre["ids"]
assert set(gold) == set(ids), set(gold) ^ set(ids)
M = {}


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(p, 3), "recall": round(r, 3), "f1": round(f, 3)}


# E1
rows = []
for i in ids:
    a = raw[i]["E1"]["answers"]["category"]
    rows.append((i, a["choice"], a["confidence"], gold[i]["category_gold"]))
hi = [x for x in rows if x[2] > 0.9]
M["E1"] = {"n": len(rows), "accuracy_overall": round(sum(x[1] == x[3] for x in rows) / len(rows), 3),
           "upstream_label_accuracy": round(sum(cand[i]["category_source"] == gold[i]["category_gold"] for i in ids) / len(ids), 3),
           "auto_accept_n(conf>0.9)": len(hi), "auto_accept_accuracy": round(sum(x[1] == x[3] for x in hi) / len(hi), 3) if hi else None,
           "wrong": [(x[0], x[1], x[3], round(x[2], 2)) for x in rows if x[1] != x[3]]}
# E2
tp = fp = fn = rtp = rfp = rfn = htp = hfp = hfn = 0
for i in ids:
    txt = run.readme(i).lower()
    for b in run.BASES:
        if b in gold[i]["render_base_uncertain"]:
            continue
        truth = b in gold[i]["render_base"]
        n = raw[i]["E2"]["answers"][b]["noul"]
        reg = bool(re.search(run.KEYWORDS[b], txt))
        p_n, p_h = n >= 0.5, reg and n >= 0.3
        tp += truth and p_n; fp += (not truth) and p_n; fn += truth and not p_n
        rtp += truth and reg; rfp += (not truth) and reg; rfn += truth and not reg
        htp += truth and p_h; hfp += (not truth) and p_h; hfn += truth and not p_h
M["E2"] = {"regex": prf(rtp, rfp, rfn), "noul_0.5": prf(tp, fp, fn), "hybrid_regex_and_noul_0.3": prf(htp, hfp, hfn)}
M["E2"]["adopt_hybrid"] = M["E2"]["hybrid_regex_and_noul_0.3"]["f1"] >= M["E2"]["regex"]["f1"]
# E3
def ok(pick, sub):
    return (pick is None) if sub is None else (bool(pick) and sub in pick)
res = {"heuristic": 0, "choice": 0, "hybrid": 0}
per = []
for i in ids:
    r = raw[i]["E3"]
    cands = [] if "skipped" in r else run.candidates(run.readme(i))
    h = run.heuristic_install(cands)
    ch = None if "skipped" in r or r["choice"] == "none" else r["chosen_text"]
    hy = ch if ("skipped" not in r and r["confidence"] >= 0.7) else h
    sub = gold[i]["install_contains"]
    cov = None if sub is None else any(sub in c for c in cands)
    res["heuristic"] += ok(h, sub); res["choice"] += ok(ch, sub); res["hybrid"] += ok(hy, sub)
    per.append((i, sub is not None, cov, ok(h, sub), ok(ch, sub), ok(hy, sub)))
n = len(ids)
M["E3"] = {k: round(v / n, 3) for k, v in res.items()}
M["E3"]["n"] = n
M["E3"]["with_install"] = sum(1 for x in per if x[1]); M["E3"]["candidate_coverage_of_positives"] = f"{sum(1 for x in per if x[2])}/{sum(1 for x in per if x[1])}"
setAB = set(pre["set_A_extractor_null_choice_found"]) | set(pre["set_B_extractor_value_choice_none"])
sab = [x for x in per if x[0] in setAB]
M["E3"]["disagreement_rows_n8"] = {"heuristic": sum(x[3] for x in sab), "choice": sum(x[4] for x in sab), "hybrid": sum(x[5] for x in sab)}
M["E3"]["adopt_hybrid"] = M["E3"]["hybrid"] >= M["E3"]["heuristic"]
M["E3"]["misses"] = [(x[0], "has_install" if x[1] else "none", f"heur={x[3]} choice={x[4]} hybrid={x[5]}") for x in per if not x[5]]
(D / "results/holdout_metrics.json").write_text(json.dumps(M, indent=1, ensure_ascii=False))
print(json.dumps(M, indent=1, ensure_ascii=False))
