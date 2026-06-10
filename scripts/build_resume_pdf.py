#!/usr/bin/env python3
"""Convert the resume Markdown file to PDF with the project resume styling.

Default:
    python3 scripts/build_resume_pdf.py

Custom paths:
    python3 scripts/build_resume_pdf.py input.md output.pdf
"""

from __future__ import annotations

import argparse
import asyncio
import html
import re
from pathlib import Path
from urllib.parse import urlparse

import markdown
from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD = ROOT / "resume" / "fuxiang-yang-resume.md"
DEFAULT_PDF = ROOT / "resume" / "fuxiang-yang-resume.pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
CHROME_PATH = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

CSS = """
@page { size: A4; margin: 11mm 14mm 10mm 14mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  color: #172033;
  background: #ffffff;
  font-family: "Times New Roman", "Songti SC", "SimSun", serif;
  font-size: 10pt;
  line-height: 1.32;
  letter-spacing: 0;
}
.resume { width: 100%; }
.avatar {
  float: right;
  width: 23mm;
  height: 23mm;
  margin: -6mm 0 3mm 8mm;
  border-radius: 50%;
  object-fit: cover;
  object-position: center;
  border: 1px solid #b8c7d8;
}
h1 {
  margin: 0 0 2px;
  padding-bottom: 3px;
  color: #102f52;
  border-bottom: 1.7px solid #1f4e79;
  font-family: "Times New Roman", "Songti SC", "SimSun", serif;
  font-size: 24pt;
  line-height: 1.12;
  font-weight: 700;
}
h1 + p {
  margin: 4px 0 7px;
  color: #27364b;
  font-size: 10pt;
  line-height: 1.35;
}
h2 {
  margin: 7px 0 3px;
  padding-bottom: 2px;
  color: #174f82;
  border-bottom: 0.8px solid #b8c7d8;
  font-size: 13.2pt;
  line-height: 1.15;
  font-weight: 700;
}
h3 {
  margin: 5px 0 1px;
  color: #172033;
  font-size: 10.6pt;
  line-height: 1.25;
  font-weight: 700;
}
p { margin: 0 0 3px; }
ul {
  margin: 1px 0 4px 0;
  padding-left: 14px;
}
li {
  margin: 0.9px 0;
  padding-left: 1px;
}
a {
  color: #174f82;
  text-decoration: none;
}
strong {
  font-weight: 700;
  color: #102f52;
}
"""


def to_file_uri_if_local(src: str, base_dir: Path) -> str:
    parsed = urlparse(src)
    if parsed.scheme or src.startswith("#"):
        return src

    image_path = Path(src)
    if not image_path.is_absolute():
        image_path = base_dir / image_path
    return image_path.resolve().as_uri()


def normalize_local_image_sources(body: str, base_dir: Path) -> str:
    pattern = re.compile(r'(<img\b[^>]*\bsrc=)(["\'])([^"\']+)(\2)', re.IGNORECASE)

    def replace(match: re.Match[str]) -> str:
        prefix, quote, src, suffix = match.groups()
        return f"{prefix}{quote}{to_file_uri_if_local(src, base_dir)}{suffix}"

    return pattern.sub(replace, body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert resume Markdown to PDF.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_MD,
        help=f"Markdown input path. Default: {DEFAULT_MD}",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=DEFAULT_PDF,
        help=f"PDF output path. Default: {DEFAULT_PDF}",
    )
    return parser.parse_args()


def build_html(md_path: Path, html_path: Path, pdf_path: Path) -> None:
    markdown_text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(markdown_text, extensions=["extra", "sane_lists"])
    body = normalize_local_image_sources(body, md_path.parent)
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(pdf_path.stem)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main class="resume">{body}</main>
</body>
</html>
"""
    html_path.write_text(document, encoding="utf-8")


async def convert(md_path: Path, pdf_path: Path) -> None:
    md_path = md_path.resolve()
    pdf_path = pdf_path.resolve()
    html_path = TMP_DIR / f"{pdf_path.stem}.html"

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")
    if not CHROME_PATH.exists():
        raise FileNotFoundError(f"Chrome executable not found: {CHROME_PATH}")

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    build_html(md_path, html_path, pdf_path)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=str(CHROME_PATH),
            headless=True,
        )
        page = await browser.new_page(viewport={"width": 1240, "height": 1754})
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
        )
        await browser.close()

    html_path.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    asyncio.run(convert(args.input, args.output))
    print(args.output.resolve())


if __name__ == "__main__":
    main()
