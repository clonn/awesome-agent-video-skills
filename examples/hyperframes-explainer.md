# HyperFrames: from a topic to an explainer

> **Not executed by us.** Commands are copied from the [HyperFrames README](https://github.com/heygen-com/hyperframes/blob/main/README.md). Card: [HyperFrames](../skills/heygen-com__hyperframes.md). The README's own example prompt is a product intro; the explainer workflow below is the one it lists for "explaining a topic".

## Prerequisites and costs

| Item | From the README |
|---|---|
| License | Apache-2.0 |
| Software | Node.js 22+ and FFmpeg |
| Agent | Claude Code (plugin), or any agent that supports skills (Codex, Cursor, Gemini CLI and others) |
| Cost | The framework is free and renders locally; the README also mentions optional HeyGen-hosted cloud rendering and AWS Lambda rendering, and generation of voice, music or images by models, which may cost money |

## Steps
1. Install the plugin for Claude Code:
   ```bash
   claude plugin marketplace add heygen-com/hyperframes
   claude plugin install hyperframes@hyperframes
   ```
   Or install standalone skills (also for OpenCode):
   ```bash
   npx skills add heygen-com/hyperframes
   ```
   The README notes the picker opens with nothing selected and that the Core Skills group is all you need.
2. Use the workflow that fits. The README's "Creation workflows" table lists `/faceless-explainer` for "explaining a topic / concept from arbitrary text", where every visual is generated (typography, abstract graphics, diagrams, data visualization). After the plugin is installed the README says to use `/hyperframes:hyperframes`.
3. Give it your topic or notes. The README's example prompt, for reference:
   > Using `/hyperframes`, create a 10-second product intro with a fade-in title, a background video, and subtle background music.
   An explainer prompt of your own is fine; the loop is the same. (This sentence is ours, not the README's.)
4. The README says the skills teach the loop: plan the video, write valid HTML, wire seekable animations, add media, lint, preview and render.
5. Or drive the CLI yourself:
   ```bash
   npx hyperframes init my-video
   cd my-video
   npx hyperframes preview      # preview in browser with live reload
   npx hyperframes render       # render to MP4
   ```

The README explains that the renderer seeks each frame in headless Chrome and encodes with FFmpeg, so the same input produces the same video.
