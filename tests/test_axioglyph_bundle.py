import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site" / "dist"

REQUIRED_FILES = {
    "index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "assets/site.css",
    "assets/site.js",
    "assets/app.js",
    "assets/empsl_core.js",
    "assets/farhp_audio.js",
    "data/EMPSL_atom_registry_v0.2.js",
    "data/EMPSL_seed_variant_registry_v0.3.js",
    "data/EMPSL_legality_report_v0.4.js",
    "rules/EMPSL_grammar_tables_v0.4.js",
    "rules/EMPSL_rule_catalog_v0.4.js",
    "examples/EMPSL_legality_examples_v0.4.js",
}


class AxioglyphBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, "-B", str(ROOT / "site" / "build.py")],
            cwd=ROOT,
            check=True,
        )

    def test_public_bundle_is_exact_and_bounded(self):
        public_files = {
            path.relative_to(DIST).as_posix()
            for path in DIST.rglob("*")
            if path.is_file()
        }
        self.assertEqual(REQUIRED_FILES, public_files)

        public_top_level = {path.name for path in DIST.iterdir()}
        self.assertNotIn("tests", public_top_level)
        self.assertNotIn("corpus", public_top_level)
        self.assertNotIn("tools", public_top_level)
        self.assertNotIn("spec", public_top_level)

    def test_discovery_files_name_the_production_origin(self):
        origin = "https://axioglyph.evemisslab.com/"
        self.assertIn(origin, (DIST / "index.html").read_text(encoding="utf-8"))
        self.assertIn(origin, (DIST / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertIn(origin, (DIST / "llms.txt").read_text(encoding="utf-8"))
        self.assertIn("noindex", (DIST / "404.html").read_text(encoding="utf-8"))
        llms = (DIST / "llms.txt").read_text(encoding="utf-8")
        for phrase in (
            "browser audio",
            "neutral, male, and female",
            "PH16 representative synthesis",
            "does not upload",
            "not natural-speech",
        ):
            self.assertIn(phrase, llms)

    def test_wrangler_uses_the_expected_assets_route(self):
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertEqual("axioglyph", config["name"])
        self.assertEqual("./site/dist", config["assets"]["directory"])
        self.assertEqual("404-page", config["assets"]["not_found_handling"])
        self.assertEqual(
            [{"pattern": "axioglyph.evemisslab.com", "custom_domain": True}],
            config["routes"],
        )


if __name__ == "__main__":
    unittest.main()
