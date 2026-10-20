# Editable asset contract

## Choose the object boundary by the intended edit

If a user might move, resize, recolor or reword an element without changing its neighbors, make it an independent object. A panel is a layout container, not automatically one bitmap.

| Element | Default representation |
| --- | --- |
| Background, card, border, number circle | Native Visio shape |
| Heading, count, explanatory text, legend | Native Visio text |
| Flow arrow, branch, merge | Native Visio line/path |
| Simple schematic bars without measured values | Native shapes; label as schematic when ambiguous |
| People, brain, equipment, complex conceptual illustration | Independent transparent PNG |
| Clinical screenshot, microscopy, real specimen | Real image, preserve evidence; opaque allowed |
| Data chart | Data-derived plot, not AI-invented values |

## Prompt template

Generate ONE isolated [illustration] using the approved master only as a style reference. Match its palette, line language and visual density. Use a genuinely transparent alpha background and comfortable transparent padding. Include only [required objects]. No panel background, card, frame, label, heading, number, watermark or process arrow. Keep all extremities visible. This illustration will be placed independently beside native Visio text and shapes.

If the actual tool schema exposes a transparent-background option, set it as well as describing transparency in the prompt. Otherwise generate an isolated subject, then use an available background-removal tool following [image-providers.md](image-providers.md). A prompt alone does not prove transparency. Do not remove white pixels indiscriminately: white clothing and object interiors are meaningful content.

## Inspect before importing

- Inspect the illustration itself for semantic correctness, style and clipping.
- Verify an alpha channel with both transparent and visible pixels. Transparent padding alone cannot prove a card was not baked into the image; inspect visually too.
- Keep one asset per independently editable semantic illustration. Split people or subcomponents further when the requested edits require it.
- Do not promise internal vector editing. Recoloring a person's clothing or changing an illustration's internal structure requires image editing/regeneration or a genuine vector source.
- Preserve icon aspect ratio when positioning it within a desired bounding box.

## Master fidelity

Keep the approved layout, proportions, colors and relationships. Native cards may replace raster cards at matching coordinates. Regenerated icons can vary in pixels while preserving their meaning and style. A user-authorized correction to object granularity does not require a fresh layout approval.
