from engine.theme import Theme, load_theme

def test_defaults_match_etalon():
    t = load_theme(None)
    assert t.accent == "#E4002B"
    assert t.heading == "#1C2333"
    assert t.heading_font == "Cambria"
    assert t.body_font == "Calibri"
    assert t.direction_palette[1] == "#2E4B7A"
    assert t.role_color("QA") == "#7E56A6"
    assert t.role_color("BE") == "#2E4B7A"

def test_profile_override():
    t = load_theme({"accent_color": "#123456",
                    "role_color_map": {"QA": "#000000"}})
    assert t.accent == "#123456"
    assert t.role_color("QA") == "#000000"   # overridden
    assert t.role_color("BE") == "#2E4B7A"   # default kept
    assert t.heading == "#1C2333"            # untouched default

def test_unknown_role_falls_back_to_body():
    t = load_theme(None)
    assert t.role_color("ZZ") == t.body

def test_direction_color_cycles():
    t = load_theme(None)
    assert t.direction_color(0) == "#E4002B"
    assert t.direction_color(4) == "#E4002B"  # wraps
