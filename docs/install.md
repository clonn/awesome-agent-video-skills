# Installing skills, plugins and MCP servers

Tools in this list arrive in a few standard forms. This page explains each one, with the official documentation it is based on (checked 2026-09-29). The exact command for a given tool is on its card and comes from its README; we have not executed any of them. Read [safety](safety.md) first.

## 1. Claude Code skills (personal or project)
A skill is a folder with a `SKILL.md` file.
- **Personal** (all your projects): `~/.claude/skills/<name>/SKILL.md`.
- **Project** (shared through the repository): `.claude/skills/<name>/SKILL.md`.
- Skills load automatically when relevant, or you can invoke one with `/skill-name`. No restart is required.

Source: [Claude Code skills](https://code.claude.com/docs/en/skills.md). Many cards show `git clone <repo> ~/.claude/skills/<name>`, which is simply this personal location.

## 2. Claude Code plugin marketplaces
A repository can publish a marketplace of plugins. In a session:
```text
/plugin marketplace add <owner/repo>
/plugin install <plugin>@<marketplace>
```
The same works from a shell as `claude plugin marketplace add <source>` and `claude plugin install <name>@<marketplace> [--scope user|project|local]`. Scopes: user (`~/.claude/settings.json`), project (`.claude/settings.json`, committed) and local (`.claude/settings.local.json`, not committed).

Source: [Install plugins](https://code.claude.com/docs/en/plugins/install.md). The docs advise reviewing a plugin's components (commands, agents, skills, hooks, MCP servers) before installing.

## 3. MCP servers with `claude mcp add`
```text
claude mcp add [--scope user|project|local] --transport stdio <name> -- <command> [args...]
claude mcp add [--scope user|project|local] --transport http <name> <url>
```
Scope `local` (the default) and `user` are stored in `~/.claude.json`; `project` writes a committed `.mcp.json`. Source: [Claude Code MCP](https://code.claude.com/docs/en/mcp.md). Anthropic does not audit third-party MCP servers ([security](https://code.claude.com/docs/en/security.md)).

## 4. Codex skills
Codex reads skills from `.agents/skills` in your repository (and parent directories), `$HOME/.agents/skills` for your personal skills, and `/etc/codex/skills` for machine-wide skills. Invoke a skill with `$skill-name` or `/skills`; `$skill-installer <name>` installs curated skills. Codex detects skill changes automatically; restart it if an update does not appear. Source: [Codex skills](https://learn.chatgpt.com/docs/build-skills) (the older address developers.openai.com/codex/skills redirects there).

## 5. The `npx skills add` CLI
`npx skills add <owner/repo>` is a cross-agent installer from Vercel Labs ([repo](https://github.com/vercel-labs/skills), MIT, [skills.sh](https://www.skills.sh/)). Useful options from its README:

| Option | Meaning |
|---|---|
| `-g, --global` | install to your user directory instead of the project |
| `-a, --agent <agents...>` | target specific agents, for example `claude-code` or `codex` |
| `-s, --skill <skills...>` | install only the named skills from a multi-skill repo |
| `-l, --list` | list the skills in a repo without installing |
| `--copy` | copy files instead of symlinking |
| `-y, --yes` | skip confirmation prompts |

By default it installs into the project (`./<agent>/skills/`); with `-g` it installs into your home directory. Prefer `--list` first, and avoid `-y` until you have read what will be installed.

## 6. "Tell your agent" prompts
Some READMEs give a prompt instead of a command, such as "Install this skill for me: <url>". The agent then clones the repository and follows its instructions, so the safety advice for scripts applies to the prompt too. Cards label these **Tell your agent**. Prompts that are written in Chinese show an English summary and a link to the README.

## 7. Other forms you will meet
`git clone` plus a manual copy, `pip install` or `pipx install` for tools with their own runtime, and Codex plugin marketplaces (used by some READMEs, for example codex-storyboard). We have not verified the Codex plugin commands against official documentation, so follow the README for those.
