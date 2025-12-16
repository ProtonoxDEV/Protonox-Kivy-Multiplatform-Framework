import tempfile
from pathlib import Path
import unittest

from PIL import Image

from protonox_studio.web.assets import ingest_asset, ensure_assets_manifest


class AssetsIngestTest(unittest.TestCase):
    def test_png_ingest_generates_webp_variant(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            src = base / "sample.png"
            img = Image.new("RGB", (4, 4), color=(255, 0, 0))
            img.save(src)

            ensure_assets_manifest(base)
            entry = ingest_asset(src, base=base)

            self.assertEqual(entry["original_name"], "sample.png")
            self.assertEqual(entry["type"], "png")
            variants = {v["kind"]: v["path"] for v in entry["variants"]}
            self.assertIn("webp", variants)
            self.assertTrue((base / variants["webp"]).exists())


if __name__ == "__main__":
    unittest.main()
