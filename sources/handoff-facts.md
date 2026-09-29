# Handoff facts (from PM, 2026-09-29)

These facts came from material the user pasted into the PM session. The executor can't fetch them, so they are recorded here in English.
Treat every number as a **claim to re-check live**, not as ground truth.

## Sources (credit both in README)

1. Article: "107 hidden gems under 50 stars: 180 open-source skills that let Claude make video, fully categorized". Author: Jason AI Chuhai (WeChat "杰森AI出海").
   - Repo: https://github.com/zhuyansen/awesome-claude-video-skills
   - Live page: https://agentskillshub.top/best/claude-video-skills/ (auto-refreshes every 8 hours)
2. Article: "An AI edit watched by 70k people: tutorial + open source" by Leaf Yeah! (@leaf_sanren), about SeeCut.

## Upstream method (what the list claims)

- The 4 inclusion rules, each a closed question the model answered by reading the README:
  1. It makes video, edits video, or makes motion graphics. 3D web pages and prompt collections don't count.
  2. It is built for agents: a skill, plugin, MCP server, or toolkit written for agents.
  3. It has a README. A repo without one can't be rated.
  4. Repos with ≥50 stars only need to be on-topic. Repos with <50 stars must also pass a README quality bar: show finished output, get started with one command, say what it produces, have complete docs, and have at least 5 stars.
- Classification and safety rating were done by TypeSafe **Jev**, reading each README one at a time. The whole run cost about $200.
- Safety rating covers the README and install steps only: 178 SAFE, 2 CAUTION (article snapshot of 180 repos).
- Observations:
  - 46 repo descriptions name Remotion and 26 name HyperFrames. Together (72) that's about 40%.
  - "Recipe cards" are becoming reusable assets: video-shotcraft has 152 shot cards, video-talkcraft has 109 motion cards.
  - 107 of 180 repos have fewer than 50 stars, and only 20 have more than 1k.
  - Editing, explainer, framework, and promo repos together make up about two-thirds of the list. Avatars and music video are still early.

## Category target counts (live page snapshot, 184 total)

| zh | English name to use | count |
|---|---|---|
| 框架与通用工具包 | Frameworks & Toolkits | 29 |
| 产品宣传与演示 | Product Promos & Demos | 26 |
| 讲解科普 | Explainers & Education | 32 |
| 剪辑与后期 | Editing & Post-production | 37 |
| 短视频与口播 | Short-form & Talking-head | 19 |
| 数字人 | AI Avatars | 5 |
| 故事与动画 | Story & Animation | 13 |
| 动效与 Logo | Motion Graphics & Logos | 11 |
| 剧本与学习 | Scriptwriting & Film Study | 10 |
| 音乐视频 | Music Videos | 2 |

Types used on the page: Claude Skill, Codex Skill, Agent Tool, MCP Server, AI Tool.
Other small-print numbers: the page says 190.8k total stars, and 137 repos have an explicit license.
Numbers disagree between sources (for example, OpenMontage shows 61.5k in the article and 56.3k on the page). **Always use live `gh api` values.**

## Must-feature repos (the user asked to include these explicitly)

- https://github.com/zhuyansen/awesome-claude-video-skills (upstream list, credit + link)
- https://github.com/cclank/lanshu-create-ai-presenter-video (#17 on page): a provider-agnostic Codex skill that makes a verified AI presenter video from scripts plus one authorized portrait.
- https://github.com/YeJe-cpu/SeeCut (#57 on page). Facts from the author's article, to be verified against the README:
  - Purpose: a *fine cut* with a "native-internet feel", not a rough cut. It takes a talking-head video (real or AI avatar) to an edited short with motion graphics and A/B-roll, and can optionally export a layered CapCut/Jianying (剪映) draft.
  - Install prompt given to the agent: "Clone https://github.com/YeJe-cpu/SeeCut, install skill/seecut into ~/.claude/skills/, run skill/seecut/scripts/preflight.sh, install everything it needs until it passes, then tell me how to start." It also needs the Antigravity CLI so the AI can watch video.
  - Usage: `/seecut 素材：<folder>` ("素材" means "footage"). The folder holds one talking-head clip plus optional screenshots of things mentioned. Try 20–30s first.
  - Pipeline: understand footage → capture real evidence (real screenshots, not fake UIs) → arrange → render → self-review → revise.
  - Uses Gemini for video understanding, because GPT and Claude only sample frames.
  - Judging is pairwise ("which is better?"), not scored. It runs twice with left/right swapped, and a new version must win both runs. It makes at most 3 revisions and stops when a new version can't win or changes are minor.
  - It uses a decision table built from 536 analyzed shots. Rule: show the speaker's face when "talking to you" and shrink or hide the face when "showing you". It also has design tokens, a component library (mostly official HyperFrames components), and per-shot build sheets.
  - The 3-step workflow: (1) avatar via HeyGen AV4 photo (~$0.04/s) or AV5 twin (~$0.12/s), with Doubao TTS recommended over built-in voices; (2) the fine-cut loop; (3) CapCut/Jianying draft via third-party jianying-headless (optional).
  - Limits: a 25s clip takes about 1 hour. Sound effects are only "usable". Screen-recording plus corner-avatar footage is under-tested. Tested on macOS only.
  - **License: PolyForm Noncommercial.** Personal use only; commercial use needs the author's permission. The card must state this.

## Must NOT do

- Don't install or run any listed repo.
- Don't paste READMEs verbatim (a short install command quoted with a source link is fine).
- Don't invent install commands.
- Don't publish to GitHub without user approval.
- Don't print or log `TYPESAFE_API_KEY`.
