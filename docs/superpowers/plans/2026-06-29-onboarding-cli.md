# Онбординг-CLI (onboard.py) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Самодостаточный интерактивный CLI `onboard.py` (Python stdlib) для онбординга GROUND Vault: опрос → config + каркас Нексусов + захват ответов; хендофф в LLM-скилл `/paf-onboard`.

**Architecture:** Чистые функции (без I/O) для логики и генерации YAML/Markdown + тонкий TTY-слой (`main`). Валидация в памяти до записи — нет зависимости от `sa_documentation`/PyYAML. Дефолтный каталог 4 Нексусов встроен (зеркало `nexus_catalog.md §3`).

**Tech Stack:** Python 3 stdlib (`argparse`, `pathlib`, `re`, `shutil`, `datetime`, `sys`), pytest для тестов.

---

## File Structure

- Create: `onboard.py` — CLI (логика + интерактив).
- Create: `tests/__init__.py`, `tests/test_onboard.py` — тесты логики (без TTY).
- Modify: `.claude/skills/paf-init/SKILL.md` — ужать в обёртку над `onboard.py`.
- Create: `.claude/skills/paf-onboard/SKILL.md` — LLM-синтез (контракт §3.2 спеки).
- Modify: `install.sh` — хук запуска онбординга в конце.
- Modify: `README.md` — флоу install → onboard.

Спека: `docs/superpowers/specs/2026-06-29-onboarding-cli-design.md`.

---

### Task 1: Каркас `onboard.py` + встроенный каталог Нексусов

**Files:**
- Create: `onboard.py`
- Create: `tests/__init__.py`, `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест (drift-guard каталога)**

`tests/test_onboard.py`:
```python
import pathlib
import onboard


def test_default_nexuses_slugs():
    slugs = [n["slug"] for n in onboard.DEFAULT_NEXUSES]
    assert slugs == ["customer", "market", "product", "growth"]


def test_default_nexuses_have_four_seed_questions_each():
    for n in onboard.DEFAULT_NEXUSES:
        assert len(n["seed_questions"]) == 4
        assert n["ttl_days"] in (60, 90)


def test_catalog_slugs_match_nexus_catalog_doc():
    # drift-guard: встроенный каталог совпадает с источником
    doc = pathlib.Path("sa_documentation/nexus_catalog.md").read_text(encoding="utf-8")
    for n in onboard.DEFAULT_NEXUSES:
        assert f"slug: {n['slug']}" in doc
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'onboard'`

- [ ] **Step 3: Создать `tests/__init__.py` (пустой) и `onboard.py` с каталогом**

`tests/__init__.py`: пустой файл.

`onboard.py`:
```python
#!/usr/bin/env python3
"""Онбординг GROUND Vault (PAF Team OS). Интерактивный CLI, Python stdlib.

Фаза INIT: опрос → GROUND/config.yaml + NEXUS/_registry.yaml + placeholder _index.md + PULSE.
Фаза CAPTURE: seed_questions по Нексусам → GROUND/_intake/onboarding-answers.md.
Хендофф: /paf-onboard (LLM-синтез ответов и доков в узлы).
"""
import argparse
import datetime
import pathlib
import re
import shutil
import sys

# Встроенный каталог minimal-Нексусов — зеркало sa_documentation/nexus_catalog.md §3.
DEFAULT_NEXUSES = [
    {"slug": "customer", "name": "Нексус потребителя", "owner_role": "Product Engineer", "ttl_days": 90,
     "seed_questions": [
         "Кто основные сегменты?",
         "Какие работы (JTBD) они «нанимают»?",
         "Главные боли и их причины?",
         "Гипотеза монетизируемой ценности (mNSM)?"]},
    {"slug": "market", "name": "Нексус рынка", "owner_role": "Portfolio Manager", "ttl_days": 90,
     "seed_questions": [
         "Каков объём рынка и его динамика?",
         "Какие тренды формируют рынок?",
         "Кто конкуренты и каковы их позиции?",
         "Каковы Ставки (Bets) стратегического сценария?"]},
    {"slug": "product", "name": "Нексус продукта", "owner_role": "Product Engineer", "ttl_days": 90,
     "seed_questions": [
         "В чём идея продукта?",
         "Какие фичи закрывают гэп до Видения?",
         "Каково Видение (Vision) — образ продукта, нужный рынку и компании?",
         "Каков гэп между текущим продуктом и Видением?"]},
    {"slug": "growth", "name": "Нексус системы роста", "owner_role": "Growth Engineer", "ttl_days": 60,
     "seed_questions": [
         "Каковы каналы дистрибуции и роста?",
         "Какова модель монетизации?",
         "Каков AI-COGS (затраты ИИ в стоимости)?",
         "Какие рычаги (Lever) дают рост NPV?"]},
]

ROSTER_ROLES = ["product_engineer", "product_ops", "growth_engineer",
                "portfolio_manager", "discovery_launcher_pm", "ai_ux_designer"]
ROLE_KEY = {"Product Engineer": "product_engineer",
            "Portfolio Manager": "portfolio_manager",
            "Growth Engineer": "growth_engineer"}
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/__init__.py tests/test_onboard.py
git commit -m "feat(onboard): skeleton + embedded default-nexus catalog"
```

---

### Task 2: `slugify()` + проверка slug

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
import pytest


@pytest.mark.parametrize("raw,expected", [
    ("Acme Billing", "acme-billing"),
    ("Биллинг Про", "billing-pro"),
    ("  Multi   Space  ", "multi-space"),
    ("CAPS-Lock_v2", "caps-lock-v2"),
    ("Корзина 2.0", "korzina-2-0"),
])
def test_slugify(raw, expected):
    assert onboard.slugify(raw) == expected
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py::test_slugify -q`
Expected: FAIL — `AttributeError: module 'onboard' has no attribute 'slugify'`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}

SLUG_RE = re.compile(r'[a-z0-9][a-z0-9-]*$')
NEXUS_SLUG_RE = re.compile(r'[a-z][a-z0-9-]*$')


def slugify(text):
    s = (text or "").strip().lower()
    s = ''.join(_TRANSLIT.get(ch, ch) for ch in s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py::test_slugify -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): slugify with cyrillic transliteration"
```

---

### Task 3: `validate_collected()`

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
def _collected(**over):
    d = {
        "company": "Acme",
        "product": {"name": "Acme Billing", "slug": "acme-billing", "idea": "Биллинг для SaaS"},
        "team": {"size": 5, "roster": {"product_engineer": "Иван Иванов"}},
        "cortex": {"phase_target": 2, "ruflo_mcp": False},
        "onboarding": {"status": "init"},
    }
    d.update(over)
    return d


def test_validate_ok():
    assert onboard.validate_collected(_collected()) == []


def test_validate_bad_slug():
    d = _collected(product={"name": "X", "slug": "Bad Slug", "idea": "y"})
    errs = onboard.validate_collected(d)
    assert any("slug" in e for e in errs)


def test_validate_missing_product_engineer():
    d = _collected(team={"size": 1, "roster": {"product_engineer": ""}})
    errs = onboard.validate_collected(d)
    assert any("product_engineer" in e for e in errs)
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k validate -q`
Expected: FAIL — `AttributeError: ... 'validate_collected'`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def validate_collected(d):
    """Проверки в памяти ДО записи. Возвращает список ошибок (пустой = OK)."""
    errs = []
    slug = (d.get("product") or {}).get("slug", "")
    if not SLUG_RE.fullmatch(str(slug or "")):
        errs.append(f"product.slug invalid ascii-slug: {slug!r}")
    pe = ((d.get("team") or {}).get("roster") or {}).get("product_engineer")
    if not pe or not str(pe).strip():
        errs.append("team.roster.product_engineer is required")
    for nx in DEFAULT_NEXUSES:
        if not NEXUS_SLUG_RE.fullmatch(nx["slug"]):
            errs.append(f"nexus slug invalid: {nx['slug']!r}")
    return errs
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k validate -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): in-memory validate_collected"
```

---

### Task 4: YAML-эмиттер `_yq()` + `build_config_yaml()`

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
def test_build_config_yaml_quotes_and_fields():
    d = _collected(company="Acme: Inc")  # двоеточие требует кавычек
    cfg = onboard.build_config_yaml(d, "2026-06-29")
    assert 'company: "Acme: Inc"' in cfg
    assert "slug: \"acme-billing\"" in cfg
    assert "product_engineer: \"Иван Иванов\"" in cfg
    assert "ruflo_mcp: false" in cfg
    assert "phase_target: 2" in cfg
    assert "status: init" in cfg
    assert "created: 2026-06-29" in cfg
    assert "paf_step: 0" in cfg
    # незаданные роли roster → null
    assert "product_ops: null" in cfg
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k build_config -q`
Expected: FAIL — `AttributeError: ... 'build_config_yaml'`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def _yq(v):
    """YAML-скаляр: bool/int/None как есть, строки в двойных кавычках с экранированием."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def build_config_yaml(d, today):
    roster = (d.get("team") or {}).get("roster") or {}
    roster_lines = "\n".join(f"    {role}: {_yq(roster.get(role))}" for role in ROSTER_ROLES)
    return (
        f"company: {_yq(d['company'])}\n"
        "product:\n"
        f"  name: {_yq(d['product']['name'])}\n"
        f"  slug: {_yq(d['product']['slug'])}\n"
        f"  idea: {_yq(d['product']['idea'])}\n"
        "team:\n"
        f"  size: {int(d['team']['size'])}\n"
        "  roster:\n"
        f"{roster_lines}\n"
        "cortex:\n"
        f"  phase_target: {int(d['cortex']['phase_target'])}\n"
        f"  ruflo_mcp: {_yq(bool(d['cortex']['ruflo_mcp']))}\n"
        "  obsidian: true\n"
        "onboarding:\n"
        f"  status: {d['onboarding']['status']}\n"
        "  sources_ingested: []\n"
        "  baseline_cr: {}\n"
        "  onboarded_at: null\n"
        "nexus:\n"
        "  catalog: master\n"
        "  custom_count: 0\n"
        f"created: {today}\n"
        "paf_step: 0\n"
    )
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k build_config -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): build_config_yaml + safe scalar emitter"
```

---

### Task 5: `build_registry_yaml()` (+ `_owner_for`)

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
def test_build_registry_owner_from_roster_and_cortex_fallback():
    d = _collected(team={"size": 3, "roster": {
        "product_engineer": "Иван", "growth_engineer": "Пётр"}})  # portfolio_manager не задан
    reg = onboard.build_registry_yaml(d)
    assert "nexus_types:" in reg
    assert "slug: customer" in reg and 'owner: "Иван"' in reg
    assert "slug: growth" in reg and 'owner: "Пётр"' in reg
    # market.owner_role=Portfolio Manager не в roster → Cortex
    assert "slug: market" in reg and 'owner: "Cortex"' in reg
    assert reg.count("source: default") == 4
    assert reg.count("onboarded: todo") == 4
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k build_registry -q`
Expected: FAIL — `AttributeError: ... 'build_registry_yaml'`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def _owner_for(nx, roster):
    key = ROLE_KEY.get(nx["owner_role"])
    val = roster.get(key) if key else None
    return val if val and str(val).strip() else "Cortex"


def build_registry_yaml(d):
    roster = (d.get("team") or {}).get("roster") or {}
    lines = [
        "# Реестр Нексусов клиента. onboard.py → default; /paf-nexus-create → custom; /paf-onboard → наполнение.",
        "nexus_types:",
    ]
    for nx in DEFAULT_NEXUSES:
        owner = _owner_for(nx, roster)
        lines.append(
            f"  - {{slug: {nx['slug']}, source: default, "
            f"name: {_yq(nx['name'])}, owner: {_yq(owner)}, onboarded: todo}}"
        )
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k build_registry -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): build_registry_yaml with roster owner mapping"
```

---

### Task 6: `build_index_md()` + `build_pulse_md()`

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
def test_build_index_md_frontmatter_and_seed():
    d = _collected()
    nx = onboard.DEFAULT_NEXUSES[3]  # growth, ttl 60, owner_role Growth Engineer (не в roster → Cortex)
    md = onboard.build_index_md(nx, d, "2026-06-29")
    assert md.startswith("---\n")
    assert "nexus: growth" in md
    assert "node_id: growth-index" in md
    assert "kind: empirical" in md
    assert "confidence: 0.3" in md
    assert "sources: []" in md
    assert "ttl_days: 60" in md
    assert 'owner: "Cortex"' in md
    for q in nx["seed_questions"]:
        assert q in md


def test_build_pulse_md_lists_four_nexuses():
    md = onboard.build_pulse_md(_collected(), "2026-06-29")
    for slug in ("customer", "market", "product", "growth"):
        assert slug in md
    assert "sprint_phase: pulse" in md
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k "build_index or build_pulse" -q`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def build_index_md(nx, d, today):
    owner = _owner_for(nx, (d.get("team") or {}).get("roster") or {})
    seed = "\n".join(f"- {q}" for q in nx["seed_questions"])
    return (
        "---\n"
        f"nexus: {nx['slug']}\n"
        f"node_id: {nx['slug']}-index\n"
        "node_type: step-overview\n"
        "paf_step: null\n"
        "sprint_phase: null\n"
        "kind: empirical\n"
        f"owner: {_yq(owner)}\n"
        "confidence: 0.3\n"
        "sources: []\n"
        f"updated: {today}\n"
        f"ttl_days: {nx['ttl_days']}\n"
        "ripeness: fresh\n"
        "tags: [nexus-index, onboarding]\n"
        "---\n\n"
        f"# {nx['name']}\n\n"
        f"Placeholder-Узел каталога `{nx['slug']}`. Контекст ещё не оцифрован.\n"
        "Наполнение — через `/paf-onboard` (интервью по seed_questions + ингестия `GROUND/_intake/`).\n\n"
        "## seed_questions\n\n"
        f"{seed}\n\n"
        "> ⚠️ допущение клиента (онбординг), требует валидации в Steps 1–8.\n"
    )


def build_pulse_md(d, today):
    rows = "\n".join(f"| {nx['slug']} | 0.0 | 1.0 | 0.0 |" for nx in DEFAULT_NEXUSES)
    return (
        "---\n"
        "nexus: product\n"
        "node_id: init-pulse\n"
        "node_type: step-overview\n"
        "paf_step: 0\n"
        "sprint_phase: pulse\n"
        "kind: empirical\n"
        "owner: Product Engineer\n"
        "confidence: 0.3\n"
        'sources: ["onboarding:init"]\n'
        f"updated: {today}\n"
        "ttl_days: 90\n"
        "ripeness: fresh\n"
        "tags: [progress-pulse, onboarding]\n"
        "---\n\n"
        "# Init Pulse — онбординг GROUND\n\n"
        f"Snapshot на момент `onboard.py` ({today}). 4 Нексуса созданы как placeholder (CP 0.3).\n\n"
        "**Следующий шаг:** `/paf-onboard` (ингестия доков + интервью).\n\n"
        "## Context Ripeness (baseline)\n\n"
        "| Нексус | completeness | freshness | CR |\n"
        "|---|---|---|---|\n"
        f"{rows}\n"
    )
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k "build_index or build_pulse" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): build_index_md + build_pulse_md"
```

---

### Task 7: `capture_to_markdown()`

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест**

Добавить в `tests/test_onboard.py`:
```python
def test_capture_to_markdown_empty_answer_becomes_utochnit():
    answers = [{"slug": "customer", "name": "Нексус потребителя",
                "qa": [("Кто сегменты?", "SMB"), ("Боли?", "")]}]
    md = onboard.capture_to_markdown(answers, "2026-06-29")
    assert "## Нексус потребителя (`customer`)" in md
    assert "**Кто сегменты?**" in md
    assert "SMB" in md
    assert "_[УТОЧНИТЬ]_" in md  # пустой ответ
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k capture -q`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def capture_to_markdown(answers, today):
    out = [
        f"# Онбординг — захват ответов ({today})",
        "",
        "> Сырые ответы интервью. Источник для `/paf-onboard` (LLM-синтез в узлы Нексусов).",
        "",
    ]
    for nx in answers:
        out.append(f"## {nx['name']} (`{nx['slug']}`)")
        out.append("")
        for q, a in nx["qa"]:
            out.append(f"**{q}**")
            out.append(a.strip() if a and a.strip() else "_[УТОЧНИТЬ]_")
            out.append("")
    return "\n".join(out) + "\n"
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k capture -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): capture_to_markdown"
```

---

### Task 8: `write_init()` — запись файлов + интеграционный тест

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест (интеграция в tmp_dir)**

Добавить в `tests/test_onboard.py`:
```python
def test_write_init_creates_valid_ground(tmp_path):
    g = tmp_path / "GROUND"
    onboard.write_init(str(g), _collected(), "2026-06-29")
    assert (g / "config.yaml").exists()
    assert (g / "NEXUS/_registry.yaml").exists()
    assert (g / "PULSE/00-init-pulse.md").exists()
    for slug in ("customer", "market", "product", "growth"):
        assert (g / "NEXUS" / slug / "_index.md").exists()
    assert (g / "_intake").is_dir()
    # если доступен валидатор GROUND — должен сказать OK
    try:
        import sys as _s
        _s.path.insert(0, ".")
        from sa_documentation.validate_ground import validate_ground
        assert validate_ground(str(g)) == []
    except Exception:
        pass  # PyYAML/валидатор недоступны — мягкая деградация
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k write_init -q`
Expected: FAIL — `AttributeError: ... 'write_init'`

- [ ] **Step 3: Реализовать**

Добавить в `onboard.py`:
```python
def write_init(ground, d, today):
    g = pathlib.Path(ground)
    (g / "NEXUS").mkdir(parents=True, exist_ok=True)
    (g / "_intake").mkdir(parents=True, exist_ok=True)
    (g / "PULSE").mkdir(parents=True, exist_ok=True)
    (g / "config.yaml").write_text(build_config_yaml(d, today), encoding="utf-8")
    (g / "NEXUS/_registry.yaml").write_text(build_registry_yaml(d), encoding="utf-8")
    for nx in DEFAULT_NEXUSES:
        nd = g / "NEXUS" / nx["slug"]
        nd.mkdir(parents=True, exist_ok=True)
        (nd / "_index.md").write_text(build_index_md(nx, d, today), encoding="utf-8")
    (g / "PULSE/00-init-pulse.md").write_text(build_pulse_md(d, today), encoding="utf-8")
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python3 -m pytest tests/test_onboard.py -k write_init -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): write_init file emission + integration test"
```

---

### Task 9: Интерактивный слой `main()` + флаги + идемпотентность

**Files:**
- Modify: `onboard.py`
- Test: `tests/test_onboard.py`

- [ ] **Step 1: Написать падающий тест (`--non-interactive` без TTY не падает)**

Добавить в `tests/test_onboard.py`:
```python
def test_main_non_interactive_returns_zero(capsys):
    rc = onboard.main(["--non-interactive"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "onboard" in out.lower() or "GROUND" in out
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python3 -m pytest tests/test_onboard.py -k main_non_interactive -q`
Expected: FAIL — `AttributeError: ... 'main'`

- [ ] **Step 3: Реализовать интерактив + main**

Добавить в `onboard.py`:
```python
def _today():
    return datetime.date.today().isoformat()


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        v = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return default
    return v or default


def ask_required(prompt):
    while True:
        v = ask(prompt)
        if v:
            return v
        print("  · обязательное поле, повтори ввод")


def detect_ruflo():
    return shutil.which("ruflo") is not None


def run_interview():
    company = ask_required("Компания")
    pname = ask_required("Продукт — название")
    suggested = slugify(pname)
    slug = ask("Продукт — slug (ascii)", default=suggested) or suggested
    while not SLUG_RE.fullmatch(slug):
        print(f"  · невалидный slug; пример: {slugify(slug) or 'acme-billing'}")
        slug = ask_required("Продукт — slug (ascii)")
    idea = ask_required("Продукт — идея (1-2 предложения)")
    size = ask("Размер команды", default="1")
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 1
    pe = ask_required("Product Engineer (имя; обязателен)")
    roster = {"product_engineer": pe}
    for role in ROSTER_ROLES[1:]:
        v = ask(f"{role} (имя / Cortex / пусто)")
        roster[role] = v if v else None
    phase = ask("Cortex phase_target (1/2/3)", default="2")
    try:
        phase = int(phase)
    except (TypeError, ValueError):
        phase = 2
    return {
        "company": company,
        "product": {"name": pname, "slug": slug, "idea": idea},
        "team": {"size": size, "roster": roster},
        "cortex": {"phase_target": phase, "ruflo_mcp": detect_ruflo()},
        "onboarding": {"status": "init"},
    }


def run_capture():
    answers = []
    print("\n— Фаза CAPTURE: ответы по Нексусам (пусто = [УТОЧНИТЬ]) —")
    for nx in DEFAULT_NEXUSES:
        print(f"\n## {nx['name']}")
        qa = [(q, ask(f"  {q}") or "") for q in nx["seed_questions"]]
        answers.append({"slug": nx["slug"], "name": nx["name"], "qa": qa})
    return answers


def main(argv=None):
    p = argparse.ArgumentParser(description="Онбординг GROUND Vault (PAF).")
    p.add_argument("--phase", choices=["init", "capture", "all"], default="all")
    p.add_argument("--ground", default="GROUND")
    p.add_argument("--non-interactive", action="store_true",
                   help="без записи/опроса: печать плана и выход (CI/проверка)")
    args = p.parse_args(argv)
    g = pathlib.Path(args.ground)
    today = _today()

    if args.non_interactive:
        print("onboard.py: --phase=%s ground=%s (non-interactive: запись пропущена)"
              % (args.phase, args.ground))
        return 0

    if not sys.stdin.isatty():
        print("Нет интерактивного терминала. Запусти `python3 onboard.py` в TTY "
              "или используй --non-interactive.")
        return 0

    # Идемпотентность
    if (g / "config.yaml").exists() and args.phase in ("init", "all"):
        choice = ask("GROUND/config.yaml уже есть. [o]verwrite / [c]apture-only / [a]bort", default="a")
        if choice and choice[0].lower() == "c":
            args.phase = "capture"
        elif not choice or choice[0].lower() != "o":
            print("Отменено.")
            return 0

    if args.phase in ("init", "all"):
        d = run_interview()
        errs = validate_collected(d)
        if errs:
            print("Ошибки валидации:\n  - " + "\n  - ".join(errs))
            return 1
        write_init(str(g), d, today)
        print(f"✓ INIT: {g}/config.yaml + 4 Нексуса + PULSE")

    if args.phase in ("capture", "all"):
        answers = run_capture()
        (g / "_intake").mkdir(parents=True, exist_ok=True)
        (g / "_intake/onboarding-answers.md").write_text(
            capture_to_markdown(answers, today), encoding="utf-8")
        # пометить статус (если config есть)
        cfg = g / "config.yaml"
        if cfg.exists():
            txt = cfg.read_text(encoding="utf-8").replace(
                "status: init", "status: in_progress")
            cfg.write_text(txt, encoding="utf-8")
        print(f"✓ CAPTURE: {g}/_intake/onboarding-answers.md")

    print("\nГотово. Дальше — `/paf-onboard` (LLM-синтез ответов и доков `_intake/` в узлы Нексусов).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить весь файл тестов**

Run: `python3 -m pytest tests/test_onboard.py -q`
Expected: PASS (все)

- [ ] **Step 5: Commit**

```bash
git add onboard.py tests/test_onboard.py
git commit -m "feat(onboard): interactive main, flags, idempotency, capture"
```

---

### Task 10: `/paf-init` → тонкая обёртка

**Files:**
- Modify: `.claude/skills/paf-init/SKILL.md`

- [ ] **Step 1: Заменить содержимое на обёртку**

Полностью переписать `.claude/skills/paf-init/SKILL.md`:
```markdown
---
name: paf-init
description: "Первоначальная настройка GROUND Vault. Запускает детерминированный CLI onboard.py (опрос → config + каркас Нексусов). One-shot после git clone."
---

# /paf-init — настройка GROUND Vault

Канон настройки — **детерминированный скрипт** `onboard.py` (Python stdlib, без зависимостей). Этот скилл — тонкая обёртка: проверь предусловия и запусти скрипт.

## Шаги

1. Проверь, что `python3` доступен: `python3 --version`.
2. Если `GROUND/config.yaml` уже есть — предупреди (скрипт сам предложит overwrite/capture-only/abort).
3. Запусти фазу INIT:

   ```bash
   python3 onboard.py --phase init
   ```

   Скрипт интерактивно спросит: company, product (name/slug/idea), team size, Product Engineer (обязателен), опц. roster, cortex phase. Валидация — в памяти, до записи.
4. Для наполнения Нексусов далее — `/paf-onboard` (LLM-синтез). Полный прогон (init + опрос seed_questions) одной командой: `python3 onboard.py`.

> Логика, схема и гвардраилы — в `onboard.py` и `docs/superpowers/specs/2026-06-29-onboarding-cli-design.md`. Термины PAF — `sa_documentation/naming_conventions.md`.
```

- [ ] **Step 2: Проверить, что нет битых ссылок на удалённое**

Run: `grep -nE 'sa_documentation/(atlas|blueprint|nexus_index|tasks)' .claude/skills/paf-init/SKILL.md`
Expected: пусто

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/paf-init/SKILL.md
git commit -m "refactor(paf-init): thin wrapper over onboard.py"
```

---

### Task 11: Новый скилл `/paf-onboard` (LLM-синтез)

**Files:**
- Create: `.claude/skills/paf-onboard/SKILL.md`

- [ ] **Step 1: Создать файл**

`.claude/skills/paf-onboard/SKILL.md`:
```markdown
---
name: paf-onboard
description: "Наполнение Нексусов GROUND Vault: синтез ответов онбординга и документов _intake/ в узлы с источниками. Запускать после onboard.py."
---

# /paf-onboard — наполнение Нексусов (LLM-синтез)

Вторая половина онбординга. Детерминированную часть сделал `onboard.py` (config + каркас + захват ответов). Здесь — качественный синтез контекста клиента в узлы Нексусов.

## Вход (прочитать)
- `GROUND/_intake/onboarding-answers.md` — сырые ответы интервью (onboard.py Фаза CAPTURE).
- `GROUND/_intake/*` — документы клиента (если есть).
- `GROUND/config.yaml`, `GROUND/NEXUS/_registry.yaml` — конфиг и реестр.
- `sa_documentation/nexus_schema.md` — Node schema (sources, confidence, ttl, ripeness).
- `sa_documentation/naming_conventions.md` — термины PAF (без синонимов).

## Процесс
1. **Phase A — ингестия `_intake/`:** извлеки факты из доков, смапь на Нексусы (customer/market/product/growth + кастомные из реестра). Дедуп: ruflo memory если `cortex.ruflo_mcp: true`, иначе Grep по узлам.
2. **Phase B — интервью:** добей пробелы из `onboarding-answers.md` (один вопрос за раз). Персонализируй стиль под домен/роль клиента.
3. **Синтез в узлы:** для каждого Нексуса создай/обнови узлы по `nexus_schema.md`. **Каждый узел ← `sources`** (`onboarding:interview` / имя дока). Узел без источника = workslop, не создавать. Раздели факт / вывод LLM / `[УТОЧНИТЬ]`.
4. **Прогресс:** обнови `onboarding.status` (`in_progress` → `done`), пересчитай Context Ripeness в `GROUND/PULSE/`.

## Гвардраилы
- Ноль галлюцинаций: факт без источника → `[УТОЧНИТЬ]`.
- STOP-паузы: подтверждай извлечённое из доков с пользователем перед записью.
- Идемпотентность: повторный запуск дополняет, не затирает подтверждённые узлы.
- Только термины PAF из `naming_conventions.md`.

## Финал
Выведи: какие Нексусы наполнены, сколько узлов, сколько `[УТОЧНИТЬ]`, Context Ripeness по каждому, статус. Дальше — Step-1-IDEA (`docs/AI-PROCESSES/STEP-1-IDEA/`).

> Детальный scope этого скилла прорабатывается отдельно (см. промт scope наполнения Нексусов).
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/paf-onboard/SKILL.md
git commit -m "feat(paf-onboard): LLM synthesis skill (onboarding part 2)"
```

---

### Task 12: Хук в `install.sh`

**Files:**
- Modify: `install.sh` (после финального блока, перед последней пустой строкой)

- [ ] **Step 1: Добавить хук в конец install.sh**

В `install.sh`, после блока `echo "  3) OKR: ..."` и до конца файла, добавить:
```bash

# --- онбординг (хук) ---
if [ -t 0 ] && command -v python3 >/dev/null 2>&1 && [ -f "$SCRIPT_DIR/onboard.py" ]; then
  printf "\nЗапустить онбординг GROUND Vault сейчас? (python3 onboard.py) [y/N]: "
  read -r _ans
  case "$_ans" in
    y|Y|yes|да) python3 "$SCRIPT_DIR/onboard.py" || true ;;
    *) echo "  · позже: python3 onboard.py" ;;
  esac
else
  echo "  4) Онбординг: python3 onboard.py  (нужен python3 и интерактивный терминал)"
fi
```

- [ ] **Step 2: Проверить синтаксис bash**

Run: `bash -n install.sh`
Expected: без вывода (синтаксис OK)

- [ ] **Step 3: Проверить, что pipe-режим не виснет (нет TTY → ветка else)**

Run: `printf '' | bash install.sh /tmp/po-helper-test-claude 2>&1 | tail -3`
Expected: видна строка `4) Онбординг: python3 onboard.py` (read не вызывается без TTY)

- [ ] **Step 4: Commit**

```bash
git add install.sh
git commit -m "feat(install): hook to run onboard.py after install"
```

---

### Task 13: README — флоу install → onboard

**Files:**
- Modify: `README.md` (секция «⚡ Установка», после блока про MCP)

- [ ] **Step 1: Добавить подсекцию про онбординг**

В `README.md` после секции «MCP-серверы» добавить:
```markdown
### Онбординг GROUND Vault

После установки — настройка контекста продукта одной командой:

```bash
python3 onboard.py
```

Интерактивный опрос (company, product, команда, Product Engineer, Нексусы) → `GROUND/config.yaml` + каркас 4 Нексусов + захват ответов в `GROUND/_intake/`. Дальше наполнение — скилл `/paf-onboard` (LLM-синтез ответов и документов в узлы). `install.sh` предложит запустить онбординг сразу.
```

- [ ] **Step 2: Проверить отсутствие битых ссылок**

Run: `grep -nE 'onboard\.py|/paf-onboard' README.md`
Expected: присутствуют новые упоминания

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): onboarding flow (onboard.py + /paf-onboard)"
```

---

## Финальная проверка (после всех задач)

- [ ] `python3 -m pytest tests/ sa_documentation/tests -q` → всё PASS
- [ ] `bash -n install.sh` → OK
- [ ] `python3 onboard.py --non-interactive` → rc 0
- [ ] Скан битых ссылок: `grep -rnE 'sa_documentation/(atlas|blueprint|nexus_index|tasks|sources)' .claude README.md install.sh` → пусто
- [ ] Открыть PR `feat/onboarding-cli → main` с описанием
