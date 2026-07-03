# Confluence Indexator — дизайн

- **Дата:** 2026-07-04
- **Статус:** дизайн утверждён PO (brainstorming), готов к `writing-plans`
- **Ветка:** `feat/confluence-indexator`
- **Методология:** Superpowers brainstorming → design → (далее writing-plans)

---

## 1. Проблема и цель

Весь бизнес-продуктовый контекст продукта живёт в Confluence. Для работы AI-агента
PO-helper важен не сам контент, а его **точное распределение по нексусам**, **полная
индексация** и **построение связей**, чтобы агент ориентировался по всей экосистеме и
знал, куда и как обращаться при принятии решений.

**Цель:** repowise-подобный пайплайн, который читает Confluence → осмысляет →
оцифровывает в атомарные узлы node schema → **роутит каждый узел в нужный нексус** →
**строит граф `[[wiki-links]]`** → генерит навигационный MOC. Итог: наполненные
`GROUND/NEXUS/<slug>/` + карта экосистемы для навигации агента.

Аналог repowise: «AI сначала изучает документ, осмысляет, оцифровывает и выстраивает
полное древо зависимостей» — перенесено на корпоративный Confluence и модель нексусов
po-helper.

## 2. Утверждённые требования

| Аспект | Решение |
|---|---|
| Доступ к Confluence | Confluence MCP / REST API — живой доступ, инкрементальный ре-индекс |
| Гранулярность | Семантический разбор (repowise-way): страница → N атомарных узлов разных типов |
| Целевые нексусы | Только существующий реестр (16 нексусов); «бездомное» → очередь `_intake/` |
| Автономия | Гибрид по confidence: уверенное — авто-запись, спорное — очередь PO |
| Граф зависимостей | `[[wiki-links]]` (вкл. кросс-нексусные) + навигационный MOC верхнего уровня |
| Форма решения | Многостадийный пайплайн-скилл (идиома `bft-writer` / `okr-planner`) + детерминированный линтер |

**Инварианты каркаса, которые дизайн обязан соблюдать:**
- **Ноль галлюцинаций** — узел без `sources[]` = workslop, не создаётся
  (`sa_documentation/nexus_schema.md` §2, принцип «Узел без sources = workslop»).
- **Оцифровка ≠ валидация** — ингестированный контекст получает `confidence: 0.3`
  (допущение онбординга, node schema §2.2), CP поднимают уже другие процессы.
- **Открытый slug нексуса** берётся из `GROUND/NEXUS/_registry.yaml` — роутинг только
  в зарегистрированные нексусы; новые не создаём.

## 3. Архитектура: пайплайн из 6 стадий

Скилл-пакет `confluence-indexator` = оркестратор `/cindex` + 6 команд-стадий. Каждая
стадия — отдельный запуск, своя роль, свой артефакт, **STOP**-пауза между ними (зеркало
`bft-writer`). Стадии повторяют repowise «study → comprehend → digitize → link» плюс
роутинг и отгрузку под модель нексусов.

```
/cindex-crawl       → Crawler        обход пространства через Confluence MCP:
                                      inventory страниц (id, title, ancestors, labels,
                                      links, space) + сырой контент
                                      → artefacts/confluence/inventory.json     [STOP: PO подтверждает scope/фильтры]
      ↓
/cindex-comprehend  → Comprehender   постранично осмысляет (о чём страница, сущности,
                                      rich picture), авто-batch
                                      → artefacts/confluence/comprehension/<id>.md
      ↓
/cindex-digitize    → Digitizer      выделяет атомарные узлы-кандидаты по node schema
                                      (node_type, черновик, sources=URL)
                                      → artefacts/confluence/nodes-draft.jsonl
      ↓
/cindex-route       → Router         классифицирует каждый узел в нексус реестра +
                                      route_confidence; спорное → очередь _intake/
                                      → artefacts/confluence/routing.jsonl (dry-run)
      ↓
/cindex-link        → Linker         строит [[wiki-links]] (внутри и кросс-нексус)
                                      из ссылок Confluence + семантической близости
                                      → рёбра в routing plan
      ↓
/cindex-deliver     → Deliverer      сухой прогон → ок PO → запись узлов в
                                      GROUND/NEXUS/<slug>/, обновление _index.md,
                                      генерация навигационного MOC, _intake/unrouted,
                                      линт графа                                 [STOP: dry-run → ок PO]
```

Резюмируемость: промежуточные артефакты в `artefacts/confluence/`; любую стадию можно
перезапустить, не теряя предыдущие.

## 4. Компоненты и раскладка файлов

```
.claude/skills/confluence-indexator/
  SKILL.md                    # оркестратор: pipeline, принципы, STOP-логика
  resources/
    node_schema.md            # ссылка на sa_documentation/nexus_schema.md (не дублируем)
    routing_table.md          # правила Confluence-сигнал → node_type → нексус (§5)
    confidence_rules.md       # пороги: авто-запись vs очередь _intake/ (§6)
    linking_rules.md          # как строить [[wiki-links]] + кросс-нексус (§7)
    moc_template.md           # шаблон навигационного MOC (§7)
  examples/
    ideal_node.md             # эталон узла из Confluence-страницы
    ideal_routing.jsonl       # эталон dry-run плана
.claude/commands/cindex-*.md  # 6 команд-стадий + /cindex (оркестратор)
sa_documentation/
  lint_graph.py               # линтер: битые [[links]], узлы без sources, orphan (§8)
```

## 5. Маппинг Confluence → node_type → нексус

Ядро `routing_table.md`. Роутинг только в существующий реестр; одна страница может дать
несколько узлов разных строк (семантический разбор), они попадают в разные нексусы, связь
сохраняется через `[[wiki-links]]`.

| Сигнал на странице | node_type | Целевой нексус |
|---|---|---|
| ADR / «Решение», «выбрали X потому что» | `decision` | `precedents` (или `system-landscape` для тех-решений) |
| Бизнес-правило BR-*, «система должна» | `rule` | `requester-domain` |
| Термин глоссария, Ubiquitous Language | `term` | `requester-domain` / `product` |
| Метрика, KPI, целевое значение | `metric` | `strategy` (KR) / `growth` |
| Сервис/API/интеграция/поток данных | `component` | `system-landscape` |
| Требование закон/стандарт/политика/security | `regulation` | `compliance` |
| SLA/НФТ/производительность | `nfr` | `compliance` |
| Риск, угроза, «что если» | `risk` | `problem` / `capacity` |
| Персона, роль, владелец, RACI | `person` | `team` |
| Внешняя команда, зона ответственности | (ext-team) | `landscape` / `ownership` |
| Сегмент, JTBD, боль клиента | (empirical) | `customer` |
| Конкурент, рыночная динамика | (empirical) | `market` |
| Roadmap, OKR, приоритет квартала | (empirical) | `strategy` |
| Ничего из выше / уверенность низкая | — | `_intake/unrouted.md` (очередь PO) |

> Примечание: строки с двумя нексусами («precedents / system-landscape») разрешаются
> Router'ом по контексту страницы; при неоднозначности — понижение `route_confidence`
> и уход в очередь (см. §6).

## 6. Поток данных и confidence-гейт

**Артефакты** (в `artefacts/confluence/`):

`inventory.json` — карта пространства после crawl:
```json
{"space":"PROD","crawled_at":"2026-07-04",
 "pages":[{"id":"131074","title":"Платёжный шлюз","ancestors":["Архитектура"],
           "labels":["adr","payments"],"links":["131099"],"url":"https://.../131074"}]}
```

`nodes-draft.jsonl` — один узел-кандидат на строку (после digitize):
```json
{"tmp_id":"n-131074-1","node_type":"decision","source_page":"131074",
 "title":"Выбор синхронного платёжного потока","body":"...",
 "sources":["confluence:https://.../131074"]}
```

`routing.jsonl` — dry-run план (после route+link), то, что PO видит перед записью:
```json
{"tmp_id":"n-131074-1","node_type":"decision","target_nexus":"precedents",
 "node_id":"precedents-sync-payment-flow","route_confidence":0.82,
 "links":["[[system-landscape-payment-gateway]]"],"action":"auto"}
{"tmp_id":"n-131099-3","node_type":"risk","target_nexus":null,
 "route_confidence":0.34,"action":"queue","reason":"нет уверенного нексуса"}
```

**Два независимых показателя уверенности — не путать:**
- `route_confidence` (уверенность классификации узла в нексус): ≥ **0.7** → `action: auto`;
  < 0.7, конфликт двух нексусов, или orphan → `action: queue` → `_intake/unrouted.md`.
- `confidence` самого **узла** = **0.3** всегда (онбординг-допущение из Confluence,
  node schema §2.2). `ttl_days` по нексусу: market/customer=90, growth=60, прочее=180.

## 7. Построение графа и навигационный MOC

**Рёбра = `[[wiki-links]]`** (`linking_rules.md`):
1. **Структурные** — из `ancestors`/`links` Confluence (родитель-потомок, явные ссылки
   страниц) переносятся в связи узлов.
2. **Семантические** — узлы, ссылающиеся на общую сущность (тот же сервис/термин/метрика),
   линкуются кросс-нексусно (напр. `decision` в `precedents` ↔ `component` в
   `system-landscape`).
3. Ссылка на ещё-не-созданный узел допустима (Obsidian-стиль), но помечается линтером.

**Навигационный MOC** `GROUND/NEXUS/_map.md` (генерит Deliverer) — даёт агенту «знать,
куда обратиться»:
- **Карта экосистемы**: по каждому нексусу — число узлов, ключевые узлы, ripeness-сводка.
- **Маршруты «вопрос → нексус/узел»**: таблица «тип вопроса → куда идти» (напр. «почему
  приняли решение X» → `precedents`; «какой SLA» → `compliance`; «кто владелец домена Y» →
  `ownership`/`team`).
- **Кросс-нексусные мосты**: список межнексусных рёбер — где темы связаны.

## 8. Обработка ошибок, идемпотентность, тестирование

**Ошибки по стадиям:**
- **Crawl**: недоступ MCP / 401 / rate-limit → стадия STOP с понятным сообщением,
  `inventory.json` не перезаписывается. Пустые/архивные страницы пропускаются с пометкой.
- **Comprehend/Digitize**: страница без явных сущностей → 0 узлов + запись в
  `artefacts/confluence/skipped.md` (честный «нечего оцифровать»). Узел-кандидат без
  `sources[]` не создаётся вовсе.
- **Route/Link**: нет уверенного нексуса / конфликт → не гадаем, `action: queue` →
  `_intake/unrouted.md`. Ссылка на несуществующий узел допустима, ловит линтер.
- **Deliver**: пишет только `action: auto` и только после ок PO на dry-run. Падение на
  середине записи безопасно — повторный прогон идемпотентен.

**Идемпотентность и ре-индекс** (живой доступ позволяет):
- `node_id` детерминированный из `source_page` + слаг заголовка → ре-индекс той же
  страницы обновляет тот же узел, а не плодит дубли.
- Узел несёт `sources: ["confluence:<url>"]` + `updated`. При ре-индексе Deliverer
  сравнивает: изменилась страница → обновляет `body`+`updated`, пересчитывает `ripeness`;
  не изменилась → пропускает.
- Ручные правки PO защищены: узел с `tags: [po-edited]` не перетирается — расхождение
  кладётся в `_intake/` на ревью.
- Удалённая в Confluence страница → узел не удаляется молча, помечается `ripeness: wilting`
  + запись в `_intake/` (решает PO).

**Тестирование и verify:**
- **Юнит-фикстуры** `sa_documentation/tests/fixtures/`: мок-`inventory.json` (ADR,
  глоссарий, риск-без-нексуса) → ожидаемый `routing.jsonl`. Проверяем детерминизм
  роутинга и генерацию `node_id`.
- **`lint_graph.py`** (новый детерминированный скрипт в стиле `validate_ground.py`) —
  гейт `verify`: битые `[[wiki-links]]` за пределами known node_id, узлы без `sources[]`,
  orphan-узлы (0 рёбер), невалидные `node_type`/`nexus` vs реестр. Возвращает список
  ошибок (пустой = OK).
- **`validate_ground.py`** — прогоняется после `deliver`: реестр/структура нексусов целы.
- **Golden-пример** `examples/ideal_node.md` + `ideal_routing.jsonl` — эталон для
  калибровки Digitizer/Router.

## 9. Вне рамок (YAGNI)

- Авто-создание новых нексусов (решено: только существующий реестр + очередь).
- Внешнее графовое хранилище / GraphRAG (решено: истина в markdown-волте + MOC).
- Двусторонняя синхронизация обратно в Confluence (только чтение из Confluence).
- Валидация контента (оцифровка ≠ валидация; CP поднимают другие процессы).

## 10. Открытые вопросы к стадии writing-plans

- Конкретный Confluence MCP-сервер и его инструменты (обнаружить/подключить на стадии
  плана; сейчас в `.mcp.json` только `ruflo`/`backlog`).
- Формат `_map.md` — согласовать с существующим `GROUND/NEXUS/_index.md`, чтобы не
  дублировать MOC (возможно, `_map.md` расширяет `_index.md`, а не заменяет).
