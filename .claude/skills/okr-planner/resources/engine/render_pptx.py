from __future__ import annotations
import sys
from pathlib import Path
from .deckspec import load_deckspec
from .theme import load_theme
from .build_slides import build_slides
from .backend_pptx import new_presentation, add_slide


def render_pptx_file(spec_path, out_path, profile: dict | None = None) -> Path:
    spec = load_deckspec(spec_path)
    theme = load_theme((profile or {}).get("present"))
    slides = build_slides(spec, theme)
    prs = new_presentation(theme)
    for s in slides:
        add_slide(prs, s, theme)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    render_pptx_file(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]}")
