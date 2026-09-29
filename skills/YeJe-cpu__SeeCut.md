# SeeCut

[YeJe-cpu/SeeCut](https://github.com/YeJe-cpu/SeeCut) · Claude Skill · 130 stars (checked 2026-09-29) · License: PolyForm-Noncommercial-1.0.0

Skill that automatically edits talking-head or avatar footage into short motion-graphic videos, checks its own output with a video model, and can export drafts.

> Note: Rendering uses the HyperFrames CLI; HeyGen is only the optional avatar step (hand-verified against the README).

> **Non-commercial license (PolyForm-Noncommercial-1.0.0).** Personal and non-commercial use only; commercial use needs the author's permission.

## At a glance

- **Category:** Editing & Post-production (upstream's label)
- **Best for:** Turning a 20-30 second talking-head clip into a motion-graphics short, with optional layered CapCut/Jianying draft export.
- **Stack:** HyperFrames (hand-verified against the README)
- **Language:** JavaScript
- **Last push:** 2026-09-29

## Install

_Not executed by us; copied from the README._

Run:

```bash
zsh skill/seecut/scripts/preflight.sh
```

README step 2 (environment check). Step 3 copies skill/seecut into ~/.claude/skills/ and is described in prose only.

Source: [README](https://github.com/YeJe-cpu/SeeCut/blob/main/README.md#%E6%9C%80%E5%BF%AB%E8%B7%91%E9%80%9A).

## Usage

```text
/seecut 素材：<你的文件夹>
```

> Gloss: 素材 means "footage"; 你的文件夹 means "your folder".

Source: [README](https://github.com/YeJe-cpu/SeeCut/blob/main/README.md#%E6%9C%80%E5%BF%AB%E8%B7%91%E9%80%9A).

## License

**Non-commercial license (PolyForm-Noncommercial-1.0.0).** Personal and non-commercial use only; commercial use needs the author's permission.

## Limits (from the README and the author's post)

- A 25-second sample currently takes about 1 hour to produce (README); longer videos take longer.
- Tested on macOS only (README).
- It needs the Antigravity CLI (`agy`) so the AI can watch the video, and a coding agent with enough quota for multi-round self-review (README).
- The author's announcement post (Leaf Yeah!, @leaf_sanren on X) adds that sound effects are only "usable" and that screen-recording plus corner-avatar footage is under-tested.
- Optional last step: export a layered CapCut/Jianying (剪映) draft.

## Safety

- **Upstream's rating:** SAFE. Upstream's grade covers the README and install steps only; we did not review the code.
- **Our notes:** none

## Links

- Repository: https://github.com/YeJe-cpu/SeeCut
- Catalog: [Editing & Post-production](../catalog/editing-and-post-production.md)
