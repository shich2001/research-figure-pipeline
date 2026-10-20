# Assembly spec

Use UTF-8 JSON. All layout coordinates and font sizes are design pixels. Origin is
top-left; `mm_per_px` converts them to the physical Visio page. Asset paths are
relative to the spec directory and must stay within it.

See [editable-example.json](editable-example.json) for a runnable native-only
fictional example. The renderer requires all four arrays, even when empty.

| Field | Meaning |
| --- | --- |
| `page` | Positive `width_px`, `height_px`, `mm_per_px` |
| `shapes` | Native backgrounds, cards, circles and simple marks |
| `texts` | Independent native labels and numeric text |
| `icons` | Independent image instances, not entire panels |
| `arrows` | Native editable line paths |

IDs must be unique ASCII names starting with a letter. Arrow `flow` with two
segments creates `flow_0` and `flow_1`; these IDs must not collide with other objects.

- Shape: `id, x, y, w, h, kind` (`rect` or `ellipse`), `fill` (#RRGGBB),
  `line` (#RRGGBB or null), `radius` (pixels, 0 for square corners).
- Text: `id, text, x, y, w, h, size, bold` (boolean), `color`, `align`
  (`left`, `center`, `right`). Unicode and explicit newlines are supported.
- Image: `id, path, x, y, w, h`, optional `role` (`illustration` by default,
  `real_sample` or `data_plot`). Preserve source aspect ratio. Illustration images
  require alpha with transparent pixels and visible content. Samples/plots may be opaque.
- Arrow: `id, points` (at least two `[x,y]` positions), `kind: "line"`,
  `color`, positive `weight`, `head` (boolean). Head is applied only to last segment.

The builder draws shapes first, then images, arrows and text. Within each array,
later objects appear above earlier objects. Put a full-page white native rectangle
first to preserve page bounds in raster export. Numbers and their circles are two
separate objects. Objects are not grouped or locked.

The bundled renderer intentionally supports a small geometry set. For filled
block arrows, custom paths or glued connectors, adapt a project-local script and
extend the validator accordingly rather than mislabeling the output.

```powershell
python scripts/validate_editability.py C:\figures\assembly_spec.json
powershell -NoProfile -File scripts/assemble_visio.ps1 -SpecPath C:\figures\assembly_spec.json -OutputStem C:\figures\draft-v1 -Python python
python scripts/validate_editability.py C:\figures\assembly_spec.json --vsdx C:\figures\draft-v1.vsdx --report C:\figures\validation.json
```

`-Font` defaults to `Microsoft YaHei`; select a font installed on the target machine.
Run using Windows PowerShell 5.1. The output parent must exist and all four output
paths must be unused. The builder leaves its new document open in visible Visio.
It does not edit existing files, import manual edits, or regenerate AI assets.

Validation checks only the first page created by this renderer. Structural success
does not prove that an illustration is scientifically appropriate, that a card
background was not baked into it, or that text fits. Inspect the exported preview.
