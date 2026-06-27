# Blueprint Pipeline — дизайн (spec)

**Дата:** 2026-06-25
**Статус:** design approved, к реализации
**Автор контекста:** PAF Team OS / GROUND Vault

---

## 1. Цель

Pipeline, который строит **BluePrint-диаграмму** — финальную, понятную всем сторонам (бизнес, продакт, технари, Delivery) форму. Диаграмма верхнеуровнево описывает **полный Scope задачи** от точки старта взаимодействия до финальной точки: что меняется и **на каком уровне** (слое) системы.

Blueprint — не самоцель, а **выход pipeline**. Pipeline собирает каноническую промежуточную модель (**Scope Model**), которая:

- **обогащается** из готового БФТ (режим ENRICH), либо
- **собирается с нуля** через исследование (режим SCRATCH).

Оба режима сходятся в общей Scope Model → единый рендер.

---

## 2. Место в экосистеме

- После `bft-writer` (БФТ готов) → blueprint pipeline визуализирует scope. Мост между БФТ (бизнес) и `/arch-gen` (C4-тех) / `/data-trace` (dataflow).
- Blueprint **верхнеуровневый** — НЕ заменяет C4/sequence/dataflow. Детали реализации → отсыл к `/arch-gen`, `/data-trace`.
- Вписан в SA-Helper конвенции (`/context-gen → ... → /validate-doc`) и в GROUND Vault (zero-hallucination, sources[], Nexus).

---

## 3. Форма pipeline

Отдельные `/blueprint-*` команды (как FNR-пайплайн), цепляемые, resumable, инспектируемые.

```
/blueprint-context              Подготовка: есть ли БФТ? Nexus? config → выбор режима (ENRICH | SCRATCH)
        │
        ├── [ENRICH]  /blueprint-extract    БФТ есть → Scope Model из БФТ (grounded, trace к разделам)
        │
        └── [SCRATCH] /blueprint-discover   БФТ нет → Scope Model с нуля через исследование
        │                                    (делегирует в /context-gen, scouting-агент, problem-analyst, Nexus)
        ▼
/blueprint-model     ◄── точка слияния. Нормализовать Scope Model:
                         journey × слои, scope-of-change маркеры, GAPs, валидация к источникам
        ▼
/blueprint-render        Grid-таблица + Mermaid + render-repair ЖЁСТКИЙ ГЕЙТ → финальный blueprint.md
```

5 скилл-файлов: `blueprint-context`, `blueprint-extract`, `blueprint-discover`, `blueprint-model`, `blueprint-render`.

---

## 4. Канонический артефакт — Scope Model

Общая для обоих режимов структурированная модель. Хранится на диске → resumable, инспектируемо, трассируемо.

**Путь:** `GROUND/BLUEPRINT/<task>/scope-model.yaml`

**Схема (черновик, финализируется в реализации):**

```yaml
task: <slug>                      # ascii-slug задачи
title: <человекочитаемое имя>
mode: enrich | scratch            # как собрана модель
created: <YYYY-MM-DD>
confidence: <0..1>                # покрытие источниками (CR-подобно)
sources:                          # все источники модели (БФТ-разделы, Nexus-узлы, web-URL, интервью)
  - {id: S1, kind: bft|nexus|web|interview, ref: <раздел/URL/узел>}

trigger:                          # точка старта взаимодействия
  actor: <кто инициирует>
  event: <что запускает>
  source: S1

end_state:                        # финальная точка
  outcome: <результат>
  source: S1

actors:                           # участники
  - {id: A1, name: <актёр>, source: S1}

journey:                          # горизонтальная ось — шаги happy-path, по порядку
  - {step: 1, name: <шаг>, actor: A1, source: S1}

layers:                           # вертикальные слои (lanes) — см. §5
  - {id: L_actor, name: "Actor / Customer"}
  - {id: L_frontstage, name: "Frontstage / UX-UI"}
  - {id: L_backstage, name: "Backstage / App-logic"}
  - {id: L_integration, name: "Integrations / Services"}
  - {id: L_data, name: "Data"}
  - {id: L_external, name: "External / Support"}

cells:                            # ячейки journey × layer = что происходит
  - {step: 1, layer: L_frontstage, action: <действие>, scope: changed|affected|context, source: S1}

scope_of_change:                  # сводка областей изменения (для бизнеса)
  - {layer: L_backstage, summary: <что меняется>, marker: changed, source: S1}

gaps:                             # явные пробелы — НЕ выдумка
  - {about: <чего не хватает>, note: <вопрос>}
```

**Правило:** каждый `actor`/`journey.step`/`cell`/`scope_of_change` обязан иметь `source`. Нет источника → элемент уходит в `gaps`, не в модель.

---

## 5. Структура диаграммы (гибрид Journey × Слои)

**Горизонталь = Journey:** trigger → шаги happy-path → end_state.

**Вертикаль = Слои (lanes)** + канонические линии Service Blueprint:

| Слой | Что показывает |
|---|---|
| **Actor / Customer** | кто инициирует, действия |
| ⎯ *line of interaction* ⎯ | |
| **Frontstage / UX-UI** | экраны, touchpoints (что видит юзер) |
| ⎯ *line of visibility* ⎯ | |
| **Backstage / App-logic** | FE+BE логика |
| **Integrations / Services** | API, внутр./внеш. сервисы |
| **Data** | хранилища, что меняется в данных |
| **External / Support** | внешние системы |

**Маркеры scope:** 🔴 changed · 🟡 affected · ⚪ context. Только при явном указании источника, иначе `(?) GAP`.

---

## 6. Стадии pipeline (детально)

### 6.1 `/blueprint-context`
- Читает: БФТ-файл (если указан/найден), `GROUND/config.yaml`, реестр Nexus, `sa_documentation/naming_conventions.md` (ноль выдуманных терминов).
- Детект режима: БФТ есть → ENRICH; нет → SCRATCH.
- Создаёт `GROUND/BLUEPRINT/<task>/` + пустой `scope-model.yaml` (frontmatter, sources[]).
- Выход: режим + список доступных источников.

### 6.2 `/blueprint-extract` (ENRICH)
- Вытаскивает из БФТ: trigger, end_state, actors, journey-шаги, systems, data, **что меняется**.
- Каждый элемент → `source` = раздел БФТ.
- Пробел в БФТ → добор из Nexus (с source) → иначе в `gaps`.
- Пишет `scope-model.yaml`.

### 6.3 `/blueprint-discover` (SCRATCH)
- Делегирует в существующие скиллы (не дублирует логику):
  - `/context-gen` — подготовка контекста;
  - scouting-агент — возможности/системы/актёры (3 Линзы PAF);
  - problem-analyst — структура проблемы/journey;
  - `mcp__ruflo__memory_search` / Nexus — контекст продукта.
- Каждый собранный факт = с источником (интервью-ответ / Nexus-узел / web-URL).
- Нет источника → `gaps`, не в модель.
- Пишет `scope-model.yaml`.

### 6.4 `/blueprint-model` (точка слияния)
- Нормализует Scope Model: упорядочивает journey, раскладывает cells по journey × layer, проставляет scope-маркеры.
- **Гейт валидации (self-review):** все journey-шаги покрыты? все меняемые слои отражены? каждая ячейка имеет source? нет выдуманных систем/актёров (omissions + hallucinations)? Фикс или в `gaps`.
- Выход: валидная нормализованная модель.

### 6.5 `/blueprint-render`
- Из Scope Model генерит **два синхронных артефакта**:
  1. **Blueprint Grid** — Markdown-таблица строки=слои × колонки=шаги (детерминированный план, тривиально верный, читаемый);
  2. **Mermaid** `flowchart` — subgraph на слой, узлы=шаги, scope-области через `class`/style, линии visibility/interaction, легенда.
- **Render-repair ЖЁСТКИЙ ГЕЙТ:**
  - Рендер Mermaid (CLI `mmdc` / `npx @mermaid-js/mermaid-cli`, иначе доступный валидатор).
  - Ошибка → авто-repair (код + лог ошибки обратно модели → фикс), до N=3 попыток.
  - **После N попыток ошибка ИЛИ валидатор недоступен → СТОП.** Скилл не завершается, не отдаёт битый артефакт. Выводит:
    ```
    ⛔ Не могу продолжить: ошибка рендера Mermaid.
    Для успешного завершения задачи нужно исправить:
    <точный лог ошибки + проблемная строка>
    Задача НЕ завершена, пока Mermaid не рендерится чисто.
    ```
  - Задача = `done` только при чистом рендере. Иначе `blocked`.
- Пишет финал `GROUND/BLUEPRINT/<task>/blueprint.md`: frontmatter (sources[], confidence/CR), Grid-таблица, Mermaid-блок, легенда, **Scope-summary** (для бизнеса, 1 экран), **Open questions / GAPs**, **trace-таблица** (элемент → источник).

---

## 7. Guardrails (zero-hallucination)

- Каждый узел диаграммы трассируется к источнику (БФТ-раздел / Nexus / web / интервью). Нет источника → `(?) GAP`, не выдумка.
- Scope-маркер только при явном указании источника.
- Верхнеуровнево: детали реализации → отсыл к `/arch-gen`, `/data-trace`.
- **Валидный Mermaid-рендер — обязательное условие завершения** (блокирующий гейт §6.5).
- Idempotent: существующий `blueprint.md` / `scope-model.yaml` не затирать без подтверждения.
- Ноль выдуманной PAF-терминологии (`sa_documentation/naming_conventions.md`).

---

## 8. Для аудитории (бизнес / продакт / технари / Delivery)

- **Grid-таблица** — точный план, читается всеми.
- **Mermaid** — визуал «область изменения с одного взгляда» (цветовые маркеры).
- **Scope-summary** — 1 экран для бизнеса/продакта.
- **Open questions / GAPs** — честно показывает неизвестное.
- **Trace-таблица** — для технарей/Delivery: откуда что взято.

---

## 9. Раскладка файлов

```
.claude/skills/blueprint-context/SKILL.md
.claude/skills/blueprint-extract/SKILL.md
.claude/skills/blueprint-discover/SKILL.md
.claude/skills/blueprint-model/SKILL.md
.claude/skills/blueprint-render/SKILL.md
.claude/skills/blueprint-render/references/   # схема Scope Model, описание слоёв, Mermaid-шаблон, легенда
```

Выход pipeline:

```
GROUND/BLUEPRINT/<task>/scope-model.yaml      # промежуточная модель (общая для обоих режимов)
GROUND/BLUEPRINT/<task>/blueprint.md          # финал (Grid + Mermaid + summary + gaps + trace)
```

---

## 10. Открытые вопросы к реализации

- Финальная схема `scope-model.yaml` (поля, валидатор — по образцу `validate_ground.py`?).
- Точный Mermaid-шаблон гибрида journey × слои (subgraph-раскладка, выравнивание колонок, styling scope-маркеров).
- Нужен ли валидатор Scope Model (Python, как `validate_ground.py`), или достаточно self-review-гейта в `/blueprint-model`.
- Формат frontmatter blueprint.md — переиспользовать `nexus_schema.md` или свой облегчённый.
