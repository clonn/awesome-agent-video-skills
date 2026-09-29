#!/usr/bin/env python3
"""Score E1-E5 from results/<mode>_raw.json against gold.json. Writes results/metrics.json and prints a summary."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "experiments/typesafe/results"
mode = sys.argv[1] if len(sys.argv) > 1 else "full"
raw = json.loads((R / f"{mode}_raw.json").read_text())
gold = {g["id"]: g for g in json.loads((ROOT / "experiments/typesafe/gold.json").read_text())}
repos = {r["id"]: r for r in json.loads((ROOT / "data/repos.json").read_text())}
cand = {c["id"]: c for c in json.loads((ROOT / "data/candidates.json").read_text())}
M = {}


def bucket(c):
    return ">0.9" if c > 0.9 else ("0.5-0.9" if c >= 0.5 else "<0.5")


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": p and round(p, 3), "recall": r and round(r, 3), "f1": f and round(f, 3)}


# ---- E1
ids_g = [i for i in gold if i in raw]
def e1(i):
    a = raw[i]["E1"]["answers"]["category"]
    return a["choice"], a["confidence"]
acc_gold = [(i, e1(i)[0] == gold[i]["category_gold"], e1(i)[1]) for i in ids_g]
maj = "editing"
agree_up = [(i, e1(i)[0] == cand[i]["category_source"], e1(i)[1]) for i in raw]
def curve(rows):
    out = {}
    for b in (">0.9", "0.5-0.9", "<0.5"):
        x = [ok for _, ok, c in rows if bucket(c) == b]
        out[b] = {"n": len(x), "accuracy": round(sum(x) / len(x), 3) if x else None}
    return out
M["E1"] = {
    "gold_accuracy": round(sum(ok for _, ok, _ in acc_gold) / len(acc_gold), 3), "gold_n": len(acc_gold),
    "gold_majority_baseline": round(sum(gold[i]["category_gold"] == maj for i in ids_g) / len(ids_g), 3),
    "upstream_gold_agreement": round(sum(cand[i]["category_source"] == gold[i]["category_gold"] for i in ids_g) / len(ids_g), 3),
    "agreement_vs_upstream_all": round(sum(ok for _, ok, _ in agree_up) / len(agree_up), 3), "all_n": len(agree_up),
    "curve_vs_gold": curve(acc_gold), "curve_vs_upstream": curve(agree_up),
    "gold_errors": [(i, e1(i)[0], gold[i]["category_gold"], round(e1(i)[1], 2)) for i, ok, _ in acc_gold if not ok],
    "upstream_disagreements_lowconf": sorted([(i, e1(i)[0], cand[i]["category_source"], round(c, 2)) for i, ok, c in agree_up if not ok], key=lambda x: x[3])[:15],
    "out_of_scope_predicted": [i for i in raw if e1(i)[0] == "out_of_scope"],
}
# ---- E2
def e2_rows(thr):
    tp = fp = fn = rtp = rfp = rfn = 0
    diffs = {"regex_wrong_noul_right": [], "noul_wrong_regex_right": []}
    for i in ids_g:
        txt = run.readme(i).lower()
        ans = raw[i]["E2"]["answers"]
        for b in run.BASES:
            if b in gold[i]["render_base_uncertain"]:
                continue
            truth = b in gold[i]["render_base"]
            pred = ans[b]["noul"] >= thr
            reg = bool(re.search(run.KEYWORDS[b], txt))
            tp += truth and pred; fp += (not truth) and pred; fn += truth and not pred
            rtp += truth and reg; rfp += (not truth) and reg; rfn += truth and not reg
            if pred == truth and reg != truth: diffs["regex_wrong_noul_right"].append((i, b, "regex says " + str(reg), round(ans[b]["noul"], 2)))
            if reg == truth and pred != truth: diffs["noul_wrong_regex_right"].append((i, b, "noul " + str(round(ans[b]["noul"], 2)), "truth " + str(truth)))
    return prf(tp, fp, fn), prf(rtp, rfp, rfn), diffs
M["E2"] = {"noul_by_threshold": {}, "regex": None}
for thr in (0.3, 0.5, 0.7, 0.9):
    n, r, d = e2_rows(thr)
    M["E2"]["noul_by_threshold"][str(thr)] = n
    if thr == 0.5:
        M["E2"]["regex"] = r
        M["E2"]["examples"] = {k: v[:12] for k, v in d.items()}
        M["E2"]["example_counts"] = {k: len(v) for k, v in d.items()}
# ---- E3
def contains(text, sub):
    return bool(text) and sub in text
rows = []
for i in ids_g:
    r = raw[i]["E3"]
    if "skipped" in r:
        cands = []; ch = None; conf = None
    else:
        cands = run.candidates(run.readme(i)); ch = r["chosen_text"] if r["choice"] != "none" else None; conf = r["confidence"]
    h = run.heuristic_install(cands)
    sub = gold[i]["install_contains"]
    if sub is None:
        rows.append({"id": i, "gold": None, "coverage": None, "choice_ok": ch is None, "heur_ok": h is None, "conf": conf})
    else:
        rows.append({"id": i, "gold": sub, "coverage": any(sub in c for c in cands), "choice_ok": contains(ch, sub), "heur_ok": contains(h, sub), "conf": conf})
pos = [x for x in rows if x["gold"]]
neg = [x for x in rows if not x["gold"]]
M["E3"] = {
    "gold_with_install": len(pos), "gold_none": len(neg),
    "candidate_coverage": round(sum(x["coverage"] for x in pos) / len(pos), 3),
    "choice_acc_positive": round(sum(x["choice_ok"] for x in pos) / len(pos), 3),
    "heuristic_acc_positive": round(sum(x["heur_ok"] for x in pos) / len(pos), 3),
    "choice_acc_on_none": round(sum(x["choice_ok"] for x in neg) / len(neg), 3),
    "heuristic_acc_on_none": round(sum(x["heur_ok"] for x in neg) / len(neg), 3),
    "choice_overall": round(sum(x["choice_ok"] for x in rows) / len(rows), 3),
    "heuristic_overall": round(sum(x["heur_ok"] for x in rows) / len(rows), 3),
    "choice_wrong": [(x["id"], x["gold"], x["coverage"]) for x in rows if not x["choice_ok"]],
    "heuristic_wrong": [(x["id"], x["gold"], x["coverage"]) for x in rows if not x["heur_ok"]],
}
# coverage across all 184: does the extractor's install text agree with the choice?
allagree = tot = 0
for i in raw:
    r = raw[i]["E3"]
    if "skipped" in r: continue
    ex = repos[i]["install"]
    tot += 1
    if ex and r["choice"] != "none" and r["chosen_text"] and (ex["command"].strip()[:60] in r["chosen_text"] or r["chosen_text"][:60] in ex["command"]):
        allagree += 1
M["E3"]["all184_choice_vs_extractor_agree"] = f"{allagree}/{tot}"
M["E3"]["all184_extractor_null_choice_not_none"] = sum(1 for i in raw if "skipped" not in raw[i]["E3"] and not repos[i]["install"] and raw[i]["E3"]["choice"] != "none")
M["E3"]["all184_extractor_present_choice_none"] = sum(1 for i in raw if "skipped" not in raw[i]["E3"] and repos[i]["install"] and raw[i]["E3"]["choice"] == "none")

# ---- hybrids (code candidates/regex first, model confirms; fallback to heuristic when unsure)
tp = fp = fn = 0
for i in ids_g:
    txt = run.readme(i).lower()
    for b in run.BASES:
        if b in gold[i]["render_base_uncertain"]:
            continue
        truth = b in gold[i]["render_base"]
        pred = bool(re.search(run.KEYWORDS[b], txt)) and raw[i]["E2"]["answers"][b]["noul"] >= 0.3
        tp += truth and pred; fp += (not truth) and pred; fn += truth and not pred
M["E2"]["hybrid_regex_and_noul_ge_0.3"] = prf(tp, fp, fn)
M["E3"]["hybrid"] = {}
for thr in (0.5, 0.7, 0.9):
    ok_pos = ok_none = 0
    for x in rows:
        i = x["id"]; r = raw[i]["E3"]
        cands = [] if "skipped" in r else run.candidates(run.readme(i))
        h = run.heuristic_install(cands)
        if "skipped" not in r and r["confidence"] >= thr:
            pick = r["chosen_text"] if r["choice"] != "none" else None
        else:
            pick = h
        if x["gold"]:
            ok_pos += contains(pick, x["gold"])
        else:
            ok_none += pick is None
    M["E3"]["hybrid"][str(thr)] = {"positive_acc": round(ok_pos / len(pos), 3), "none_acc": round(ok_none / len(neg), 3), "overall": round((ok_pos + ok_none) / len(rows), 3)}
# ---- E4
def e4(i, k): return raw[i]["E4"]["answers"][k]["noul"]
g4 = {}
for k, key in (("makes_video", "makes_video"), ("agent_oriented", "in_scope")):
    pass
tp = fp = fn = tn = 0
for i in ids_g:
    truth = gold[i]["makes_video"]; pred = e4(i, "makes_video") >= 0.5
    tp += truth and pred; fp += (not truth) and pred; fn += truth and not pred; tn += (not truth) and not pred
M["E4"] = {"makes_video_vs_gold": {"tp": tp, "fp": fp, "fn": fn, "tn": tn}}
flag = [(i, round(e4(i, "makes_video"), 2), round(e4(i, "agent_oriented"), 2)) for i in raw if e4(i, "makes_video") < 0.5 or e4(i, "agent_oriented") < 0.5]
M["E4"]["upstream_inclusion_agreement"] = f"{len(raw)-len(flag)}/{len(raw)} pass makes_video>=0.5 and agent_oriented>=0.5"
M["E4"]["flagged_out_of_scope"] = sorted(flag, key=lambda x: x[1])[:20]
M["E4"]["mean_probs"] = {k: round(sum(e4(i, k) for i in raw) / len(raw), 3) for k in ("makes_video", "agent_oriented", "shows_output", "one_command_start")}
# ---- E5
sc = sorted(((raw[i]["E5"]["answers"]["beginner"]["score"], raw[i]["E5"]["answers"]["beginner"]["confidence"], i) for i in raw), reverse=True)
M["E5"] = {"top10": [(i, round(s, 2), round(c, 2)) for s, c, i in sc[:10]], "bottom5": [(i, round(s, 2), round(c, 2)) for s, c, i in sc[-5:]],
           "score_range": [round(sc[-1][0], 2), round(sc[0][0], 2)], "mean": round(sum(s for s, _, _ in sc) / len(sc), 2)}
# ---- cost/latency
cl = {}
for i in raw:
    for e, v in raw[i].items():
        if "latency" in v:
            cl.setdefault(e, []).append((v["latency"], v["usage"].get("input_tokens", 0)))
M["cost_latency"] = {}
for e, x in sorted(cl.items()):
    lat = sorted(a for a, _ in x); tok = sum(b for _, b in x)
    M["cost_latency"][e] = {"calls": len(x), "p50_s": lat[len(lat)//2], "p95_s": lat[int(len(lat)*.95)-1], "input_tokens": tok, "avg_tokens_per_call": round(tok/len(x)), "cost_usd": round(tok*0.042e-6, 5)}
(R / "metrics.json").write_text(json.dumps(M, indent=1, ensure_ascii=False))
print(json.dumps(M, indent=1, ensure_ascii=False))
