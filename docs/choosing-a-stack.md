# Choosing a stack

Most tools in this list do not render video themselves. They give a coding agent instructions (a "skill") and lean on a rendering base. Picking the base first narrows the list quickly. Counts below come from the "Built with" column, which is our judgment (a base counts only if the README names it and it is actually used; see [methodology](methodology.md)), as of the check date on the [README](../README.md). ffmpeg is the most common dependency (it appears in about 106 rows, often as a helper for cutting or encoding), so it is not a reason to choose a tool.

| Base | What it is | Rows | Good fit | Watch out for |
|---|---|---:|---|---|
| **Remotion** | React framework that renders video from code ([remotion.dev](https://www.remotion.dev/)) | 59 | Product promos, kinetic text, data-driven scenes; large ecosystem of skills such as [video-shotcraft](../skills/Vincentwei1021__video-shotcraft.md) | Its [license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) is free for individuals, non-profits and organizations of up to 3 employees; larger companies need a paid license (checked 2026-09-29). |
| **HyperFrames** | Framework that turns HTML, CSS and seekable animation (GSAP and similar) into deterministic MP4 through a CLI ([repo](https://github.com/heygen-com/hyperframes), Apache-2.0, needs Node.js 22+ and FFmpeg per its README) | 42 | Anything you can lay out as a web page; talking-head overlays such as [SeeCut](../skills/YeJe-cpu__SeeCut.md) | Fewer ready-made skills than Remotion, but it is the base of many recent talking-head tools. |
| **Manim** | Python library for mathematical animation ([Manim Community](https://docs.manim.community/en/stable/), MIT) | 5 | Math and CS explainers in the 3Blue1Brown style | Narrow scope; see [notes-to-video](../catalog/explainers-and-education.md) for a notes-to-explainer pipeline. |
| **Lottie / p5.js / Blender** | Vector animation format, creative-coding library, 3D suite | 3 / 4 / 3 | Logo and UI motion ([lottie](../skills/diffusionstudio__lottie.md)); painterly code art ([PDoomVideo](../skills/JohnHeibel__PDoomVideo.md)); 3D educational films | Small choices; each is a specialist tool. |
| **HeyGen** | Hosted avatar-video service | 9 | AI presenters ([heygen-com/skills](../skills/heygen-com__skills.md), [lanshu](../skills/cclank__lanshu-create-ai-presenter-video.md) is provider-neutral) | Paid API; check each README for cost. SeeCut's README gives per-second prices for its avatar step. |
| **Desktop editors (Premiere Pro, After Effects)** | Agent controls the Adobe app through an MCP server | 1 + 1 rows judged, plus 4 MCP entries in the [Frameworks catalog](../catalog/frameworks-and-toolkits.md) and [Editing catalog](../catalog/editing-and-post-production.md) | You already work in the app and want the agent to drive it | The READMEs of the Premiere MCP servers say Premiere Pro (2020 or newer) must be installed and a local bridge set up; they run on your machine's app, not headless. |

## A quick way to decide
1. **Do you have footage?** Start in [Editing](../catalog/editing-and-post-production.md) or [Short-form and talking-head](../catalog/short-form-and-talking-head.md). No footage: [Explainers](../catalog/explainers-and-education.md), [Promos](../catalog/product-promos-and-demos.md) or [Story and animation](../catalog/story-and-animation.md).
2. **Do you need a presenter?** Look at [AI Avatars](../catalog/ai-avatars.md); expect paid third-party services.
3. **Do you want code you can review and re-render?** Choose a Remotion or HyperFrames tool. The output is a project you can diff.
4. **Are you a company?** Check the licenses: Remotion's company terms above, and the `NC` (non-commercial) marker in the list tables.
5. **Do you want everything in one place?** [OpenMontage](../skills/calesthio__OpenMontage.md) is a multi-pipeline system, at the cost of a larger setup.

Nothing here has been run by us; verify each tool's requirements in its own README.
