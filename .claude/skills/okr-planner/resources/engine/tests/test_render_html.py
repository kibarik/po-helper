from pathlib import Path
from engine.build_slides import build_slides
from engine.render_html import render_html_file
from engine.theme import load_theme

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_build_slides_order(minimal_spec):
    slides = build_slides(minimal_spec, load_theme(None))
    arches = [s.archetype for s in slides]
    assert arches[0] == "title"
    assert "big_picture" in arches and "glossary" in arches
    assert "direction_divider" in arches and "sprint_lifecycle_table" in arches
    assert arches[-1] == "takeaways"
    # pages are 1..n and footer propagated
    assert slides[1].page == 1  # title has no page number; first numbered content = 1
    assert all(s.footer == minimal_spec.footer for s in slides if s.page)

def test_render_html_file(tmp_path):
    out = render_html_file(FIX, tmp_path / "deck.html")
    doc = out.read_text(encoding="utf-8")
    assert out.exists() and doc.startswith("<!doctype html>")
    assert "Продажа мероприятий TicketsCloud" in doc
    assert "http://" not in doc and "https://" not in doc  # self-contained
