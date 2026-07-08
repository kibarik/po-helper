from __future__ import annotations
import sys
from pathlib import Path
from .deckspec import load_deckspec
from .theme import load_theme
from .build_slides import build_slides
from .backend_html import render_page


def render_html_file(spec_path, out_path, profile: dict | None = None) -> Path:
    spec = load_deckspec(spec_path)
    theme = load_theme((profile or {}).get("present"))
    slides = build_slides(spec, theme)
    doc = render_page(slides, theme, title=f"{spec.product} · {spec.quarter}")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


if __name__ == "__main__":
    render_html_file(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]}")
