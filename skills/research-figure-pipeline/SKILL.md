---
name: research-figure-pipeline
description: Create and refine publication-quality research diagrams from manuscript evidence, using an approved generated master, independent transparent illustrations, and editable native Visio shapes, text and arrows. Deliver local Visio files with exported previews and editability checks.
---

# Research Figure Pipeline — Editable Elements

Use for research workflows, method and system diagrams, and multi-module scientific figures. Preserve source facts and deliver a figure the user can actually fine-tune.

Derived from Fu Jincheng's [research-figure-pipeline](https://github.com/FuJincheng-01/research-figure-pipeline). This fork adds element-level editability; it retains the approved-master and visible local Visio workflow.

## Default editing contract

- Native Visio objects: panel backgrounds, cards, borders, headings, body text, counts, badges, legends, arrows and simple geometric marks.
- Independent transparent images: complex illustrations, such as people, equipment and conceptual icons. Use one asset for each semantic illustration the user should move or replace independently.
- Real samples and screenshots: preserve real evidence; rectangular opaque images are appropriate here. Explicitly mark them as real samples rather than requiring transparency.
- Do not flatten a whole figure, column or card containing editable content into an image unless the user explicitly requests that tradeoff.
- Transparent PNGs are still raster images. State that users can move/resize/replace an illustration but cannot edit its internal strokes as vector paths. An SVG wrapping a PNG does not change this.
- Prefer native simple shapes over generated images for simple circles, bars and badges. Use image generation for complex illustration content.

## Workflow

Before generating images, read [references/image-providers.md](references/image-providers.md) and select tools available in the current host. Respect the user's provider restrictions. In WorkBuddy, prefer its built-in image tools; do not assume a public MCP endpoint or silently fall back to OpenAI/Google services. For a requested capability test, use [references/workbuddy-smoke-test.md](references/workbuddy-smoke-test.md).

1. **Extract source truth.** Read the manuscript body and authorized source material. Record labels, counts, order and relationships. Honor excluded source figures. Do not turn planned work into completed results or invent clinical effects.
2. **Create the master.** Use the verified image generation tool available in the current host to establish layout, proportions, palette and visual language. Show the complete master and obtain explicit approval before generating final illustration assets or assembling Visio. If that approval already exists in the conversation, continue without asking again.
3. **Plan editable objects.** After approval, read [references/editable-assets.md](references/editable-assets.md). Inventory native objects, independent generated illustrations, and real samples. Use the approved master as the coordinate and style reference. Preserve its visual hierarchy and relationships; regenerated illustrations need not be pixel-identical. If the user requests editability repairs, separate the affected elements while preserving the approved design; do not restart master approval for a structural repair alone.
4. **Generate assets.** Use the master as a style reference and generate each required illustration separately. Request genuine transparency when the tool supports it; otherwise use an available background-removal tool and verify the resulting alpha channel. Do not bake in cards, captions, numbers or process arrows. Keep real evidence real. Save prompts, original assets and tool provenance. Crops may serve as references or preserve real samples; do not substitute crops of a flattened master for regenerated final illustrations without user authorization.
5. **Assemble in local Visio.** Read [references/assembly-spec.md](references/assembly-spec.md). Create a JSON spec and use `scripts/assemble_visio.ps1`, or adapt a project-local copy if the diagram needs unsupported geometry. Keep Visio visible. Native elements must remain independent and unlocked. The bundled builder creates a new document and refuses existing output paths; use a new output stem to preserve manual edits. It does not reverse-sync edits from VSDX to JSON.
6. **Verify both appearance and editability.** Export from Visio, inspect the actual preview at publication scale and verify source content. Run `scripts/validate_editability.py` against the spec and VSDX. Apply [references/checklists.md](references/checklists.md). Repair defects before delivery.

## Assembly and tool boundaries

- Final assembly and export use the user's Windows Microsoft Visio through PowerShell COM. Attach to `Visio.Application` or start it, then set `Visible = $true`.
- Final deliverables include the actual `.vsdx` plus a Visio-exported preview. Do not substitute a browser, draw.io, PowerPoint or externally composed bitmap as the final Visio figure.
- The bundled renderer handles native rectangles/ellipses, text, independently imported images and line paths. It is a reusable starting point, not an arbitrary diagram engine. Line paths are editable segments, not automatically glued connectors.
- Keep image aspect ratios. Avoid tiny text, overfilled cards and arrows touching content.
- Image generation must not invent measured charts or experimental results. Quantitative plots should come from actual data using appropriate plotting tools and be identified as plot assets.
- `scripts/split_modules.py` creates reference crops and PNG-containing SVG wrappers; it does not segment objects or vectorize them.
- `scripts/compare_previews.py` is an optional pixel-difference aid. It cannot validate research meaning or editability, and regenerated illustrations will differ from the master.

## Deliverables

Keep each study's source facts and generated assets in that study's output folder, not in the reusable skill:

```text
master.png
assembly_spec.json
figure.vsdx
figure.png
figure.pdf
editing_notes.txt
validation.json
assets/icons/
assets/real_samples/
tools/
```

Save prompts and any adapted build scripts. Explain exactly which elements are native, which are raster, and whether arrows are connected or merely positioned. Report the file and preview links, validation outcome and material limitations. Do not claim pixel-level vector editability for generated illustrations.
