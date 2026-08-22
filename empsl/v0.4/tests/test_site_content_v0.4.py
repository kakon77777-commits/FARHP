import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

REQUIRED_SECTIONS = {
    "concept",
    "system",
    "lab",
    "evidence",
    "method",
    "roadmap",
    "faq",
}

REQUIRED_LAB_IDS = {
    "glyph",
    "variantMeta",
    "inferredClass",
    "gid",
    "frame",
    "seedBase",
    "seedTransform",
    "transformRole",
    "onset",
    "hu",
    "rime",
    "structure",
    "tone",
    "phase",
    "operator",
    "semanticKind",
    "concept",
    "inputTypes",
    "outputType",
    "arityMode",
    "arityValue",
    "reading",
    "gloss",
    "acousticSource",
    "acousticClass",
    "phaseSignature",
    "profileId",
    "confidence",
    "confidenceValue",
    "rawMode",
    "legalExample",
    "invalidExample",
    "repair",
    "exportSvg",
    "exportJson",
    "status",
    "activityStatus",
    "issues",
    "json",
    "stats",
    "variantGallery",
    "ruleGrid",
}

REQUIRED_LABELED_CONTROLS = {
    "gid",
    "frame",
    "seedBase",
    "seedTransform",
    "transformRole",
    "onset",
    "hu",
    "rime",
    "structure",
    "tone",
    "phase",
    "operator",
    "semanticKind",
    "concept",
    "arityMode",
    "arityValue",
    "inputTypes",
    "outputType",
    "reading",
    "gloss",
    "acousticSource",
    "acousticClass",
    "phaseSignature",
    "confidence",
    "profileId",
    "rawMode",
}


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.labels_for = set()
        self.resource_urls = []
        self.heading_count = 0
        self.aria_live_count = 0
        self.status_role_count = 0
        self.meta_names = set()
        self.title_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "label" and values.get("for"):
            self.labels_for.add(values["for"])
        if tag in {"h1", "h2", "h3"}:
            self.heading_count += 1
        if "aria-live" in values:
            self.aria_live_count += 1
        if values.get("role") == "status":
            self.status_role_count += 1
        if tag == "script" and values.get("src"):
            self.resource_urls.append(values["src"])
        if tag == "link" and values.get("href"):
            self.resource_urls.append(values["href"])
        if tag == "meta":
            name = values.get("name") or values.get("property")
            if name:
                self.meta_names.add(name)
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)


PARSER = SiteParser()
PARSER.feed(HTML)


class SiteContractTests(unittest.TestCase):
    def test_brand_and_dual_entry_exist(self):
        self.assertIn("Axioglyph｜理符", HTML)
        self.assertIn("Built on EMPSL v0.4", HTML)
        self.assertIn('href="#concept"', HTML)
        self.assertIn('href="#lab"', HTML)
        self.assertIn("符號，不只是被畫出來。它可以被證明。", HTML)

    def test_required_sections_and_lab_controls_exist(self):
        self.assertTrue(REQUIRED_SECTIONS <= PARSER.ids)
        self.assertTrue(REQUIRED_LAB_IDS <= PARSER.ids)
        self.assertGreaterEqual(PARSER.heading_count, 12)

    def test_form_controls_have_explicit_labels(self):
        self.assertTrue(REQUIRED_LABELED_CONTROLS <= PARSER.labels_for)

    def test_resources_are_relative_and_feedback_is_accessible(self):
        for url in PARSER.resource_urls:
            self.assertFalse(url.startswith("/"), url)
        self.assertIn("assets/site.css", PARSER.resource_urls)
        self.assertIn("assets/site.js", PARSER.resource_urls)
        self.assertGreaterEqual(PARSER.aria_live_count, 1)
        self.assertGreaterEqual(PARSER.status_role_count, 1)

    def test_metadata_and_research_boundaries_are_present(self):
        self.assertIn("Axioglyph", "".join(PARSER.title_parts))
        self.assertTrue({"description", "og:title", "og:description"} <= PARSER.meta_names)
        for phrase in (
            "128",
            "256",
            "4,096",
            "30 條",
            "Stable ID",
            "不是歷史語言復原",
            "Versioned Lexicon",
            "Typed AST",
        ):
            self.assertIn(phrase, HTML)


if __name__ == "__main__":
    unittest.main()
