from __future__ import annotations
from html import escape
from .layout import Element, Slide
from .theme import Theme

_STAGE_W, _STAGE_H = 1280, 720


def _runs_html(e: Element, theme: Theme) -> str:
    parts = []
    for txt, color, bold in (e.runs or []):
        weight = "700" if bold else "400"
        parts.append(f'<span style="color:{color};font-weight:{weight}">{escape(txt)}</span>')
    return "".join(parts)


def element_html(e: Element, theme: Theme) -> str:
    style = [
        "position:absolute",
        f"left:{e.fx*100:.1f}%", f"top:{e.fy*100:.1f}%",
        f"width:{e.fw*100:.1f}%", f"height:{e.fh*100:.1f}%",
        "box-sizing:border-box", "overflow:hidden",
    ]
    if e.fill:
        style.append(f"background:{e.fill}")
    if e.radius:
        style.append(f"border-radius:{e.radius*min(e.fw*_STAGE_W, e.fh*_STAGE_H):.0f}px")
    if e.kind in ("text", "chip"):
        style.append(f"color:{e.color or theme.body}")
        style.append(f"font-family:'{e.font or theme.body_font}',sans-serif")
        style.append(f"font-size:{(e.size_pt or 12):.1f}pt")
        style.append(f"font-weight:{'700' if e.bold else '400'}")
        style.append(f"text-align:{e.align}")
        style.append("display:flex")
        style.append("flex-direction:column")
        style.append(f"justify-content:{'center' if e.valign=='middle' else 'flex-start'}")
        if e.align == "center":
            style.append("align-items:center")
        elif e.align == "right":
            style.append("align-items:flex-end")
    inner = _runs_html(e, theme) if e.runs else escape(e.text)
    return f'<div style="{";".join(style)}">{inner}</div>'


def render_slide(s: Slide, theme: Theme) -> str:
    body = "".join(element_html(e, theme) for e in s.elements)
    footer = ""
    if s.footer or s.page:
        footer = (
            f'<div class="ftl">{escape(s.footer)}</div>'
            f'<div class="ftr">{s.page}</div>'
        )
    return f'<section class="slide" data-arch="{escape(s.archetype)}">{body}{footer}</section>'


def render_page(slides: list[Slide], theme: Theme, title: str = "Deck") -> str:
    css = f"""
    *{{margin:0;padding:0}}
    body{{background:#3a3f4b;font-family:'{theme.body_font}',sans-serif}}
    .deck{{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px}}
    .slide{{position:relative;width:{_STAGE_W}px;height:{_STAGE_H}px;background:#fff;
      box-shadow:0 8px 30px rgba(0,0,0,.35);overflow:hidden}}
    .ftl{{position:absolute;left:4.2%;bottom:3.5%;color:{theme.muted};font-size:9.5pt}}
    .ftr{{position:absolute;right:4.2%;bottom:3.5%;color:{theme.muted};font-size:9.5pt}}
    @media print{{body{{background:#fff}}.deck{{gap:0;padding:0}}
      .slide{{box-shadow:none;page-break-after:always}}}}
    """
    sections = "".join(render_slide(s, theme) for s in slides)
    return (
        "<!doctype html>\n<html lang=\"ru\"><head><meta charset=\"utf-8\">"
        f"<title>{escape(title)}</title><style>{css}</style></head>"
        f"<body><div class=\"deck\">{sections}</div></body></html>"
    )
