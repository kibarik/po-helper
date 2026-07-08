from __future__ import annotations
from .layout import Element, text, rect, chip
from .theme import Theme


def _kicker_headline(data: dict, theme: Theme, y=0.07) -> list[Element]:
    els = [text(0.042, y, 0.9, 0.04, data.get("kicker", ""),
                color=theme.accent, size_pt=12, bold=True)]
    if data.get("headline"):
        els.append(text(0.042, y + 0.05, 0.9, 0.09, data["headline"],
                        color=theme.heading, font=theme.heading_font, size_pt=25, bold=True))
    return els


def title(data: dict, theme: Theme) -> list[Element]:
    return [
        rect(0, 0, 1, 1, fill="#141A2E"),
        text(0.06, 0.30, 0.8, 0.05, data.get("kicker", ""), color=theme.accent, size_pt=13, bold=True),
        text(0.06, 0.37, 0.85, 0.18, data.get("headline", ""), color="#FFFFFF",
             font=theme.heading_font, size_pt=40, bold=True),
        text(0.06, 0.62, 0.7, 0.1, data.get("sub", ""), color="#AEB6CE", size_pt=13),
    ]


def big_picture(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    cards = data.get("cards", [])[:4]
    n = len(cards) or 1
    gap, mx = 0.02, 0.042
    cw = (1 - 2 * mx - gap * (n - 1)) / n
    for i, c in enumerate(cards):
        x = mx + i * (cw + gap)
        els.append(rect(x, 0.30, cw, 0.52, fill=theme.card_bg, radius=0.04))
        els.append(rect(x + 0.015, 0.34, 0.05, 0.088, fill=c.get("color", theme.accent), radius=0.2))
        els.append(text(x + 0.015, 0.34, 0.05, 0.088, str(c.get("n", i + 1)),
                        color="#FFFFFF", font=theme.heading_font, size_pt=22, bold=True,
                        align="center", valign="middle"))
        els.append(text(x + 0.015, 0.46, cw - 0.03, 0.08, c.get("title", ""),
                        color=theme.heading, font=theme.heading_font, size_pt=16, bold=True))
        els.append(text(x + 0.015, 0.56, cw - 0.03, 0.22, c.get("note", ""),
                        color=theme.body, size_pt=12))
    return els


def why_market(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    stats = data.get("stats", [])[:3]
    n = len(stats) or 1
    mx, gap = 0.042, 0.03
    cw = (1 - 2 * mx - gap * (n - 1)) / n
    for i, s in enumerate(stats):
        x = mx + i * (cw + gap)
        els.append(text(x, 0.30, cw, 0.10, s.get("value", ""), color=theme.accent,
                        font=theme.heading_font, size_pt=32, bold=True))
        els.append(text(x, 0.42, cw, 0.12, s.get("label", ""), color=theme.body, size_pt=13))
    els.append(rect(0.042, 0.66, 0.916, 0.2, fill=theme.card_bg, radius=0.03))
    els.append(text(0.06, 0.69, 0.88, 0.14, data.get("shift", ""),
                    color=theme.heading, size_pt=14, bold=True))
    return els


def glossary(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    terms = data.get("terms", [])
    mx, top, gap = 0.042, 0.28, 0.02
    col_w = (1 - 2 * mx - gap) / 2
    row_h = 0.14
    for i, t in enumerate(terms[:6]):
        col, row = i % 2, i // 2
        x = mx + col * (col_w + gap)
        y = top + row * (row_h + 0.015)
        els.append(rect(x, y, col_w, row_h, fill=theme.card_bg, radius=0.03))
        els.append(text(x + 0.012, y + 0.015, col_w - 0.024, 0.05, t.get("term", ""),
                        color=theme.heading, font=theme.heading_font, size_pt=15, bold=True))
        els.append(text(x + 0.012, y + 0.07, col_w - 0.024, 0.06, t.get("plain", ""),
                        color=theme.body, size_pt=12))
    return els


def how_to_read(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    els += [
        rect(0.042, 0.32, 0.44, 0.34, fill=theme.card_bg, radius=0.03),
        text(0.06, 0.35, 0.4, 0.05, "СЕЙЧАС", color=theme.muted, size_pt=13, bold=True),
        text(0.06, 0.42, 0.4, 0.2, data.get("now_note", "Как есть сегодня."),
             color=theme.body, size_pt=12),
        rect(0.518, 0.32, 0.44, 0.34, fill=theme.card_bg, radius=0.03),
        text(0.536, 0.35, 0.4, 0.05, "СТАНЕТ", color="#2F7D54", size_pt=13, bold=True),
        text(0.536, 0.42, 0.4, 0.2, data.get("becomes_note", "Какой результат хотим."),
             color=theme.heading, size_pt=12),
        text(0.042, 0.72, 0.916, 0.1, data.get("footnote", ""), color=theme.muted, size_pt=11),
    ]
    return els


def direction_divider(data: dict, theme: Theme) -> list[Element]:
    color = data.get("color", theme.accent)
    return [
        rect(0, 0, 0.012, 1, fill=color),
        text(0.06, 0.28, 0.3, 0.12, str(data.get("number", "")), color=color,
             font=theme.heading_font, size_pt=54, bold=True),
        text(0.06, 0.44, 0.5, 0.04, data.get("kicker", "НАПРАВЛЕНИЕ"),
             color=theme.muted, size_pt=12, bold=True),
        text(0.06, 0.49, 0.85, 0.1, data.get("title", ""), color=theme.heading,
             font=theme.heading_font, size_pt=30, bold=True),
        text(0.06, 0.62, 0.8, 0.16, data.get("blurb", ""), color=theme.body, size_pt=13),
    ]


def _list_columns(data, theme, groups):
    els = _kicker_headline(data, theme)
    mx, gap, top = 0.042, 0.02, 0.30
    n = len(groups) or 1
    cw = (1 - 2 * mx - gap * (n - 1)) / n
    for i, (label, items, accent) in enumerate(groups):
        x = mx + i * (cw + gap)
        els.append(text(x, top, cw, 0.05, label, color=accent, size_pt=12, bold=True))
        for j, it in enumerate(items[:6]):
            els.append(text(x, top + 0.07 + j * 0.075, cw, 0.07, "• " + it,
                            color=theme.body, size_pt=12))
    return els


def order_of_work(data: dict, theme: Theme) -> list[Element]:
    ow = data.get("order", {})
    groups = [
        ("СНАЧАЛА · ИЮЛЬ", ow.get("now", []), theme.accent),
        ("К АВГУСТУ", ow.get("august", []), "#2E4B7A"),
        ("ДАЛЬШЕ", ow.get("later", []), "#2F7D54"),
    ]
    return _list_columns(data, theme, groups)


def right_now(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    items = data.get("items", [])
    for i, it in enumerate(items[:5]):
        y = 0.30 + i * 0.115
        els.append(rect(0.042, y, 0.05, 0.09, fill=theme.accent, radius=0.15))
        els.append(text(0.042, y, 0.05, 0.09, str(i + 1), color="#FFFFFF",
                        font=theme.heading_font, size_pt=18, bold=True,
                        align="center", valign="middle"))
        els.append(text(0.11, y + 0.005, 0.6, 0.05, it.get("title", ""),
                        color=theme.heading, size_pt=15, bold=True))
        els.append(text(0.11, y + 0.055, 0.8, 0.04, it.get("note", ""),
                        color=theme.muted, size_pt=11))
    return els


def after_meeting(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    els.append(text(0.042, 0.32, 0.9, 0.4, data.get("body", ""), color=theme.body, size_pt=15))
    return els


def takeaways(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    items = data.get("items", [])
    for i, it in enumerate(items[:4]):
        y = 0.30 + i * 0.135
        els.append(text(0.042, y, 0.05, 0.1, str(i + 1), color=theme.accent,
                        font=theme.heading_font, size_pt=26, bold=True, valign="middle"))
        els.append(text(0.10, y + 0.005, 0.85, 0.06, it.get("title", ""),
                        color=theme.heading, font=theme.heading_font, size_pt=16, bold=True))
        els.append(text(0.10, y + 0.065, 0.85, 0.05, it.get("note", ""),
                        color=theme.body, size_pt=12))
    return els


ARCHETYPES = {
    "title": title, "big_picture": big_picture, "why_market": why_market,
    "glossary": glossary, "how_to_read": how_to_read,
    "direction_divider": direction_divider, "order_of_work": order_of_work,
    "right_now": right_now, "after_meeting": after_meeting, "takeaways": takeaways,
}
