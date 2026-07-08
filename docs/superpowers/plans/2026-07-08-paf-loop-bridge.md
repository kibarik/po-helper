# PAF Loop Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Замкнуть петлю Pulse→Bunch→Harvest в po-helper — материализовать пустые `GROUND/PULSE/BUNCH/RESULTS` и обратную запись в Нексус, не ломая корп-спину OKR→Scrum→БФТ.

**Architecture:** Аддитивный мост. Единый read-only канон схемы (`paf_loop_schema.md`) описывает три loop-артефакта как empirical `sprint-phase`-узлы. `validate_ground.py` расширяется машинной проверкой этих артефактов (единственный исполняемый контракт — TDD здесь). Пять существующих стадий `sprint-planner`/`okr-planner` дополняются материализацией артефакта; одна новая под-стадия (`okr`-режим) замыкает верхний уровень. Golden-примеры в `examples/` служат и образцом для скиллов, и фикстурами, которые валидатор проверяет — примеры не могут разойтись со схемой.

**Tech Stack:** Python 3 + PyYAML (валидатор + pytest), Markdown+YAML-frontmatter (скиллы, артефакты, канон).

## Global Constraints

- **Схемы артефактов — из спеки** [docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md](../specs/2026-07-08-paf-loop-bridge-design.md) §3. Все структурированные поля живут во **frontmatter** (машиночитаемо), проза — в теле.
- **Три loop-артефакта:** `node_type: sprint-phase`, `sprint_phase: pulse|bunch|harvest`, `kind: empirical` (отличие от нормативных STEP-нот `normative`).
- **`nexus_writeback` у harvest обязателен** — это замыкание петли; без него артефакт невалиден.
- **Методология `docs/AI-PROCESSES/**` — read-only.** Правки только в `sa_documentation/`, `.claude/skills/`, `GROUND/README.md`.
- **Каждый факт в артефакте — с источником** (`sources[]` непустой); выдуманные NPV/mNSM запрещены → `[УТОЧНИТЬ]` (анти-workslop).
- **Тесты:** `python3 -m pytest sa_documentation/tests/ -q` из корня репо. Все зелёные перед мержем.
- **Коммиты:** в конце каждой задачи; сообщения на русском, тело как в репозитории.

---

### Task 1: Канон схемы петли + декларация write-targets

**Files:**
- Create: `sa_documentation/paf_loop_schema.md`
- Modify: `sa_documentation/nexus_process_map.md` (§4 «Обратная запись»)
- Modify: `GROUND/README.md` (блок «Структура» — пометить, кто пишет PULSE/BUNCH/RESULTS)

**Interfaces:**
- Produces: канонический словарь полей loop-артефактов (frontmatter-ключи), на который ссылаются Task 2 (валидатор), Task 3/4 (скиллы). Точные ключи и enum перечислены в §3 спеки и продублированы в этом файле.

- [ ] **Step 1: Создать `sa_documentation/paf_loop_schema.md`**

Содержимое (полностью):

```markdown
# PAF Loop Schema — Pulse / Bunch / Harvest узлы GROUND (мост)

> Единый словарь трёх loop-артефактов, материализующих цикл Product Sprint в `GROUND/PULSE|BUNCH|RESULTS`. Реализация моста из спеки `docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md`. Выровнено по каноническим `docs/AI-PROCESSES/STEP-*/{1.pulse,3.bunch,6.harvest}.md` и `4.progress-pulse.md`.
> **Все структурированные поля — во frontmatter** (машиночитаемо, проверяется `validate_ground.py`). Тело ноты — человеческая проза.

## Общее (все три артефакта)

Наследуют базовую Node schema ([[nexus_schema]] §2) + правила:

| Ключ | Значение |
|---|---|
| `node_type` | `sprint-phase` (не выдумывать новый тип) |
| `sprint_phase` | `pulse` \| `bunch` \| `harvest` |
| `kind` | `empirical` (контекст клиента, не методология) |
| `nexus` | первичная Линза цикла: `product` (Линза Продукта) \| `growth`/`market` (Бизнес/Стратегия) |
| `paf_step` | `null` (операционный цикл, не привязан к шагу) |
| `owner` | RACI Accountable: спринт → Product Engineer; harvest → +Growth Engineer; квартал → Portfolio Manager |
| `confidence` | float 0..1 (уровень доказательств) |
| `sources` | непустой список (нет источника = workslop) |
| `ttl_days` | ≈ длина окна (спринт=14) → wilting на границе окна = сигнал «пора Harvest» |
| `level` | `sprint` \| `quarter` |
| `cycle_ref` | идентификатор цикла (`S14`, `Q3`) |

## PULSE (`sprint_phase: pulse`, папка `PULSE/`)

Канонические 5 частей ([[docs/AI-PROCESSES/STEP-0-FOUNDATION/4.progress-pulse|4.progress-pulse]] §54):

| Ключ | Обяз. | Значение |
|---|---|---|
| `nexus_snapshot` | ✅ | map: `{<nexus>: {ripeness: <float>, gaps: [...]}}` — Context Ripeness **вычисляется** (не вписывается руками) |
| `gap_vs_vision` | — | разрыв текущего состояния и Vision |
| `intent` | ✅ | какую часть гэпа закрываем в цикле |
| `cp_start` | — | текущий CP ключевых гипотез |
| `lens` | ✅ | `product` \| `business` \| `strategy` (3PL) |

Правило: Pulse **не генерирует решения** (это Scout); не приукрашивать спелость/CP.

## BUNCH (`sprint_phase: bunch`, папка `BUNCH/`) — вместо беклога

| Ключ | Обяз. | Значение |
|---|---|---|
| `parent_bunch` | ✅ для `level: sprint` | ссылка на квартальный Банч (вложенность по ссылке) |
| `goal_map_ref` | — | под какую Карту Целей (OKR) сформирован |
| `bunch_size` | ✅ | лимит скорости восприятия рынка |
| `bunch_window` | ✅ | период ожидания результата |
| `items` | ✅ | непустой список; каждый: `ref` (ССЫЛКА на JIRA, не копия) + `kind` (`hypothesis`\|`feature`\|`mechanic` / `lever`\|`bet`) + `trace` (путь к узлу Нексуса — обязателен, нет → резервная) + опц. `vp_offer`, `initial_cp` (ICE/RICE 1–10) |
| `gate` | ✅ | Pitch-штамп: `{final_cp, cost_of_risk, decision}`; `decision` ∈ `commit`\|`defer`\|`refuse` (осознанный отказ) |
| `selection_rationale` | — | ① max mNSM ② min риск(CP) ③ эффект в окне |
| `npv_estimate` | — | число или `[УТОЧНИТЬ: growth тонкий]` |

Критерий выхода в Pitch: ≥3 items с трассировкой на ≥1 источник. Банч формируется заново каждый цикл из состояния Нексуса — беклог не воскресает.

## HARVEST (`sprint_phase: harvest`, папка `RESULTS/`) — урожай + writeback

| Ключ | Обяз. | Значение |
|---|---|---|
| `bunch_ref` | — | какой Банч собрали |
| `rolls_up_to` | ✅ для `level: sprint` | ссылка на квартальный Harvest |
| `outcomes` | — | `{cp_change (обяз. валюта L0), mNSM_delta (L1+), npv_actual (L2+)}` |
| `insights` | ✅ | что узнали |
| `nexus_writeback` | ✅ | **сердце моста**; непустой список; каждый: `{nexus, node, change, source}`. Пишется по Node schema: проставить `sources`, поднять `confidence`, обновить `updated` в целевом узле |
| `next_intent` | — | передача в следующий Pulse |

## Уровни зрелости метрик (прогрессивно, анти-workslop)

| Уровень | Разблокировка (вычисляемо) | Обязательно |
|---|---|---|
| L0 CP-only | `growth` тонкий | `cp_change`, `nexus_writeback`, `insights`; `npv/mNSM = [УТОЧНИТЬ]` |
| L1 mNSM | Context Ripeness `growth` ≥ 0.6 | `mNSM_delta`, ребро mNSM→NPV |
| L2 NPV/дерево | Business Sprint активен | композитный NPV Ставок, дерево метрик |

## Bridge-отклонения от чистого PAF (зафиксировано)

1. Pulse привязан к Scrum-каденции (канон: event-based/Kanban).
2. Pitch — штамп `gate` на Банче, не отдельная фаза.
3. Scout свёрнут в `po-research` + гэп-идентификацию Pulse.

**Version:** 1.0 · **Связанные:** [[nexus_schema]] · [[nexus_process_map]] · [[docs/AI-PROCESSES/operating-model|operating-model]]
```

- [ ] **Step 2: Обновить `nexus_process_map.md` §4 — добавить loop-папки как write-targets**

Найти в `sa_documentation/nexus_process_map.md` таблицу в §4 «Обратная запись (процесс → Нексус)». После строки `| release-guard ... |` добавить строки и абзац:

```markdown
| `sprint-planner` (петля) | `PULSE/S{n}` (sprint-sync) · `BUNCH/S{n}` (sprint-deliver) · `RESULTS/S{n}` + writeback в `product` (sprint-fact) |
| `okr-planner` (петля) | `PULSE/Q{n}` (okr-context-gen) · `BUNCH/Q{n}` (okr-deliver) · `RESULTS/Q{n}` + writeback в `market`/`growth` (okr-harvest-quarter) |

> **Loop-артефакты** (Pulse/Bunch/Harvest) — материализация цикла Product Sprint, схема в [[paf_loop_schema]]. `harvest.nexus_writeback` замыкает петлю: результат цикла возвращается инкрементом в Нексус, а не оседает в доке.
```

- [ ] **Step 3: Обновить `GROUND/README.md` — кто пишет loop-папки**

В блоке «Структура» заменить три строки-комментария:

Найти:
```
├── PULSE/               ← Progress Pulse (динамика продукта)
├── BUNCH/               ← Банчи (связки инициатив/экспериментов)
└── RESULTS/             ← Harvesting (урожай — результаты и инсайты)
```
Заменить на:
```
├── PULSE/               ← Progress Pulse: sprint-sync/okr-context-gen (схема paf_loop_schema)
├── BUNCH/               ← Банчи: sprint-deliver/okr-deliver (вместо беклога)
└── RESULTS/             ← Harvesting: sprint-fact/okr-harvest-quarter + writeback в Нексус
```

- [ ] **Step 4: Проверить, что канон read-only не тронут**

Run: `git status --short docs/AI-PROCESSES/`
Expected: пусто (никаких изменений в методологии).

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/paf_loop_schema.md sa_documentation/nexus_process_map.md GROUND/README.md
git commit -m "docs(paf-loop): канон схемы петли + декларация PULSE/BUNCH/RESULTS как write-targets

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Валидатор loop-артефактов (TDD)

**Files:**
- Modify: `sa_documentation/validate_ground.py`
- Create: `sa_documentation/tests/test_loop_artifacts.py`

**Interfaces:**
- Consumes: схема из Task 1 (`paf_loop_schema.md`).
- Produces:
  - `_parse_frontmatter(text: str) -> dict | None` — YAML между первыми `---`.
  - `validate_loop_artifacts(ground_dir: str|Path) -> list[str]` — сканирует `PULSE/BUNCH/RESULTS`, валидирует каждый loop-артефакт; возвращает список ошибок.
  - `validate_ground()` теперь включает эти ошибки в свой результат.

- [ ] **Step 1: Написать падающий тест `test_loop_artifacts.py`**

Create `sa_documentation/tests/test_loop_artifacts.py`:

```python
import pathlib
from sa_documentation.validate_ground import validate_loop_artifacts

VALID_PULSE = """---
nexus: product
node_id: pulse-s14
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.5
sources: ["sprint-sync:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
nexus_snapshot:
  product: {ripeness: 0.72, gaps: ["mNSM не валидирована"]}
intent: "закрыть гэп по гипотезе X"
lens: product
---
# Pulse
"""

VALID_BUNCH = """---
nexus: product
node_id: bunch-s14
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.4
sources: ["OKR-Q3", "sprint-deliver:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
parent_bunch: bunch-q3
bunch_size: 5
bunch_window: sprint-14
items:
  - {ref: PROJ-123, kind: hypothesis, trace: "GROUND/NEXUS/product/feature-x.md", initial_cp: 3}
gate: {final_cp: 0.5, cost_of_risk: "переоценка объёма", decision: commit}
---
# Bunch
"""

VALID_HARVEST = """---
nexus: product
node_id: harvest-s14
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.6
sources: ["sprint-fact:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
rolls_up_to: harvest-q3
outcomes: {cp_change: "+0.2", mNSM_delta: "[УТОЧНИТЬ]", npv_actual: "[УТОЧНИТЬ]"}
insights: ["пилот подтвердил ценность для SMB"]
nexus_writeback:
  - {nexus: product, node: feature-x, change: "cp 0.4->0.6", source: harvest-s14}
---
# Harvest
"""


def _mk(tmp_path, folder, name, text):
    d = tmp_path / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text)


def test_valid_artifacts_pass(tmp_path):
    _mk(tmp_path, "PULSE", "S14-pulse.md", VALID_PULSE)
    _mk(tmp_path, "BUNCH", "S14-bunch.md", VALID_BUNCH)
    _mk(tmp_path, "RESULTS", "S14-harvest.md", VALID_HARVEST)
    assert validate_loop_artifacts(tmp_path) == []


def test_harvest_missing_writeback_fails(tmp_path):
    broken = VALID_HARVEST.replace(
        'nexus_writeback:\n  - {nexus: product, node: feature-x, change: "cp 0.4->0.6", source: harvest-s14}\n',
        "",
    )
    _mk(tmp_path, "RESULTS", "S14-harvest.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("nexus_writeback" in e for e in errs), errs


def test_bunch_bad_decision_fails(tmp_path):
    broken = VALID_BUNCH.replace("decision: commit", "decision: maybe")
    _mk(tmp_path, "BUNCH", "S14-bunch.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("gate.decision" in e for e in errs), errs


def test_sprint_bunch_without_parent_fails(tmp_path):
    broken = VALID_BUNCH.replace("parent_bunch: bunch-q3\n", "")
    _mk(tmp_path, "BUNCH", "S14-bunch.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("parent_bunch" in e for e in errs), errs


def test_pulse_missing_lens_fails(tmp_path):
    broken = VALID_PULSE.replace("lens: product\n", "")
    _mk(tmp_path, "PULSE", "S14-pulse.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("lens" in e for e in errs), errs


def test_non_loop_pulse_note_skipped(tmp_path):
    # init-pulse / summary без sprint_phase не должны падать
    _mk(tmp_path, "PULSE", "00-init-pulse.md", "# просто заметка без frontmatter\n")
    assert validate_loop_artifacts(tmp_path) == []
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

Run: `python3 -m pytest sa_documentation/tests/test_loop_artifacts.py -q`
Expected: FAIL — `ImportError: cannot import name 'validate_loop_artifacts'`.

- [ ] **Step 3: Реализовать в `validate_ground.py`**

Добавить в `sa_documentation/validate_ground.py` после блока `import` (после строки `import yaml`):

```python
LOOP_PHASES = ("pulse", "bunch", "harvest")
LOOP_DIRS = {"PULSE": "pulse", "BUNCH": "bunch", "RESULTS": "harvest"}
_LOOP_BASE_REQUIRED = (
    "nexus", "node_id", "node_type", "sprint_phase", "kind", "owner",
    "confidence", "sources", "updated", "ttl_days", "ripeness",
    "level", "cycle_ref",
)


def _parse_frontmatter(text):
    """YAML-frontmatter между первыми --- ... ---. None если нет/битый."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _validate_loop_node(fm, rel):
    errs = []
    for k in _LOOP_BASE_REQUIRED:
        if fm.get(k) in (None, "", []):
            errs.append(f"{rel}: missing required field {k!r}")
    if fm.get("node_type") != "sprint-phase":
        errs.append(f"{rel}: node_type must be 'sprint-phase'")
    if fm.get("kind") != "empirical":
        errs.append(f"{rel}: kind must be 'empirical'")
    conf = fm.get("confidence")
    if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
        errs.append(f"{rel}: confidence must be float 0..1")
    level = fm.get("level")
    if level not in ("quarter", "sprint"):
        errs.append(f"{rel}: level must be quarter|sprint")

    phase = fm.get("sprint_phase")
    if phase == "pulse":
        if not isinstance(fm.get("nexus_snapshot"), dict):
            errs.append(f"{rel}: pulse requires nexus_snapshot (map)")
        if not fm.get("intent"):
            errs.append(f"{rel}: pulse requires intent")
        if fm.get("lens") not in ("product", "business", "strategy"):
            errs.append(f"{rel}: pulse lens must be product|business|strategy")
    elif phase == "bunch":
        if not fm.get("bunch_size"):
            errs.append(f"{rel}: bunch requires bunch_size")
        if not fm.get("bunch_window"):
            errs.append(f"{rel}: bunch requires bunch_window")
        items = fm.get("items")
        if not isinstance(items, list) or not items:
            errs.append(f"{rel}: bunch requires non-empty items")
        else:
            for i, it in enumerate(items):
                if not isinstance(it, dict) or not it.get("ref") or not it.get("trace"):
                    errs.append(f"{rel}: item[{i}] requires ref and trace")
        gate = fm.get("gate")
        if not isinstance(gate, dict) or gate.get("decision") not in ("commit", "defer", "refuse"):
            errs.append(f"{rel}: bunch requires gate.decision in commit|defer|refuse")
        if level == "sprint" and not fm.get("parent_bunch"):
            errs.append(f"{rel}: sprint bunch requires parent_bunch")
    elif phase == "harvest":
        wb = fm.get("nexus_writeback")
        if not isinstance(wb, list) or not wb:
            errs.append(f"{rel}: harvest requires non-empty nexus_writeback")
        else:
            for i, w in enumerate(wb):
                if not isinstance(w, dict) or not all(
                    w.get(k) for k in ("nexus", "node", "change", "source")
                ):
                    errs.append(f"{rel}: writeback[{i}] requires nexus,node,change,source")
        if not fm.get("insights"):
            errs.append(f"{rel}: harvest requires insights")
        if level == "sprint" and not fm.get("rolls_up_to"):
            errs.append(f"{rel}: sprint harvest requires rolls_up_to")
    return errs


def validate_loop_artifacts(ground_dir):
    """Валидировать loop-артефакты в PULSE/BUNCH/RESULTS. Список ошибок (пустой = OK)."""
    ground_dir = pathlib.Path(ground_dir)
    errs = []
    for folder in LOOP_DIRS:
        d = ground_dir / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            fm = _parse_frontmatter(p.read_text())
            # не loop-артефакт (init-pulse, summary, без frontmatter) → пропустить
            if not fm or fm.get("sprint_phase") not in LOOP_PHASES:
                continue
            errs.extend(_validate_loop_node(fm, f"{folder}/{p.name}"))
    return errs
```

Затем интегрировать в `validate_ground()` — перед финальным `return errs` добавить:

```python
    errs.extend(validate_loop_artifacts(ground_dir))
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

Run: `python3 -m pytest sa_documentation/tests/test_loop_artifacts.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Регрессия — весь набор зелёный**

Run: `python3 -m pytest sa_documentation/tests/ -q`
Expected: PASS (8 passed) — старые `test_ok`/`test_bad` не сломаны (у `ground_ok`/`ground_bad` нет loop-папок → пропускаются).

- [ ] **Step 6: Commit**

```bash
git add sa_documentation/validate_ground.py sa_documentation/tests/test_loop_artifacts.py
git commit -m "feat(validate): проверка loop-артефактов Pulse/Bunch/Harvest во frontmatter

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Материализация спринтового уровня (sprint-planner) + golden-примеры

**Files:**
- Create: `.claude/skills/sprint-planner/examples/loop/S-pulse.md`
- Create: `.claude/skills/sprint-planner/examples/loop/S-bunch.md`
- Create: `.claude/skills/sprint-planner/examples/loop/S-harvest.md`
- Modify: `.claude/skills/sprint-planner/SKILL.md`
- Create: `sa_documentation/tests/test_examples_valid.py`

**Interfaces:**
- Consumes: схема Task 1, `validate_loop_artifacts` Task 2.
- Produces: три golden-примера спринтового уровня (образец для скилла + фикстуры валидатора). Именование выходов, на которые ссылается Task 5: `PULSE/{sprint}-pulse.md`, `BUNCH/{sprint}-bunch.md`, `RESULTS/{sprint}-harvest.md`.

- [ ] **Step 1: Создать `examples/loop/S-pulse.md`**

```markdown
---
nexus: product
node_id: pulse-s14
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.5
sources: ["sprint-sync:S14", "GROUND/NEXUS/product/_index.md"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [pulse]
level: sprint
cycle_ref: S14
nexus_snapshot:
  product: {ripeness: 0.72, gaps: ["mNSM-гипотеза фичи X не валидирована"]}
  growth: {ripeness: 0.30, gaps: ["каналы активации не заполнены"]}
gap_vs_vision: "нет валидированной ценности фичи X относительно Vision продукта"
intent: "в S14 закрыть гэп по ценностной гипотезе фичи X (пилот на SMB)"
cp_start: "CP гипотезы X = 0.3"
lens: product
---

# Progress Pulse — Sprint 14

> Снимок состояния Нексуса на входе в цикл. Не генерирует решения (это Scout) — честно фиксирует «где мы».

Ripeness вычислен `validate_ground.py` (полнота × актуальность), не вписан руками. Гэп признан без приукрашивания.
```

- [ ] **Step 2: Создать `examples/loop/S-bunch.md`**

```markdown
---
nexus: product
node_id: bunch-s14
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.4
sources: ["OKR-Q3", "sprint-deliver:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [bunch]
level: sprint
cycle_ref: S14
parent_bunch: bunch-q3
goal_map_ref: OKR-Q3
bunch_size: 5
bunch_window: sprint-14
items:
  - {ref: PROJ-123, kind: hypothesis, vp_offer: "быстрый онбординг SMB за 5 минут", trace: "GROUND/NEXUS/product/feature-x.md", initial_cp: 3}
  - {ref: PROJ-124, kind: feature, vp_offer: "автоинвойс по расписанию", trace: "GROUND/NEXUS/product/invoicing.md", initial_cp: 4}
gate:
  final_cp: 0.5
  cost_of_risk: "риск переоценки объёма X на ~3 SP"
  decision: commit
selection_rationale: "① max mNSM (онбординг двигает активацию) ② min риск (CP выше у PROJ-124) ③ эффект в окне S14"
npv_estimate: "[УТОЧНИТЬ: growth тонкий]"
---

# Bunch — Sprint 14

> Связка в моменте под Карту Целей OKR-Q3. Не беклог: сформирована из текущего состояния Нексуса, `items` — ссылки на JIRA, не копии.
```

- [ ] **Step 3: Создать `examples/loop/S-harvest.md`**

```markdown
---
nexus: product
node_id: harvest-s14
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.6
sources: ["sprint-fact:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [harvest]
level: sprint
cycle_ref: S14
bunch_ref: bunch-s14
rolls_up_to: harvest-q3
outcomes:
  cp_change: "+0.2 (гипотеза X валидирована пилотом на 8 SMB)"
  mNSM_delta: "[УТОЧНИТЬ: growth тонкий]"
  npv_actual: "[УТОЧНИТЬ: growth тонкий]"
insights:
  - "пилот подтвердил ценность быстрого онбординга для сегмента SMB"
  - "автоинвойс требует интеграции с БАЗИС — вынесено в S15"
nexus_writeback:
  - {nexus: product, node: feature-x, change: "confidence 0.4->0.6, статус: пилот-подтверждён", source: harvest-s14}
next_intent: "вход в S15-pulse: масштабировать онбординг X, начать интеграцию автоинвойса"
---

# Harvest — Sprint 14

> Урожай цикла. `nexus_writeback` замыкает петлю: инкремент возвращается в узел Нексуса `product` (поднять confidence, обновить updated, добавить source).
```

- [ ] **Step 4: Дополнить `SKILL.md` — материализация в стадиях**

В `.claude/skills/sprint-planner/SKILL.md` в таблице «Роли и артефакты» (после строки стадии `↺ ФАКТ`) добавить колонку-примечание не нужно — вместо этого вставить новую секцию перед «## Принципы качества»:

```markdown
## PAF-петля (материализация Pulse→Bunch→Harvest)

Три стадии дополнительно материализуют loop-артефакты по схеме [[sa_documentation/paf_loop_schema|paf_loop_schema]] (образцы — `examples/loop/`). Это замыкает цикл Product Sprint в `GROUND/`, не меняя основной выход стадии.

| Стадия | Доп. артефакт | Ключевое |
|---|---|---|
| `/sprint-sync` | `GROUND/PULSE/{sprint}-pulse.md` | снимок Нексуса (Context Ripeness **вычислять**, не выдумывать) + гэп + intent + lens |
| `/sprint-deliver` | `GROUND/BUNCH/{sprint}-bunch.md` | обёртка ПЛАНа в Банч; `items` — ссылки на JIRA; `gate` из спринт-гейтов (Светофор) = Pitch-штамп; `parent_bunch` = квартальный Банч |
| `/sprint-fact` | `GROUND/RESULTS/{sprint}-harvest.md` | урожай + **`nexus_writeback` в `product`** (обязательно: поднять confidence узла, обновить updated, добавить source) + `rolls_up_to` = квартальный Harvest |

Правила: NPV/mNSM — прогрессивно (L0 CP-only сейчас → `[УТОЧНИТЬ]`, не выдумка); Банч формируется из текущего Нексуса, беклог не воскрешать; артефакт проходит `validate_ground.py` (loop-проверка). Bridge-каденция: Pulse привязан к границе спринта (осознанное отклонение, см. paf_loop_schema).
```

- [ ] **Step 5: Написать тест валидности примеров `test_examples_valid.py`**

Create `sa_documentation/tests/test_examples_valid.py`:

```python
import pathlib
import shutil
from sa_documentation.validate_ground import validate_loop_artifacts

REPO = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE_DIRS = [
    REPO / ".claude/skills/sprint-planner/examples/loop",
    REPO / ".claude/skills/okr-planner/examples/loop",
]
PHASE_TO_FOLDER = {"pulse": "PULSE", "bunch": "BUNCH", "harvest": "RESULTS"}


def test_shipped_examples_are_schema_valid(tmp_path):
    """Golden-примеры скиллов не могут разойтись со схемой."""
    copied = 0
    for ed in EXAMPLE_DIRS:
        if not ed.is_dir():
            continue
        for p in ed.glob("*.md"):
            # разложить пример по нужной папке по имени файла (S-pulse/Q-bunch/...)
            for phase, folder in PHASE_TO_FOLDER.items():
                if phase in p.stem.lower():
                    dest = tmp_path / folder
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy(p, dest / p.name)
                    copied += 1
                    break
    assert copied > 0, "no example loop artifacts found"
    errs = validate_loop_artifacts(tmp_path)
    assert errs == [], f"shipped examples invalid: {errs}"
```

- [ ] **Step 6: Запустить тест — проверить примеры**

Run: `python3 -m pytest sa_documentation/tests/test_examples_valid.py -q`
Expected: PASS (примеры Task 3 валидны; okr-каталог ещё пуст — не мешает).

- [ ] **Step 7: Проверить, что SKILL ссылается на схему**

Run: `grep -c "paf_loop_schema\|nexus_writeback" .claude/skills/sprint-planner/SKILL.md`
Expected: ≥ 2.

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/sprint-planner/ sa_documentation/tests/test_examples_valid.py
git commit -m "feat(sprint-planner): материализация Pulse/Bunch/Harvest + golden-примеры + guard

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Материализация квартального уровня (okr-planner) + квартальный Harvest

**Files:**
- Create: `.claude/skills/okr-planner/examples/loop/Q-pulse.md`
- Create: `.claude/skills/okr-planner/examples/loop/Q-bunch.md`
- Create: `.claude/skills/okr-planner/examples/loop/Q-harvest.md`
- Modify: `.claude/skills/okr-planner/SKILL.md`

**Interfaces:**
- Consumes: схема Task 1, `validate_loop_artifacts` Task 2, тест примеров Task 3 (переиспользуется — он уже сканирует okr-каталог).
- Produces: квартальные loop-артефакты (`level: quarter`) + под-режим `/okr-harvest-quarter`.

- [ ] **Step 1: Создать `examples/loop/Q-pulse.md`**

```markdown
---
nexus: growth
node_id: pulse-q3
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Portfolio Manager
confidence: 0.5
sources: ["okr-context-gen:Q3", "GROUND/NEXUS/market/_index.md"]
updated: 2026-07-08
ttl_days: 90
ripeness: fresh
tags: [pulse]
level: quarter
cycle_ref: Q3
nexus_snapshot:
  market: {ripeness: 0.40, gaps: ["конкурентные ставки не картированы"]}
  growth: {ripeness: 0.30, gaps: ["рычаги NPV не ранжированы"]}
gap_vs_vision: "нет ранжированных рычагов роста относительно квартальной Карты Целей"
intent: "в Q3 сформировать связку Ставок под 3 OBJ и поднять спелость growth"
cp_start: "CP ставок квартала = 0.3"
lens: strategy
---

# Progress Pulse — Q3 (Линза Стратегии/Бизнеса)

> Снимок Нексусов рынка/роста на входе в квартал. Целеполагание портфеля — зона человека (Portfolio Manager).
```

- [ ] **Step 2: Создать `examples/loop/Q-bunch.md`**

```markdown
---
nexus: market
node_id: bunch-q3
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Portfolio Manager
confidence: 0.4
sources: ["okr-deliver:Q3"]
updated: 2026-07-08
ttl_days: 90
ripeness: fresh
tags: [bunch]
level: quarter
goal_map_ref: OKR-Q3
bunch_size: 3
bunch_window: Q3
items:
  - {ref: OBJ-1, kind: bet, trace: "GROUND/NEXUS/market/segment-smb.md", initial_cp: 3}
  - {ref: OBJ-2, kind: lever, trace: "GROUND/NEXUS/growth/activation.md", initial_cp: 2}
gate:
  final_cp: 0.45
  cost_of_risk: "ставка на SMB не окупится при CAC выше плана"
  decision: commit
selection_rationale: "① max mNSM портфеля ② min каннибализация ③ эффект в окне квартала → композитный NPV"
npv_estimate: "[УТОЧНИТЬ: growth тонкий, L2 не разблокирован]"
---

# Bunch квартала — Q3 (Ставки/Рычаги)

> Крупный Банч под Goal Map. Квартальный уровень (без `parent_bunch`). Спринтовые Банчи ссылаются сюда через `parent_bunch: bunch-q3`.
```

- [ ] **Step 3: Создать `examples/loop/Q-harvest.md`**

```markdown
---
nexus: growth
node_id: harvest-q3
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Portfolio Manager
confidence: 0.55
sources: ["okr-harvest-quarter:Q3", "RESULTS/S14-harvest.md"]
updated: 2026-07-08
ttl_days: 90
ripeness: fresh
tags: [harvest]
level: quarter
bunch_ref: bunch-q3
outcomes:
  cp_change: "+0.15 (ставка на SMB частично подтверждена спринтами S12–S14)"
  mNSM_delta: "[УТОЧНИТЬ: growth тонкий]"
  npv_actual: "[УТОЧНИТЬ: L2 не разблокирован]"
insights:
  - "онбординг-рычаг подтверждён на уровне спринтов, требует масштабирования в Q4"
  - "рычаг автоинвойса заблокирован интеграцией БАЗИС"
nexus_writeback:
  - {nexus: growth, node: activation, change: "confidence 0.3->0.45, добавлен рычаг онбординга", source: harvest-q3}
  - {nexus: market, node: segment-smb, change: "ставка частично подтверждена", source: harvest-q3}
next_intent: "вход в Q4-pulse: масштабировать онбординг-рычаг, разблокировать автоинвойс"
---

# Harvest квартала — Q3

> Rollup спринтовых урожаев (`RESULTS/S*-harvest.md`, у которых `rolls_up_to: harvest-q3`). Writeback в `market`/`growth`. Квартальный уровень — без `rolls_up_to`.
```

- [ ] **Step 4: Дополнить `okr-planner/SKILL.md` — материализация + под-режим квартального Harvest**

В `.claude/skills/okr-planner/SKILL.md` добавить секцию (перед финальным разделом/связями скилла):

```markdown
## PAF-петля (квартальный уровень)

OKR-скилл материализует loop-артефакты уровня `quarter` по схеме [[sa_documentation/paf_loop_schema|paf_loop_schema]] (образцы — `examples/loop/`), связывая квартальную Карту Целей с петлёй Product Sprint.

| Стадия | Артефакт | Ключевое |
|---|---|---|
| `/okr-context-gen` | `GROUND/PULSE/{Q}-pulse.md` | снимок Нексусов рынка/роста + intent квартала (`lens: strategy`) |
| `/okr-deliver` | `GROUND/BUNCH/{Q}-bunch.md` | связка Ставок/Рычагов под Goal Map (`level: quarter`, без `parent_bunch`); спринтовые Банчи ссылаются сюда |
| `/okr-harvest-quarter` | `GROUND/RESULTS/{Q}-harvest.md` | **новый под-режим**: конец квартала — rollup спринтовых урожаев (`RESULTS/S*-harvest.md` с `rolls_up_to` = этот Q) → `nexus_writeback` в `market`/`growth` → `next_intent` для Pulse Q+1 |

### Под-режим `/okr-harvest-quarter <quarter>`
Роль: Quarter Harvester. Шаги:
1. Собрать все `GROUND/RESULTS/S*-harvest.md`, у которых `rolls_up_to` = `harvest-{quarter}`.
2. Свести `outcomes.cp_change` и `insights` спринтов в квартальный итог.
3. Сформировать `nexus_writeback` в `market`/`growth` (агрегированный инкремент).
4. Записать `GROUND/RESULTS/{quarter}-harvest.md` (`level: quarter`, owner Portfolio Manager) + применить writeback к узлам Нексуса.
5. Заполнить `next_intent` — вход в Pulse следующего квартала.
STOP после записи → PO ревьюит перед применением writeback.

Правила те же: NPV/mNSM прогрессивно (`[УТОЧНИТЬ]`, не выдумка); артефакт проходит `validate_ground.py`.
```

- [ ] **Step 5: Прогнать guard примеров (теперь и okr-каталог)**

Run: `python3 -m pytest sa_documentation/tests/test_examples_valid.py -q`
Expected: PASS (валидны и sprint-, и okr-примеры).

- [ ] **Step 6: Проверить, что SKILL описывает под-режим**

Run: `grep -c "okr-harvest-quarter\|nexus_writeback\|paf_loop_schema" .claude/skills/okr-planner/SKILL.md`
Expected: ≥ 3.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/okr-planner/
git commit -m "feat(okr-planner): квартальные Pulse/Bunch + под-режим okr-harvest-quarter (rollup+writeback)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Сквозная проверка петли + финальная верификация

**Files:**
- Create: (временно, для смоука) артефакты в изолированной копии — не коммитятся в `GROUND/`.
- Modify: `docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md` (отметка «реализовано»).

**Interfaces:**
- Consumes: всё из Task 1–4.

- [ ] **Step 1: Смоук — один оборот петли на временном GROUND**

Собрать во временной папке связанную цепочку из golden-примеров и проверить сквозную валидность + связность ссылок:

Run:
```bash
python3 - <<'PY'
import pathlib, shutil, tempfile
from sa_documentation.validate_ground import validate_loop_artifacts, _parse_frontmatter
root = pathlib.Path(".").resolve()
tmp = pathlib.Path(tempfile.mkdtemp())
pairs = [
    ("sprint-planner/examples/loop/S-pulse.md",  "PULSE/S14-pulse.md"),
    ("sprint-planner/examples/loop/S-bunch.md",  "BUNCH/S14-bunch.md"),
    ("sprint-planner/examples/loop/S-harvest.md","RESULTS/S14-harvest.md"),
    ("okr-planner/examples/loop/Q-bunch.md",     "BUNCH/Q3-bunch.md"),
    ("okr-planner/examples/loop/Q-harvest.md",   "RESULTS/Q3-harvest.md"),
]
for src, dst in pairs:
    d = tmp / dst; d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(root/".claude/skills"/src, d)
errs = validate_loop_artifacts(tmp)
assert errs == [], errs
# связность вложенности: S-bunch.parent_bunch == Q-bunch.node_id
sb = _parse_frontmatter((tmp/"BUNCH/S14-bunch.md").read_text())
qb = _parse_frontmatter((tmp/"BUNCH/Q3-bunch.md").read_text())
sh = _parse_frontmatter((tmp/"RESULTS/S14-harvest.md").read_text())
qh = _parse_frontmatter((tmp/"RESULTS/Q3-harvest.md").read_text())
assert sb["parent_bunch"] == qb["node_id"], "S-bunch не ссылается на Q-bunch"
assert sh["rolls_up_to"] == qh["node_id"], "S-harvest не роллапится в Q-harvest"
assert sh["nexus_writeback"], "нет writeback — петля не замкнута"
print("SMOKE OK: петля валидна и связна")
PY
```
Expected: `SMOKE OK: петля валидна и связна`.

- [ ] **Step 2: Полный набор тестов зелёный**

Run: `python3 -m pytest sa_documentation/tests/ -q`
Expected: PASS (все: старые 2 + loop 6 + examples 1).

- [ ] **Step 3: Канон методологии не тронут**

Run: `git status --short docs/AI-PROCESSES/ && git log --oneline -5`
Expected: `docs/AI-PROCESSES/` без изменений; 4 коммита Task 1–4 на месте.

- [ ] **Step 4: Отметить спеку реализованной**

В `docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md` в строке `**Status:**` (шапка) дописать: ` · implemented 2026-07-08 (план docs/superpowers/plans/2026-07-08-paf-loop-bridge.md)`.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md
git commit -m "chore(paf-loop): сквозная проверка петли зелёная, спека отмечена реализованной

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- §2 Топология (вложенная петля) → Task 3 (спринт) + Task 4 (квартал) + Task 5 (проверка связности вложенности). ✅
- §3 Схемы (Pulse/Bunch/Harvest) → Task 1 (канон) + Task 2 (валидатор enforce). ✅
- §4 Сборка: `paf_loop_schema.md` → T1; `nexus_process_map §4` → T1; 5 швов → T3(3)+T4(2); новая стадия `okr-harvest-quarter` → T4; `validate_ground.py`+фикстуры → T2. ✅
- §5 Метрики L0/L1/L2 → канон T1 + правила в SKILL T3/T4 + `[УТОЧНИТЬ]` в примерах. ✅
- §6 YAGNI → ничего лишнего не строим (нет Scout/Pitch/Bale скиллов). ✅
- §7 Bridge-deviations → зафиксированы в `paf_loop_schema.md` (T1) и SKILL (T3). ✅
- §8 «done» → Task 5 смоук воспроизводит критерий (оборот цикла + writeback). ✅

**2. Placeholder scan:** `[УТОЧНИТЬ]` в примерах/схеме — намеренная анти-workslop разметка (часть контракта), не заглушка плана. Код валидатора и тесты — полные. Нет TBD/TODO. ✅

**3. Type consistency:** `validate_loop_artifacts`, `_parse_frontmatter`, `_validate_loop_node` — одинаковые сигнатуры в T2 (определение), T3/T5 (использование). Имена папок `PULSE/BUNCH/RESULTS` и `sprint_phase` enum `pulse|bunch|harvest` согласованы во всех задачах и с `nexus_schema.md:28`. Поля примеров (`parent_bunch`, `rolls_up_to`, `gate.decision`, `nexus_writeback`) точно совпадают с проверками валидатора. ✅

---

**Готовность:** план покрывает весь scope §4 спеки, единственный исполняемый контракт (валидатор) под TDD, скилл-правки защищены guard-тестом валидности примеров.
