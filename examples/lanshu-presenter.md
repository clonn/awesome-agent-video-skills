# lanshu: an AI presenter video from a script and one portrait

> **Not executed by us.** Commands are copied from the [lanshu-create-ai-presenter-video README](https://github.com/cclank/lanshu-create-ai-presenter-video/blob/main/README.md). Card: [lanshu](../skills/cclank__lanshu-create-ai-presenter-video.md).

## Prerequisites and costs

| Item | From the README |
|---|---|
| License | MIT |
| Agent | An Agent Skills harness, or any coding agent that can read files and run shell commands |
| Software | Python 3.9+, FFmpeg with `ffprobe`, Bash, `jq`, `awk`, `sed` |
| Services | At least one voice synthesis, presenter video generation and lip-sync capability: a cloud CLI, an API or a local model. The skill is provider-neutral, so you choose; prices depend on your choice |
| Optional | A timeline compositor such as HyperFrames for captions, motion graphics and final rendering |
| Cost controls | Before the first paid call the agent states the uploads, requested seconds, known price, pilot size and retry ceiling |
| Consent | Image rights and adult-presenter status are confirmed before any upload; voice cloning needs explicit authorization |

## Steps
1. Install (Claude Code example from the README; the folder name must stay `lanshu-create-ai-presenter-video`):
   ```bash
   git clone https://github.com/cclank/lanshu-create-ai-presenter-video.git \
     ~/.claude/skills/lanshu-create-ai-presenter-video
   ```
   For Codex the README uses `~/.codex/skills/` and invokes it with `$lanshu-create-ai-presenter-video`.
2. Describe the video (README quick start):
   ```text
   Turn this script and portrait into a 30-second 16:9 presenter video with live captions.
   ```
3. Or set up a job manually. Point `SKILL_DIR` at your installation and initialize:
   ```bash
   SKILL_DIR=~/.claude/skills/lanshu-create-ai-presenter-video

   python3 "$SKILL_DIR/scripts/init_job.py" \
     --job-dir ~/Videos/my-presenter-video \
     --presenter-image ~/Pictures/presenter.png \
     --topic "Context engineering in one minute" \
     --duration 60 \
     --aspect 9:16 \
     --rights-confirmed \
     --adult-presenter-confirmed
   ```
4. Complete the manual review and upload approvals in `job.json`, then run preflight:
   ```bash
   python3 "$SKILL_DIR/scripts/preflight.py" ~/Videos/my-presenter-video/job.json
   ```
5. After each stage, record artifacts in `job.json` and let the checker compute the state:
   ```bash
   python3 "$SKILL_DIR/scripts/check_state.py" ~/Videos/my-presenter-video/job.json --write
   ```

The README says nothing is delivered until the output passes decode and loudness checks. Use only a portrait you are authorized to use.
