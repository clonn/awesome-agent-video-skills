# Methodology: which judgments are ours, and how they were made

This list is based on [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) (CC0 1.0), which itself draws on an article by Jason AI Chuhai and the live page at https://agentskillshub.top/best/claude-video-skills/. Everything below says who made each call.

## What stays upstream's
- The list of repositories, the ten categories (`category_source`) and the security grades (`safety_upstream`: SAFE or CAUTION). Upstream reports that its classification and safety grading were done by TypeSafe Jev reading each README; the grade covers the README and install steps only. We label these as upstream's and never change them automatically.

## What we fetched
- Stars, license, language, last push and archived flag come from the GitHub API, each with a `checked_at` timestamp. Where GitHub reports no license, we read the repository's LICENSE file (`license_detail`, `noncommercial`).

## What we copied
- Install and usage snippets are copied verbatim from each README with a source link, or left empty ("See README"). Descriptions are written in our own words (25 words or fewer).

## Our own judgments (TypeSafe Jev)
Run offline by `scripts/judge.py` (the only script that needs `TYPESAFE_API_KEY`) and cached in `data/judgments.json` with model (`jev-1.13.0`), date and question version. The site build reads only the cache and never calls the API. Jev is TypeSafe's System One model: each call asks closed questions about a README and returns probabilities and a confidence ([docs](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md), [Noul](https://docs.typesafe.ai/primitives/noul.md), [Choice](https://docs.typesafe.ai/primitives/choice.md)). Cost of the full 184-repo experiment run: about $0.085 for 919 calls at $0.042 per million input tokens.

| Judgment | Primitive | Rule | Effect |
|---|---|---|---|
| Render base (Remotion, HyperFrames, Manim, ffmpeg, ...) | One Noul per base | A base is listed only if its name appears in the README **and** Noul (does the project actually use it, not just mention it) is at least 0.3. Vetoed mentions are logged per row. | Applied to the data |
| Category | Choice over the ten categories plus "out of scope" | Suggestion only; disagreements above 0.9 confidence are reviewed by hand | Review queue only |
| Install pick | Choice among command candidates extracted by code | Suggestion only; the extractor plus manual overrides decide what is shown | Review queue only |
| Inclusion flags (makes video? built for agents?) | Two Noul | Below 0.5 goes to the review queue | Review queue only |

Hand decisions from the queue are recorded in `data/review_decisions.json` and applied by the build.

## Evidence and known limits
Numbers are in `experiments/typesafe/REPORT.md`.
- **Gold sets are small and labeled by us.** 30 rows labeled by the executor session from README evidence, plus a 20-row holdout labeled blind by a separate reviewer that saw no model output. Differences of a row or two are noise.
- **Thresholds were fixed before the holdout** (`holdout_prereg.json`). Result: render-base hybrid F1 1.00 on the holdout (regex alone 0.75), so it is applied. The install hybrid scored 75% against 80% for the extractor, so it is **not** applied. Category confidence above 0.9 was right on 8 of 8 holdout rows, but overall accuracy (65%) is no better than upstream's labels (70%), so categories stay upstream's.
- **The holdout has no AI-avatar or music-video rows**, so those two categories are untested.
- **Text only:** the model reads README text, not images or videos, so it cannot judge whether a README shows finished output.
- **Categories overlap.** Seven of 30 gold labels differ from upstream's, which is as likely to be labeler disagreement as upstream error.
- Judgments are a snapshot; re-run `scripts/judge.py` after the data changes.

## Reproduce
`python3 scripts/make_repos.py` and `python3 scripts/validate.py` need no key. `python3 scripts/judge.py` refreshes the cache and needs `TYPESAFE_API_KEY`.
