# `/okr-present` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a final quarter stage `/okr-present` to the `okr-planner` skill that renders everything in the vault into an editable HTML deck (correction surface), then finalizes a native `.pptx` deck and a `.xlsx` roadmap.

**Architecture:** A small Python engine under `.claude/skills/okr-planner/resources/engine/`. A canonical `deck-spec.yaml` (vault-anchored) is the single source. Each slide **archetype** is described **once** as a backend-agnostic list of positioned `Element`s (fractions of the slide, 0..1). Two thin backends render those elements — HTML (`<div>`s in a 16:9 stage) and PPTX (python-pptx autoshapes) — so HTML and PPTX are guaranteed pixel-parity from one layout. A third renderer emits the `.xlsx` roadmap from the same spec. The skill command drives phases A–E (collect+audit → author framing → build spec → render HTML → correction loop → finalize pptx/xlsx).

**Tech Stack:** Python 3.11+, `pyyaml`, `python-pptx`, `openpyxl`, `pytest`. No browser dependency (PPTX is native, not screenshot-based).

## Global Constraints

- **Slide geometry:** 16:9, `13.333in × 7.5in` = `12192000 × 6858000` EMU. HTML stage = `1280 × 720` px.
- **Fonts:** headings `Cambria`, body/labels `Calibri` (verbatim from эталон).
- **Theme defaults (verbatim hex from эталон `GDS-Q3-2026.pptx`):** accent `#E4002B`, heading `#1C2333`, body `#434C60`, muted `#8B94A6`, card-bg `#F5F7FB`, direction palette `["#E4002B","#2E4B7A","#0F7A8C","#2F7D54"]`, role→color `{BA:#B37D0C, SA:#B37D0C, ADR:#B37D0C, BE:#2E4B7A, FE:#2E4B7A, QA:#7E56A6, RELEASE:#2F8557, DBA:#0F7A8C}`.
- **Zero hallucination:** every deck-spec fact carries `src:` (vault anchor) or `authored: true`. No source → the value is `[УТОЧНИТЬ]`, never invented.
- **Determinism:** renderers take (spec, theme) only, no network, re-runnable (overwrite outputs).
- **Framework generality:** theme defaults live in code but every value is overridable from `domain-profile.md` `present:` section. The GDS эталон is a fixture/example, never hardcoded into logic.
- **Install deps with:** `python3 -m pip install --break-system-packages pyyaml python-pptx openpyxl pytest`.
- **Commit style:** end each commit message with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

---

## File Structure

```
.claude/skills/okr-planner/
  SKILL.md                              # MODIFY: add /okr-present as final stage
  resources/
    deck_spec_schema.md                 # NEW doc: deck-spec schema + archetype catalog
    theme.md                            # NEW doc: design system reference
    present_gates.md                    # NEW doc: consistency Светофор
    engine/
      __init__.py
      deckspec.py                       # dataclasses + load_deckspec(path)->DeckSpec
      theme.py                          # Theme dataclass + load_theme(profile)->Theme
      layout.py                         # Element dataclass + grid/frac helpers
      archetypes.py                     # render_archetype(name,data,theme)->list[Element]
      backend_html.py                   # elements_to_html + page shell
      backend_pptx.py                   # elements_to_slide + presentation shell
      render_html.py                    # spec+theme -> deck.html  (CLI)
      render_pptx.py                    # spec+theme -> deck.pptx  (CLI)
      render_roadmap.py                 # spec+theme -> roadmap.xlsx (CLI)
      gates.py                          # audit(spec)->TrafficLight
      tests/
        conftest.py                     # fixture: minimal DeckSpec + tmp paths
        fixtures/minimal_deck.yaml
        test_deckspec.py
        test_theme.py
        test_layout.py
        test_backend_html.py
        test_backend_pptx.py
        test_archetypes.py
        test_render_html.py
        test_render_pptx.py
        test_render_roadmap.py
        test_gates.py
  examples/
    ideal_deck_spec.yaml                # NEW: reverse-engineered from GDS-Q3-2026
.claude/commands/
  okr-present.md                        # NEW: command entry (phases A-E)
domain-profile.template.md              # MODIFY: paths + present: section
```

---

### Task 1: Engine scaffold + deck-spec model & loader

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/__init__.py`
- Create: `.claude/skills/okr-planner/resources/engine/deckspec.py`
- Create: `.claude/skills/okr-planner/resources/engine/tests/conftest.py`
- Create: `.claude/skills/okr-planner/resources/engine/tests/fixtures/minimal_deck.yaml`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_deckspec.py`

**Interfaces:**
- Produces: `load_deckspec(path: str|Path) -> DeckSpec`; dataclasses `Step(role,text)`, `Risk(text)`, `KR(id,title,now,becomes,steps,risks,sprint_cells,owners,src)`, `OBJ(id,title,krs)`, `Direction(name,color,number,blurb,objs)`, `Authored(market,quarter_shift,glossary,order_of_work,right_now,after_meeting,takeaways)`, `DeckSpec(product,quarter,subtitle,footer,directions,authored)`. `sprint_cells: dict[str,list[str]]`, `market: list[dict]`, `glossary: list[dict]`.

- [ ] **Step 1: Install deps**

Run: `python3 -m pip install --break-system-packages pyyaml python-pptx openpyxl pytest`
Expected: ends with `Successfully installed` (or "already satisfied").

- [ ] **Step 2a: Create `tests/conftest.py`** (path-only, no engine import at top so it is safe to exist before `deckspec.py`)

```python
import sys
from pathlib import Path
import pytest

# put resources/ on sys.path so `import engine.*` works
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@pytest.fixture
def minimal_spec():
    from engine.deckspec import load_deckspec  # lazy: module created in Step 5
    return load_deckspec(Path(__file__).parent / "fixtures" / "minimal_deck.yaml")
```

- [ ] **Step 2: Create the test fixture** `tests/fixtures/minimal_deck.yaml`

```yaml
product: GDS
quarter: Q3-2026
subtitle: витрина Ticketland
footer: "GDS · Q3 · витрина Ticketland"
directions:
  - name: Надёжный источник
    color: "#E4002B"
    number: 1
    blurb: "Витрина берёт данные из старой базы БАЗИС и падает вместе с ней."
    objs:
      - id: OBJ1
        title: Надёжный источник данных
        krs:
          - id: "1.1"
            title: Продажа мероприятий TicketsCloud на витрине
            now: "Мероприятия продаются через старую базу БАЗИС."
            becomes: "Те же мероприятия продаются напрямую из TicketsCloud."
            steps:
              - {role: SA, text: Исследование коннектора UMC→web_db}
              - {role: BE, text: TicketsCloud → UMC}
              - {role: QA, text: Отладка генерации виджета}
            risks:
              - {text: "Блокер: дедубликация web_db (KR 1.1.E1)"}
            sprint_cells: {S1: [SA·ADR], S2: [BE·Go], S4: [FE·PHP], S5: [QA]}
            owners: [Чеботков, Ананьев]
            src: "OKR-Q3-2026.md#KR-1.1"
authored:
  market:
    - {value: "≈227 млрд ₽", label: "объём билетного рынка РФ", src: "PO-authored"}
  quarter_shift: "уводим витрину со старой базы БАЗИС на TicketsCloud"
  glossary:
    - {term: БАЗИС, plain: "старая билетная база"}
  order_of_work:
    now: ["Докатить кино и рестораны", "Починить критбаги"]
    august: ["★ Продажи TicketsCloud на витрине"]
    later: ["Дешевле Live — исследование"]
  right_now:
    - {title: "Докатить кино на витрину", note: "долг прошлого квартала"}
  after_meeting: "Детальные задачи распишем в JIRA — вместе."
  takeaways:
    - {title: "Всё крутится вокруг витрины Ticketland", note: "4 направления"}
```

- [ ] **Step 3: Write the failing test** `tests/test_deckspec.py`

```python
from pathlib import Path
from engine.deckspec import load_deckspec, DeckSpec, KR

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_loads_top_level():
    spec = load_deckspec(FIX)
    assert isinstance(spec, DeckSpec)
    assert spec.product == "GDS"
    assert spec.quarter == "Q3-2026"
    assert spec.footer == "GDS · Q3 · витрина Ticketland"
    assert len(spec.directions) == 1

def test_nested_kr():
    spec = load_deckspec(FIX)
    kr = spec.directions[0].objs[0].krs[0]
    assert isinstance(kr, KR)
    assert kr.id == "1.1"
    assert kr.now.startswith("Мероприятия")
    assert kr.steps[1].role == "BE"
    assert kr.sprint_cells["S2"] == ["BE·Go"]
    assert kr.owners == ["Чеботков", "Ананьев"]
    assert kr.src == "OKR-Q3-2026.md#KR-1.1"

def test_authored_block():
    spec = load_deckspec(FIX)
    assert spec.authored.market[0]["value"] == "≈227 млрд ₽"
    assert spec.authored.order_of_work["august"][0].startswith("★")
    assert spec.authored.glossary[0]["term"] == "БАЗИС"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_deckspec.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engine.deckspec'`.

- [ ] **Step 5: Create `engine/__init__.py`** (empty file) and **`engine/deckspec.py`**

```python
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
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_deckspec.py -v`
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine
git commit -m "feat(okr-present): deck-spec model + YAML loader

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Theme module + domain-profile merge

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/theme.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_theme.py`

**Interfaces:**
- Produces: `Theme` dataclass (fields: `accent, heading, body, muted, card_bg: str`; `direction_palette: list[str]`; `role_color_map: dict[str,str]`; `heading_font, body_font: str`; `slide_w_in=13.333, slide_h_in=7.5`); `load_theme(present: dict | None = None) -> Theme` merges a domain-profile `present:` dict over defaults; `Theme.role_color(role: str) -> str` returns mapped color or `body`; `Theme.direction_color(index: int) -> str` cycles the palette.

- [ ] **Step 1: Write the failing test** `tests/test_theme.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_theme.py -v`
Expected: FAIL — `No module named 'engine.theme'`.

- [ ] **Step 3: Create `engine/theme.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field

_DEFAULT_PALETTE = ["#E4002B", "#2E4B7A", "#0F7A8C", "#2F7D54"]
_DEFAULT_ROLES = {
    "BA": "#B37D0C", "SA": "#B37D0C", "ADR": "#B37D0C",
    "BE": "#2E4B7A", "FE": "#2E4B7A",
    "QA": "#7E56A6", "RELEASE": "#2F8557", "DBA": "#0F7A8C",
}


@dataclass
class Theme:
    accent: str = "#E4002B"
    heading: str = "#1C2333"
    body: str = "#434C60"
    muted: str = "#8B94A6"
    card_bg: str = "#F5F7FB"
    direction_palette: list[str] = field(default_factory=lambda: list(_DEFAULT_PALETTE))
    role_color_map: dict[str, str] = field(default_factory=lambda: dict(_DEFAULT_ROLES))
    heading_font: str = "Cambria"
    body_font: str = "Calibri"
    slide_w_in: float = 13.333
    slide_h_in: float = 7.5

    def role_color(self, role: str) -> str:
        return self.role_color_map.get(role.strip().upper(), self.body)

    def direction_color(self, index: int) -> str:
        return self.direction_palette[index % len(self.direction_palette)]


_KEYS = {
    "accent_color": "accent", "heading_color": "heading", "body_color": "body",
    "muted_color": "muted", "card_bg": "card_bg",
    "direction_palette": "direction_palette", "heading_font": "heading_font",
    "body_font": "body_font",
}


def load_theme(present: dict | None = None) -> Theme:
    t = Theme()
    if not present:
        return t
    for src_key, attr in _KEYS.items():
        if present.get(src_key):
            setattr(t, attr, present[src_key])
    if present.get("role_color_map"):
        merged = dict(_DEFAULT_ROLES)
        merged.update({k.upper(): v for k, v in present["role_color_map"].items()})
        t.role_color_map = merged
    return t
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_theme.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/theme.py .claude/skills/okr-planner/resources/engine/tests/test_theme.py
git commit -m "feat(okr-present): theme with domain-profile override

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Layout core — Element + fraction helpers

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/layout.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_layout.py`

**Interfaces:**
- Produces: `Element` dataclass (`kind: str` in `{"rect","text","chip"}`; `fx,fy,fw,fh: float` fractions 0..1; `text=""`; `runs: list[tuple[str,str,bool]]|None` = list of `(text,color,bold)`; `fill=None`; `color=None`; `font=None`; `size_pt=None`; `bold=False`; `align="left"`; `valign="top"`; `radius=0.0`); helpers `Slide(archetype:str, elements:list[Element], footer:str, page:int)`; `text(fx,fy,fw,fh,s,**kw)->Element`, `rect(fx,fy,fw,fh,fill,**kw)->Element`, `chip(fx,fy,fw,fh,s,fill,**kw)->Element` factory functions.

- [ ] **Step 1: Write the failing test** `tests/test_layout.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_layout.py -v`
Expected: FAIL — `No module named 'engine.layout'`.

- [ ] **Step 3: Create `engine/layout.py`**

```python
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
    return Element("chip", fx, fy, fw, fh, text=s, fill=fill, **kw)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_layout.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/layout.py .claude/skills/okr-planner/resources/engine/tests/test_layout.py
git commit -m "feat(okr-present): backend-agnostic layout Element

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: HTML backend — elements → self-contained page

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/backend_html.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_backend_html.py`

**Interfaces:**
- Consumes: `Slide`, `Element` (Task 3); `Theme` (Task 2).
- Produces: `render_page(slides: list[Slide], theme: Theme, title: str) -> str` returns a full self-contained HTML document (inline CSS, no external assets); each slide is a `<section class="slide">` sized `1280×720`; elements are absolute-positioned `<div>`s. `element_html(e: Element, theme: Theme) -> str` for unit tests.

- [ ] **Step 1: Write the failing test** `tests/test_backend_html.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_backend_html.py -v`
Expected: FAIL — `No module named 'engine.backend_html'`.

- [ ] **Step 3: Create `engine/backend_html.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_backend_html.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/backend_html.py .claude/skills/okr-planner/resources/engine/tests/test_backend_html.py
git commit -m "feat(okr-present): HTML backend (elements -> self-contained page)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: PPTX backend — elements → native slide

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/backend_pptx.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_backend_pptx.py`

**Interfaces:**
- Consumes: `Slide`, `Element` (Task 3); `Theme` (Task 2).
- Produces: `new_presentation(theme: Theme) -> Presentation` (16:9, blank); `add_slide(prs, s: Slide, theme: Theme) -> None` renders one `Slide` onto a blank layout using native shapes (rect→autoshape, text→textbox, chip→rounded rect + centered text; `runs` become multiple runs in one paragraph).

- [ ] **Step 1: Write the failing test** `tests/test_backend_pptx.py`

```python
from engine.backend_pptx import new_presentation, add_slide
from engine.layout import text, rect, chip, Slide
from engine.theme import load_theme
from pptx.util import Emu

T = load_theme(None)

def test_presentation_is_16_9():
    prs = new_presentation(T)
    assert round(Emu(prs.slide_width).inches, 2) == 13.33
    assert round(Emu(prs.slide_height).inches, 2) == 7.5

def test_add_slide_creates_shapes_with_text():
    prs = new_presentation(T)
    s = Slide("title", [
        rect(0, 0, 1, 1, fill="#141A2E"),
        text(0.1, 0.4, 0.6, 0.1, "КВАРТАЛ GDS", color="#FFFFFF", size_pt=25, bold=True),
        chip(0.1, 0.6, 0.12, 0.05, "BE·Go", fill="#2E4B7A"),
    ], footer="GDS · Q3", page=1)
    add_slide(prs, s, T)
    assert len(prs.slides) == 1
    texts = [sh.text_frame.text for sh in prs.slides[0].shapes if sh.has_text_frame]
    assert any("КВАРТАЛ GDS" in t for t in texts)
    assert any("BE·Go" in t for t in texts)
    assert any("GDS · Q3" in t for t in texts)  # footer drawn

def test_saves_to_disk(tmp_path):
    prs = new_presentation(T)
    add_slide(prs, Slide("t", [text(0, 0, 1, 0.1, "X")], page=1), T)
    out = tmp_path / "d.pptx"
    prs.save(out)
    assert out.exists() and out.stat().st_size > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_backend_pptx.py -v`
Expected: FAIL — `No module named 'engine.backend_pptx'`.

- [ ] **Step 3: Create `engine/backend_pptx.py`**

```python
from __future__ import annotations
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from .layout import Element, Slide
from .theme import Theme

_EMU_W = 12192000
_EMU_H = 6858000
_ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}


def _rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


def new_presentation(theme: Theme) -> Presentation:
    prs = Presentation()
    prs.slide_width = Emu(_EMU_W)
    prs.slide_height = Emu(_EMU_H)
    return prs


def _emu(e: Element):
    return (Emu(int(e.fx * _EMU_W)), Emu(int(e.fy * _EMU_H)),
            Emu(int(e.fw * _EMU_W)), Emu(int(e.fh * _EMU_H)))


def _fill_shape(shape, hexstr):
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(hexstr)
    shape.line.fill.background()


def _write_text(tf, e: Element, theme: Theme):
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(45720)
    tf.margin_top = tf.margin_bottom = Emu(18288)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if e.valign == "middle" else MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = _ALIGN.get(e.align, PP_ALIGN.LEFT)
    runs = e.runs or [(e.text, e.color or theme.body, e.bold)]
    for txt, color, bold in runs:
        r = p.add_run()
        r.text = txt
        r.font.name = e.font or theme.body_font
        r.font.size = Pt(e.size_pt or 12)
        r.font.bold = bold
        r.font.color.rgb = _rgb(color or theme.body)


def add_slide(prs: Presentation, s: Slide, theme: Theme) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    for e in s.elements:
        x, y, w, h = _emu(e)
        if e.kind == "rect":
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if e.radius
                                         else MSO_SHAPE.RECTANGLE, x, y, w, h)
            _fill_shape(shp, e.fill or "#FFFFFF")
            if e.text or e.runs:
                _write_text(shp.text_frame, e, theme)
        elif e.kind == "chip":
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
            _fill_shape(shp, e.fill or theme.card_bg)
            e2 = Element("text", e.fx, e.fy, e.fw, e.fh, text=e.text, runs=e.runs,
                         color=e.color or "#FFFFFF", font=e.font, size_pt=e.size_pt or 9,
                         bold=True, align="center", valign="middle")
            _write_text(shp.text_frame, e2, theme)
        else:  # text
            box = slide.shapes.add_textbox(x, y, w, h)
            _write_text(box.text_frame, e, theme)
    if s.footer or s.page:
        fl = slide.shapes.add_textbox(Emu(int(0.042 * _EMU_W)), Emu(int(0.93 * _EMU_H)),
                                      Emu(int(0.6 * _EMU_W)), Emu(int(0.05 * _EMU_H)))
        _write_text(fl.text_frame, Element("text", 0, 0, 0, 0, text=s.footer,
                                           color=theme.muted, size_pt=9.5), theme)
        fr = slide.shapes.add_textbox(Emu(int(0.9 * _EMU_W)), Emu(int(0.93 * _EMU_H)),
                                      Emu(int(0.06 * _EMU_W)), Emu(int(0.05 * _EMU_H)))
        _write_text(fr.text_frame, Element("text", 0, 0, 0, 0, text=str(s.page),
                                           color=theme.muted, size_pt=9.5, align="right"), theme)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_backend_pptx.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/backend_pptx.py .claude/skills/okr-planner/resources/engine/tests/test_backend_pptx.py
git commit -m "feat(okr-present): native PPTX backend (elements -> shapes)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Archetypes — narrative slides

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/archetypes.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_archetypes.py`

**Interfaces:**
- Consumes: `text, rect, chip, Element` (Task 3); `Theme` (Task 2); `DeckSpec` and children (Task 1).
- Produces: `ARCHETYPES: dict[str, callable]` mapping name → `fn(data: dict, theme: Theme) -> list[Element]`. This task implements the narrative archetypes: `title`, `big_picture`, `why_market`, `glossary`, `how_to_read`, `direction_divider`, `order_of_work`, `right_now`, `after_meeting`, `takeaways`. Each `data` dict is prepared by `render_html.py`/`render_pptx.py` (Task 8/9). A shared `kicker+headline(...)` helper produces the top red kicker + navy headline used on most slides.

- [ ] **Step 1: Write the failing test** `tests/test_archetypes.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_archetypes.py -v`
Expected: FAIL — `No module named 'engine.archetypes'`.

- [ ] **Step 3: Create `engine/archetypes.py`** (narrative archetypes)

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_archetypes.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/archetypes.py .claude/skills/okr-planner/resources/engine/tests/test_archetypes.py
git commit -m "feat(okr-present): narrative slide archetypes

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 7: Archetypes — data tables

**Files:**
- Modify: `.claude/skills/okr-planner/resources/engine/archetypes.py` (append 3 archetypes + register)
- Modify: `.claude/skills/okr-planner/resources/engine/tests/test_archetypes.py` (add tests)

**Interfaces:**
- Produces (added to `ARCHETYPES`): `sprint_lifecycle_table`, `roles_sprint_table`, `now_becomes_detail`. Data shapes: lifecycle `{"kicker","headline","sprints":["S1",...],"rows":[{"label":str,"cells":{"S1":["SA·ADR"],...}}],"owners":str}`; roles `{"kicker","headline","sprints":[...],"rows":[{"role","expertise","people","cells":{"S1":"1.1"}}],"note"}`; detail `{"kicker","title","now","becomes","stages":[{"label","steps":[{"role","text"}]}],"risks":[str]}`. Chip fill = `theme.role_color(first_role_token)`.

- [ ] **Step 1: Add failing tests** (append to `tests/test_archetypes.py`)

```python
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
```

- [ ] **Step 2: Run to verify new tests fail**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_archetypes.py -k "table or detail" -v`
Expected: FAIL — `KeyError: 'sprint_lifecycle_table'`.

- [ ] **Step 3: Append archetypes to `engine/archetypes.py`** (before the `ARCHETYPES = {...}` dict, then add keys)

```python
def _first_role(cell_text: str) -> str:
    # "SA·ADR" or "BE·Go" -> "SA" / "BE"
    return cell_text.split("·")[0].strip()


def sprint_lifecycle_table(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    els.append(text(0.042, 0.20, 0.916, 0.05,
                    "Каждая строка — шаг направления; слева направо — жизненный цикл.",
                    color=theme.body, size_pt=11))
    sprints = data.get("sprints", [])
    rows = data.get("rows", [])
    lx, top = 0.042, 0.28
    label_w = 0.30
    grid_w = 1 - 2 * 0.042 - label_w
    n = len(sprints) or 1
    col_w = grid_w / n
    # header
    for j, sp in enumerate(sprints):
        els.append(text(lx + label_w + j * col_w, top, col_w, 0.04, sp,
                        color=theme.muted, size_pt=10, bold=True, align="center"))
    row_h = min(0.075, (0.60 - top) / (len(rows) or 1))
    for i, r in enumerate(rows):
        y = top + 0.05 + i * row_h
        els.append(text(lx, y, label_w - 0.01, row_h, r.get("label", ""),
                        color=theme.heading, size_pt=11, bold=True, valign="middle"))
        for j, sp in enumerate(sprints):
            for k, cellval in enumerate(r.get("cells", {}).get(sp, [])):
                cx = lx + label_w + j * col_w + 0.004
                els.append(chip(cx, y + 0.006 + k * 0.032, col_w - 0.008, 0.028, cellval,
                                fill=theme.role_color(_first_role(cellval)),
                                color="#FFFFFF", size_pt=8))
    if data.get("owners"):
        els.append(text(0.042, 0.85, 0.916, 0.06, "ОТВЕТСТВЕННЫЕ",
                        color=theme.accent, size_pt=10, bold=True))
        els.append(text(0.042, 0.885, 0.916, 0.06, data["owners"],
                        color=theme.body, size_pt=10))
    return els


def roles_sprint_table(data: dict, theme: Theme) -> list[Element]:
    els = _kicker_headline(data, theme)
    sprints = data.get("sprints", [])
    rows = data.get("rows", [])
    lx, top = 0.042, 0.26
    label_w = 0.26
    grid_w = 1 - 2 * 0.042 - label_w
    n = len(sprints) or 1
    col_w = grid_w / n
    els.append(text(lx, top, label_w, 0.04, "ЭКСПЕРТИЗА И ЛЮДИ",
                    color=theme.muted, size_pt=10, bold=True))
    for j, sp in enumerate(sprints):
        els.append(text(lx + label_w + j * col_w, top, col_w, 0.04, sp,
                        color=theme.muted, size_pt=10, bold=True, align="center"))
    row_h = min(0.09, (0.80 - top) / (len(rows) or 1))
    for i, r in enumerate(rows):
        y = top + 0.05 + i * row_h
        els.append(rect(lx, y, 0.05, row_h - 0.01, fill=theme.role_color(r.get("role", "")),
                        radius=0.1))
        els.append(text(lx, y, 0.05, row_h - 0.01, r.get("role", ""), color="#FFFFFF",
                        size_pt=10, bold=True, align="center", valign="middle"))
        els.append(text(lx + 0.055, y, label_w - 0.06, row_h - 0.01,
                        f"{r.get('expertise','')} · {r.get('people','')}",
                        color=theme.heading, size_pt=9, valign="middle"))
        for j, sp in enumerate(sprints):
            cv = r.get("cells", {}).get(sp)
            if cv:
                els.append(text(lx + label_w + j * col_w, y, col_w, row_h - 0.01, cv,
                                color=theme.body, size_pt=9, align="center", valign="middle"))
    if data.get("note"):
        els.append(text(0.042, 0.86, 0.916, 0.05, data["note"], color=theme.muted, size_pt=11))
    return els


def now_becomes_detail(data: dict, theme: Theme) -> list[Element]:
    els = [
        text(0.042, 0.06, 0.9, 0.04, data.get("kicker", ""), color=theme.accent,
             size_pt=12, bold=True),
        text(0.042, 0.11, 0.9, 0.07, data.get("title", ""), color=theme.heading,
             font=theme.heading_font, size_pt=22, bold=True),
        text(0.042, 0.20, 0.55, 0.05, "", color=theme.body, size_pt=12.5,
             runs=[("СЕЙЧАС  ", theme.muted, True), (data.get("now", ""), theme.body, False)]),
        text(0.042, 0.26, 0.55, 0.05, "", color=theme.heading, size_pt=12.5,
             runs=[("СТАНЕТ  ", "#2F7D54", True), (data.get("becomes", ""), theme.heading, False)]),
        text(0.042, 0.34, 0.55, 0.04, "ОБРАЗ ДЕЙСТВИЯ", color=theme.accent, size_pt=11, bold=True),
    ]
    y = 0.40
    for st in data.get("stages", [])[:4]:
        els.append(text(0.042, y, 0.55, 0.035, st.get("label", ""),
                        color=theme.heading, size_pt=11, bold=True))
        y += 0.045
        for step in st.get("steps", [])[:5]:
            els.append(text(0.055, y, 0.53, 0.03, "", size_pt=9,
                            runs=[(step.get("role", "") + "  ", theme.role_color(step.get("role", "")), True),
                                  (step.get("text", ""), theme.body, False)]))
            y += 0.032
        y += 0.005
    # risks column
    els.append(text(0.62, 0.34, 0.35, 0.04, "РИСКИ", color=theme.accent, size_pt=11, bold=True))
    for i, rk in enumerate(data.get("risks", [])[:8]):
        ry = 0.40 + i * 0.06
        els.append(rect(0.62, ry + 0.004, 0.012, 0.012, fill=theme.accent, radius=0.5))
        els.append(text(0.64, ry, 0.33, 0.055, rk, color=theme.body, size_pt=8.5))
    return els
```

Then extend the registry:

```python
ARCHETYPES.update({
    "sprint_lifecycle_table": sprint_lifecycle_table,
    "roles_sprint_table": roles_sprint_table,
    "now_becomes_detail": now_becomes_detail,
})
```

- [ ] **Step 4: Run all archetype tests**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_archetypes.py -v`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/archetypes.py .claude/skills/okr-planner/resources/engine/tests/test_archetypes.py
git commit -m "feat(okr-present): data-table archetypes (lifecycle/roles/detail)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: `render_html.py` — spec → deck.html (orchestrator + CLI)

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/build_slides.py` (spec → `list[Slide]`)
- Create: `.claude/skills/okr-planner/resources/engine/render_html.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_render_html.py`

**Interfaces:**
- Consumes: `load_deckspec` (T1), `load_theme` (T2), `ARCHETYPES` (T6/7), `render_page` (T4), `Slide` (T3).
- Produces: `build_slides(spec: DeckSpec, theme: Theme) -> list[Slide]` — maps the spec into the ordered deck (title → big_picture → why_market → glossary → how_to_read → per-direction[divider → sprint_lifecycle_table → roles_sprint_table → now_becomes_detail per KR] → order_of_work → right_now → after_meeting → takeaways), assigning `page` numbers and `footer`. `render_html_file(spec_path, out_path, profile=None) -> Path`. CLI: `python -m engine.render_html <spec.yaml> <out.html>`.

- [ ] **Step 1: Write the failing test** `tests/test_render_html.py`

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_html.py -v`
Expected: FAIL — `No module named 'engine.build_slides'`.

- [ ] **Step 3: Create `engine/build_slides.py`**

```python
from __future__ import annotations
from .deckspec import DeckSpec, Direction
from .theme import Theme
from .archetypes import ARCHETYPES
from .layout import Slide

_LIFECYCLE_STAGES = ["Дизайн и данные", "Разработка", "Отладка и выкатка"]


def _kr_detail_data(kr) -> dict:
    # group образ действия steps into a single "stages" block (simple: one stage)
    stages = [{"label": "Образ действия", "steps": [{"role": s.role, "text": s.text}
                                                    for s in kr.steps]}]
    return {"kicker": f"KR {kr.id}", "title": kr.title,
            "now": kr.now or "[УТОЧНИТЬ]", "becomes": kr.becomes or "[УТОЧНИТЬ]",
            "stages": stages, "risks": [r.text for r in kr.risks]}


def _lifecycle_rows(direction: Direction) -> list[dict]:
    rows = []
    for obj in direction.objs:
        for kr in obj.krs:
            rows.append({"label": kr.title, "cells": kr.sprint_cells})
    return rows


def _collect_sprints(spec: DeckSpec) -> list[str]:
    seen = []
    for d in spec.directions:
        for o in d.objs:
            for kr in o.krs:
                for sp in kr.sprint_cells:
                    if sp not in seen:
                        seen.append(sp)
    return sorted(seen, key=lambda s: int(s.lstrip("S") or 0))


def build_slides(spec: DeckSpec, theme: Theme) -> list[Slide]:
    sprints = _collect_sprints(spec)
    plan: list[tuple[str, dict]] = []

    plan.append(("title", {"kicker": f"КВАРТАЛ {spec.product} · {spec.quarter}",
                           "headline": f"Что мы делаем\nс {spec.subtitle}",
                           "sub": "Общая картина квартала простым языком."}))
    cards = [{"n": d.number, "title": d.name,
              "note": d.blurb, "color": d.color or theme.direction_color(i)}
             for i, d in enumerate(spec.directions)]
    plan.append(("big_picture", {"kicker": "ОБЩАЯ КАРТИНА",
                                 "headline": "Что мы делаем в этом квартале", "cards": cards}))
    if spec.authored.market:
        plan.append(("why_market", {"kicker": "ЗАЧЕМ ЭТО ВСЁ", "headline": "Контекст рынка",
                                    "stats": spec.authored.market,
                                    "shift": spec.authored.quarter_shift}))
    if spec.authored.glossary:
        plan.append(("glossary", {"kicker": "СЛОВАРЬ", "headline": "Что есть что — простыми словами",
                                  "terms": spec.authored.glossary}))
    plan.append(("how_to_read", {"kicker": "КАК ЧИТАТЬ ДАЛЬШЕ",
                                 "headline": "По одной задаче на слайд: что сейчас и что станет",
                                 "footnote": "Как устроено внутри — здесь не разбираем. Только результат."}))

    for i, d in enumerate(spec.directions):
        color = d.color or theme.direction_color(i)
        plan.append(("direction_divider", {"number": f"{d.number:02d}", "kicker": "НАПРАВЛЕНИЕ",
                                            "title": d.name, "blurb": d.blurb, "color": color}))
        plan.append(("sprint_lifecycle_table",
                     {"kicker": f"НАПРАВЛЕНИЕ {d.number} · КАК РАБОТАЕМ",
                      "headline": "Как двигаемся по спринтам", "sprints": sprints,
                      "rows": _lifecycle_rows(d), "owners": ""}))
        for obj in d.objs:
            for kr in obj.krs:
                plan.append(("now_becomes_detail", _kr_detail_data(kr)))

    if spec.authored.order_of_work:
        plan.append(("order_of_work", {"kicker": "КАК ДВИГАЕМСЯ", "headline": "Порядок работ",
                                       "order": spec.authored.order_of_work}))
    if spec.authored.right_now:
        plan.append(("right_now", {"kicker": "ПРЯМО СЕЙЧАС", "headline": "Что делаем в первую очередь",
                                   "items": spec.authored.right_now}))
    if spec.authored.after_meeting:
        plan.append(("after_meeting", {"kicker": "ЧТО ПОСЛЕ ЭТОЙ ВСТРЕЧИ",
                                       "headline": "Детальные задачи распишем в JIRA",
                                       "body": spec.authored.after_meeting}))
    if spec.authored.takeaways:
        plan.append(("takeaways", {"kicker": "ЧТО ЗАПОМНИТЬ", "headline": "Главное",
                                   "items": spec.authored.takeaways}))

    slides: list[Slide] = []
    page = 0
    for name, data in plan:
        els = ARCHETYPES[name](data, theme)
        if name == "title":
            slides.append(Slide(name, els, footer="", page=0))
        else:
            page += 1
            slides.append(Slide(name, els, footer=spec.footer, page=page))
    return slides
```

- [ ] **Step 4: Create `engine/render_html.py`**

```python
from __future__ import annotations
import sys
from pathlib import Path
from .deckspec import load_deckspec
from .theme import load_theme
from .build_slides import build_slides
from .backend_html import render_page


def render_html_file(spec_path, out_path, profile: dict | None = None) -> Path:
    spec = load_deckspec(spec_path)
    theme = load_theme((profile or {}).get("present"))
    slides = build_slides(spec, theme)
    doc = render_page(slides, theme, title=f"{spec.product} · {spec.quarter}")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


if __name__ == "__main__":
    render_html_file(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]}")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_html.py -v`
Expected: 2 passed.

- [ ] **Step 6: Manual smoke — open the HTML**

Run: `cd .claude/skills/okr-planner/resources && python3 -m engine.render_html engine/tests/fixtures/minimal_deck.yaml /tmp/deck_smoke.html && python3 -c "print(Path('/tmp/deck_smoke.html').stat().st_size)" 2>/dev/null; wc -c /tmp/deck_smoke.html`
Expected: a non-trivial byte count (> 3000).

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/build_slides.py .claude/skills/okr-planner/resources/engine/render_html.py .claude/skills/okr-planner/resources/engine/tests/test_render_html.py
git commit -m "feat(okr-present): spec->slides mapping + HTML renderer CLI

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: `render_pptx.py` — spec → deck.pptx (CLI)

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/render_pptx.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_render_pptx.py`

**Interfaces:**
- Consumes: `build_slides` (T8), `new_presentation`/`add_slide` (T5), `load_deckspec`/`load_theme`.
- Produces: `render_pptx_file(spec_path, out_path, profile=None) -> Path`. CLI: `python -m engine.render_pptx <spec.yaml> <out.pptx>`.

- [ ] **Step 1: Write the failing test** `tests/test_render_pptx.py`

```python
from pathlib import Path
from engine.render_pptx import render_pptx_file
from pptx import Presentation

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_render_pptx_file(tmp_path):
    out = render_pptx_file(FIX, tmp_path / "deck.pptx")
    assert out.exists()
    prs = Presentation(str(out))
    assert len(prs.slides) >= 6   # title + big_picture + glossary + divider + lifecycle + detail + closings
    all_text = " ".join(sh.text_frame.text for sl in prs.slides
                        for sh in sl.shapes if sh.has_text_frame)
    assert "Продажа мероприятий TicketsCloud" in all_text
    assert "БАЗИС" in all_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_pptx.py -v`
Expected: FAIL — `No module named 'engine.render_pptx'`.

- [ ] **Step 3: Create `engine/render_pptx.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_pptx.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/render_pptx.py .claude/skills/okr-planner/resources/engine/tests/test_render_pptx.py
git commit -m "feat(okr-present): native PPTX renderer CLI

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 10: `render_roadmap.py` — spec → roadmap.xlsx

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/render_roadmap.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_render_roadmap.py`

**Interfaces:**
- Consumes: `load_deckspec`, `load_theme`, `_collect_sprints` (import from `build_slides`).
- Produces: `render_roadmap_file(spec_path, out_path, profile=None) -> Path`. Sheet `Roadmap {quarter}`: row 1 sprint headers (`S1 … Sn`), then per direction a bold header row spanning the initiatives, then one row per KR with its `sprint_cells` chips written into the matching sprint column (joined by `\n`). A legend block at the bottom (phase legend + stack note). CLI: `python -m engine.render_roadmap <spec.yaml> <out.xlsx>`.

- [ ] **Step 1: Write the failing test** `tests/test_render_roadmap.py`

```python
from pathlib import Path
from engine.render_roadmap import render_roadmap_file
from openpyxl import load_workbook

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_roadmap_structure(tmp_path):
    out = render_roadmap_file(FIX, tmp_path / "roadmap.xlsx")
    assert out.exists()
    wb = load_workbook(out)
    ws = wb.active
    assert ws.title.startswith("Roadmap")
    values = [str(c.value) for row in ws.iter_rows() for c in row if c.value]
    assert any("Надёжный источник" in v for v in values)     # direction header
    assert any("Продажа мероприятий" in v for v in values)   # KR row
    assert any("S1" in v for v in values)                     # sprint header
    assert any("SA·ADR" in v for v in values)                 # chip content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_roadmap.py -v`
Expected: FAIL — `No module named 'engine.render_roadmap'`.

- [ ] **Step 3: Create `engine/render_roadmap.py`**

```python
from __future__ import annotations
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from .deckspec import load_deckspec
from .theme import load_theme
from .build_slides import _collect_sprints


def _hexfill(theme_hex: str) -> PatternFill:
    h = theme_hex.lstrip("#").upper()
    return PatternFill("solid", fgColor=h)


def render_roadmap_file(spec_path, out_path, profile: dict | None = None) -> Path:
    spec = load_deckspec(spec_path)
    theme = load_theme((profile or {}).get("present"))
    sprints = _collect_sprints(spec)
    wb = Workbook()
    ws = wb.active
    ws.title = f"Roadmap {spec.quarter}"[:31]
    wrap = Alignment(wrap_text=True, vertical="center", horizontal="center")

    # header row
    ws.cell(1, 1, "Инициативы в квартале").font = Font(bold=True)
    for j, sp in enumerate(sprints):
        c = ws.cell(1, 2 + j, sp)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = _hexfill(theme.heading)
        c.alignment = wrap
    ws.column_dimensions["A"].width = 46
    for j in range(len(sprints)):
        ws.column_dimensions[chr(ord("B") + j)].width = 12

    r = 2
    for i, d in enumerate(spec.directions):
        hc = ws.cell(r, 1, d.name)
        hc.font = Font(bold=True, color="FFFFFF")
        hc.fill = _hexfill(d.color or theme.direction_color(i))
        for j in range(len(sprints)):
            ws.cell(r, 2 + j).fill = hc.fill
        r += 1
        for obj in d.objs:
            for kr in obj.krs:
                ws.cell(r, 1, kr.title).alignment = Alignment(wrap_text=True, vertical="center")
                for j, sp in enumerate(sprints):
                    cells = kr.sprint_cells.get(sp, [])
                    if cells:
                        cc = ws.cell(r, 2 + j, "\n".join(cells))
                        cc.alignment = wrap
                        cc.font = Font(size=9)
                r += 1

    r += 1
    ws.cell(r, 1, "Легенда фаз: Аналитика (BA/SA/ADR/PO) · Разработка (BE/FE) · "
                  "Отладка (QA) · Релиз (RM)").font = Font(italic=True, size=9)
    ws.cell(r + 1, 1, "S1 закоммичен из спринт-плана; далее — ориентировочно.").font = \
        Font(italic=True, size=9, color="8B94A6")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out))
    return out


if __name__ == "__main__":
    render_roadmap_file(sys.argv[1], sys.argv[2])
    print(f"wrote {sys.argv[2]}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_render_roadmap.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/render_roadmap.py .claude/skills/okr-planner/resources/engine/tests/test_render_roadmap.py
git commit -m "feat(okr-present): roadmap xlsx renderer

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: `gates.py` — consistency Светофор

**Files:**
- Create: `.claude/skills/okr-planner/resources/engine/gates.py`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_gates.py`

**Interfaces:**
- Consumes: `DeckSpec` and children (T1).
- Produces: `audit(spec: DeckSpec) -> Report` where `Report(level: str in {"🔴","🟡","🟢"}, red: list[str], yellow: list[str])`. Red conditions: KR with no `now` or no `becomes`; a KR whose `sprint_cells` is empty (no owner/lifecycle presence); OBJ not under any direction is impossible by structure so skip; market stat with no `src`. Yellow: risk-less KR; sprint cell chip without a `·stack` suffix; glossary empty while deck uses jargon (approx: yellow if `glossary` empty). `format_report(report) -> str` for console.

- [ ] **Step 1: Write the failing test** `tests/test_gates.py`

```python
from engine.gates import audit
from engine.deckspec import load_deckspec
from pathlib import Path
import copy

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_clean_spec_is_green_or_yellow(minimal_spec):
    rep = audit(minimal_spec)
    assert rep.level in ("🟢", "🟡")
    assert rep.red == []

def test_missing_becomes_is_red(minimal_spec):
    spec = copy.deepcopy(minimal_spec)
    spec.directions[0].objs[0].krs[0].becomes = None
    rep = audit(spec)
    assert rep.level == "🔴"
    assert any("becomes" in m or "СТАНЕТ" in m for m in rep.red)

def test_market_without_src_is_red(minimal_spec):
    spec = copy.deepcopy(minimal_spec)
    spec.authored.market = [{"value": "100", "label": "x"}]  # no src
    rep = audit(spec)
    assert rep.level == "🔴"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_gates.py -v`
Expected: FAIL — `No module named 'engine.gates'`.

- [ ] **Step 3: Create `engine/gates.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from .deckspec import DeckSpec


@dataclass
class Report:
    level: str
    red: list[str] = field(default_factory=list)
    yellow: list[str] = field(default_factory=list)


def audit(spec: DeckSpec) -> Report:
    red, yellow = [], []
    for d in spec.directions:
        for obj in d.objs:
            for kr in obj.krs:
                tag = f"KR {kr.id}"
                if not kr.now:
                    red.append(f"{tag}: нет СЕЙЧАС (now)")
                if not kr.becomes:
                    red.append(f"{tag}: нет СТАНЕТ (becomes)")
                if not kr.sprint_cells:
                    red.append(f"{tag}: нет ни одной sprint-ячейки (нет исполнителя/цикла)")
                if not kr.risks:
                    yellow.append(f"{tag}: без рисков")
                for sp, cells in kr.sprint_cells.items():
                    for c in cells:
                        if "·" not in c:
                            yellow.append(f"{tag} {sp}: чип '{c}' без стека")
    for m in spec.authored.market:
        if not m.get("src"):
            red.append(f"Рыночное число '{m.get('value','?')}' без источника")
    if not spec.authored.glossary:
        yellow.append("Пустой глоссарий")
    level = "🔴" if red else ("🟡" if yellow else "🟢")
    return Report(level=level, red=red, yellow=yellow)


def format_report(rep: Report) -> str:
    lines = [f"Светофор консистентности: {rep.level}"]
    for m in rep.red:
        lines.append(f"  🔴 {m}")
    for m in rep.yellow:
        lines.append(f"  🟡 {m}")
    if not rep.red and not rep.yellow:
        lines.append("  всё покрыто")
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_gates.py -v`
Expected: 3 passed.

- [ ] **Step 5: Run the FULL engine suite**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests -v`
Expected: all pass (deckspec 3 + theme 4 + layout 3 + backend_html 4 + backend_pptx 3 + archetypes 9 + render_html 2 + render_pptx 1 + render_roadmap 1 + gates 3 = 33 passed).

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/okr-planner/resources/engine/gates.py .claude/skills/okr-planner/resources/engine/tests/test_gates.py
git commit -m "feat(okr-present): consistency gates (Светофор)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 12: Resource docs — schema, theme, gates references

**Files:**
- Create: `.claude/skills/okr-planner/resources/deck_spec_schema.md`
- Create: `.claude/skills/okr-planner/resources/theme.md`
- Create: `.claude/skills/okr-planner/resources/present_gates.md`

These are reference docs the command reads; no unit tests. Content must match the code from Tasks 1–11 exactly (field names, archetype names, hex values).

- [ ] **Step 1: Write `resources/deck_spec_schema.md`**

Document: the YAML top-level keys (`product, quarter, subtitle, footer, directions[], authored{}`), the nested `Direction/OBJ/KR/Step/Risk` shapes with every field from `deckspec.py`, the `sprint_cells` format (`{S1: ["SA·ADR", ...]}`), the `authored` sub-keys (`market[], quarter_shift, glossary[], order_of_work{now,august,later}, right_now[], after_meeting, takeaways[]`), and the rule "each fact carries `src:` or `authored: true`". Then the **archetype catalog** — the 13 names from `ARCHETYPES` with a one-line description and the `data` dict each expects (copy shapes from Task 6/7 interfaces). End with the slide ORDER produced by `build_slides` (Task 8).

- [ ] **Step 2: Write `resources/theme.md`**

Document the `present:` profile keys and their defaults (copy the exact hex table from Global Constraints), the role→color map, fonts, slide geometry, and the parity note: "HTML and PPTX render the same `Element` layout; theme is the single visual contract." State that empty profile → эталон defaults.

- [ ] **Step 3: Write `resources/present_gates.md`**

Document the Светофор from `gates.py`: 🔴 conditions (KR without now/becomes, KR with no sprint cells, market number without src), 🟡 conditions (KR without risks, chip without stack, empty glossary), 🟢. Note it prints in phase A and again before D2.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/okr-planner/resources/deck_spec_schema.md .claude/skills/okr-planner/resources/theme.md .claude/skills/okr-planner/resources/present_gates.md
git commit -m "docs(okr-present): deck-spec schema, theme, gates references

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 13: `examples/ideal_deck_spec.yaml` + integration smoke

**Files:**
- Create: `.claude/skills/okr-planner/examples/ideal_deck_spec.yaml`
- Test: `.claude/skills/okr-planner/resources/engine/tests/test_integration.py`

**Interfaces:** none new — validates the whole engine end-to-end on a realistic multi-direction spec reverse-engineered from `GDS-Q3-2026.pptx`.

- [ ] **Step 1: Write `examples/ideal_deck_spec.yaml`**

Reverse-engineer from the эталон content already extracted: 4 directions (Надёжный источник / Больше на витрине / Стабильность / Дешевле Live) with the palette colors, each with its KRs (1.1, 1.2, 2.1/2.2/2.4/2.5/2.6, 3.3/3.4/3.5, 4.1/4.2/4.3), `now/becomes` from the СЕЙЧАС/СТАНЕТ slides, `steps` from ОБРАЗ ДЕЙСТВИЯ, `risks` from РИСКИ, `sprint_cells` from the lifecycle tables, `owners` from ОТВЕТСТВЕННЫЕ, and the `authored` block (market ≈227 млрд/64%/топ-3, glossary 6 terms, order_of_work, right_now 4, takeaways 4). Every KR gets a `src:` like `OKR-Q3-2026.md#KR-1.1`. Keep it faithful but it need not be 100% complete — it is an example/fixture.

- [ ] **Step 2: Write the integration test** `tests/test_integration.py`

```python
from pathlib import Path
from engine.render_html import render_html_file
from engine.render_pptx import render_pptx_file
from engine.render_roadmap import render_roadmap_file
from engine.deckspec import load_deckspec
from engine.gates import audit
from pptx import Presentation

IDEAL = Path(__file__).resolve().parents[3] / "examples" / "ideal_deck_spec.yaml"

def test_ideal_spec_loads_and_audits():
    spec = load_deckspec(IDEAL)
    assert len(spec.directions) == 4
    rep = audit(spec)
    assert rep.red == [], f"unexpected red gates: {rep.red}"

def test_end_to_end_three_artifacts(tmp_path):
    html = render_html_file(IDEAL, tmp_path / "deck.html")
    pptx = render_pptx_file(IDEAL, tmp_path / "deck.pptx")
    xlsx = render_roadmap_file(IDEAL, tmp_path / "roadmap.xlsx")
    assert html.exists() and pptx.exists() and xlsx.exists()
    prs = Presentation(str(pptx))
    assert len(prs.slides) >= 20   # эталон-scale deck
    assert "http://" not in html.read_text(encoding="utf-8")
```

- [ ] **Step 3: Run integration test**

Run: `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests/test_integration.py -v`
Expected: 2 passed. (If `test_ideal_spec_loads_and_audits` reports red gates, fix the YAML — the gate is doing its job.)

- [ ] **Step 4: Manual eyeball**

Run: `cd .claude/skills/okr-planner/resources && python3 -m engine.render_html ../examples/ideal_deck_spec.yaml /tmp/ideal_deck.html && open /tmp/ideal_deck.html`
Expected: browser shows the multi-direction deck; compare structure to `GDS-Q3-2026.pptx`. Note visual deltas for later polish (not blocking).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/okr-planner/examples/ideal_deck_spec.yaml .claude/skills/okr-planner/resources/engine/tests/test_integration.py
git commit -m "test(okr-present): ideal deck-spec fixture + end-to-end integration

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 14: `/okr-present` command + SKILL.md pipeline update

**Files:**
- Create: `.claude/commands/okr-present.md`
- Modify: `.claude/skills/okr-planner/SKILL.md` (add final stage to the pipeline + roles table + resources list)

No unit tests (markdown instructions). Validation = the command reads correctly and references real paths/scripts.

- [ ] **Step 1: Write `.claude/commands/okr-present.md`**

Front-matter `description:` line (mirror sibling commands like `okr-deliver.md`). Body sections:
- **Использование:** `/okr-present <quarter>`; inputs = all vault (`{okr_output_doc}`, `{sprint_roadmap_doc}`, `{sprint_output_doc}` per sprint, `{kr_epic_map_doc}`, `landscape-{quarter}.md`, `GROUND/NEXUS/team/*`, `domain-profile`); outputs = `{quarter_deck_html}` then `{quarter_deck_doc}` + `{quarter_roadmap_xlsx}`.
- **Важно:** роль Quarter Storyteller + Consistency Auditor; модель vault→render; HTML — поверхность правок; финал pptx после «принято».
- **Инструкция для LLM (фазы A–E):**
  - **A · Сбор + аудит:** прочитать `SKILL.md`, `resources/deck_spec_schema.md`, `resources/present_gates.md`; собрать данные из vault; заполнить `deck-spec.yaml` (каждый факт с `src:`); прогнать `python3 -m engine.gates` (or call `audit`) → распечатать Светофор; 🔴 → СТОП, вернуть PO. Artifact: `{deck_spec_doc}`.
  - **B · Доавторинг рамки:** опрос PO по одному вопросу (направления+цвета, рынок+источник, глоссарий, order_of_work/right_now/takeaways); дописать `authored:` в spec (`authored: true`). STOP.
  - **C · deck-spec dry-run:** показать перечень слайдов (`build_slides` order) + якоря; STOP.
  - **D1 · Рендер HTML:** `cd .claude/skills/okr-planner/resources && python3 -m engine.render_html {deck_spec_doc} {quarter_deck_html}`; предложить открыть/опубликовать как Artifact. STOP.
  - **E · Коррекция:** PO называет правки → факт в vault→spec, рамка в spec, вёрстка в theme → перезапустить D1. Цикл до «принято».
  - **D2 · Финализация:** `python3 -m engine.render_pptx …` + `python3 -m engine.render_roadmap …`; повторный Светофор; коммит артефактов. STOP.
- **Гигиена:** артефакты под git в `{planning_root}/presentation/`, не в tmp/worktree; трекер не трогаем (read-only).

Copy the exact command invocations above verbatim into the file.

- [ ] **Step 2: Update `SKILL.md`** — add the stage to the Pipeline block and the roles/artifacts table

In the `## Pipeline` fenced diagram, after `/okr-grooming`, append:
```
─────────── Финал квартала ───────────
/okr-present <quarter> → deck.html (поверхность правок) → .pptx + Roadmap.xlsx
        (собирает весь vault · линза консистентности · принято = AI↔PO выровнены)
```
In the "Роли и артефакты" table add a row:
```
| Финал | /okr-present | Quarter Storyteller + Consistency Auditor | {quarter_deck_html} → {quarter_deck_doc} + {quarter_roadmap_xlsx} |
```
In the resources list (near bottom of SKILL.md) add:
```
- resources/deck_spec_schema.md — схема deck-spec + каталог архетипов слайдов.
- resources/theme.md — дизайн-система (общая HTML/PPTX; дефолт = эталон).
- resources/present_gates.md — Светофор консистентности презентации.
- resources/engine/ — рендер-движок (deckspec/theme/layout/archetypes + render_html/pptx/roadmap).
- examples/ideal_deck_spec.yaml — эталонная deck-spec (реверс из GDS-Q3-2026).
```

- [ ] **Step 3: Sanity check the command references resolve**

Run: `cd .claude/skills/okr-planner/resources && python3 -m engine.render_html engine/tests/fixtures/minimal_deck.yaml /tmp/cmd_check.html && echo OK`
Expected: prints `wrote /tmp/cmd_check.html` then `OK` (confirms the exact CLI the command tells the LLM to run works).

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/okr-present.md .claude/skills/okr-planner/SKILL.md
git commit -m "feat(okr-present): /okr-present command + okr-planner pipeline stage

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 15: `domain-profile.template.md` — paths + present section

**Files:**
- Modify: `domain-profile.template.md` (add to `paths:` and a new `present:` block)

- [ ] **Step 1: Add paths** under the existing `paths:` section (after `sprint_fact_doc`)

```yaml
  # Финал квартала (/okr-present)
  deck_spec_doc:        "{okr_workspace}/present/deck-spec.yaml"
  quarter_deck_html:    "{planning_root}/presentation/{product}-{quarter}.html"
  quarter_deck_doc:     "{planning_root}/presentation/{product}-{quarter}.pptx"
  quarter_roadmap_xlsx: "{planning_root}/presentation/Roadmap-{product}-{quarter}.xlsx"
```

- [ ] **Step 2: Add the `present:` block** (near the other config sections, e.g. after `capacity:`)

```yaml
# Дизайн-система презентации квартала (/okr-present). Пусто → дефолты эталона.
present:
  product_display_name: ""            # дефолт: profile.product
  footer_subtitle:      ""            # напр. «витрина Ticketland»
  accent_color:         "#E4002B"
  heading_color:        "#1C2333"
  body_color:           "#434C60"
  muted_color:          "#8B94A6"
  card_bg:              "#F5F7FB"
  heading_font:         "Cambria"
  body_font:            "Calibri"
  direction_palette:    ["#E4002B", "#2E4B7A", "#0F7A8C", "#2F7D54"]
  role_color_map:
    SA: "#B37D0C"
    ADR: "#B37D0C"
    BA: "#B37D0C"
    BE: "#2E4B7A"
    FE: "#2E4B7A"
    QA: "#7E56A6"
    RELEASE: "#2F8557"
    DBA: "#0F7A8C"
```

- [ ] **Step 3: Verify the keys match `theme.load_theme`**

Run: `cd .claude/skills/okr-planner/resources && python3 -c "
from engine.theme import load_theme
p = {'accent_color':'#111111','role_color_map':{'QA':'#222222'}}
t = load_theme(p)
assert t.accent == '#111111' and t.role_color('QA') == '#222222'
print('profile keys wired OK')"`
Expected: `profile keys wired OK`.

- [ ] **Step 4: Commit**

```bash
git add domain-profile.template.md
git commit -m "feat(okr-present): domain-profile paths + present theme section

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Final verification

- [ ] **Full suite green:** `cd .claude/skills/okr-planner/resources && python3 -m pytest engine/tests -v` → all pass (~35 tests).
- [ ] **Three artifacts from the ideal spec:** run the three CLIs on `examples/ideal_deck_spec.yaml` into `/tmp/` and open each; deck structure matches `GDS-Q3-2026.pptx` at the archetype level.
- [ ] **Gate discipline:** temporarily blank a KR `becomes` in a copy and confirm `audit` returns 🔴.
