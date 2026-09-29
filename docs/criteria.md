# Selection criteria

## Upstream's inclusion rules
Every repository in this list comes from [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) (CC0 1.0), which reports that it applies four rules. As upstream describes them (paraphrased):

1. **It makes or edits video or motion graphics.** A 3D web page or a prompt collection does not count. A few entries under Scriptwriting & Film Study come before the video (screenwriting, shot analysis) and are listed by the maintainer's choice.
2. **An agent operates it:** a skill, plugin, MCP server, or toolkit written for the agent.
3. **It has a README.** Without one it cannot be graded.
4. **Repositories with 50 stars or more** are listed on topic alone. Under 50 stars, a repository must also clear a README quality bar: it shows the result, starts with one command, states a concrete outcome and has complete docs, and it needs at least 5 stars.

Upstream says these are closed questions answered one repository at a time by a decision model (TypeSafe Jev) reading each README. The same run produced the security grade and the categories. We did not repeat that run. Ratings and categories in this list are **upstream's** and are labeled so.

## What we added
- **Coverage rule:** every upstream entry stays. A renamed or dead repository is flagged in its notes, never silently dropped. Currently two repositories have been renamed on GitHub.
- **Live facts:** stars, license, language and last push are fetched from the GitHub API and dated.
- **Our own review flags:** a separate check asks whether each README's project makes video and is agent-oriented. On our audit, 19 rows were flagged; we reviewed them by hand and removed none. See [methodology](methodology.md). The flags do not change upstream's inclusion.
- **Showcase label:** three entries are the source code of a finished video rather than a reusable tool; they stay listed and are marked `(showcase)`.

## What we do not do
We do not install or run any listed repository, so nothing here certifies that a tool works. See [safety](safety.md).
