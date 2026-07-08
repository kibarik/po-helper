from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class Step:
    role: str
    text: str


@dataclass
class Risk:
    text: str


@dataclass
class KR:
    id: str
    title: str
    now: str | None
    becomes: str | None
    steps: list[Step]
    risks: list[Risk]
    sprint_cells: dict[str, list[str]]
    owners: list[str]
    src: str | None = None


@dataclass
class OBJ:
    id: str
    title: str
    krs: list[KR]


@dataclass
class Direction:
    name: str
    color: str | None
    number: int
    blurb: str
    objs: list[OBJ]


@dataclass
class Authored:
    market: list[dict] = field(default_factory=list)
    quarter_shift: str = ""
    glossary: list[dict] = field(default_factory=list)
    order_of_work: dict = field(default_factory=dict)
    right_now: list[dict] = field(default_factory=list)
    after_meeting: str = ""
    takeaways: list[dict] = field(default_factory=list)


@dataclass
class DeckSpec:
    product: str
    quarter: str
    subtitle: str
    footer: str
    directions: list[Direction]
    authored: Authored


def _kr(d: dict) -> KR:
    return KR(
        id=str(d["id"]),
        title=d["title"],
        now=d.get("now"),
        becomes=d.get("becomes"),
        steps=[Step(s["role"], s["text"]) for s in d.get("steps", [])],
        risks=[Risk(r["text"]) for r in d.get("risks", [])],
        sprint_cells={k: list(v) for k, v in (d.get("sprint_cells") or {}).items()},
        owners=list(d.get("owners", [])),
        src=d.get("src"),
    )


def load_deckspec(path: str | Path) -> DeckSpec:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    directions = [
        Direction(
            name=dd["name"],
            color=dd.get("color"),
            number=dd.get("number", i + 1),
            blurb=dd.get("blurb", ""),
            objs=[OBJ(o["id"], o["title"], [_kr(k) for k in o.get("krs", [])])
                  for o in dd.get("objs", [])],
        )
        for i, dd in enumerate(raw.get("directions", []))
    ]
    a = raw.get("authored", {}) or {}
    authored = Authored(
        market=a.get("market", []),
        quarter_shift=a.get("quarter_shift", ""),
        glossary=a.get("glossary", []),
        order_of_work=a.get("order_of_work", {}),
        right_now=a.get("right_now", []),
        after_meeting=a.get("after_meeting", ""),
        takeaways=a.get("takeaways", []),
    )
    return DeckSpec(
        product=raw["product"], quarter=raw["quarter"],
        subtitle=raw.get("subtitle", ""), footer=raw.get("footer", ""),
        directions=directions, authored=authored,
    )
