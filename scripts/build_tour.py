#!/usr/bin/env python3
"""Render tour/*.md (7 goal pages + start page). Picks and reasons are handwritten below; links are checked against data/repos.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

repos = {r["id"]: r for r in json.loads((ROOT / "data/repos.json").read_text())}
CATSLUG = {c[0]: c[2] for c in build.CATS}

GOALS = [
    ("edit-talking-head", "Edit a talking-head video",
     "You have footage of someone speaking and want it tightened, captioned or dressed up.",
     [("YeJe-cpu/SeeCut", "Turns a 20-30 second talking-head clip into a motion-graphics short and checks its own result; note the non-commercial license."),
      ("louisedesadeleer/cut-video", "Removes silences and filler from long recordings using forced-alignment word timing while keeping laughs and comedic pauses."),
      ("Agentchengfeng/chengfeng-videocut-skills", "A Codex plugin that adds workflow skills for cutting speech, subtitles, visuals and export, backed by a separate runtime.")],
     ["SeeCut is non-commercial only and a 25-second sample takes about an hour (README).", "cut-video needs ffmpeg and a forced aligner that its README says it installs on first run."]),
    ("make-explainer", "Make an explainer video",
     "You have a topic or notes and want a narrated video that teaches it.",
     [("Vincentwei1021/video-talkcraft", "Builds voiceover-driven explainers with word-level sync, motion recipe cards and a camera system; its license is non-commercial."),
      ("Alisa0808/vox-director", "Takes a topic and produces a paper-collage explainer, covering script, keyframes, motion, voice-over, music and captions."),
      ("aijiduonadegou/Paper-Cut", "A Codex skill for paper-cut style explainers with approval gates and quality checks along the way.")],
     ["Explainer tools usually call hosted image or speech models; read each README for accounts and cost.", "For math-style animation see the Manim tools in the [Explainers catalog](../catalog/explainers-and-education.md)."]),
    ("product-promo", "Make a product promo or demo",
     "You want a launch film, ad or feature demo for a product.",
     [("Vincentwei1021/video-shotcraft", "Shot recipe cards plus a Remotion template for cinematic product films; the license is Apache-2.0."),
      ("op7418/guizang-product-video-skill", "Builds software-update promo videos in code from real product components, with original music and sound effects."),
      ("gorkem-bwl/onboarding-video-generator", "Produces short, silent, looping feature videos in Remotion sized for a two-column web page (README default: 1280x960, about 10-15 seconds).")],
     ["Remotion has company-size license terms; see [choosing a stack](../docs/choosing-a-stack.md)."]),
    ("motion-logo", "Animate a logo or make motion graphics",
     "You want an animated logo, titles, kinetic type or UI motion.",
     [("nolangz/pixel2motion", "Converts raster logos to SVG, then produces animated logo HTML demos, previews and motion checks."),
      ("diffusionstudio/lottie", "Generates Lottie animations from prompts and previews them live in a bundled player."),
      ("acelera-agency/html-animation", "Builds animated logos and kinetic type as a single HTML file and exports MP4 in several aspect ratios (README); needs ffmpeg.")],
     ["Lottie output is a vector animation file rather than a finished video; check that your destination supports it."]),
    ("ai-avatar", "Make an AI presenter video",
     "You want a digital human to present a script.",
     [("cclank/lanshu-create-ai-presenter-video", "A provider-neutral skill that goes from a script and one authorized portrait to a checked presenter video."),
      ("heygen-com/skills", "Agent skills for creating avatar videos through HeyGen's API."),
      ("Upload-Post/avatar-mix", "Uses your HeyGen avatar with animated HyperFrames backgrounds, music, sound effects and captions from a URL or script; the README asks for HeyGen avatar and voice IDs.")],
     ["Avatar services are paid third-party products; costs and consent for the portrait are yours to check.", "Use only images you are authorized to use."]),
    ("story-animation", "Make a story or animation",
     "You want an animated tale, short drama or cinematic scene.",
     [("gnipbao/story-to-handdrawn-video", "Turns Chinese stories or ordered images into 3:4 portrait hand-drawn animations rendered with Remotion; the README is mostly Chinese."),
      ("lemomo-ai/lemo-opuscar", "A library of film-style prompts, each backed by a short film made entirely in code, for an agent to direct your story."),
      ("Mr-funny/hbg-life-simulation", "Turns long Chinese life-story scripts into narrated comic-style videos with a consistent character (README, in Chinese).")],
     ["Two of these three READMEs are written in Chinese; the cards summarize what matters."]),
    ("music-video", "Make a music video",
     "You want a video for a song, made in code.",
     [("JohnHeibel/PDoomVideo", "Complete source of a p5.js music video generated by Claude; a showcase to study, with no license file."),
      ("ledbetterljoshua/functional-emotions-video", "Source of a painted music video made in Claude Code with a custom brush renderer; a showcase to study."),
      ("heygen-com/hyperframes", "Our suggestion, not a music-video tool: this category has only two entries, so a general base that renders HTML animation to MP4 is the way to start your own.")],
     ["Both music entries are showcases (finished projects), not reusable tools."]),
]


def link(rid):
    r = repos[rid]
    if r["featured"]:
        return f"[{rid}](../skills/{build.slug(r)}.md)"
    return f"[{rid}]({r['url']}) ([catalog](../catalog/{CATSLUG[r['category_source']]}.md))"


def main():
    out = {}
    idx = ["# Tour: pick by goal", "", "Seven goals, three picks each, with a one-sentence reason grounded in the tool's card or README. "
           "Nothing here was run by us; see [safety](../docs/safety.md) before installing.", ""]
    for slug_, title, intro, picks, before in GOALS:
        for rid, _ in picks:
            assert rid in repos, rid
        idx.append(f"- [{title}]({slug_}.md)")
        L = [f"# {title}", "", intro, "", "## Three picks", ""]
        for n, (rid, why) in enumerate(picks, 1):
            r = repos[rid]
            L += [f"{n}. **{link(rid)}** ({r['type']}, {build.stars(r['stars'])} stars, {build.lic_short(r)}): {why}"]
        L += ["", "## Before you start", ""] + [f"- {b}" for b in before]
        L += ["- Install methods: [install guide](../docs/install.md). Choosing a base: [choosing a stack](../docs/choosing-a-stack.md).", "",
              "[All goals](README.md) · [Back to the list](../README.md)", ""]
        out[f"tour/{slug_}.md"] = "\n".join(L)
    idx += ["", "[Back to the list](../README.md)", ""]
    out["tour/README.md"] = "\n".join(idx)
    for path, text in out.items():
        (ROOT / path).write_text(text)
    print(len(out), "tour pages")


if __name__ == "__main__":
    main()
