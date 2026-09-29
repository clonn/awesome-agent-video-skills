# cut-video: remove silences and filler from a long recording

> **Not executed by us.** Commands are copied from the [cut-video README](https://github.com/louisedesadeleer/cut-video/blob/main/README.md). Card: [cut-video](../skills/louisedesadeleer__cut-video.md).

## Prerequisites and costs

| Item | From the README |
|---|---|
| License | MIT (as reported by GitHub; see the card) |
| Platform | macOS (uses VideoToolbox hardware decode; the README says it works on Linux and Windows if you remove the `-hwaccel videotoolbox` flags) |
| Agent | Claude Code |
| Software | `ffmpeg` with `libx264`, `whisper` (`pip install openai-whisper`, transcript text only) |
| Installed on first run | Montreal Forced Aligner: the skill creates a `mfa` conda env and downloads the English model, installing miniforge through Homebrew if conda is missing |
| Cost | Runs entirely on your machine; the README says no cloud APIs |

## Steps
1. Install, then restart Claude Code so `/cut-video` is available:
   ```bash
   git clone https://github.com/louisedesadeleer/cut-video.git ~/.claude/skills/cut-video
   ```
2. In Claude Code, run the slash command and paste a video path when asked:
   ```text
   /cut-video
   ```
3. The README says the skill then: makes a 1080p H.264 proxy; transcribes with Whisper; force-aligns with the aligner; prints a proposed cut list with timestamps and total compression; re-checks every keep boundary; waits for your "go"; renders and verifies the result.
4. Pick a tone preset when asked: `aggressive` (default, about 40-60% runtime reduction), `balanced`, `sentimental` or `documentary`.

## What it does not do
Per the README it does not add zooms, layouts, B-roll, captions or motion graphics; pair it with another tool for those.
