from engine.archetypes import ARCHETYPES
from engine.theme import load_theme

T = load_theme(None)

def _texts(elements):
    return " ".join(e.text for e in elements if e.text) + " ".join(
        r[0] for e in elements for r in (e.runs or []))

def test_title():
    els = ARCHETYPES["title"]({"kicker": "КВАРТАЛ GDS · 2026 Q3",
                               "headline": "Что мы делаем с витриной",
                               "sub": "Общая картина."}, T)
    assert any(e.kind == "rect" for e in els)          # dark background
    assert "Что мы делаем" in _texts(els)

def test_big_picture_four_cards():
    cards = [{"n": i, "title": f"D{i}", "note": "x", "color": "#E4002B"} for i in range(1, 5)]
    els = ARCHETYPES["big_picture"]({"kicker": "ОБЩАЯ КАРТИНА",
                                     "headline": "Четыре вещи", "cards": cards}, T)
    # 4 number badges (rects with the direction color) present
    assert sum(1 for e in els if e.kind == "rect" and e.fill == "#E4002B") >= 1
    assert "D4" in _texts(els)

def test_why_market_numbers():
    els = ARCHETYPES["why_market"]({"kicker": "ЗАЧЕМ", "headline": "Рынок",
                                    "stats": [{"value": "≈227 млрд ₽", "label": "рынок"}],
                                    "shift": "уводим витрину"}, T)
    assert "≈227 млрд ₽" in _texts(els)

def test_glossary_terms():
    els = ARCHETYPES["glossary"]({"kicker": "СЛОВАРЬ", "headline": "Что есть что",
                                  "terms": [{"term": "БАЗИС", "plain": "старая база"}]}, T)
    assert "БАЗИС" in _texts(els) and "старая база" in _texts(els)

def test_direction_divider():
    els = ARCHETYPES["direction_divider"]({"number": "01", "kicker": "НАПРАВЛЕНИЕ",
                                           "title": "Надёжный источник",
                                           "blurb": "текст", "color": "#E4002B"}, T)
    assert "Надёжный источник" in _texts(els)

def test_takeaways():
    els = ARCHETYPES["takeaways"]({"kicker": "ЧТО ЗАПОМНИТЬ", "headline": "Тезисы",
                                   "items": [{"title": "A", "note": "b"}]}, T)
    assert "A" in _texts(els)

def test_sprint_lifecycle_table_has_chips():
    els = ARCHETYPES["sprint_lifecycle_table"]({
        "kicker": "НАПРАВЛЕНИЕ 1", "headline": "Как работаем",
        "sprints": ["S1", "S2", "S3"],
        "rows": [{"label": "Новый источник", "cells": {"S1": ["SA·ADR"], "S2": ["BE·Go"]}}],
        "owners": "ADR — Чеботков"}, T)
    assert any(e.kind == "chip" and "SA·ADR" in e.text for e in els)
    # SA chip uses the gold role color
    sa = [e for e in els if e.kind == "chip" and "SA" in e.text][0]
    assert sa.fill == "#B37D0C"

def test_roles_sprint_table():
    els = ARCHETYPES["roles_sprint_table"]({
        "kicker": "РАЗБИВКА", "headline": "Кто над чем",
        "sprints": ["S1", "S2"],
        "rows": [{"role": "BE", "expertise": "Backend", "people": "Величко",
                  "cells": {"S1": "TC→UMC"}}],
        "note": "S1 закоммичен."}, T)
    joined = " ".join(e.text for e in els if e.text)
    assert "Backend" in joined and "TC→UMC" in joined

def test_now_becomes_detail():
    els = ARCHETYPES["now_becomes_detail"]({
        "kicker": "KR 1.1", "title": "Продажа TC",
        "now": "через БАЗИС", "becomes": "напрямую из TC",
        "stages": [{"label": "Разработка", "steps": [{"role": "BE", "text": "TC→UMC"}]}],
        "risks": ["Блокер дедуб"]}, T)
    joined = " ".join(e.text for e in els if e.text) + " ".join(
        r[0] for e in els for r in (e.runs or []))
    assert "через БАЗИС" in joined and "напрямую из TC" in joined and "Блокер" in joined
