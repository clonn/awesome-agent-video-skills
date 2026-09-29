# TypeSafe experiments: where a Jev judgment can replace fragile code in this curation pipeline

Date: 2026-09-29. Model: `jev-latest` (Jev 1.13, per https://docs.typesafe.ai/models.md). Client: stdlib HTTP, `experiments/typesafe/client.py`.
Docs used: [api](https://docs.typesafe.ai/api.md), [models](https://docs.typesafe.ai/models.md), [choice](https://docs.typesafe.ai/primitives/choice.md), [noul](https://docs.typesafe.ai/primitives/noul.md), [score](https://docs.typesafe.ai/primitives/score.md), [confidence](https://docs.typesafe.ai/confidence.md), [how to build](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [python usage](https://docs.typesafe.ai/sdk/python/usage.md).
These are **our own judgments** (executor, method and date above), not upstream's. Reproduce: `python3 experiments/typesafe/run.py full && python3 experiments/typesafe/evaluate.py full` (needs `TYPESAFE_API_KEY`; raw answers in `results/full_raw.json`, metrics in `results/metrics.json`).

## Caveats (read first)
- **Gold set is small (n=30) and labeled by the executor from README evidence**, not by an independent second person. Per-field evidence is in `gold.json`. Differences of a few points are noise.
- 7 of 30 gold categories differ from upstream's label, so category "truth" is itself contestable (editing vs short-form vs general is a judgment call).
- Thresholds in the hybrid variants (E2 0.3, E3 0.7) were **picked by looking at the same 30 gold rows**, so those numbers are optimistic. Confirm on fresh rows before adopting.
- E5 has no gold ranking yet: the plan says a PM-agreed ranking of 10 repos. Only the score distribution is reported.
- README text was truncated (E1 3,000 chars, E2 8,000, E4/E5 6,000, E3 1,500 plus code-extracted candidates); some misses are missing evidence, not model error.

## Cost and latency (full run: 184 repos x 5 experiments = 919 calls, 0 errors)
Pricing: $0.042 per million input tokens, output free ([models](https://docs.typesafe.ai/models.md)). Pilot (20 repos, 100 calls): 235,900 input tokens, $0.0099, p50 0.41 s, p95 0.73 s.

| Experiment | calls | avg input tokens | p50 s | p95 s | cost USD |
|---|---:|---:|---:|---:|---:|
| E1 Choice category | 184 | 2,014 | 0.45 | 0.71 | 0.0156 |
| E2 Noul x10 render base | 184 | 2,887 | 0.41 | 0.74 | 0.0223 |
| E3 Choice install pick | 183 | 1,485 | 0.39 | 0.69 | 0.0114 |
| E4 Noul x4 inclusion | 184 | 2,280 | 0.42 | 0.71 | 0.0176 |
| E5 Score beginner-friendliness | 184 | 2,298 | 0.39 | 0.75 | 0.0178 |
| **Total** | 919 | | | | **0.0847** |

Upstream reports about $200 for its 180-repo classification run, so a full pass here is about 2,000x cheaper. Cost is not a constraint at this scale.

## E1 Category (Choice: 10 categories + out_of_scope)
| Metric | Value |
|---|---|
| Accuracy vs gold (n=30) | 83.3% (majority-class baseline 16.7%) |
| Upstream label vs gold | 76.7% |
| Agreement with upstream, all 184 | 76.1% |

Confidence vs accuracy (vs gold / vs upstream): >0.9: 95.5% (n=22) / 89.6% (n=96); 0.5-0.9: 60% (n=5) / 67.2% (n=67); <0.5: 33% (n=3) / 42.9% (n=21). Confidence is well ordered.
Gold errors (5): OpenStoryline (general vs editing, conf 0.44), jtxvideo (editing vs shorts, 0.52), video-gen (general vs editing, 0.71), Editor-IA-Pro (general vs editing, 0.92), ai-self-media-packaging (shorts vs editing, 0.45). All are neighbor-category calls where the README plausibly supports both.
Predicted out_of_scope: EverMind-AI/Raven, JimLiu/taohuayuan, remotion-dev/skills.
**Recommendation: adopt with threshold.** Use it to propose a category and auto-accept only at confidence >0.9; send the rest (about 36% of repos, 88 of 184) to human review. Do not treat it as ground truth: it agrees with upstream's label no better than upstream's own labels agree with our gold.

## E2 Render base (one Noul per base) vs regex keyword baseline
Scored on 28 certain positives and all certain negatives (labels marked uncertain are excluded).
| Method | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Regex "keyword appears in README" | 28 | 8 | 0 | 0.778 | 1.000 | 0.875 |
| Noul >= 0.5 | 25 | 7 | 3 | 0.781 | 0.893 | 0.833 |
| Noul >= 0.3 | 28 | 10 | 0 | 0.737 | 1.000 | 0.848 |
| Noul >= 0.9 | 18 | 1 | 10 | 0.947 | 0.643 | 0.766 |
| **Hybrid: regex match AND Noul >= 0.3** | 28 | 5 | 0 | 0.848 | 1.000 | **0.918** |

Where regex is wrong and Noul right (4): After Effects named only as "No After Effects" (html-animation, Noul 0.01) or in a comparison (lottie, 0.04); p5.js mentioned in "The painted look isn't p5" (functional-emotions, 0.03); Lottie in the name of a custom `lottie_engine` (motion-skills, 0.37).
Where Noul is wrong and regex right (6): 3 missed positives at 0.5 (codex-storyboard Remotion 0.40 / HyperFrames 0.41, packaging skill HyperFrames 0.44; the README says these are optional or alternative renderers) and 3 false positives on ffmpeg (0.75-0.80, where ffmpeg is a listed dependency).
**Recommendation: adopt the hybrid** (regex proposes, Noul vetoes mentions that are not use). Noul alone does not beat regex here; standalone rejected. Re-tune the 0.3 veto on fresh rows.

## E3 Install-command selection (code extracts candidates, Choice picks one or "none")
Candidate coverage on gold: 100% (25/25 positives contain the gold command in some candidate). Gold has 25 repos with an install command and 5 without.
| Method | Accuracy on 25 with install | Accuracy on 5 with none | Overall (30) |
|---|---:|---:|---:|
| Heuristic: first block containing install/clone/npx/cp | 84% | 20% | 73.3% |
| Choice alone | 72% | 100% | 76.7% |
| **Hybrid: Choice if confidence >= 0.7, else heuristic** | 88% | 100% | **90.0%** |
(0.9 threshold gives the same 90.0%; at 0.5 it equals Choice alone.)

Choice-alone errors (7): 4 said "none" at moderate confidence (0.29-0.68) although a clone or install block was a candidate (OpenStoryline, OpenMontage, ai-self-media-packaging, Raven); 3 picked a different but plausible install (a `cp -R` skill copy, a PowerShell copy, a mkdir/cp block). Several "errors" are gold-strictness: the alternates are legitimate install steps.
On all 184: Choice and the shipped extractor agree on 92 of 183. Extractor null but Choice picks a command: 23 (e.g. `npx skills add JimLiu/baocut -g -a claude-code codex -y`, `/plugin marketplace add bangtutorial/bang-motion`, `claude mcp add ...`; the heading heuristic misses installs under non-standard headings). Extractor has a value but Choice says "none": 25 (some are correct catches, e.g. cs-shotcraft's snippet is usage text not an install; some are Choice misses, e.g. a real `/plugin marketplace add` at conf 0.88).
**Recommendation: adopt with threshold.** Keep candidate generation in code and verbatim output (Choice only selects, so nothing is generated and the no-fabrication rule holds). Use confidence >= 0.7 else fall back to the heuristic, and route disagreements between the two to a human. This directly fixes the extractor misses PM flagged.

## E4 Inclusion rules (four Noul: makes video, agent-oriented, shows output, one-command start)
- makes_video vs gold: 26/26 positives and 4/4 negatives correct (n=30).
- Across all 184 upstream-included repos, 167 pass makes_video >= 0.5 and agent_oriented >= 0.5; **17 are flagged**. Most-flagged are the craft carve-out repos (screenwriting-skills 0.01, video-script-builder 0.07, viral-video-decomposer 0.08, video-shot-analysis-feishu 0.17, ...): these do not make video, which upstream's own rule 1 states, so they are listed "by maintainer's choice". Also flagged: JimLiu/taohuayuan (0.19 / 0.02), EverMind-AI/Raven (0.36 / 0.36), and three source-code/CLI repos with low agent_oriented (PDoomVideo 0.31, functional-emotions-video 0.10, AKMessi/vex 0.34).
- Mean probabilities: makes_video 0.89, agent_oriented 0.93, shows_output 0.45, one_command_start 0.84. shows_output looks weak (README excerpt is text-only, so images and videos are invisible to the model); do not trust it.
**Recommendation: adopt makes_video and agent_oriented as review flags** (not as auto-removal). Reject shows_output and one_command_start as-is. The flagged list is worth a manual look before publishing.

## E5 Score: beginner-friendliness (5 levels)
Scores range 0.02-3.19 (mean 2.01), confidence mostly 0.4-0.65. Top 10: jc-remotion-skills 3.19, riffkit/skill 2.95, magichourhq/skills 2.94, JimLiu/taohuayuan 2.72, codex-video-short-maker 2.68, laoxu-video-script 2.64, codex-storyboard 2.60, lipnardo 2.50, naive-video-skill 2.50, book-video-production-skill 2.46. Bottom: Raven 0.02, AdobePremiereProMCP 0.18, OpenChatCut 0.36, anidoodle 0.69, OpenMontage 0.75.
No rank correlation is reported: the PM-agreed 10-repo gold ranking does not exist yet. Mid-range confidence is low, and the ordering rewards repos with short READMEs, which is plausible but unverified.
**Recommendation: undecided pending a gold ranking.** Do not use it to order the tour until it has been checked against a human ranking of 10 repos.

## Failure analysis
| Failure | Cause class | Example |
|---|---|---|
| Neighbor-category disagreements (E1) | Missing evidence / genuine ambiguity in the label set | OpenStoryline general vs editing |
| Optional or alternative renderers scored low (E2) | Model, under an "actually uses" question | codex-storyboard Remotion 0.40 |
| ffmpeg dependency read as use (E2) | Model | onboarding-video-generator 0.80 |
| Choice says "none" although a clone block exists (E3) | Model or short state (README cut at 1,500 chars) | OpenMontage 0.56 |
| Extractor misses installs under odd headings (E3) | Code | bang-motion `/plugin marketplace add` |
| Text-only excerpt cannot show output (E4 shows_output) | Missing evidence | mean 0.45 |
| Service | None observed: 919 calls, 0 errors, p95 < 1 s | |

## What stays in code
Candidate generation (fenced-block and command extraction, regex keyword hits), the enum of categories and bases, thresholds, fallback to the heuristic, human-review routing, and all verbatim output. The model only decides among candidates or answers a closed yes/no.

## Holdout check (task 2.7)
Thresholds and the adopt rule were committed before labeling (`holdout_prereg.json`, commit aa61bb4). Twenty new rows (not in the 30-row gold set) were labeled blind by a fresh subagent that saw no model outputs and no gold.json (`holdout_gold.json`). The 20 include 4 rows from the "extractor null / Choice found" set and 4 from "extractor value / Choice none". Coverage of categories is uneven (no avatar or music rows). Small n: treat differences of one or two rows as noise. Reproduce: `python3 experiments/typesafe/evaluate_holdout.py`.

| Experiment | Preregistered rule | Holdout result | Baseline | Adopt? |
|---|---|---|---|---|
| E1 Choice category | auto-accept only at confidence > 0.9 | 8 of 20 rows above 0.9, **8/8 correct**; overall accuracy 65% (upstream label 70%) | upstream label | Yes, as a suggestion only (categories stay upstream's) |
| E2 Render base | regex match AND Noul >= 0.3 | **F1 1.00** (P 1.00, R 1.00, 18 TP, 0 FP, 0 FN) | regex F1 0.75 (P 0.60, 12 FP); Noul alone 0.5: F1 0.87 | **Yes** |
| E3 Install | Choice if confidence >= 0.7, else heuristic | overall 75% | heuristic 80%; Choice alone 70% | **No** (below baseline) |

E3 detail: on the 8 disagreement rows, heuristic 6/8, Choice 6/8, hybrid 5/8. Candidate coverage 16/17 positives. Misses: zack-d-films and vibe-editing (gold says no install command; the heuristic and hybrid returned one), lemo-opuscar (Choice said none), wechat-article-remotion, ai-video-editing-skill. The 90% figure in the first evaluation was optimistic because the threshold was tuned on the same 30 rows; on unseen rows the hybrid does not beat the shipped heuristic. Do not replace the extractor with it. It is still useful as a **review signal**: rows where the extractor and Choice disagree go to the human review queue.

E2 caveat: the hybrid's perfect score on 18 positives is a small sample, and regex gating means it can never add a base the README does not name.
