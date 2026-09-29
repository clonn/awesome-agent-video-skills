# Contributing

The single source of truth is `data/repos.json`. Rendered files are generated; do not edit them by hand.

## Add a repo
1. Add an entry to `data/repos.json` following the schema in `spec.md`.
2. Run `python3 scripts/build.py`.
3. Commit the data change and the regenerated files together.

## Checks
- Syntax: `python3 -m py_compile scripts/*.py`
- Links (stdlib script, no installs): `python3 scripts/check_links.py` (add `--local-only` to skip network)
- Idempotency: run `python3 scripts/build.py` twice; `git diff` must be empty after the second run.
