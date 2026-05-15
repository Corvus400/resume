#!/usr/bin/env python3
"""Build resume HTML from README.md for PDF generation via weasyprint.

Reads README.md, transforms <details>/<summary>/</details> into Markdown
headings, splits on <div class="page-break"></div>, and emits a single
HTML document with the slide-style.css inlined.

CSS path resolves to $RUNNER_TEMP/slide-style.css (set by GitHub Actions),
falling back to ./slide-style.css for local invocation.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

runner_temp = os.environ.get("RUNNER_TEMP")
css_path = pathlib.Path(runner_temp) / "slide-style.css" if runner_temp else pathlib.Path("slide-style.css")

src = README.read_text(encoding="utf-8")

# Strip leading HTML-comment frontmatter (md-to-pdf style)
src = re.sub(r"^<!--[\s\S]*?-->\s*", "", src, count=1)

# Decompose <details>/<summary>/</details> into Markdown h3 headings
# (avoids md_in_html and Python-Markdown's HTML pass-through quirks)
src = re.sub(
    r"<details>\s*<summary>(.*?)</summary>\s*",
    r"### \1\n\n",
    src,
    flags=re.S,
)
src = src.replace("</details>", "")

# GFM Alert is not rendered by weasyprint; flatten to bold-prefixed quote
src = src.replace("> [!TIP]", "> **TIP**")

body = markdown.markdown(
    src,
    extensions=["tables", "fenced_code", "attr_list"],
)

parts = re.split(r'<div class="page-break"></div>', body)
pages = "\n".join(
    f'<div class="page">{p}<div class="page-number">{i + 1}</div></div>'
    for i, p in enumerate(parts)
)

css = css_path.read_text(encoding="utf-8")

sys.stdout.write(
    '<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">'
    '<title>職務経歴書</title>'
    f'<style>{css}</style></head><body>{pages}</body></html>'
)
