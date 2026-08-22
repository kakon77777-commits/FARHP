"""Build the public Axioglyph Worker asset bundle.

Only browser runtime files cross this boundary. Research source, tests, tools,
corpus data, specifications, and archives stay in the repository.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "empsl" / "v0.4"
SITE = ROOT / "site"
DIST = SITE / "dist"
ORIGIN = "https://axioglyph.evemisslab.com/"

RUNTIME_FILES = (
    "index.html",
    "assets/site.css",
    "assets/site.js",
    "assets/app.js",
    "assets/empsl_core.js",
    "data/EMPSL_atom_registry_v0.2.js",
    "data/EMPSL_seed_variant_registry_v0.3.js",
    "data/EMPSL_legality_report_v0.4.js",
    "rules/EMPSL_grammar_tables_v0.4.js",
    "rules/EMPSL_rule_catalog_v0.4.js",
    "examples/EMPSL_legality_examples_v0.4.js",
)


def copy(relative_path: str, source_root: Path = SOURCE) -> None:
    source = source_root / relative_path
    target = DIST / relative_path
    if not source.is_file():
        raise FileNotFoundError(f"required public asset is missing: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for relative_path in RUNTIME_FILES:
        copy(relative_path)
    for support_file in ("404.html", "llms.txt"):
        copy(support_file, SITE)

    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}sitemap.xml\n",
        encoding="utf-8",
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{ORIGIN}</loc></url>"
        "</urlset>\n",
        encoding="utf-8",
    )

    count = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"built Axioglyph public bundle: {count} files -> {DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
