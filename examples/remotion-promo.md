# video-shotcraft: a cinematic product promo with Remotion

> **Not executed by us.** Commands are copied from the [video-shotcraft README](https://github.com/Vincentwei1021/video-shotcraft/blob/main/README.md). Card: [video-shotcraft](../skills/Vincentwei1021__video-shotcraft.md).

## Prerequisites and costs

| Item | From the README |
|---|---|
| License | Apache-2.0 for the skill. The README says Remotion itself is [free for individuals and small teams; companies may need a paid license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) |
| Agent | Claude Code or Codex |
| Software | Not listed in one place. The README's notes on rendering on a headless Linux box mention Node 22 and a Chrome headless-shell binary |
| Assets | The bundled audio has its own license terms (see the README's attribution file) |
| Cost | The skill is free; check any hosted services your prompts pull in |

## Steps
1. Install. The most direct way, per the README, is to hand the repo to your agent:
   ```text
   Install this skill for me: https://github.com/Vincentwei1021/video-shotcraft
   ```
   Or with the skills CLI:
   ```bash
   npx skills add Vincentwei1021/video-shotcraft
   ```
   Or manually:
   ```bash
   git clone https://github.com/Vincentwei1021/video-shotcraft.git
   cd video-shotcraft
   ln -s "$(pwd)" ~/.claude/skills/video-shotcraft   # Claude Code
   # or
   ln -s "$(pwd)" ~/.codex/skills/video-shotcraft    # Codex
   ```
2. Ask for a promo. Example requests from the README:
   ```text
   Use video-shotcraft to create a promo for my desktop product.
   Use the deck-deal-flyin and row-embed shot cards to present this feature.
   Design a product close-up inspired by spotlight-hero-card.
   ```
3. If you name no shot cards, the skill introduces its built-in template first and asks whether to use it. The template, Ink Press, is described as 36.2 seconds, 1920x1080, 30 fps and 10 shots. You can also browse the shot cards in the README's Gallery before you start.
4. The README describes an optional browser workbench for editing the delivered film afterwards, and a JianYing (CapCut CN) project export; see the README for those.
