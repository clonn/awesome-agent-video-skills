# awesome-agent-video-skills Plans.md

Created: 2026-09-29 · PM: session project-claude-opus55-27 · Executor: project-claude-opus55-c3
Contract: `spec.md` (wins over this file). Inputs: `sources/handoff-facts.md`.
team_validation_mode: manual-pass (PM plus advisor review of Product, Architecture, Security, QA, and Skeptic perspectives)
Spec delta: new root spec.md created (product contract, data schema, layout).
Rule: after finishing each **phase**, send a report to the PM (SendMessage → project-claude-opus55-27) and wait for `pm:確認済`.

---

## Phase 0: Setup

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 0.1 | Read upstream `zhuyansen/awesome-claude-video-skills`: LICENSE, README, data files (json/yaml/csv), and how it builds | Report states the license name and whether derivation with attribution is allowed, plus the data file path. **If derivation is not allowed, stop and report** | - | pm:確認済 |
| 0.2 | `git init`, create dirs per spec Layout, add `.gitignore` (ignore `.claude/state/`, `.env*`, `experiments/**/raw/`) | `git status` clean after the first commit; all dirs exist | 0.1 | pm:確認済 |
| 0.3 | Check lint baseline: `python3 -m py_compile` for scripts and a markdown link check tool (use lychee or a stdlib script, no global installs without asking) | The chosen check commands are written in CONTRIBUTING.md | 0.2 | pm:確認済 |

## Phase 1: Data [tdd:skip:data-curation]

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 1.1 | Build the candidate list: upstream data ∪ live page ∪ must-feature repos | List count reported; per-category counts compared against the targets in handoff-facts (29/26/32/37/19/5/13/11/10/2); every diff explained | 0.1 | pm:確認済 |
| 1.2 | Enrich via `gh api` (stars, license, language, pushed_at, archived, default branch); save raw READMEs to `sources/readmes/<owner>__<repo>.md` (gitignored) | Every entry has `checked_at`; 404s and renames are listed in the report | 1.1 | pm:確認済 |
| 1.3 | Extract `install` / `usage` **verbatim** from each README, with a section anchor URL; otherwise null | Every non-null value has a `source_url`; 10 random entries re-checked against their README with 0 mismatches | 1.2 | pm:確認済 |
| 1.4 | Write `description_en` in our own words (≤25 words), map `category_en`, `type`, `render_base`, `safety_upstream`, and `featured` (~25: top per category + SeeCut + lanshu + the article highlights) | `data/repos.json` validates against the spec schema (write a small stdlib validator in scripts/) | 1.2 | pm:確認済 |
| 1.5 | PM review fixes: (a) CJK: `usage` with CJK → render "See README"; `install` → drop full-line comments only and mark "(comment lines omitted)"; CJK inside the command itself stays verbatim with an English gloss. (b) Add `install.kind` = shell \| agent_prompt \| config; render "Run:" vs "Tell your agent:". (c) For license Other/null, read the LICENSE file and add `license_detail` (SPDX-ish), plus `noncommercial: true` where it applies. (d) Hand-verify the must-feature rows: SeeCut has install=null, render_base=[], license Other, but the README should show an install prompt, HyperFrames, and PolyForm NC. (e) Count null-install rows whose README has an install section under a CJK heading or an unfenced prompt, and feed them to E3. (f) featured +3: cut-video, Paper-Cut, data-animation-skills (25 total) | validate.py passes with new fields; SeeCut row correct; miss list reported | 1.4 | pm:依頼中 |

## Phase 2: TypeSafe experiments (user-requested; key in env `TYPESAFE_API_KEY`) — run in parallel with Phase 1.3/1.4

Goal: find where Jev judgments can replace fragile parsing or hand-labeling in this curation pipeline, measure the results, and hand me the numbers so I can propose changes.
Rules: read the live docs first (https://docs.typesafe.ai/llms.txt, how-to-build-with-system-one.md, primitives choice/noul/score, confidence.md, and the Python SDK or HTTP API page). Check the key is set with `[ -n "$TYPESAFE_API_KEY" ]`; never echo it. **Pilot on 20 repos first** and report cost, tokens, and latency before any full 184 run. Put code in `experiments/typesafe/`, results in `experiments/typesafe/results/*.json`, and a summary in `experiments/typesafe/REPORT.md`.

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 2.0 | Gold set: hand-verify 30 repos (a stratified mix across categories and star tiers) for category, render_base, install command, and in-scope yes/no, using README evidence | `experiments/typesafe/gold.json` with 30 rows plus an evidence note per field | 1.2 | cc:完了 |
| 2.1 | **E1 Category (Choice)**: state = name, description, and README excerpt (first ~3k chars); 10 categories + "out of scope" | Accuracy vs gold and agreement vs upstream labels; list disagreements with confidence; show the confidence-vs-accuracy curve | 2.0 | cc:完了 |
| 2.2 | **E2 Render base (one Noul per base, multi-label) vs regex keyword baseline**: this is the fragile-parsing case, because a mention is not the same as actual use | Precision/recall for both methods on gold; examples where regex is wrong and Noul is right, and the reverse | 2.0 | cc:完了 |
| 2.3 | **E3 Install-command selection (select, not generate)**: code extracts all fenced code blocks + inline commands as candidates; Choice picks the install one or "none" | Exact-match accuracy vs gold for Choice vs a heuristic baseline (first block containing install/clone/npx/cp); candidate-coverage rate | 2.0 | cc:完了 |
| 2.4 | **E4 Inclusion rules (Noul per rule)**: video-making? agent-oriented? README shows output? one-command start? | Agreement with upstream inclusion; flag repos likely out of scope | 2.0 | cc:完了 |
| 2.5 | **E5 Score: beginner-friendliness of the README** (ordered levels), a candidate driver for "Quick picks" / tour ordering | Rank correlation with PM-agreed gold ranking of 10 repos; the report shows the top 10 | 2.0 | cc:WIP |
| 2.6 | Write REPORT.md: a table per experiment (metric, baseline, cost, latency), failure analysis (missing evidence / model / code / service), and a recommendation per experiment (adopt / adopt with threshold / reject) | REPORT.md exists and PM has been sent a summary | 2.1–2.5 | cc:完了 |

## Phase 3: Generated output

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 3.1 | `scripts/build.py` → `README.md` (intro, credits, quick picks, category index, full table) + `catalog/<category>.md` | Running it twice gives an empty `git diff`; the count in README equals `len(repos.json)` | 1.4 | pm:依頼中 |
| 3.2 | Per-repo card template → `skills/<owner>__<repo>.md` for featured entries: what it is, best for, stack, install, usage, license, safety (upstream), links | Cards exist for all `featured: true`; SeeCut card includes the PolyForm NC notice + limits | 3.1 | pm:依頼中 |

## Phase 4: Handwritten docs [tdd:skip:docs-only]

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 4.1 | `docs/install.md`: the ways to install (personal `~/.claude/skills`, project `.claude/skills`, `npx skills add`, plugin marketplace, `claude mcp add`, Codex skills). **Verify against current official docs** (claude-code-guide agent / context7), not memory | Every method cites an official doc URL | 3.1 | pm:依頼中 |
| 4.2 | `docs/how-to-use.md`, `docs/choosing-a-stack.md` (HyperFrames vs Remotion vs Manim vs NLE MCPs such as Premiere/AE), `docs/criteria.md`, `docs/safety.md` | Each exists; criteria and safety attribute upstream's method | 3.1 | pm:依頼中 |
| 4.3 | `tour/`: pages by goal (edit talking-head, explainer, product promo, motion logo, AI avatar, story/animation, music video), with 3 picks + why each, plus `tour/README.md` as the start page | 7 goal pages; each pick links to a card or a catalog row | 3.2 | pm:依頼中 |
| 4.4 | `examples/`: 5 README-derived walkthroughs: SeeCut (talking-head → fine cut → CapCut draft), lanshu AI presenter, HyperFrames explainer, Remotion product promo (video-shotcraft), silence cut (cut-video). Each is marked "not executed by us" and lists prerequisites and costs | 5 files; every command traced to a README URL | 3.2 | pm:依頼中 |
| 4.5 | `CONTRIBUTING.md` (how to add a repo = edit repos.json + run build), `LICENSE` | Exists and follows the outcome of 0.1 | 0.1 | pm:依頼中 |

## Phase 5: QA

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 5.1 | Link check on every URL | 0 broken, or each broken link is listed with a reason | Phase 3, 4 | pm:依頼中 |
| 5.2 | CJK grep on rendered files (`[\p{Han}]`) | Only glossed proper nouns remain | Phase 3, 4 | pm:依頼中 |
| 5.3 | Build idempotency + schema validation + category count check | All pass; output pasted into the report | Phase 3 | pm:依頼中 |
| 5.4 | Spot-check 10 random cards against their README | 0 factual mismatches | Phase 3 | pm:依頼中 |

## Phase 6: Publish — GATED (user approval required)

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 6.1 | `gh repo create` + push | User has approved in the PM session | Phase 5 | blocked (awaiting user approval) |

## Backlog / Optional
- i18n: zh-TW / zh-CN READMEs from `description_zh_source`.
- Scheduled refresh (like upstream's 8h), maybe via GitHub Actions. Depends on the Phase 2 recommendation.
