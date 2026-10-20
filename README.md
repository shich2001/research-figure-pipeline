# Research Figure Pipeline — Editable Elements

**科研绘图：独立透明插画 + Visio 原生可编辑元素**

## 来源与致谢 / Attribution

本仓库是 [FuJincheng-01/research-figure-pipeline](https://github.com/FuJincheng-01/research-figure-pipeline) 的衍生 fork，原作者为 **Fu Jincheng**。原项目建立了“生成总图 → 用户确认 → 分模块生成 → 本地可见 Visio COM 组装”的流程。本 fork 由 **shich2001** 维护，在该流程上增加元素级可编辑性、通用组装脚本和结构校验；不代表原作者或原项目的官方版本。

This is a derivative fork of **Fu Jincheng's [Research Figure Pipeline](https://github.com/FuJincheng-01/research-figure-pipeline)**, maintained by **shich2001**. It retains the original master-approval and visible local Visio workflow and adds element-level editability. It is not an official upstream release. The original copyright notice and [MIT license](LICENSE) are retained.

仓库名与 skill 调用名继续使用 `research-figure-pipeline`，展示名称增加 **Editable Elements**，便于识别功能差异。

## 改进内容

| 内容 | 本 fork 的默认交付 |
| --- | --- |
| 背景、卡片、边框、编号圆圈 | 独立 Visio 原生形状 |
| 标题、文字、数据、编号 | 独立原生文本 |
| 箭头、分支与汇合 | 原生线段 |
| 人物、设备等复杂插画 | 独立透明 PNG，按需分别移动、缩放和替换 |
| 真实样本、截图、数据图 | 保留真实来源；允许不透明背景 |

禁止默认把整列或整张图作为最终图片模块。生成插画的内部仍然是位图，不能逐笔编辑；包裹 PNG 的 SVG 也不会自动变成矢量。独立对象不等于自动布局：当前通用脚本的箭头是线段，移动节点后可能需要调整连线。

## 使用流程

1. 从授权论文正文提取研究事实与数据。
2. 生成总图，确认布局和风格。
3. 用户确认后，拆分原生元素和独立插画；已有确认无需重复询问。
4. 单独生成透明插画，保留真实样本。
5. 编写组装 JSON，在本地可见 Visio 中创建可编辑对象。
6. 检查导出预览，并校验透明度和 VSDX 对象结构。

总图确定外观，JSON 描述对象，Visio 完成最终组装。支持不同研究和布局，不内置任何真实研究的内容或数据。

## 环境与安装

- Codex 或具备相应工具的环境，需要图像生成能力。
- Windows + 本地 Microsoft Visio；Windows PowerShell 5.1 用于 COM。
- Python 3.10+ 和 Pillow：`python -m pip install Pillow`。

### 安装为 skill

```powershell
git clone https://github.com/shich2001/research-figure-pipeline.git
Copy-Item -LiteralPath .\research-figure-pipeline\skills\research-figure-pipeline -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

若已有同名 skill，先备份后更新该目录，避免安装两个同名版本。新对话中使用：

```text
使用 $research-figure-pipeline，根据我的论文制作可微调科研流程图。
先确认总图；背景、卡片、文字、编号和箭头使用原生对象，
复杂插画生成独立透明素材，最后交付 VSDX 和预览。
```

### 插件安装

仓库保留上游 `install.ps1` 和插件封装。运行 `powershell -NoProfile -File .\install.ps1` 会复制插件、更新个人 marketplace，并在找到 Codex CLI 时执行插件安装。已安装独立 skill 的用户无需再重复安装插件。

## 通用组装与校验

格式见 [assembly-spec.md](skills/research-figure-pipeline/references/assembly-spec.md)，虚构示例见 [editable-example.json](skills/research-figure-pipeline/references/editable-example.json)。

```powershell
$skill = ".\skills\research-figure-pipeline"
python "$skill\scripts\validate_editability.py" .\figure\assembly_spec.json
powershell -NoProfile -File "$skill\scripts\assemble_visio.ps1" -SpecPath .\figure\assembly_spec.json -OutputStem .\figure\figure-v1 -Python python
python "$skill\scripts\validate_editability.py" .\figure\assembly_spec.json --vsdx .\figure\figure-v1.vsdx --report .\figure\validation.json
```

输出目录须已存在。组装器新建 Visio 文档，拒绝覆盖已有 VSDX/PNG/SVG/PDF；修改后请使用新输出名。手工修改 VSDX 不会回写 JSON。PNG/PDF/SVG 为导出文件，以 VSDX 作为微调源文件。

校验器检查真实 alpha、图片比例、对象 ID、原生文本和图片类型、预期箭头线段。它不能判断研究事实、图片是否误带背景卡片或版式是否美观，仍须人工/视觉检查。

## 项目文件

```text
.codex-plugin/plugin.json       插件信息与上游作者信息
skills/research-figure-pipeline/
  SKILL.md                     默认工作流和可编辑性约定
  agents/openai.yaml           展示名称与默认调用
  references/
    editable-assets.md         素材边界、透明提示词和编辑限制
    assembly-spec.md            JSON 数据格式与执行方式
    editable-example.json      虚构原生对象示例
    checklists.md              视觉与结构验收
  scripts/
    assemble_visio.ps1          通用 Visio COM 组装
    validate_editability.py     素材与 VSDX 结构校验
    split_modules.py            参考裁图和 PNG 包装 SVG
    compare_previews.py         可选的像素差异诊断
tests/                         结构校验的行为测试
```

## English overview

Create publication-style figures with independently editable native Visio backgrounds, cards, labels, badges and arrows, plus isolated transparent raster illustrations. Approve the master first, preserve its layout and source facts, then assemble visibly through local Microsoft Visio COM.

The reusable JSON renderer refuses existing output paths and never clears a user's existing document. The validator checks actual alpha transparency, aspect ratio and expected native/image/text/arrow objects. It does not prove scientific correctness or visual quality. Generated illustrations remain raster, and line segments are not glued connectors. Use a new output stem for rebuilds to preserve manual edits.

Requires Windows, Microsoft Visio, Windows PowerShell 5.1, Python 3.10+ and Pillow. The skill name remains `$research-figure-pipeline`. See the attribution above and the retained [MIT license](LICENSE).
