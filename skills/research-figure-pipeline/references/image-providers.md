# Image tools by host

The workflow does not require a particular image model. Discover tools in the active host and use their current schemas; tool names in documentation are discovery hints, not executable API specifications.

## WorkBuddy

1. Inspect the tools exposed in the current session. When discovery is available, search for image generation (`ImageGen`, 生图), image editing and background removal (抠图/透明背景). Official CLI documentation mentions `ToolSearch` and `DeferExecuteTool`; use these only if actually exposed, according to their returned instructions.
2. Read the generation tool's complete schema before calling it. Do not invent arguments, model IDs, a server URL, MCP configuration or an external API key requirement.
3. Use WorkBuddy's available built-in image tools. Do not silently install or route through an external OpenAI, Google or other paid service. A built-in tool does not prove a specific underlying model: record the model if disclosed, otherwise say "not disclosed". If the user strictly forbids any possible use of a provider and the backend cannot be established, resolve that before generation.
4. Native transparency is preferred when supported. Otherwise preserve the original generation, use an available cutout/background-removal tool, and save its result as a separate PNG. Inspect the subject and actual alpha values. A white or checkerboard background is not transparency.
5. Save returned files using the host's documented file mechanism. Never guess an inaccessible internal asset URL or read application credentials to reproduce its private requests.
6. If a required tool is absent, name the missing capability and stop that stage. Continue source extraction or native layout planning where useful. Do not claim a generated result, silently substitute another provider, or describe an opaque asset as a successful transparent illustration.

Image calls may consume WorkBuddy credits. Report cost or credit usage only if the app/tool provides it; unknown is not free. For a requested small capability test, limit the initial run to one generation and, if needed, one background-removal call. Do not automatically repeat failed generations.

## Codex

Use the available image generation tool and its actual documented schema, following host image-generation instructions. Use transparent output for isolated illustrations. This path remains supported; it is not a fallback to call from WorkBuddy without user authorization.

## Existing assets

If generation is unavailable or the user prefers existing artwork, use authorized local assets and record provenance. Inspect alpha and visual quality. Build simple geometry, labels and arrows as native objects. Do not claim existing images were newly generated.

## Evidence and limits

Checked 2026-10-20:

- [Official tool reference](https://www.workbuddy.cn/docs/cli/tools-reference): lists ImageGen and deferred tool discovery. It is a CLI reference, not a complete WorkBuddy desktop image-call schema.
- [WorkBuddy changelog](https://www.workbuddy.cn/docs/workbuddy/Changelog): documents built-in image generation and image-processing features including cutout; availability still depends on the active client/account.
- [Official skill structure](https://open.workbuddy.cn/en/docs/skill): describes SKILL.md, references and scripts in a skill package.

These sources do not establish a public standalone ImageGen MCP endpoint. Local skill packaging, tool discovery, actual image generation and successful transparent output are separate verification stages.
