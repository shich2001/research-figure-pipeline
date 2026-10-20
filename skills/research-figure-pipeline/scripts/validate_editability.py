#!/usr/bin/env python3
"""Validate an editable figure spec and optionally its exported Visio package."""
import argparse
import json
import math
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from PIL import Image

NS = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_spec(path):
    path = Path(path).resolve()
    spec = json.loads(path.read_text(encoding="utf-8-sig"))
    page = spec["page"]
    for field in ("width_px", "height_px", "mm_per_px"):
        require(isinstance(page[field], (int, float)) and math.isfinite(page[field]) and page[field] > 0,
                f"page.{field} must be finite and positive")
    import re
    ids = set()
    images = []
    for group in ("shapes", "texts", "icons", "arrows"):
        require(isinstance(spec.get(group), list), f"{group} must be a list")
        for item in spec[group]:
            name = item["id"]
            require(isinstance(name, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name),
                    "IDs must start with a letter and use ASCII letters, numbers or underscores")
            require(name not in ids, f"Duplicate ID: {name}")
            ids.add(name)
            if group != "arrows":
                for key in ("x", "y", "w", "h"):
                    require(isinstance(item[key], (float, int)) and math.isfinite(item[key]),
                            f"{name}.{key} must be finite")
                require(item["w"] > 0 and item["h"] > 0, f"{name}: nonpositive dimensions")
                require(0 <= item["x"] <= page["width_px"]-item["w"]+0.01 and
                        0 <= item["y"] <= page["height_px"]-item["h"]+0.01, f"{name}: outside page")
            for key in ("fill", "line", "color"):
                if item.get(key) is not None:
                    require(isinstance(item[key], str) and re.fullmatch(r"#[0-9a-fA-F]{6}", item[key]),
                            f"{name}: {key} must be #RRGGBB")
            if group == "shapes":
                require(item["kind"] in ("rect", "ellipse"), f"{name}: unsupported shape")
                require("fill" in item and item.get("radius", -1) >= 0, f"{name}: fill/radius required")
            elif group == "texts":
                require(isinstance(item["text"], str) and item["text"].strip(), f"{name}: empty text")
                require(isinstance(item["size"], (float, int)) and math.isfinite(item["size"]) and item["size"] > 0,
                        f"{name}: invalid font size")
                require(item["align"] in ("left", "center", "right"), f"{name}: invalid alignment")
                require(isinstance(item["bold"], bool) and "color" in item, f"{name}: bold/color required")
            elif group == "icons":
                asset = (path.parent / item["path"]).resolve()
                require(asset.is_relative_to(path.parent), f"{name}: asset must be inside spec directory")
                role = item.get("role", "illustration")
                require(role in ("illustration", "real_sample", "data_plot"), f"{name}: invalid role")
                with Image.open(asset) as im:
                    fraction = None
                    if role == "illustration":
                        require("A" in im.getbands(), f"{name}: illustration needs alpha transparency")
                        alpha = im.getchannel("A")
                        require(alpha.getextrema()[0] == 0 and alpha.getextrema()[1] > 0,
                                f"{name}: needs transparent background and visible foreground")
                        fraction = alpha.histogram()[0] / (im.width * im.height)
                    require(abs((item["w"]/item["h"]) / (im.width/im.height)-1) < .02,
                            f"{name}: image aspect ratio distorted")
                    images.append({"id": name, "role": role, "size": im.size, "transparent_fraction": fraction})
            else:
                require(item["kind"] == "line", f"{name}: bundled renderer supports line arrows only")
                pts = item["points"]
                require(len(pts) >= 2, f"{name}: at least two points required")
                require(isinstance(item["head"], bool) and item["weight"] > 0 and "color" in item,
                        f"{name}: head, weight and color required")
                for pt in pts:
                    require(len(pt) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in pt),
                            f"{name}: invalid point")
                    require(0 <= pt[0] <= page["width_px"] and 0 <= pt[1] <= page["height_px"],
                            f"{name}: arrow point outside page")
                require(all(p != q for p, q in zip(pts, pts[1:])), f"{name}: zero-length segment")
    # Arrow segments become actual shape IDs; detect collisions with every other object.
    rendered_ids = [x["id"] for g in ("shapes", "texts", "icons") for x in spec[g]]
    rendered_ids += [f'{a["id"]}_{i}' for a in spec["arrows"] for i in range(len(a["points"])-1)]
    require(len(rendered_ids) == len(set(rendered_ids)), "Rendered shape ID collision")
    return spec, {"images": images, "expected_objects": len(rendered_ids)}


def validate_vsdx(spec, path):
    with ZipFile(path) as z:
        page = ET.fromstring(z.read("visio/pages/page1.xml"))
        shapes = page.findall("./v:Shapes/v:Shape", NS)
        named = {s.get("NameU"): s for s in shapes}
        expected = {x["id"] for g in ("shapes", "texts", "icons") for x in spec[g]}
        expected.update(f'{a["id"]}_{i}' for a in spec["arrows"] for i in range(len(a["points"])-1))
        require(len(named) == len(shapes) and set(named) == expected, "VSDX object set differs from spec")
        for group in ("shapes", "texts", "icons"):
            for item in spec[group]:
                shape = named[item["id"]]
                foreign = shape.find("v:ForeignData", NS) is not None
                require(foreign == (group == "icons"), f'{item["id"]}: native/image representation mismatch')
                if group == "texts":
                    node = shape.find("v:Text", NS)
                    require(node is not None and "".join(node.itertext()).strip() == item["text"].strip(),
                            f'{item["id"]}: text differs')
        for a in spec["arrows"]:
            for i in range(len(a["points"])-1):
                s = named[f'{a["id"]}_{i}']
                require(s.find("v:ForeignData", NS) is None and s.get("Type") == "Shape",
                        f'{a["id"]}: expected native line segment')
        return {"objects": len(shapes), "native_texts": len(spec["texts"]),
                "independent_images": len(spec["icons"]), "native_shapes": len(spec["shapes"]),
                "arrow_segments": sum(len(a["points"])-1 for a in spec["arrows"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec")
    parser.add_argument("--vsdx")
    parser.add_argument("--report")
    args = parser.parse_args()
    try:
        spec, report = validate_spec(args.spec)
        if args.vsdx:
            report["visio"] = validate_vsdx(spec, args.vsdx)
        report["status"] = "passed"
        report["scope"] = "Structural checks only; visually inspect assets and exported preview."
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload+"\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
