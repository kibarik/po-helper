# Spec: ATLAS — слой навигации над Нексусами/Кортексами + задачи

**Дата:** 2026-06-27 · **Ветка:** `feat/cortext-backlog` · **Статус:** approved (design)

## 0. Контекст и проблема

`po-helper` («PAF Team OS») хранит знания как markdown-узлы с YAML frontmatter
(`sa_documentation/nexus_schema.md`): `GROUND/NEXUS/**` (empirical-контекст клиента) и
`AI-PROCESSES/**` (normative-фреймворк, 64 ноты). Узлы индексируются семантическим RAG
(ruflo `mcp__ruflo__memory_search`, ns=`ai-kortex`). Агенты Кортекса живут в `.claude/agents/`.

Файлов много, они часто меняются. Узкое место — **навигация**: LLM не должна сканировать
весь vault, а человеку нужен простой способ найти нужный узел. Семантический RAG не
закрывает **структурный/фасетный** запрос («дай все wilting-узлы market с CP<0.5», «какие
задачи привязаны к узлу X»).

**Цель:** тонкий слой навигации НАД существующими файлами — единый хаб для (а) узлов знаний
(Нексусы), (б) агентов (Кортекс), (в) задач/Банчей. Файлы остаются на местах; RAG не трогаем.

### Исследование (deep-research, 2026-06-27)

5 углов, 18 источников, 25 утверждений adversarial-проверено (24 ✓, 1 убито). Выводы:
- Все жизнеспособные OSS-решения хранят **plain markdown + frontmatter** → универсально для
  любой LLM, минимум лок-ина.
- **Obsidian Dataview** (MIT) — авто-индекс/вьюхи прямо из существующего frontmatter, 0
  конвертации; человеческий UI. Минусы: Obsidian-only (нет MCP), деградация на очень больших
  high-churn vault.
- **Backlog.md** (MIT) — задачи как plain .md+frontmatter в `backlog/`, MCP уже подключён в
  сессии, ветка названа под него.
- **Не берём:** Basic Memory (AGPL-3.0 — копилефт-риск для распространяемой коробки), Dendron
  (maintenance mode ~2023 + конфликты md-расширений), filesystem-direct MCP-KB
  (vault-cortex/kObsidian/seekstone — дублируют ruflo-RAG + риск ломки `[[wikilinks]]` при
  rename/move).
- Опровергнуто (0-3): заявление seekstone «~575× меньше токенов vs Obsidian REST» — не цитировать.

**Вывод исследования:** у проекта уже есть RAG → тяжёлый MCP-KB-сервер дублировал бы retrieval.
Правильный слой = **собственный генерируемый манифест** (универсально, без новых зависимостей)
+ Dataview для человека + Backlog.md для задач.

## 1. Решение (обзор)

```
ATLAS/                      ← НОВЫЙ слой навигации (хаб). Источники остаются на местах.
├── README.md               ← entrypoint человек+LLM: что это, как искать
├── INDEX.md                ← человеко-MOC: Нексусы/Кортексы/задачи (Dataview-вьюхи + ген-блок)
├── manifest.json           ← машинный индекс (ГЕНЕРИТСЯ) для LLM-навигации
└── views/                  ← Dataview-вьюхи (опц., человеку)
    ├── by-nexus.md
    ├── wilting.md
    ├── low-cp.md
    └── tasks.md

backlog/                    ← Backlog.md (нативная структура), задачи/Банчи
└── tasks/*.md
```

`ATLAS` — имя хаба (нейтрально, не конфликтует с Нексус/Кортекс и «запрещёнными синонимами»
из `.claude/CORTEX.md`).

**Принципы:**
- ATLAS — **производный, read-mostly** слой: человек правит исходные узлы, не манифест.
- Генератор **только читает** исходники → не ренеймит → не ломает wikilinks.
- `manifest.json` — plain JSON, универсально для любой LLM. **Дополняет** RAG (структурный/
  фасетный поиск), не дублирует семантику.
- Dataview — **опциональная** человеческая надстройка; без неё навигация деградирует к
  `INDEX.md` / `manifest.json` (не хард-зависимость коробки).

## 2. Компоненты

### 2.1 `manifest.json` (центр дизайна)

Плоский JSON, один проход по frontmatter. Контракт:

```json
{
  "generated": "2026-06-27",
  "schema_version": "1.0",
  "nodes": [
    {
      "node_id": "aip-7-harvest",
      "title": "Harvest (Step 7)",
      "kind": "normative",
      "nexus": "product",
      "node_type": "sprint-phase",
      "owner": "Product Engineer",
      "confidence": 1.0,
      "ripeness": "fresh",
      "paf_step": 7,
      "sprint_phase": "harvest",
      "path": "AI-PROCESSES/STEP-7-.../harvest.md",
      "links": ["aip-7-overview"],
      "tags": ["pmf", "fit-point"]
    }
  ],
  "tasks": [
    {
      "task_id": "task-10",
      "title": "Add core search",
      "status": "in-progress",
      "nexus_nodes": ["aip-7-harvest"],
      "path": "backlog/tasks/task-10 - Add core search.md"
    }
  ],
  "nexuses": [
    { "slug": "product", "count": 30, "context_ripeness": 0.72 }
  ],
  "agents": [
    {
      "name": "nexus-builder",
      "phase": "сквозной",
      "path": ".claude/agents/nexus-builder.md"
    }
  ]
}
```

- `nodes[]` — все узлы из `GROUND/NEXUS/**` и `AI-PROCESSES/**` (поля из Node schema §2 схемы).
- `tasks[]` — из `backlog/tasks/*.md` (поля Backlog.md frontmatter + `nexus_nodes`).
- `nexuses[]` — агрегат: `count`, `context_ripeness` (формула `nexus_schema.md` §4).
- `agents[]` — из `.claude/agents/*.md` (имя + фаза цикла Sprint + путь).

### 2.2 `INDEX.md` (человеко-MOC)

Markdown-MOC. Между маркерами `<!-- ATLAS:GENERATED:START -->` … `:END` — ген-блок
(таблица Нексусов с count/Context Ripeness, список агентов, счётчики задач по статусу). Вне
маркеров — ручной текст (как пользоваться). Dataview-вьюхи подключаются ссылками на `views/`.

### 2.3 Генератор: расширить `sa_documentation/nexus_index.py`

Файл уже существует (bulk-реиндекс RAG). Добавляем emit-функцию:
- **Обход:** `GROUND/NEXUS/**.md`, `AI-PROCESSES/**.md` (frontmatter-узлы), `.claude/agents/*.md`,
  `backlog/tasks/*.md`.
- **Парс** frontmatter (тот же парсер, что для RAG) → собрать `nodes/tasks/nexuses/agents`.
- **Context Ripeness** по Нексусу — формула `nexus_schema.md` §4
  (`completeness × freshness`).
- **Запись:** `ATLAS/manifest.json` + регенерация ген-блока в `ATLAS/INDEX.md` (idempotent,
  только между маркерами).
- **Гарантии:** только чтение исходников; идемпотентность (повторный запуск без изменений →
  идентичный вывод); устойчивость к отсутствию опц. полей.
- **Запуск:** вручную (`python3 sa_documentation/nexus_index.py --atlas`) / git-hook / CI.

### 2.4 Связь задача ↔ узел

- Backlog-задача: frontmatter `nexus_nodes: [node_id, ...]` + `[[node_id]]` в теле.
- Генератор резолвит обе стороны → в манифесте `tasks[].nexus_nodes` и (вычисляемые) обратные
  backlinks на стороне узла (через `nodes[].links` остаются wiki-рёбра, backlinks задач —
  отдельным проходом при необходимости).
- Гайдрейл `.claude/CORTEX.md`: «Банч ≠ беклог» — знание (узнаём) и задача (делаем) разные
  сущности, только связаны ссылкой.

### 2.5 Dataview-вьюхи (`ATLAS/views/`, опц.)

MIT-плагин Obsidian, читает frontmatter напрямую (0 конвертации):
- `by-nexus.md` — `TABLE owner, confidence, ripeness GROUP BY nexus`.
- `wilting.md` — `LIST WHERE ripeness = "wilting"`.
- `low-cp.md` — `TABLE WHERE confidence < 0.5`.
- `tasks.md` — задачи по статусу (читает `backlog/` frontmatter).

### 2.6 Backlog.md

Инициализация `backlog/` (`backlog init`) документируется в онбординге; MCP-сервер уже
подключён в окружении (`backlog://workflow/overview`). Используется для задач/Банчей фазы
EXECUTE и рабочих элементов.

## 3. Интеграция в дистрибутив (онбординг)

- `ATLAS/` скелет (README + INDEX с маркерами + пустой views/) — в коробку.
- `nexus_index.py --atlas` — описать в `GROUND/README.md` и/или новом шаге онбординга.
- Backlog.md init — в доках онбординга.
- Dataview — опц. человеческий плагин Obsidian (док-инструкция, не хард-деп).
- (Phase 3, опц., вне этого спека) hook `settings.json` на регенерацию манифеста по событию.

## 4. Не-цели (YAGNI)

- Не переносим существующие файлы (выбран «слой над»).
- Не добавляем MCP-KB-сервер (дубль RAG).
- Не трогаем ruflo-RAG-пайплайн.
- Не автоматизируем event-driven регенерацию в этом спеке (Phase 3).

## 5. Тестирование

- Генератор — TDD (как `ground_schema` валидатор): фикстуры с узлами/задачами/агентами →
  ассерты на структуру `manifest.json`, агрегаты `context_ripeness`, идемпотентность,
  устойчивость к битому/неполному frontmatter.
- Проверка: ген-блок `INDEX.md` обновляется только между маркерами, ручной текст не затронут.

## 6. Открытые вопросы (из исследования, к плану)

- Точный порог производительности Dataview на текущем объёме vault (митигация: scope-запросы
  FROM/#tag/LIMIT).
- Нужен ли отдельный проход backlinks задача→узел в манифест, или достаточно `tasks[].nexus_nodes`.

## 7. Связанные

- `sa_documentation/nexus_schema.md` (Node schema, wilting §4)
- `.claude/CORTEX.md` (агенты, гайдрейлы)
- `GROUND/README.md` (структура vault)
- Источники исследования: Backlog.md (MIT), Obsidian Dataview (MIT), llm-wiki-skills (MIT)
