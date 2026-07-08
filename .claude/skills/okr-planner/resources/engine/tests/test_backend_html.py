from engine.backend_html import render_page, element_html
from engine.layout import text, rect, chip, Slide
from engine.theme import load_theme

T = load_theme(None)

def test_element_text_positioned_percent():
    html = element_html(text(0.1, 0.2, 0.3, 0.05, "Hello", color="#111"), T)
    assert "left:10.0%" in html and "top:20.0%" in html
    assert "Hello" in html

def test_chip_has_fill():
    html = element_html(chip(0.0, 0.0, 0.1, 0.04, "BE", fill="#2E4B7A"), T)
    assert "#2E4B7A" in html and "BE" in html

def test_page_is_self_contained():
    slides = [Slide("title", [text(0.1, 0.1, 0.5, 0.1, "Deck")], footer="F", page=1)]
    doc = render_page(slides, T, title="Deck")
    assert doc.strip().startswith("<!doctype html>")
    assert "<style>" in doc and "http://" not in doc and "https://" not in doc
    assert "1280px" in doc and "720px" in doc
    assert "Deck" in doc and "class=\"slide\"" in doc

def test_runs_render_mixed_colors():
    e = text(0, 0, 1, 0.1, "", runs=[("СЕЙЧАС ", "#8B94A6", True), ("текст", "#434C60", False)])
    html = element_html(e, T)
    assert "СЕЙЧАС" in html and "#8B94A6" in html and "текст" in html
