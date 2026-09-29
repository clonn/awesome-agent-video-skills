# Contributing

The single source of truth is `data/repos.json`. Everything else is generated (or handwritten under `docs/`, `tour/`, `examples/`).

## Add or fix a repository
1. Add the repository to `data/candidates.json` (or edit the row), then refresh live facts: `python3 scripts/enrich.py` (uses the `gh` CLI, read-only).
2. Re-extract snippets: `python3 scripts/extract_snippets.py`. Snippets must stay **verbatim** from the README with a source link, or be null (rendered as "See README"). Never write an install command by hand. Fix a wrong extraction with an entry in `data/overrides.json`.
3. Write `description_en` in your own words (25 words or fewer) in `data/descriptions_en.json`.
4. Regenerate: `python3 scripts/make_repos.py && python3 scripts/validate.py && python3 scripts/build.py`.
5. Commit the data and the regenerated files together.

## Rules
- Rendered files are English only. Chinese, Japanese or Korean text is allowed only inside code fences with an English gloss, or as a glossed proper noun such as CapCut/Jianying (剪映). `scripts/build.py` fails otherwise.
- Label who made each judgment: upstream's grades and categories are upstream's; ours are documented in `docs/methodology.md`.
- We never install or run listed repositories. Examples are README-derived and marked "not executed by us".
- Publishing requires the maintainer's approval.

## Checks
- Syntax: `python3 -m py_compile scripts/*.py experiments/typesafe/*.py`
- Schema and counts: `python3 scripts/validate.py`
- Idempotency: run `python3 scripts/build.py` twice; `git diff` must be empty the second time.
- Links (stdlib, no installs): `python3 scripts/check_links.py` (add `--local-only` to skip the network).
- Full QA run: `python3 scripts/qa.py`.
- Judgments (optional; needs `TYPESAFE_API_KEY`): `python3 scripts/judge.py`. The build never calls the API.
