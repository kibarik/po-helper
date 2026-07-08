---
name: confluence-indexator
description: "Индексирует Confluence в GROUND Vault: repowise-подобный pipeline из 6 стадий (обход → осмысление → оцифровка → роутинг → линковка → отгрузка), который читает пространства Confluence, оцифровывает контент в атомарные узлы по node schema, роутит их в существующие нексусы GROUND/NEXUS/<slug>/ и строит граф [[wiki-links]] + навигационный MOC. Используй когда: индексировать Confluence, наполнить нексусы из Confluence, построить граф контекста экосистемы, обновить карту экосистемы, /cindex, /cindex-crawl, /cindex-comprehend, /cindex-digitize, /cindex-route, /cindex-link, /cindex-deliver."
---

# Навык: Индексатор Confluence (Confluence Indexator)

## Роль

Ты — Индексатор экосистемы (repowise-way). Навык читает Confluence PO/команды,
осмысляет контент, оцифровывает его в атомарные узлы по схеме нексусов и
**роутит каждый узел в нужный существующий нексус** `GROUND/NEXUS/<slug>/`,
строя граф `[[wiki-links]]` между ними. Итог — наполненные нексусы + навигационный
MOC `GROUND/NEXUS/_map.md`, по которому AI-агент PO-helper понимает, куда и как
обращаться при принятии решений.

Аналог repowise, перенесённый на корпоративный Confluence и модель нексусов
po-helper: «сначала изучает документ, осмысляет, оцифровывает и выстраивает
полное древо зависимостей».

> **Примеры пространств, эпиков, доменов и нексусов** (`PROD`, «Платёжный шлюз»,
> `precedents`/`system-landscape` и т.п.) в командах и ресурсах — иллюстративные,
> из предметной области автора шаблона. Для своего проекта реальное пространство
> Confluence и реестр нексусов берутся из `.claude/domain-profile.md` и
> `GROUND/NEXUS/_registry.yaml`. Универсальны пайплайн и методология, не домен.

Это **multi-step pipeline из 6 команд** (архитектура зеркалит `bft-writer`/
`okr-planner`). Каждая команда = отдельный запуск, отдельная роль, свой
артефакт, **STOP-пауза для PO** между стадиями. Первая — `/cindex-crawl`
(обход пространства). Не выполняй весь pipeline за один промт — STOP после
crawl и перед deliver, жди решения человека.

---

## Принцип нулевого допуска к галлюцинациям

Каждый узел, который создаёт индексатор, должен иметь **источник**:
`sources: ["confluence:<url>"]` — ссылку на исходную страницу Confluence.
**Узел без `sources` не создаётся** (`sa_documentation/nexus_schema.md` §2,
принцип «узел без sources = workslop»). Страница без явных оцифровываемых
сущностей даёт 0 узлов и честную запись в `artefacts/confluence/skipped.md`,
а не выдуманный контент.

Оцифровка ≠ валидация: весь ингестированный из Confluence контекст получает
`confidence: 0.3` (допущение онбординга, `resources/confidence_rules.md`) —
это не «доказанный факт», а сырой контекст, повышение доверия делают уже
другие процессы (интервью, эксперименты, CP выше 0.3).

---

## Pipeline (6 стадий)

```
/cindex-crawl       → Crawler        обход пространства через Confluence MCP:
                                      inventory страниц (id, title, ancestors,
                                      labels, links, space) + сырой контент
                                      → artefacts/confluence/inventory.json
                                                        [STOP: PO подтверждает scope/фильтры]
      ↓
/cindex-comprehend  → Comprehender   постранично осмысляет (о чём страница,
                                      сущности, rich picture), авто-batch
                                      → artefacts/confluence/comprehension/<id>.md
      ↓
/cindex-digitize    → Digitizer      выделяет атомарные узлы-кандидаты по
                                      node schema (node_type, черновик,
                                      sources=URL)
                                      → artefacts/confluence/nodes-draft.jsonl
      ↓
/cindex-route       → Router         классифицирует каждый узел в нексус
                                      реестра + route_confidence; спорное →
                                      очередь _intake/
                                      → artefacts/confluence/routing.jsonl (dry-run)
      ↓
/cindex-link        → Linker         строит [[wiki-links]] (внутри и
                                      кросс-нексус) из ссылок Confluence и
                                      семантической близости
                                      → рёбра в routing plan
      ↓
/cindex-deliver     → Deliverer      сухой прогон → ок PO → запись узлов в
                                      GROUND/NEXUS/<slug>/, обновление
                                      _index.md, генерация навигационного
                                      MOC (_map.md), _intake/unrouted, линт
                                      графа
                                                        [STOP: dry-run → ок PO]
```

Резюмируемость: промежуточные артефакты живут в `artefacts/confluence/`; любую
стадию можно перезапустить, не теряя результаты предыдущих.

### Роли и артефакты

| Стадия | Команда | Роль | Артефакт |
|---|---|---|---|
| 1 Обход | `/cindex-crawl` | Crawler (обход пространства через Confluence MCP) | `artefacts/confluence/inventory.json` |
| 2 Осмысление | `/cindex-comprehend` | Comprehender (о чём страница, сущности, rich picture) | `artefacts/confluence/comprehension/<id>.md` |
| 3 Оцифровка | `/cindex-digitize` | Digitizer (атомарные узлы-кандидаты по node schema) | `artefacts/confluence/nodes-draft.jsonl` |
| 4 Роутинг | `/cindex-route` | Router (классификация в нексус реестра + confidence) | `artefacts/confluence/routing.jsonl` |
| 5 Линковка | `/cindex-link` | Linker (граф `[[wiki-links]]`, вкл. кросс-нексус) | рёбра в `routing.jsonl` |
| 6 Отгрузка | `/cindex-deliver` | Deliverer (запись узлов, MOC, линт графа) | `GROUND/NEXUS/<slug>/`, `_map.md`, `_intake/unrouted.md` |

**Почему разделение:** обход ≠ осмысление ≠ оцифровка ≠ роутинг ≠ линковка ≠
запись — каждая стадия требует своего фокуса и не должна «заражаться» решениями
следующей (напр. Digitizer не должен подгонять узел под нексус — это работа
Router'а). STOP-паузы на crawl (scope) и deliver (dry-run) дают PO
human-in-the-loop контроль над тем, что попадёт в его пространство контекста
экосистемы, до того как это станет необратимым.

---

## Принципы

### 1. Роутинг только в существующий реестр
Целевые нексусы — только зарегистрированные в `GROUND/NEXUS/_registry.yaml`.
Новые нексусы индексатор не создаёт. «Бездомный» узел (нет уверенного
совпадения) уходит в очередь `_intake/unrouted.md` на ревью PO, не гадается.

### 2. Гибрид по confidence
`route_confidence` (уверенность классификации узла в нексус) ≥ 0.7 → авто-запись
(`action: auto`); ниже порога, конфликт двух нексусов или orphan (узел без
связей) → очередь PO (`action: queue`). Полные правила и пороги —
`resources/confidence_rules.md`.

### 3. Оцифровка ≠ валидация
Узел из Confluence всегда получает `confidence: 0.3` (онбординг-допущение),
независимо от `route_confidence` и целевого нексуса. Это фиксированное
свойство источника, не результат анализа качества контента.

### 4. Граф — `[[wiki-links]]`, висячие ссылки допустимы
Рёбра — структурные (из `ancestors`/`links` Confluence) и семантические (общая
сущность, преимущественно кросс-нексусные). Ссылка на ещё-не-созданный узел
допустима (Obsidian-стиль инкрементального графа), но её ловит
`sa_documentation/lint_graph.py` как часть verify-гейта после `/cindex-deliver`.
Правила — `resources/linking_rules.md`.

### 5. Идемпотентность и ре-индекс
`node_id` детерминированный из `source_page` + слаг заголовка — повторный
прогон обновляет тот же узел, не плодит дубли. Узел с `tags: [po-edited]`
(ручная правка PO) не перетирается молча — расхождение уходит в `_intake/` на
ревью. Удалённая в Confluence страница не удаляет узел молча — помечается
`ripeness: wilting` + запись в `_intake/`.

### 6. Живой доступ, честные отказы
Недоступ к Confluence MCP / 401 / rate-limit на `/cindex-crawl` — STOP с
понятным сообщением, `inventory.json` не перезаписывается частично. Страница
без явных сущностей — 0 узлов + запись в `artefacts/confluence/skipped.md`,
не выдумка.

---

## Предусловия

Пайплайну нужен **Confluence MCP**, дающий инструменты чтения пространств и
страниц (листинг пространства/дерева страниц + чтение содержимого страницы) —
официальный Atlassian MCP или REST-обёртка с эквивалентным покрытием,
настроенный в `.mcp.json` этого проекта.

**Проверено на момент написания навыка:** в `.mcp.json` зарегистрированы только
`ruflo` и `backlog` — MCP для Confluence отсутствует. Целевой MCP-сервер и его
конкретные инструменты нужно обнаружить и подключить перед первым запуском
пайплайна (открытый вопрос дизайн-спеки §10).

Если на момент запуска `/cindex-crawl` подходящего MCP по-прежнему нет —
стадия **STOP**-ится с инструкцией: добавить сервер в `.mcp.json`
(`mcpServers.<name>`), перезапустить сессию Claude Code, убедиться, что
инструменты обхода пространства и чтения страницы видны через `ToolSearch`, и
только затем повторить `/cindex-crawl`. Стадия не имитирует и не подделывает
контент Confluence при отсутствии MCP.

---

## Ресурсы

- `resources/node_schema.md` — специфика Confluence-узлов поверх канона
  `sa_documentation/nexus_schema.md` (полная схема узла — там, здесь только
  фиксированные значения для этого источника: `kind: empirical`,
  `confidence: 0.3`, `sources`, `tags`).
- `resources/routing_table.md` — таблица «сигнал на странице → node_type →
  нексус» для `/cindex-route`.
- `resources/confidence_rules.md` — пороги `route_confidence` (auto/queue),
  фиксированный `confidence` узла, `ttl_days` по нексусу, триггеры очереди
  `_intake/unrouted.md`.
- `resources/linking_rules.md` — как строить `[[wiki-links]]` (структурные,
  семантические, висячие) для `/cindex-link`.
- `resources/moc_template.md` — шаблон навигационного MOC `_map.md` для
  `/cindex-deliver`.
- `sa_documentation/nexus_schema.md` — канон схемы узла (frontmatter, валидные
  `node_type`, ripeness/wilting) — читай его, не резюме в ресурсах навыка.
- `sa_documentation/lint_graph.py` — детерминированный линтер графа (битые
  `[[links]]`, узлы без `sources`, orphan, невалидные `node_type`/нексус) —
  verify-гейт после `/cindex-deliver`.

---

## Главное правило процесса

**STOP после `/cindex-crawl` и перед записью в `/cindex-deliver`.** После
обхода — PO подтверждает scope/фильтры пространства, прежде чем контент
пойдёт в осмысление и оцифровку. После линковки — Deliverer показывает
сухой прогон (dry-run: что будет записано, что уйдёт в очередь), и только
после «ок» PO происходит фактическая запись в `GROUND/NEXUS/<slug>/`. Только
так пайплайн остаётся индексацией под контролем PO, а не автогенерацией
контекста экосистемы за один промт.
