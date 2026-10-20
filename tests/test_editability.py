import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/research-figure-pipeline"
loader = importlib.util.spec_from_file_location("validator", SKILL / "scripts/validate_editability.py")
v = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v)


class EditabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = json.loads((SKILL/"references/editable-example.json").read_text(encoding="utf-8"))

    def save(self):
        p = self.root/"spec.json"
        p.write_text(json.dumps(self.spec), encoding="utf-8")
        return p

    def icon(self, transparent=True, role="illustration"):
        # Tiny synthetic alpha fixture, not an artwork or a published asset.
        im = Image.new("RGBA", (10, 10), (20, 100, 200, 255))
        if transparent:
            im.putpixel((0, 0), (0, 0, 0, 0))
        im.save(self.root/"fixture.png")
        self.spec["icons"] = [{"id":"icon", "path":"fixture.png", "x":200, "y":200,
                              "w":20, "h":20, "role":role}]

    def test_native_only_spec(self):
        _, report = v.validate_spec(self.save())
        self.assertEqual(report["expected_objects"], 9)

    def test_alpha_and_real_sample_exception(self):
        self.icon()
        v.validate_spec(self.save())
        self.icon(False)
        with self.assertRaisesRegex(ValueError, "transparent background"):
            v.validate_spec(self.save())
        self.spec["icons"][0]["role"] = "real_sample"
        v.validate_spec(self.save())

    def test_distorted_image(self):
        self.icon()
        self.spec["icons"][0]["w"] = 40
        with self.assertRaisesRegex(ValueError, "aspect ratio"):
            v.validate_spec(self.save())

    def test_out_of_bounds(self):
        self.spec["texts"][0]["x"] = 100
        with self.assertRaisesRegex(ValueError, "outside page"):
            v.validate_spec(self.save())

    def test_duplicate_and_rendered_ids(self):
        self.spec["texts"][0]["id"] = "canvas"
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            v.validate_spec(self.save())
        self.spec["texts"][0]["id"] = "flow_0"
        with self.assertRaisesRegex(ValueError, "collision"):
            v.validate_spec(self.save())

    def package(self):
        ns = "{"+v.NS["v"]+"}"
        page = ET.Element(ns+"PageContents")
        shapes = ET.SubElement(page, ns+"Shapes")
        for group in ("shapes", "texts", "icons"):
            for obj in self.spec[group]:
                s = ET.SubElement(shapes, ns+"Shape", NameU=obj["id"], Type="Shape")
                if group == "texts":
                    ET.SubElement(s, ns+"Text").text = obj["text"]
                elif group == "icons":
                    ET.SubElement(s, ns+"ForeignData")
        for arrow in self.spec["arrows"]:
            for i in range(len(arrow["points"])-1):
                ET.SubElement(shapes, ns+"Shape", NameU=f'{arrow["id"]}_{i}', Type="Shape")
        return page, shapes

    def write_package(self, page):
        path = self.root/"fixture.vsdx"
        with ZipFile(path, "w") as z:
            z.writestr("visio/pages/page1.xml", ET.tostring(page))
        return path

    def test_package_text_mismatch_and_flattened_native_object(self):
        page, shapes = self.package()
        v.validate_vsdx(self.spec, self.write_package(page))
        ns = "{"+v.NS["v"]+"}"
        text = page.find(".//"+ns+"Text")
        text.text = "Wrong value"
        with self.assertRaisesRegex(ValueError, "text differs"):
            v.validate_vsdx(self.spec, self.write_package(page))
        page, shapes = self.package()
        ET.SubElement(shapes[0], ns+"ForeignData")
        with self.assertRaisesRegex(ValueError, "representation mismatch"):
            v.validate_vsdx(self.spec, self.write_package(page))

    def test_missing_arrow(self):
        page, shapes = self.package()
        shapes.remove(shapes[-1])
        with self.assertRaisesRegex(ValueError, "object set differs"):
            v.validate_vsdx(self.spec, self.write_package(page))


if __name__ == "__main__":
    unittest.main()
