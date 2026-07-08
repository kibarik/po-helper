from engine.layout import Element, Slide, text, rect, chip

def test_text_factory_defaults():
    e = text(0.1, 0.2, 0.3, 0.05, "Hi", color="#111111", size_pt=18, bold=True)
    assert e.kind == "text"
    assert (e.fx, e.fy, e.fw, e.fh) == (0.1, 0.2, 0.3, 0.05)
    assert e.text == "Hi" and e.color == "#111111" and e.bold is True

def test_rect_and_chip():
    r = rect(0, 0, 1, 1, fill="#F5F7FB")
    assert r.kind == "rect" and r.fill == "#F5F7FB"
    c = chip(0.5, 0.5, 0.1, 0.04, "BE·Go", fill="#2E4B7A")
    assert c.kind == "chip" and c.text == "BE·Go" and c.align == "center"

def test_slide_holds_elements():
    s = Slide("title", [text(0, 0, 1, 0.1, "T")], footer="F", page=1)
    assert s.archetype == "title" and len(s.elements) == 1 and s.page == 1
