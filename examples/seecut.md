# SeeCut: from a talking-head clip to a fine cut

> **Not executed by us.** Everything below is taken from the [SeeCut README](https://github.com/YeJe-cpu/SeeCut/blob/main/README.md) (Chinese) and summarized in English. Card: [SeeCut](../skills/YeJe-cpu__SeeCut.md).

## Prerequisites and costs

| Item | From the README |
|---|---|
| License | PolyForm Noncommercial 1.0.0: personal use only; commercial use needs the author's permission |
| Platform | Tested on macOS only |
| Agent | Claude Code tested; other skill-capable agents "in theory" work. Multi-round self-review needs generous quota |
| Video-watching model | Antigravity CLI (`agy`), which lets the AI actually watch the video; Google account login, with a free weekly-refreshing quota and a paid tier with more |
| Renderer and tools | HyperFrames CLI (`npx -y hyperframes@latest`), ffmpeg, Node 22+, Python 3, `pip install faster-whisper`, `npm i playwright-core` in the project folder; all free |
| Optional avatar step | HeyGen account plus API wallet: about $0.04 per second (photo-driven AV4) or $0.12 per second (digital twin AV5); Doubao TTS from Volcano Engine has a free starting quota |
| Time | A 25-second sample takes about 1 hour |

## Steps (README section "the fastest way to run it")
1. Prepare a folder with one 20-30 second vertical, half-body talking-head clip, plus 3-6 optional screenshots of things mentioned in it. Start with a short sample before a full video.
2. Set up the environment and run the README's check until every required item passes:
   ```bash
   zsh skill/seecut/scripts/preflight.sh
   ```
3. Put `skill/seecut` into `~/.claude/skills/` (or your agent's skills directory), then open a new conversation and run the README's command:
   ```text
   /seecut 素材：<你的文件夹>
   ```
   Gloss: 素材 means "footage"; 你的文件夹 means "your folder".
4. You get a rendered video (saved to `~/Downloads`), a layered project package and a delivery report saying what changed in each version and the quality-check verdict.

**How it works (README):** understand the footage, capture real evidence (real screenshots, not invented UIs), arrange, render, self-review with pairwise comparison (new version must beat the old one), and revise up to three times.

## Optional: hand the setup to your agent
This one-line prompt is **not from the README**. It is reported in the author's announcement post (Leaf Yeah!, @leaf_sanren on X) and translated here; treat it as the author's suggestion, not verified text:

> Clone https://github.com/YeJe-cpu/SeeCut, install skill/seecut into ~/.claude/skills/, run skill/seecut/scripts/preflight.sh, install everything it needs until it passes, then tell me how to start.

## Optional: a layered CapCut/Jianying (剪映) draft
The README lists this as an optional third step (a layered project that opens as an editable draft in Jianying, the Chinese edition of CapCut). The post says it relies on a third-party tool, jianying-headless. See the README's `jianying/` folder.

## Limits
Sound effects are only "usable" and screen-recording plus corner-avatar footage is under-tested (author's post).
