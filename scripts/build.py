#!/usr/bin/env python3
"""Render README.md, catalog/*.md and skills/*.md from data/repos.json (stdlib only, offline, deterministic).
Run twice -> no diff. Rendered files are English only (CJK allowed only inside code blocks, glosses, and glossed proper nouns)."""
import json
import re
import sys
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[㐀-鿿가-힯぀-ヿ]")
CATS = [  # (source id, English name, slug, best-for)
    ("general", "Frameworks & Toolkits", "frameworks-and-toolkits", "a general-purpose toolkit or framework for agent-made video"),
    ("promo", "Product Promos & Demos", "product-promos-and-demos", "product launch films, ads and feature demos"),
    ("explainer", "Explainers & Education", "explainers-and-education", "knowledge videos, tutorials and narrated lessons"),
    ("editing", "Editing & Post-production", "editing-and-post-production", "cutting, captions, B-roll and finishing footage you already have"),
    ("shorts", "Short-form & Talking-head", "short-form-and-talking-head", "vertical short-form and talking-head videos for social platforms"),
    ("avatar", "AI Avatars", "ai-avatars", "videos presented by a digital human or AI avatar"),
    ("story", "Story & Animation", "story-and-animation", "animated stories, short dramas and cinematic scenes"),
    ("motion", "Motion Graphics & Logos", "motion-graphics-and-logos", "animated logos, titles, kinetic type and UI motion"),
    ("craft", "Scriptwriting & Film Study", "scriptwriting-and-film-study", "planning before you shoot: scripts, shot analysis and learning from existing videos"),
    ("music", "Music Videos", "music-videos", "music videos generated in code"),
]
CAT = {c[0]: c for c in CATS}
NO_LICENSE = "No license file. Default copyright applies; ask the author before reuse."
LONG_PROMPT = 600


def q(u):
    """Percent-encode non-ASCII characters (e.g. CJK heading anchors) so rendered pages stay ASCII in URLs."""
    return quote(u, safe=":/?#[]@!$&'()*+,;=%-._~")


def stars(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def slug(r):
    return r["id"].replace("/", "__")


def lic(r):
    """(short label, longer sentence or None)"""
    if r["license"] and r["license"] not in ("Other",):
        s = r["license"]
        return (s if not r["noncommercial"] else s + " (non-commercial)"), None
    d = r.get("license_detail") or ""
    if d == "No license file found":
        return "No license file", NO_LICENSE
    if d.startswith("Custom license"):
        return "Custom license", "Custom license terms; read the LICENSE file in the repository before reuse."
    return d or "Unknown", None


def lic_short(r):
    label, _ = lic(r)
    if label == "No license file":
        return "\u2014"
    return label.replace(" (non-commercial)", "") + (" NC" if r["noncommercial"] else "")


def lic_note(r):
    label, sentence = lic(r)
    if r["noncommercial"]:
        name = r.get("license_detail") or label
        extra = " The license is mixed; see the LICENSE file for which parts are covered." if r["id"] == "PoetCoderJun/MotionTalk" else ""
        return f"**Non-commercial license ({name}).** Personal and non-commercial use only; commercial use needs the author's permission.{extra}"
    return sentence


def trunc(s, n=LONG_PROMPT):
    return s if len(s) <= n else s[:n].rstrip() + "\n... (prompt continues; see the README)"


def install_md(r, short=False):
    ins = r["install"]
    if not ins:
        return f"See [README]({r['url']}#readme)."
    src = f"[README]({q(ins['source_url'])})"
    if ins["kind"] == "agent_prompt" and ins["cjk"]:
        return f"Prompt (translated from the README): {ins['gloss']} Source: {src}."
    if ins["kind"] == "agent_prompt":
        body = "Tell your agent:\n\n```text\n" + trunc(ins["display_command"]) + "\n```"
    else:
        body = "Run:\n\n```bash\n" + ins["display_command"] + "\n```"
    if short:
        return body
    extra = []
    if ins["comments_omitted"]:
        extra.append("(comment lines omitted)")
    if ins["cjk"] and ins.get("gloss"):
        extra.append("> Gloss: " + ins["gloss"])
    if ins.get("note"):
        extra.append(ins["note"])
    if ins.get("purpose"):
        extra.append(ins["purpose"])
    return body + "\n\n" + " ".join(x for x in extra if not x.startswith("> ")) + ("\n" if any(not x.startswith("> ") for x in extra) else "") \
        + ("\n".join(x for x in extra if x.startswith("> ")) + "\n" if any(x.startswith("> ") for x in extra) else "") + f"\nSource: {src}."


def usage_md(r):
    u = r["usage"]
    if not u:
        return f"See [README]({r['url']}#readme)."
    if u["cjk"]:
        if u.get("gloss"):
            return f"```text\n{u['snippet']}\n```\n\n> Gloss: {u['gloss']}\n\nSource: [README]({q(u['source_url'])})."
        return f"See [README]({q(u['source_url'])})."
    return f"```text\n{trunc(u['snippet'])}\n```\n\nSource: [README]({q(u['source_url'])})."


def stack_line(r):
    if r["stack_note"]:
        return "other: " + r["stack_note"]
    bases = [x for x in r["render_base"] if x != "ffmpeg"]
    also = "ffmpeg" in r["render_base"]
    if not bases:
        return "No rendering framework named" + ("; also uses ffmpeg" if also else " in the README")
    jr = r["judgments"].get("render_base")
    tail = " (our judgment: named in the README and confirmed as actually used; see [methodology](../docs/methodology.md))" \
        if jr and not jr["overridden_by_hand"] else " (hand-verified against the README)"
    return ", ".join(bases) + tail + ("\n- **Also uses:** ffmpeg" if also else "")


def card(r):
    c = CAT[r["category_source"]]
    label, _ = lic(r)
    L = [f"# {r['name']}", "",
         f"[{r['id']}]({r['url']}) · {r['type']} · {stars(r['stars'])} stars (checked {r['stars_checked_at'][:10]}) · License: {label}", "",
         r["description_en"], ""]
    if r["entry_kind"] == "showcase":
        L += ["> **Showcase.** This is the source project behind a finished video, not a reusable tool.", ""]
    if r["notes"]:
        L += [f"> Note: {r['notes']}", ""]
    n = lic_note(r)
    if n:
        L += [f"> {n}", ""]
    L += ["## At a glance", "",
          f"- **Category:** {c[1]} (upstream's label)",
          (f"- **Best for:** {r['best_for']}" if r["best_for"] else f"- **Best for (by category):** {c[3]}"),
          "- **Stack:** " + stack_line(r),
          f"- **Language:** {r['language'] or 'Not reported'}",
          f"- **Last push:** {r['pushed_at'][:10]}" + (" (archived)" if r["archived"] else ""), "",
          "## Install", "", "_Not executed by us; copied from the README._", "", install_md(r), ""]
    if r["safety_notes"]:
        L += ["**Our safety notes:**", ""] + [f"- {s}" for s in r["safety_notes"]] + [""]
    L += ["## Usage", "", usage_md(r), "",
          "## License", "", (lic_note(r) or f"{label}. See the repository's license file."), "",
          "## Safety", "",
          f"- **Upstream's rating:** {(r['safety_upstream'] or 'not rated').upper()}. Upstream's grade covers the README and install steps only; we did not review the code.",
          f"- **Our notes:** {'; '.join(r['safety_notes']) if r['safety_notes'] else 'none'}", "",
          "## Links", "", f"- Repository: {r['url']}", f"- Catalog: [{c[1]}](../catalog/{c[2]}.md)", ""]
    text = "\n".join(L)
    if r["id"] == "YeJe-cpu/SeeCut":
        text = text.replace("## Safety", SEECUT_EXTRA + "## Safety", 1)
    return text


SEECUT_EXTRA = """## Limits (from the README and the author's post)

- A 25-second sample currently takes about 1 hour to produce (README); longer videos take longer.
- Tested on macOS only (README).
- It needs the Antigravity CLI (`agy`) so the AI can watch the video, and a coding agent with enough quota for multi-round self-review (README).
- The author's announcement post (Leaf Yeah!, @leaf_sanren on X) adds that sound effects are only "usable" and that screen-recording plus corner-avatar footage is under-tested.
- Optional last step: export a layered CapCut/Jianying (剪映) draft.

"""


def row(r, cards):
    name = f"[{r['id']}]({r['url']})"
    if r["id"] in cards:
        name += f" ([card](skills/{slug(r)}.md))"
    bases = [x for x in r["render_base"] if x != "ffmpeg"]
    typ = r["type"] + (" (showcase)" if r["entry_kind"] == "showcase" else "")
    return f"| {name} | {stars(r['stars'])} | {typ} | {', '.join(bases) or '-'} | {lic_short(r)} | {r['description_en']} |"


HEAD = "| Repo | Stars | Type | Built with | License | What it does |\n|---|---:|---|---|---|---|"


def main():
    repos = json.loads((ROOT / "data/repos.json").read_text())
    by_cat = {c[0]: sorted([r for r in repos if r["category_source"] == c[0]], key=lambda r: (-r["stars"], r["id"].lower())) for c in CATS}
    featured = sorted([r for r in repos if r["featured"]], key=lambda r: (-r["stars"], r["id"].lower()))
    cards = {r["id"] for r in featured}
    checked = max(r["stars_checked_at"] for r in repos)[:10]
    docs = [(t, p) for t, p in (("Methodology: which judgments are ours", "docs/methodology.md"), ("Installing skills, plugins and MCP servers", "docs/install.md"),
                                ("How to use these tools", "docs/how-to-use.md"), ("Choosing a stack", "docs/choosing-a-stack.md"),
                                ("Selection criteria", "docs/criteria.md"), ("Safety", "docs/safety.md"), ("Guided tour by goal", "tour/README.md"),
                                ("Worked examples", "examples/README.md")) if (ROOT / p).exists()]
    out = {}
    start = [(t, p) for t, p in (("Tour", "tour/README.md"), ("Install", "docs/install.md"), ("Choosing a stack", "docs/choosing-a-stack.md")) if (ROOT / p).exists()]
    credits = ["## Credits", "",
               "- This list is based on [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) (CC0 1.0) and the live page [Agent Skills Hub](https://agentskillshub.top/best/claude-video-skills/). "
               "Categories and security grades are **upstream's**, produced by upstream's own method; we label them as such.",
               "- Source article (Chinese; title translated): \"107 hidden gems under 50 stars: 180 open-source skills that let Claude make video, fully categorized\" by Jason AI Chuhai.",
               "- SeeCut is featured thanks to the author's announcement post (Chinese) by Leaf Yeah! (@leaf_sanren on X).",
               "- What we add: per-tool cards, install and usage text copied from each README (with links), live facts, licenses, and clearly labeled judgments of our own. "
               "See [methodology](docs/methodology.md)."]
    L = ["# awesome-agent-video-skills", "",
         "A curated, English-first list of open-source skills, plugins, MCP servers and toolkits that let coding agents (Claude Code, Codex and others) make, edit or animate video.", "",
         "Based on [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) (CC0) \u2014 see [Credits](#credits).", ""]
    if start:
        L += ["**Start here:** " + " \u00b7 ".join(f"[{t}]({p})" for t, p in start), ""]
    L += [f"**{len(repos)} repositories** in {len(CATS)} categories. Stars, licenses and push dates come from the GitHub API and were checked on {checked}.", "",
          "**How to read this list.** Install and usage text is copied from each repository's README and was **not executed by us**. If a README has none, we say \"See README\". "
          "Upstream's SAFE/CAUTION grade covers the README and install steps only. Always read a tool's license and install steps before running it. "
          "In the tables, `NC` after a license means non-commercial only, and `\u2014` means the repository has no license file (default copyright applies). "
          "The \"Built with\" column lists rendering frameworks and services; ffmpeg is omitted because so many tools use it as a helper (cards show it under \"Also uses\").", ""]
    if docs:
        L += ["## Guides", ""] + [f"- [{t}]({p})" for t, p in docs] + [""]
    L += ["## Quick picks", "", "Featured tools, each with a card (what it is, install, usage, license, safety).", "", HEAD]
    L += [row(r, cards) for r in featured] + [""]
    L += ["## Categories", "", "| Category | Repos | Page |", "|---|---:|---|"]
    for sid, name, sl, _ in CATS:
        L.append(f"| {name} | {len(by_cat[sid])} | [catalog/{sl}.md](catalog/{sl}.md) |")
    L += ["", f"## All {len(repos)} repositories", "", HEAD]
    L += [row(r, cards) for r in sorted(repos, key=lambda r: (-r["stars"], r["id"].lower()))] + [""]
    L += credits + [""]
    L += ["## License of this repository", "", "Documentation is CC-BY-4.0 and scripts are MIT. Each listed project keeps its own license; check it before reuse.", ""]
    out["README.md"] = "\n".join(L)
    for sid, name, sl, best in CATS:
        rows = by_cat[sid]
        C = [f"# {name}", "", f"{len(rows)} repositories. Best for {best}. Category is upstream's label. [Back to the list](../README.md).", "", HEAD.replace("(", "(")]
        C += [row(r, cards).replace("(skills/", "(../skills/") for r in rows] + [""]
        out[f"catalog/{sl}.md"] = "\n".join(C)
    for r in featured:
        out[f"skills/{slug(r)}.md"] = card(r)
    # guard: no CJK outside code fences / gloss lines / glossed proper nouns
    bad = []
    for path, text in out.items():
        fence = False
        for n, ln in enumerate(text.split("\n"), 1):
            if ln.lstrip().startswith("```"):
                fence = not fence
                continue
            if not fence and CJK.search(ln) and not ln.startswith("> Gloss:") and "剪映" not in ln:
                bad.append((path, n, ln[:80]))
    if bad:
        print("CJK outside allowed places:", bad[:10])
        return 1
    for path, text in out.items():
        p = ROOT / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.rstrip("\n") + "\n")
    # remove stale generated cards
    keep = {f"skills/{slug(r)}.md" for r in featured}
    for f in (ROOT / "skills").glob("*.md"):
        if f"skills/{f.name}" not in keep:
            f.unlink()
    print(f"README: {len(repos)} repos; catalog pages: {len(CATS)}; cards: {len(featured)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
