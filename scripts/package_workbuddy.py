"""Build a WorkBuddy ZIP without changing the Codex skill's frontmatter."""
import argparse
import json
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New ZIP path; existing files are refused")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "skills" / "research-figure-pipeline"
    version = json.loads((root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    skill_text = (source / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = skill_text.removeprefix("---\n").split("\n---\n", 1)
    extra = (
        '\ndisplay_name: 科研绘图流程 · 可编辑元素'
        '\ndescription_zh: 从论文生成科研流程图，使用独立透明插画与 Visio 原生形状、文字和箭头，支持 WorkBuddy 内置生图工具发现。'
        '\ndescription_en: Research diagrams with transparent illustrations, native editable Visio objects, and host-aware image tool discovery.'
        f'\nversion: {version}'
        '\nauthor: "Fu Jincheng (original); shich2001 (fork)"'
    )
    package_skill = f"---\n{frontmatter}{extra}\n---\n{body}"
    prefix = "research-figure-pipeline/"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(prefix + "SKILL.md", package_skill.encode("utf-8"))
        archive.write(root / "LICENSE", prefix + "LICENSE")
        for folder in ("references", "scripts"):
            for path in sorted((source / folder).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    archive.write(path, prefix + path.relative_to(source).as_posix())
    print(f"Built WorkBuddy {version} package: {args.output.resolve()}")


if __name__ == "__main__":
    main()
