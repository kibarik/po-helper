# Confluence Indexator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Пайплайн-скилл, который читает Confluence, семантически оцифровывает страницы в атомарные узлы node schema, роутит их в существующие нексусы, строит граф `[[wiki-links]]` и генерит навигационный MOC.

**Architecture:** Скилл-пакет `confluence-indexator` = оркестратор `/cindex` + 6 команд-стадий (`crawl → comprehend → digitize → route → link → deliver`), зеркало идиомы `bft-writer`. Семантика — на LLM-стадиях; детерминированная валидация графа — на Python-линтере `lint_graph.py` (в стиле `validate_ground.py`). Истина живёт в markdown-волте `GROUND/NEXUS/`.

**Tech Stack:** Markdown skills/commands (`.claude/skills`, `.claude/commands`), Python 3 + PyYAML для валидаторов, pytest для тестов, Confluence MCP (выбирается в Task 5).

## Global Constraints

- **Ноль галлюцинаций:** узел без непустого `sources[]` не создаётся и является ошибкой линтера. Значение — `["confluence:<url>"]`.
- **Оцифровка ≠ валидация:** каждый ингестированный узел получает `confidence: 0.3` (frontmatter node schema §2.2).
- **`ttl_days`** по нексусу: `market`/`customer` = 90, `growth` = 60, все прочие = 180.
- **Роутинг только в зарегистрированные нексусы** из `GROUND/NEXUS/_registry.yaml`; новые не создаём.
- **Два разных показателя:** `route_confidence` (классификация узла в нексус, порог auto ≥ 0.7) ≠ `confidence` (доверие к узлу, всегда 0.3).
- **Node schema** — источник истины `sa_documentation/nexus_schema.md`; поля frontmatter: `nexus, node_id, node_type, paf_step, kind, owner, confidence, sources, updated, ttl_days, ripeness, tags`.
- **`node_id`** — детерминированный ascii-slug `<nexus>-<translit(slug заголовка)>`, паттерн `[a-z][a-z0-9-]*`.
- Скиллы/команды пишутся на русском, стиль — как в существующем `bft-writer` (frontmatter `description`, секции «Использование»/«Роль»/«Инструкция для LLM»).
- Спека: `docs/superpowers/specs/2026-07-04-confluence-indexator-design.md` — единый источник требований.

---

## File Structure

**Создаём:**
- `sa_documentation/cindex_ids.py` — детерминированная генерация `node_id` (переиспользуется линтером и как эталон правил для скилла).
- `sa_documentation/lint_graph.py` — линтер графа узлов нексусов.
- `sa_documentation/tests/test_cindex_ids.py` — тесты генератора id.
- `sa_documentation/tests/test_lint_graph.py` — тесты линтера.
- `sa_documentation/tests/fixtures/graph_ok/` и `graph_bad/` — фикстуры узлов-нексусов.
- `sa_documentation/tests/fixtures/cindex/inventory_sample.json` — мок пространства Confluence.
- `sa_documentation/tests/fixtures/cindex/routing_expected.jsonl` — ожидаемый dry-run план.
- `.claude/skills/confluence-indexator/SKILL.md` — оркестратор.
- `.claude/skills/confluence-indexator/resources/{routing_table,confidence_rules,linking_rules,node_schema,moc_template}.md`.
- `.claude/skills/confluence-indexator/examples/{ideal_node.md,ideal_routing.jsonl}`.
- `.claude/commands/cindex.md` + `.claude/commands/cindex-{crawl,comprehend,digitize,route,link,deliver}.md`.

**Модифицируем:**
- `README.md` — добавить строку пайплайна в таблицу процессов.

---

## Task 1: Детерминированный генератор `node_id`

**Files:**
- Create: `sa_documentation/cindex_ids.py`
- Test: `sa_documentation/tests/test_cindex_ids.py`

**Interfaces:**
- Produces: `make_node_id(nexus: str, title: str) -> str` — возвращает `<nexus>-<slug>`, где slug = транслит+кебаб заголовка, паттерн `[a-z][a-z0-9-]*`, макс. 60 символов, детерминированный (одинаковый вход → одинаковый выход).
- Produces: `slugify(text: str) -> str` — транслитерация кириллицы в ascii + кебаб-кейс.

- [ ] **Step 1: Write the failing test**

```python
# sa_documentation/tests/test_cindex_ids.py
from sa_documentation.cindex_ids import make_node_id, slugify


def test_slugify_cyrillic():
    assert slugify("Выбор синхронного потока") == "vybor-sinhronnogo-potoka"


def test_slugify_strips_punctuation_and_case():
    assert slugify("SLA / Доступность 99.9%!") == "sla-dostupnost-99-9"


def test_make_node_id_is_deterministic():
    a = make_node_id("precedents", "Выбор синхронного платёжного потока")
    b = make_node_id("precedents", "Выбор синхронного платёжного потока")
    assert a == b == "precedents-vybor-sinhronnogo-platezhnogo-potoka"


def test_make_node_id_matches_pattern():
    import re
    nid = make_node_id("system-landscape", "Payment Gateway")
    assert re.fullmatch(r"[a-z][a-z0-9-]*", nid)


def test_make_node_id_truncates_to_60():
    nid = make_node_id("market", "оч" * 100)
    assert len(nid) <= 60
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/aleksishmanov/projects/po-helper/.claude/worktrees/confident-raman-b58290 && python3 -m pytest sa_documentation/tests/test_cindex_ids.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sa_documentation.cindex_ids'`

- [ ] **Step 3: Write minimal implementation**

```python
# sa_documentation/cindex_ids.py
"""Детерминированная генерация node_id для Confluence Indexator.

node_id = "<nexus>-<slug(title)>", ascii, паттерн [a-z][a-z0-9-]*, <= 60 символов.
См. docs/superpowers/specs/2026-07-04-confluence-indexator-design.md §6, §8.
"""
import re

# Практичная таблица транслитерации ГОСТ-подобная (нижний регистр).
_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    text = text.strip().lower()
    out = []
    for ch in text:
        if ch in _TRANSLIT:
            out.append(_TRANSLIT[ch])
        elif ch.isascii() and (ch.isalnum()):
            out.append(ch)
        else:
            out.append(" ")
    slug = "".join(out)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def make_node_id(nexus: str, title: str, max_len: int = 60) -> str:
    slug = slugify(title)
    nid = f"{nexus}-{slug}" if slug else nexus
    if not re.match(r"[a-z]", nid):
        nid = "n-" + nid
    return nid[:max_len].rstrip("-")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_cindex_ids.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/cindex_ids.py sa_documentation/tests/test_cindex_ids.py
git commit -m "feat: deterministic node_id generator for Confluence indexator"
```

---

## Task 2: Линтер графа — sources и node_type/nexus

**Files:**
- Create: `sa_documentation/lint_graph.py`
- Create: `sa_documentation/tests/fixtures/graph_ok/precedents/precedents-sync-flow.md`
- Create: `sa_documentation/tests/fixtures/graph_bad/precedents/no-sources.md`
- Test: `sa_documentation/tests/test_lint_graph.py`

**Interfaces:**
- Consumes: `GROUND/NEXUS/_registry.yaml` (список валидных slug нексусов), node schema §3 (валидные `node_type`).
- Produces: `lint_graph(nexus_root: str) -> list[str]` — возвращает список строк-ошибок (пустой = OK); аналог `validate_ground`.
- Produces: константа `VALID_NODE_TYPES: set[str]` — из node schema §3.

- [ ] **Step 1: Write the failing test**

Сначала создай фикстуры-узлы.

`sa_documentation/tests/fixtures/graph_ok/precedents/precedents-sync-flow.md`:
```markdown
---
nexus: precedents
node_id: precedents-sync-flow
node_type: decision
paf_step: null
kind: empirical
owner: Cortex
confidence: 0.3
sources: ["confluence:https://wiki/131074"]
updated: 2026-07-04
ttl_days: 180
ripeness: fresh
tags: [confluence-indexed]
---
Решение: синхронный платёжный поток.
```

`sa_documentation/tests/fixtures/graph_bad/precedents/no-sources.md` (тот же frontmatter, но `sources: []` и `node_type: banana`):
```markdown
---
nexus: precedents
node_id: precedents-no-sources
node_type: banana
paf_step: null
kind: empirical
owner: Cortex
confidence: 0.3
sources: []
updated: 2026-07-04
ttl_days: 180
ripeness: fresh
tags: []
---
Плохой узел.
```

`graph_ok` и `graph_bad` также должны содержать `_registry.yaml` — скопируй `GROUND/NEXUS/_registry.yaml` в оба (`graph_ok/_registry.yaml`, `graph_bad/_registry.yaml`).

```python
# sa_documentation/tests/test_lint_graph.py
import pathlib
from sa_documentation.lint_graph import lint_graph

ROOT = pathlib.Path(__file__).parent


def test_graph_ok():
    errs = lint_graph(ROOT / "fixtures/graph_ok")
    assert errs == [], f"unexpected: {errs}"


def test_missing_sources_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("sources" in e for e in errs)


def test_invalid_node_type_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("node_type" in e and "banana" in e for e in errs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_lint_graph.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sa_documentation.lint_graph'`

- [ ] **Step 3: Write minimal implementation**

```python
# sa_documentation/lint_graph.py
"""Линтер графа узлов нексусов Confluence Indexator.

Проверяет: sources[] непуст, node_type/nexus валидны против реестра,
[[wiki-links]] не битые, нет orphan-узлов. Возвращает список ошибок.
См. docs/superpowers/specs/2026-07-04-confluence-indexator-design.md §8.
"""
import pathlib
import re
import yaml

VALID_NODE_TYPES = {
    "spine", "operating-model", "gates", "bootstrap", "step-overview",
    "sprint-phase", "person", "deliverable", "channel", "component",
    "decision", "rule", "regulation", "nfr", "risk", "term", "metric",
}


def _load_registry_slugs(nexus_root: pathlib.Path) -> set:
    reg_p = nexus_root / "_registry.yaml"
    if not reg_p.exists():
        return set()
    reg = yaml.safe_load(reg_p.read_text()) or {}
    return {t.get("slug") for t in reg.get("nexus_types", []) or []}


def _parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def lint_graph(nexus_root) -> list:
    errs = []
    nexus_root = pathlib.Path(nexus_root)
    valid_nexus = _load_registry_slugs(nexus_root)

    for md in sorted(nexus_root.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        fm = _parse_frontmatter(md.read_text())
        nid = fm.get("node_id", md.stem)
        if not fm.get("sources"):
            errs.append(f"{nid}: empty sources[] (workslop)")
        nt = fm.get("node_type")
        if nt not in VALID_NODE_TYPES:
            errs.append(f"{nid}: invalid node_type {nt!r}")
        nx = fm.get("nexus")
        if valid_nexus and nx not in valid_nexus:
            errs.append(f"{nid}: nexus {nx!r} not in registry")
    return errs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_lint_graph.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/lint_graph.py sa_documentation/tests/test_lint_graph.py sa_documentation/tests/fixtures/graph_ok sa_documentation/tests/fixtures/graph_bad
git commit -m "feat: graph linter — sources + node_type/nexus checks"
```

---

## Task 3: Линтер графа — битые wiki-links и orphan-узлы

**Files:**
- Modify: `sa_documentation/lint_graph.py`
- Modify: `sa_documentation/tests/test_lint_graph.py`
- Create: `sa_documentation/tests/fixtures/graph_bad/precedents/broken-link.md`

**Interfaces:**
- Consumes: `lint_graph` из Task 2.
- Produces: расширенный `lint_graph` — добавляет проверки `broken wiki-link` (ссылка на `node_id`, которого нет в волте) и `orphan` (узел без входящих и исходящих `[[...]]`, при наличии >1 узла в волте).

- [ ] **Step 1: Write the failing test**

Добавь фикстуру `graph_bad/precedents/broken-link.md` (валидный frontmatter как в graph_ok, но `node_id: precedents-broken`, `sources: ["confluence:x"]`, тело содержит `Смотри [[precedents-nonexistent]].`). Добавь тесты:

```python
def test_broken_wikilink_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("broken wiki-link" in e and "precedents-nonexistent" in e for e in errs)


def test_orphan_node_is_flagged():
    # graph_bad содержит >1 узла, no-sources.md ни на кого не ссылается и никто на него
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("orphan" in e for e in errs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_lint_graph.py -v`
Expected: FAIL — новые два теста падают (нет логики wiki-links/orphan)

- [ ] **Step 3: Write minimal implementation**

Замени тело цикла в `lint_graph` так, чтобы сначала собрать все узлы и рёбра, затем проверять. Полная новая версия функции:

```python
def lint_graph(nexus_root) -> list:
    errs = []
    nexus_root = pathlib.Path(nexus_root)
    valid_nexus = _load_registry_slugs(nexus_root)

    nodes = {}      # node_id -> frontmatter
    out_links = {}  # node_id -> set(target node_id)
    in_links = {}   # target node_id -> count

    for md in sorted(nexus_root.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        text = md.read_text()
        fm = _parse_frontmatter(text)
        nid = fm.get("node_id", md.stem)
        nodes[nid] = fm
        targets = set(re.findall(r"\[\[([a-z0-9-]+)\]\]", text))
        out_links[nid] = targets
        for t in targets:
            in_links[t] = in_links.get(t, 0) + 1

    for nid, fm in nodes.items():
        if not fm.get("sources"):
            errs.append(f"{nid}: empty sources[] (workslop)")
        nt = fm.get("node_type")
        if nt not in VALID_NODE_TYPES:
            errs.append(f"{nid}: invalid node_type {nt!r}")
        nx = fm.get("nexus")
        if valid_nexus and nx not in valid_nexus:
            errs.append(f"{nid}: nexus {nx!r} not in registry")
        for t in out_links[nid]:
            if t not in nodes:
                errs.append(f"{nid}: broken wiki-link [[{t}]]")
        if len(nodes) > 1 and not out_links[nid] and in_links.get(nid, 0) == 0:
            errs.append(f"{nid}: orphan (no wiki-links in or out)")
    return errs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_lint_graph.py sa_documentation/tests/test_cindex_ids.py -v`
Expected: PASS (all). Проверь, что `graph_ok` всё ещё чист (в нём один узел → orphan не триггерится).

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/lint_graph.py sa_documentation/tests/test_lint_graph.py sa_documentation/tests/fixtures/graph_bad
git commit -m "feat: graph linter — broken wiki-links + orphan detection"
```

---

## Task 4: Ресурсы скилла — routing_table, confidence_rules, linking_rules, node_schema, moc_template

**Files:**
- Create: `.claude/skills/confluence-indexator/resources/routing_table.md`
- Create: `.claude/skills/confluence-indexator/resources/confidence_rules.md`
- Create: `.claude/skills/confluence-indexator/resources/linking_rules.md`
- Create: `.claude/skills/confluence-indexator/resources/node_schema.md`
- Create: `.claude/skills/confluence-indexator/resources/moc_template.md`

**Interfaces:**
- Produces: файлы-ресурсы, на которые ссылаются команды-стадии (Tasks 6–9) и SKILL.md (Task 5).

- [ ] **Step 1: Написать `routing_table.md`** — скопируй таблицу маппинга из спеки §5 дословно (14 строк), добавь заголовок и правило: «одна страница → несколько узлов разных строк; при неоднозначности двух нексусов — понизить `route_confidence` и уйти в очередь».

- [ ] **Step 2: Написать `confidence_rules.md`** — зафиксируй: `route_confidence ≥ 0.7 → action: auto`, иначе `action: queue`; `confidence` узла всегда `0.3`; `ttl_days`: market/customer=90, growth=60, прочее=180; триггеры очереди: низкий route_confidence, конфликт двух нексусов, orphan, отсутствие нексуса.

- [ ] **Step 3: Написать `linking_rules.md`** — три правила из спеки §7: структурные рёбра (ancestors/links Confluence), семантические (общая сущность → кросс-нексус), допустимость висячих ссылок (ловит линтер). Формат ребра — `[[<node_id>]]`.

- [ ] **Step 4: Написать `node_schema.md`** — НЕ дублировать схему; файл-указатель: «Node schema — источник истины `sa_documentation/nexus_schema.md` (§2 поля, §3 node_type, §4 wilting). Для Confluence-узлов: `kind: empirical`, `confidence: 0.3`, `sources: ["confluence:<url>"]`, `tags: [confluence-indexed]`.»

- [ ] **Step 5: Написать `moc_template.md`** — шаблон `GROUND/NEXUS/_map.md` из спеки §7: три секции (Карта экосистемы; Маршруты «вопрос → нексус/узел»; Кросс-нексусные мосты). Дать конкретный markdown-скелет с примерными строками.

- [ ] **Step 6: Verify — файлы на месте и содержат ключевые правила**

Run:
```bash
cd /Users/aleksishmanov/projects/po-helper/.claude/worktrees/confident-raman-b58290
ls .claude/skills/confluence-indexator/resources/
grep -l "route_confidence" .claude/skills/confluence-indexator/resources/confidence_rules.md
grep -l "confluence-indexed" .claude/skills/confluence-indexator/resources/node_schema.md
grep -c "|" .claude/skills/confluence-indexator/resources/routing_table.md   # таблица присутствует
```
Expected: все 5 файлов в листинге; grep находит правила; в routing_table минимум 15 строк с `|`.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/confluence-indexator/resources
git commit -m "feat: confluence-indexator skill resources (routing/confidence/linking/schema/moc)"
```

---

## Task 5: Оркестратор SKILL.md + выбор Confluence MCP

**Files:**
- Create: `.claude/skills/confluence-indexator/SKILL.md`

**Interfaces:**
- Consumes: ресурсы Task 4.
- Produces: `SKILL.md` — точка входа: описание pipeline, принципы, STOP-логика, ссылки на команды-стадии и ресурсы. Frontmatter `name` + `description` (для триггера скилла).

- [ ] **Step 1: Обнаружить/зафиксировать Confluence MCP.** Проверь доступные MCP-инструменты на Confluence:
```bash
# в сессии агента: ToolSearch query "confluence" — найти инструменты чтения пространств/страниц
```
Если готового Confluence MCP нет — зафиксируй в SKILL.md раздел «Предусловия»: требуется MCP с инструментами `get_spaces`/`get_pages`/`get_page_content` (Atlassian official MCP или REST-обёртка), настраивается в `.mcp.json`; при отсутствии — стадия `/cindex-crawl` останавливается с инструкцией по подключению.

- [ ] **Step 2: Написать SKILL.md** со структурой (по образцу `.claude/skills/bft-writer/SKILL.md`):
  - Frontmatter: `name: confluence-indexator`, `description:` с триггерами («индексировать Confluence», «наполнить нексусы из Confluence», «/cindex», «построить граф контекста»).
  - Секция «Роль»: Индексатор экосистемы (repowise-way).
  - Секция «Принцип нулевого допуска к галлюцинациям» (как в bft): узел без `sources` → не создаётся.
  - Секция «Pipeline (6 стадий)» — ASCII-схема из спеки §3 с STOP-паузами.
  - Таблица «Стадия | Команда | Роль | Артефакт».
  - Секция «Предусловия» (Confluence MCP из Step 1).
  - Ссылки на ресурсы (`resources/*.md`) и напоминание про `sa_documentation/nexus_schema.md`.

- [ ] **Step 3: Verify**

Run:
```bash
test -f .claude/skills/confluence-indexator/SKILL.md
grep -q "confluence-indexator" .claude/skills/confluence-indexator/SKILL.md
grep -q "STOP" .claude/skills/confluence-indexator/SKILL.md
grep -qi "галлюцинац" .claude/skills/confluence-indexator/SKILL.md
```
Expected: все проверки проходят (exit 0).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/confluence-indexator/SKILL.md
git commit -m "feat: confluence-indexator orchestrator SKILL.md"
```

---

## Task 6: Golden-пример узла и dry-run плана + прогон линтера

**Files:**
- Create: `.claude/skills/confluence-indexator/examples/ideal_node.md`
- Create: `.claude/skills/confluence-indexator/examples/ideal_routing.jsonl`
- Create: `sa_documentation/tests/fixtures/cindex/inventory_sample.json`
- Create: `sa_documentation/tests/test_examples_conform.py`

**Interfaces:**
- Consumes: `lint_graph` (Task 3), `make_node_id` (Task 1), node schema.
- Produces: эталоны, на которые ссылаются стадии digitize/route; тест, доказывающий, что `ideal_node.md` проходит линтер и его `node_id` соответствует генератору.

- [ ] **Step 1: Написать `ideal_node.md`** — валидный узел `decision` в `precedents` (frontmatter по Global Constraints: `confidence: 0.3`, `sources: ["confluence:https://wiki/131074"]`, `tags: [confluence-indexed]`, `ripeness: fresh`), тело со ссылкой `[[system-landscape-payment-gateway]]`.

- [ ] **Step 2: Написать `ideal_routing.jsonl`** — 2 строки из спеки §6: одна `action: auto` (route_confidence 0.82), одна `action: queue` (route_confidence 0.34, target_nexus null).

- [ ] **Step 3: Написать `inventory_sample.json`** — мок пространства из спеки §6 (3 страницы: ADR «Платёжный шлюз» с label `adr`; глоссарий; страница-риск без явного нексуса).

- [ ] **Step 4: Написать тест соответствия**

```python
# sa_documentation/tests/test_examples_conform.py
import json
import pathlib
import shutil
from sa_documentation.lint_graph import lint_graph, _parse_frontmatter
from sa_documentation.cindex_ids import make_node_id

REPO = pathlib.Path(__file__).resolve().parents[2]
EX = REPO / ".claude/skills/confluence-indexator/examples"


def test_ideal_node_passes_linter(tmp_path):
    # собрать мини-волт: реестр + ideal_node в папке нексуса
    (tmp_path / "precedents").mkdir()
    shutil.copy(REPO / "GROUND/NEXUS/_registry.yaml", tmp_path / "_registry.yaml")
    shutil.copy(EX / "ideal_node.md", tmp_path / "precedents/ideal_node.md")
    # плюс узел-цель, чтобы wiki-link не был битым и не было orphan
    (tmp_path / "system-landscape").mkdir()
    tgt = tmp_path / "system-landscape/payment-gateway.md"
    tgt.write_text(
        "---\nnexus: system-landscape\nnode_id: system-landscape-payment-gateway\n"
        "node_type: component\npaf_step: null\nkind: empirical\nowner: Cortex\n"
        "confidence: 0.3\nsources: [\"confluence:https://wiki/131099\"]\n"
        "updated: 2026-07-04\nttl_days: 180\nripeness: fresh\ntags: []\n---\n"
        "Шлюз. См. [[precedents-sync-payment-flow]].\n"
    )
    errs = lint_graph(tmp_path)
    assert errs == [], f"ideal_node не проходит линтер: {errs}"


def test_ideal_node_id_matches_generator():
    fm = _parse_frontmatter((EX / "ideal_node.md").read_text())
    assert fm["node_id"] == make_node_id(fm["nexus"], "Выбор синхронного платёжного потока")


def test_ideal_routing_is_valid_jsonl():
    lines = (EX / "ideal_routing.jsonl").read_text().strip().splitlines()
    recs = [json.loads(l) for l in lines]
    assert any(r["action"] == "auto" for r in recs)
    assert any(r["action"] == "queue" for r in recs)
```

Убедись, что `node_id` в `ideal_node.md` = `precedents-vybor-sinhronnogo-platezhnogo-potoka` (совпадает с генератором), а `[[system-landscape-payment-gateway]]` — точное имя узла-цели.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest sa_documentation/tests/test_examples_conform.py -v`
Expected: PASS (3 passed). Если падает `test_ideal_node_passes_linter` — поправь frontmatter/ссылки в `ideal_node.md`, а не тест.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/confluence-indexator/examples sa_documentation/tests/fixtures/cindex/inventory_sample.json sa_documentation/tests/test_examples_conform.py
git commit -m "feat: golden examples + conformance tests for confluence-indexator"
```

---

## Task 7: Команды-стадии crawl / comprehend / digitize

**Files:**
- Create: `.claude/commands/cindex.md`
- Create: `.claude/commands/cindex-crawl.md`
- Create: `.claude/commands/cindex-comprehend.md`
- Create: `.claude/commands/cindex-digitize.md`

**Interfaces:**
- Consumes: SKILL.md (Task 5), ресурсы (Task 4).
- Produces: тонкие команды (frontmatter `description` + «Использование» + «Роль» + «Инструкция для LLM»), по образцу `.claude/commands/bft-problem.md`.

- [ ] **Step 1: `cindex.md`** — оркестратор: печатает pipeline из 6 стадий и текущий статус (какие артефакты в `artefacts/confluence/` уже есть), советует следующую команду. Вход: `<space_key>`.

- [ ] **Step 2: `cindex-crawl.md`** — роль Crawler. Вход `<space_key>`. Инструкция: через Confluence MCP обойти пространство, собрать `inventory.json` (поля из спеки §6: id, title, ancestors, labels, links, url). Ошибки MCP/401/rate-limit → STOP с сообщением, не перезаписывать прошлый inventory. Пустые/архивные страницы — пометка. Выход: `artefacts/confluence/inventory.json`. STOP: PO подтверждает scope.

- [ ] **Step 3: `cindex-comprehend.md`** — роль Comprehender. Вход `inventory.json`. Постранично: о чём страница, сущности, rich picture → `artefacts/confluence/comprehension/<id>.md`. Страница без сущностей → запись в `skipped.md`. Авто-batch (без STOP).

- [ ] **Step 4: `cindex-digitize.md`** — роль Digitizer. Вход comprehension. По `routing_table.md` выделить атомарные узлы-кандидаты (node_type + черновик тела), КАЖДЫЙ с `sources: ["confluence:<url>"]` (без источника — не создавать). Выход: `artefacts/confluence/nodes-draft.jsonl` (формат из спеки §6).

- [ ] **Step 5: Verify**

Run:
```bash
for c in cindex cindex-crawl cindex-comprehend cindex-digitize; do test -f .claude/commands/$c.md && head -1 .claude/commands/$c.md | grep -q "^---" || echo "BAD: $c"; done
grep -q "inventory.json" .claude/commands/cindex-crawl.md
grep -q "sources" .claude/commands/cindex-digitize.md
```
Expected: нет строк `BAD:`; grep-проверки проходят.

- [ ] **Step 6: Commit**

```bash
git add .claude/commands/cindex.md .claude/commands/cindex-crawl.md .claude/commands/cindex-comprehend.md .claude/commands/cindex-digitize.md
git commit -m "feat: cindex stage commands — crawl, comprehend, digitize"
```

---

## Task 8: Команды-стадии route / link

**Files:**
- Create: `.claude/commands/cindex-route.md`
- Create: `.claude/commands/cindex-link.md`

**Interfaces:**
- Consumes: `nodes-draft.jsonl`, `routing_table.md`, `confidence_rules.md`, `linking_rules.md`, `cindex_ids.py` (правила node_id).
- Produces: `artefacts/confluence/routing.jsonl` (dry-run план из спеки §6).

- [ ] **Step 1: `cindex-route.md`** — роль Router. Для каждого узла-кандидата: определить `target_nexus` по `routing_table.md` (только реестр), присвоить `route_confidence`, сгенерить `node_id` по правилам `cindex_ids.py` (`<nexus>-<slug заголовка>`). Применить `confidence_rules.md`: `≥0.7 → auto`, иначе `queue` + `reason`. Выход: `routing.jsonl` со всеми полями кроме `links`.

- [ ] **Step 2: `cindex-link.md`** — роль Linker. Дополнить каждую запись `routing.jsonl` полем `links: ["[[<node_id>]]"]` по `linking_rules.md`: структурные рёбра из `ancestors`/`links` inventory + семантические кросс-нексусные (общая сущность). Висячие ссылки допустимы. Обновляет `routing.jsonl` на месте.

- [ ] **Step 3: Verify**

Run:
```bash
for c in cindex-route cindex-link; do test -f .claude/commands/$c.md && head -1 .claude/commands/$c.md | grep -q "^---" || echo "BAD: $c"; done
grep -q "route_confidence" .claude/commands/cindex-route.md
grep -q "wiki-link\|\[\[" .claude/commands/cindex-link.md
```
Expected: нет `BAD:`; grep проходят.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/cindex-route.md .claude/commands/cindex-link.md
git commit -m "feat: cindex stage commands — route, link"
```

---

## Task 9: Команда-стадия deliver + генерация MOC + прогон линтеров

**Files:**
- Create: `.claude/commands/cindex-deliver.md`

**Interfaces:**
- Consumes: `routing.jsonl` (Task 8), `moc_template.md` (Task 4), `lint_graph.py` (Task 3), `validate_ground.py`, `make_node_id`.
- Produces: узлы в `GROUND/NEXUS/<slug>/`, обновлённые `_index.md`, `GROUND/NEXUS/_map.md`, `GROUND/_intake/unrouted.md`.

- [ ] **Step 1: `cindex-deliver.md`** — роль Deliverer. Алгоритм в инструкции для LLM:
  1. Сухой прогон: показать сводку плана (сколько узлов auto / queue, по каким нексусам, сколько рёбер). **STOP: ок PO.**
  2. Для `action: auto`: создать/обновить `GROUND/NEXUS/<target_nexus>/<node_id>.md` с полным frontmatter (node schema; `confidence: 0.3`, `sources`, `ttl_days` по нексусу, `ripeness: fresh`, `tags: [confluence-indexed]`) + тело + `[[links]]`.
  3. Идемпотентность: если узел с таким `node_id` есть и помечен `tags: [po-edited]` — не перетирать, расхождение → `_intake/`; иначе обновить `body`+`updated`, пересчитать `ripeness`.
  4. Для `action: queue`: добавить запись в `GROUND/_intake/unrouted.md` (таблица: tmp_id, node_type, reason, source_page).
  5. Обновить `GROUND/NEXUS/<slug>/_index.md` затронутых нексусов (добавить ссылки на новые узлы).
  6. Сгенерить/обновить `GROUND/NEXUS/_map.md` по `moc_template.md` (3 секции).
  7. Прогнать линтеры (Step 2).

- [ ] **Step 2: Прописать в команде verify-блок** — deliver обязан в конце выполнить:
```bash
python3 -m sa_documentation.lint_graph GROUND/NEXUS   # ожидается пусто (OK)
python3 sa_documentation/validate_ground.py GROUND    # ожидается OK
```
Добавь в `lint_graph.py` CLI-хвост (если ещё нет), чтобы `python3 -m sa_documentation.lint_graph <path>` печатал ошибки и возвращал код 1 при непустом списке:
```python
if __name__ == "__main__":
    import sys
    errs = lint_graph(sys.argv[1] if len(sys.argv) > 1 else "GROUND/NEXUS")
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
```

- [ ] **Step 3: Verify (структура команды + CLI линтера)**

Run:
```bash
test -f .claude/commands/cindex-deliver.md
grep -q "_map.md" .claude/commands/cindex-deliver.md
grep -q "po-edited" .claude/commands/cindex-deliver.md
python3 -m sa_documentation.lint_graph sa_documentation/tests/fixtures/graph_ok; echo "exit: $?"
```
Expected: файл есть; grep проходят; линтер на `graph_ok` печатает пусто и `exit: 0`.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/cindex-deliver.md sa_documentation/lint_graph.py
git commit -m "feat: cindex-deliver — write nodes, MOC, intake queue, lint gates"
```

---

## Task 10: Интеграция — README + полный прогон тестов

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: всё вышеперечисленное.
- Produces: запись о пайплайне в README; зелёный набор тестов.

- [ ] **Step 1: Добавить в README** строку про `confluence-indexator` в таблицу процессов/навыков (рядом с bft/okr): краткое «наполнение нексусов из Confluence + граф + MOC», команда `/cindex <space>`.

- [ ] **Step 2: Полный прогон тестов**

Run: `python3 -m pytest sa_documentation/tests/ -v`
Expected: PASS (все тесты Tasks 1–6 зелёные).

- [ ] **Step 3: Verify — скилл и команды на месте**

Run:
```bash
ls .claude/skills/confluence-indexator/ .claude/skills/confluence-indexator/resources/ .claude/skills/confluence-indexator/examples/
ls .claude/commands/cindex*.md
grep -q "cindex" README.md && echo "README ok"
```
Expected: полный набор файлов; `README ok`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: register confluence-indexator pipeline in README"
```

---

## Self-Review

**1. Spec coverage** (спека → задачи):
- §3 пайплайн 6 стадий → Tasks 5,7,8,9 (SKILL + 7 команд). ✓
- §4 раскладка файлов → Tasks 4,5,6,7,8,9. ✓
- §5 routing table → Task 4 (routing_table.md), применяется в Task 8. ✓
- §6 форматы артефактов + confidence-гейт → Task 4 (confidence_rules), Task 6 (golden jsonl), Tasks 7–8 (команды). ✓
- §7 граф + MOC → Task 4 (linking_rules, moc_template), Task 8 (link), Task 9 (MOC gen). ✓
- §8 ошибки/идемпотентность/тесты → Tasks 1–3 (линтер+id), Task 6 (fixtures), Task 9 (idempotency, lint gates). ✓
- Инвариант «ноль галлюцинаций» → Task 2 (sources check), Task 7 (digitize sources). ✓

**2. Placeholder scan:** код линтера и генератора id приведён полностью; команды описаны через конкретные роли/входы/выходы/verify-grep, а не «add error handling». Контент-задачи (skills/commands) имеют структурные verify-команды вместо фейковых pytest — сознательная адаптация (см. заметку в начале плана). Нет «TBD/TODO/implement later».

**3. Type consistency:** `make_node_id(nexus, title)`, `slugify(text)`, `lint_graph(nexus_root) -> list`, `_parse_frontmatter(text) -> dict`, `VALID_NODE_TYPES` — имена согласованы между Tasks 1,2,3,6,9. `node_id` формат `<nexus>-<slug>` единый везде. `action` ∈ {auto, queue}, поля `route_confidence`/`target_nexus`/`links` согласованы между спекой §6 и Tasks 6,8.

## Открытые пункты для исполнителя
- **Confluence MCP** (Task 5 Step 1): конкретный сервер и имена инструментов подтвердить в начале исполнения; при отсутствии — краул-стадия печатает инструкцию по подключению, остальной пайплайн (на готовом `inventory.json`) тестируется автономно на фикстуре `inventory_sample.json`.
- **`_map.md` vs `_index.md`**: по решению PO — `_map.md` отдельный навигационный слой; при желании позже слить в `_index.md`.
