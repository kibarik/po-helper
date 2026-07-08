from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Element:
    kind: str                       # "rect" | "text" | "chip"
    fx: float
    fy: float
    fw: float
    fh: float
    text: str = ""
    runs: list[tuple[str, str, bool]] | None = None   # (text, color, bold)
    fill: str | None = None
    color: str | None = None
    font: str | None = None
    size_pt: float | None = None
    bold: bool = False
    align: str = "left"             # left | center | right
    valign: str = "top"             # top | middle
    radius: float = 0.0             # 0..1 fraction of min(fw,fh)


@dataclass
class Slide:
    archetype: str
    elements: list[Element]
    footer: str = ""
    page: int = 0


def text(fx, fy, fw, fh, s="", **kw) -> Element:
    return Element("text", fx, fy, fw, fh, text=s, **kw)


def rect(fx, fy, fw, fh, fill=None, **kw) -> Element:
    return Element("rect", fx, fy, fw, fh, fill=fill, **kw)


def chip(fx, fy, fw, fh, s="", fill=None, **kw) -> Element:
    kw.setdefault("align", "center")
    kw.setdefault("valign", "middle")
    kw.setdefault("bold", True)
    kw.setdefault("radius", 0.18)
    return Element("chip", fx, fy, fw, fh, text=s, fill=fill, **kw)
