# WorkBuddy capability test

Use only when the user requests a small integration test. This tests one asset, not a final research figure; master approval is not required for this test. Full figure production retains the normal approved-master workflow.

1. Read `image-providers.md`. Discover generation and transparency/cutout tools, inspect their actual schemas, and report the host/tool names. Respect provider restrictions.
2. In a new user-selected output directory, save the prompt and generate exactly one illustration:

   > 一名护士坐在桌旁，面对笔记本电脑使用咨询平台。简洁科研插画，柔和蓝绿配色，轮廓清楚，完整人物和电脑，适当留白。仅一个独立插画主体；不要文字、编号、卡片、外框、标题、流程箭头或水印。支持时使用真实透明背景。

3. Preserve the original image. If it lacks transparency, use at most one available background-removal call. Do not simulate success with white-to-alpha conversion or a checkerboard image. If cutout is unavailable, report that limitation and retain the original.
4. Open and inspect the output. With Pillow, read the original mode, dimensions and alpha extrema; count fully transparent and nonzero-alpha pixels. Passing requires an alpha channel with at least one fully transparent and one visible pixel, plus visual inspection showing no baked-in card, checkerboard or clipped subject. Transparent padding around an opaque rectangle fails the visual check.
5. Save `smoke-test-report.json` with `host`, `generation_tool`, `cutout_tool`, `model_if_disclosed`, `original_file`, `transparent_file`, `alpha_check`, `visual_check`, `credits_if_reported`, `status`, and `limitations`. Use null/unknown for undisclosed fields, not invented values. Status is `passed` only after a real generation and both checks pass; otherwise use `blocked` or `failed` with reasons.
6. Show the image and report to the user. Do not automatically batch-generate study illustrations. This test does not validate full Visio assembly or research accuracy.
