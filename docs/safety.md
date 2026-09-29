# Safety

Installing a skill, plugin or MCP server gives software the ability to influence what your coding agent does on your machine. Nothing in this list was installed or run by us. This page says what the labels mean and how to reduce risk.

## Upstream's rating
Upstream grades each repository SAFE or CAUTION. Its grade reads the README and install steps only, not the code, and was produced by upstream's decision model (see [criteria](criteria.md)). In this list 181 rows are SAFE, 2 are CAUTION (video-recap-skills-plus and remotion-video-skill) and 1 was added after upstream's snapshot and is unrated. These are **upstream's** labels. A SAFE grade is not a security review.

## Our notes
When a card's install step has a pattern that deserves a warning, we add it as a separate **Our safety notes** line. They are ours, not upstream's:
- **Remote script piped into a shell** (`curl ... | bash`): the command downloads and runs whatever the URL serves at that moment. Cards for Monet, hyperdirector and remotion-motion-graphics-skill carry this note. Download the script, read it, then run it, or pick a different install method.
- **Hosted MCP servers:** connecting with `claude mcp add --transport http <name> <url>` sends your requests, and possibly project content, to a third party. The card for mcp-flow-google carries this note. Anthropic states it does not audit third-party MCP servers ([Claude Code security](https://code.claude.com/docs/en/security.md)).
- **Agent prompts:** "Tell your agent" installs let an agent follow instructions it fetches. Read the repository's `SKILL.md` first.

## Licenses and reuse
- **Non-commercial (`NC`):** 7 rows have a non-commercial license (for example SeeCut, PolyForm Noncommercial). Personal use is fine; commercial use needs the author's permission. MotionTalk's license is mixed, so read its LICENSE file.
- **No license file (`—`):** 27 rows. Default copyright applies; ask the author before reuse.
- **Everything else:** the license shown is what GitHub reports. Each project keeps its own license.
- Remotion has company-size license terms; see [choosing a stack](choosing-a-stack.md).

## A short checklist
1. Read the card, then the README, then the script or `SKILL.md` you are about to trust.
2. Prefer a throwaway project or environment for your first run.
3. Do not paste API keys into prompts; several READMEs tell the agent explicitly not to read or upload local keys, which is a good sign but not a guarantee.
4. Check where your files go: hosted services (avatars, text-to-speech, image and video models) receive what you send them.
5. Claude Code asks you to review commands and trust new MCP servers before use ([security docs](https://code.claude.com/docs/en/security.md), [plugin install](https://code.claude.com/docs/en/plugins/install.md)); do not approve blindly.
