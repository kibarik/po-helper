---
description: 'Отгрузка узлов Confluence в GROUND: запись нексусов, MOC, очередь intake, линт-гейты (роль: Deliverer). Сухой прогон → ок PO → запись'
---

## Использование

```
/cindex-deliver <space_key>
```

Вход: `artefacts/confluence/routing.jsonl`. Выход: узлы в
`GROUND/NEXUS/<slug>/`, обновлённые `_index.md`, `GROUND/NEXUS/_map.md`,
`GROUND/_intake/unrouted.md`.

## Важно

**Роль: Deliverer.** Финальная (6-я) стадия pipeline после `/cindex-link`.
Берёшь готовый routing-план (нексус + `node_id` + `[[links]]` на каждую
запись) и материализуешь его в `GROUND Vault`: пишешь узлы, обновляешь
индексы нексусов, генерируешь навигационный MOC, ставишь неоднозначное в
очередь PO, прогоняешь линт-гейты.

**Анти-правило (приоритет):** запись в `GROUND/NEXUS/` — только после
явного «ок» PO. Команда работает в 2 такта:
1. **Сухой прогон** — сводка плана (сколько auto/queue, по каким нексусам,
   сколько рёбер) БЕЗ записи, STOP.
2. После «ок» PO — запись узлов, `_index.md`, `_map.md`, `_intake/`, линт.

**Ноль галлюцинаций (жёсткое правило):** пишется только то, что уже несёт
`sources` из `routing.jsonl`/`nodes-draft.jsonl`. Deliverer не придумывает
содержимое узла заново — только переносит и оформляет по node schema.

---

## Инструкция для LLM

### ТАКТ 1. СУХОЙ ПРОГОН (без записи)

#### Этап 1: Загрузка входа и правил

1. Прочитай `artefacts/confluence/routing.jsonl`. Нет файла →
   `[УТОЧНИТЬ: запусти /cindex-route <space_key> и /cindex-link <space_key>]`.
2. Прочитай `artefacts/confluence/nodes-draft.jsonl` — источник `title`,
   `body`, `sources`, `source_page` для join по `tmp_id`.
3. Прочитай `sa_documentation/nexus_schema.md` §2 — полный список полей
   frontmatter Узла и признак обязательности; §4 — формула `ripeness` из
   `updated`+`ttl_days`.
4. Прочитай `.claude/skills/confluence-indexator/resources/node_schema.md` —
   фиксированные значения Confluence-узла (`kind: empirical`,
   `confidence: 0.3`, `tags` включает `confluence-indexed`).
5. Прочитай `.claude/skills/confluence-indexator/resources/confidence_rules.md`
   §3 — `ttl_days` по нексусу (`market`/`customer`=90, `growth`=60, прочие=180).
6. Прочитай `GROUND/NEXUS/_registry.yaml` — список зарегистрированных `slug`
   (единственный допустимый набор `target_nexus`, Router уже это гарантировал,
   но Deliverer не доверяет слепо — перепроверяет перед записью).
7. Прочитай `.claude/skills/confluence-indexator/resources/moc_template.md` —
   шаблон `GROUND/NEXUS/_map.md` (3 секции, скелет, правила заполнения).

#### Этап 2: Сборка сводки плана

Сгруппируй записи `routing.jsonl` (join с `nodes-draft.jsonl` по `tmp_id`):
- Число записей с `action: auto`, разбивка по `target_nexus`.
- Число записей с `action: queue`, разбивка по `reason`.
- Число рёбер (`links`) всего, сколько из них кросс-нексусных.
- Для каждой `auto`-записи проверь: `node_id` уже существует в
  `GROUND/NEXUS/<target_nexus>/<node_id>.md`? Если да — пометь
  `update` вместо `create`, и отдельно — существующий узел несёт
  `tags: [po-edited]`? Если да — пометь `конфликт → в _intake/` (см. Этап 5).

#### Этап 3: Вывод сводки + STOP

```
── СУХОЙ ПРОГОН ОТГРУЗКИ Confluence <space_key> ──
Записи не было. Источник: artefacts/confluence/routing.jsonl (<N> записей).

▸ AUTO (запись в GROUND/NEXUS/<slug>/): <X> узлов
   precedents: <a> (create: <a1>, update: <a2>, конфликт po-edited: <a3>)
   system-landscape: <b> (...)
   ...

▸ QUEUE (→ GROUND/_intake/unrouted.md): <Y> узлов
   низкая уверенность: <c>, конфликт нексусов: <d>, нет нексуса: <e>

▸ Рёбра: <M> всего (<S> структурных, <K> семантических кросс-нексусных)

▸ Затронутые _index.md: <список slug>
▸ GROUND/NEXUS/_map.md: будет перегенерирован целиком

── СТОП ──
PO: подтверди «ок» → выполню запись + обновление индексов + MOC + линт-гейты.
Без «ок» — ничего не пишу.
```

---

### ТАКТ 2. ЗАПИСЬ (только после явного «ок» PO)

#### Шаг 1: Запись `action: auto` узлов

Для каждой записи `routing.jsonl` с `action: auto`:

1. Путь: `GROUND/NEXUS/<target_nexus>/<node_id>.md`.
2. **Идемпотентность** — файл уже существует?
   - Существует и несёт `tags: [po-edited]` (ручная правка PO) → **НЕ
     перетирать**. Вместо этого запиши расхождение в `GROUND/_intake/`
     (файл `GROUND/_intake/<node_id>-divergence.md`: что несёт Confluence
     сейчас vs что в узле PO, ссылка на оба источника) — на ревью PO.
   - Существует и без `tags: [po-edited]` → обнови `body` + `updated`
     (сегодняшняя дата) и пересчитай `ripeness` по `nexus_schema.md` §4.
     Остальные поля (`node_id`, `nexus`, `node_type`, `sources`) не трогай
     без причины — только если источник (`sources`) действительно изменился.
   - Не существует → создай с полным frontmatter (см. ниже) + телом + `[[links]]`.
3. **Frontmatter** (все поля обязательны, `nexus_schema.md` §2):
   ```yaml
   ---
   nexus: <target_nexus>
   node_id: <node_id>
   node_type: <node_type>
   paf_step: null
   kind: empirical
   owner: <owner из GROUND/NEXUS/<target_nexus>/_index.md, RACI Accountable нексуса — не выдумывать>
   confidence: 0.3
   sources: [<из nodes-draft.jsonl, формат "confluence:<url>">]
   updated: <today, YYYY-MM-DD>
   ttl_days: <90 если target_nexus in {market, customer}; 60 если growth; иначе 180>
   ripeness: fresh
   tags: [confluence-indexed]
   ---
   ```
   Если узел уже существовал и `tags` нёс доп. значения (не только
   `confluence-indexed`) — сохрани их, добавь `confluence-indexed`, если его
   не было.
4. **Тело** — `title` как `# H1`, `body` из `nodes-draft.jsonl` как есть (не
   выдумывать сверх источника), затем список связей: `[[node_id]]` на
   каждую запись из `links` (поле `routing.jsonl`, добавлено `/cindex-link`).
5. Не создавай запись без `sources` — если по какой-то причине она пуста на
   этой стадии, это баг предыдущих стадий: STOP, доложи PO, не пиши узел.

#### Шаг 2: Очередь `action: queue`

Для каждой записи `routing.jsonl` с `action: queue`: добавь строку в таблицу
`GROUND/_intake/unrouted.md` (создай файл с заголовком таблицы, если его ещё
нет):

```markdown
# Очередь неразмеченных узлов Confluence

| tmp_id | node_type | reason | source_page |
|---|---|---|---|
| n-131099-3 | risk | нет уверенного нексуса | 131099 |
```

Не выдумывай `target_nexus`/`node_id` для этих записей — они разрешатся
вручную PO (ревью → при необходимости повторный `/cindex-route` вручную).

#### Шаг 3: Обновление `_index.md` затронутых нексусов

**Обязательный шаг — не пропускать.** Для каждого `target_nexus`, в который
на Шаге 1 создан или обновлён хотя бы один узел:

1. Открой `GROUND/NEXUS/<target_nexus>/_index.md`.
2. В разделе «Узлы» (или создай такой раздел, если его нет) добавь/обнови
   ссылку на каждый новый/обновлённый узел: `[[node_id]]` — короткое
   описание (`title`).
3. Не удаляй существующие ссылки на узлы, не тронутые этим прогоном.
4. Обнови `updated` в frontmatter `_index.md` на сегодняшнюю дату, если
   список узлов изменился.

#### Шаг 4: Генерация `GROUND/NEXUS/_map.md`

Сгенерируй/перегенерируй **целиком** по
`.claude/skills/confluence-indexator/resources/moc_template.md` — три
секции строго в этом порядке:
1. **Карта экосистемы** — по одному ряду на каждый нексус из
   `_registry.yaml` (не только затронутые этим прогоном): число узлов,
   1-3 ключевых (самых связанных/цитируемых) узла, ripeness-сводка
   (`fresh`/`ripening`/`wilting`, `nexus_schema.md` §4).
2. **Маршруты «вопрос → нексус/узел»** — таблица собранная из реально
   встретившихся типов вопросов/сигналов (`routing_table.md`), не
   исчерпывающий список заранее.
3. **Кросс-нексусные мосты** — только реально построенные семантические
   кросс-нексусные рёбра (Правило 2 `linking_rules.md`); внутринексусные
   структурные рёбра сюда не выносятся.

`_map.md` не редактируется PO вручную (источник — граф узлов) — эта
команда всегда перегенерирует его целиком, не патчит частично.

#### Шаг 5: Верификация — линт-гейты (обязательно, конец команды)

Прогони оба гейта и покажи их вывод PO дословно:

```bash
python3 -m sa_documentation.lint_graph GROUND/NEXUS   # ожидается пусто (OK)
python3 sa_documentation/validate_ground.py GROUND    # ожидается OK
```

- `lint_graph` вывел непустой список ошибок (битые `[[links]]`, узел без
  `sources`, orphan, невалидный `node_type`/`nexus`) → **не считать
  отгрузку завершённой**: доложи PO список ошибок построчно, предложи
  исправление (обычно — донаправить в `_intake/` или доисправить связь),
  не эмулируй "всё ок".
- `validate_ground` вывел что-то, кроме `OK` → аналогично, доложи PO.

#### Этап 6: Финальный отчёт

```
✅ Отгрузка Confluence <space_key> завершена.
Записано/обновлено узлов: <X> (по нексусам: ...).
В очередь _intake/unrouted.md: <Y>.
Расхождений po-edited → _intake/: <Z>.
_index.md обновлены: <список slug>.
GROUND/NEXUS/_map.md перегенерирован.

Линт-гейты:
lint_graph.py: <OK (пусто) | N ошибок — см. выше>
validate_ground.py: <OK | ошибки — см. выше>
```

Если хотя бы один гейт не прошёл — вместо `✅` выведи `⚠️` и явно скажи, что
отгрузка требует ручного исправления перед следующим индексом.

## Запреты

1. **НЕ пиши в `GROUND/NEXUS/` без явного «ок» PO** — сухой прогон
   обязателен для каждого запуска.
2. **НЕ перетирай узел с `tags: [po-edited]`** — расхождение только в
   `_intake/`, никогда молчаливая перезапись ручной правки PO.
3. **НЕ пропускай обновление `_index.md`** затронутых нексусов — это
   отдельный обязательный шаг (Шаг 3), не побочный эффект записи узла.
4. **НЕ патчи `_map.md` частично** — перегенерируй целиком по
   `moc_template.md` при каждом запуске.
5. **НЕ создавай узел без `sources`** и не выдумывай содержимое сверх
   `nodes-draft.jsonl`/`routing.jsonl`.
6. **НЕ заявляй успех при непустом выводе `lint_graph.py` или отличном от
   `OK` выводе `validate_ground.py`** — оба гейта обязательны в конце.
7. **НЕ изобретай `owner`** узла — бери из `_index.md` целевого нексуса
   (RACI Accountable), не из головы.
