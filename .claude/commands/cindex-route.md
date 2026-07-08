---
description: 'Роутинг узлов-кандидатов в целевой нексус реестра + route_confidence + node_id (роль: Router)'
---

## Использование

```
/cindex-route <space_key>
```

Вход: `artefacts/confluence/nodes-draft.jsonl`. Выход:
`artefacts/confluence/routing.jsonl`.

## Важно

**Роль: Router.** Ты классифицируешь каждый узел-кандидат в конкретный
существующий нексус, оцениваешь уверенность классификации и генерируешь
детерминированный `node_id`. Ты **не** строишь связи `[[wiki-links]]` (это
`/cindex-link`) и **не** пишешь в `GROUND/NEXUS/<slug>/` (это
`/cindex-deliver`, после STOP на сухом прогоне).

Четвёртая стадия пайплайна (`.claude/skills/confluence-indexator/SKILL.md`).
Авто-batch, без STOP — следующая обязательная пауза после `/cindex-link`,
перед `/cindex-deliver`.

**Ноль галлюцинаций (жёсткое правило):**
- Роутинг — **только** в slug из `GROUND/NEXUS/_registry.yaml`. Нет
  зарегистрированного нексуса под сигнал — узел уходит в `_intake/unrouted.md`
  (через `action: queue`), новый нексус не изобретается.
- `node_type` — только канонические значения `sa_documentation/nexus_schema.md`
  §3 (то, что уже присвоил `/cindex-digitize`). Router не меняет `node_type`
  и не придумывает новых значений.
- `route_confidence` (уверенность классификации, порог 0.7) — **не то же
  самое**, что `confidence` узла (фиксированные 0.3, поле добавляет
  `/cindex-deliver`). Не путать, не трогать `confidence` на этой стадии.

---

## Инструкция для LLM

### Этап 1: Загрузка входа и правил

1. Прочитай `artefacts/confluence/nodes-draft.jsonl`. Нет файла →
   `[УТОЧНИТЬ: запусти /cindex-digitize <space_key>]`.
2. Прочитай
   `.claude/skills/confluence-indexator/resources/routing_table.md` целиком —
   на этой стадии, в отличие от `/cindex-digitize`, колонка «Целевой нексус»
   и раздел «Правило множественности и неоднозначности» используются
   полностью.
3. Прочитай `GROUND/NEXUS/_registry.yaml` — список `slug` реально
   зарегистрированных нексусов клиента. Это единственный допустимый набор
   значений для `target_nexus`.
4. Прочитай
   `.claude/skills/confluence-indexator/resources/confidence_rules.md` —
   пороги `route_confidence` и триггеры очереди (раздел «Триггеры очереди
   `_intake/unrouted.md`», пункты 1, 2, 4 — применимы на этой стадии; пункт 3
   «Orphan» решается по связям `[[wiki-links]]`, которых на этой стадии ещё
   нет — это забота `lint_graph.py` после `/cindex-deliver`, здесь не
   применяй).
5. Прочитай `sa_documentation/cindex_ids.py` — точный детерминированный
   алгоритм `node_id` (транслитерация кириллицы, kebab-case, паттерн
   `<nexus>-<slug(title)>`, максимум 60 символов). Используй ровно этот
   алгоритм (`make_node_id(nexus, title)` / `slugify(title)`), не изобретай
   свою транслитерацию или разделители — иначе повторный прогон индексатора
   перестанет быть идемпотентным.

### Этап 2: Роутинг каждого узла-кандидата (батч, без STOP)

Для каждой строки `nodes-draft.jsonl`:

1. По `node_type` найди соответствующую строку `routing_table.md` (колонка
   «Целевой нексус»). Строки с двумя вариантами через «/» (`decision`, `term`,
   `metric`, `risk`) разрешай по контексту страницы/`body` узла (тех-решение
   vs бизнес-решение, платформенный термин vs домен заказчика, продуктовый
   риск vs риск мощности, KR-метрика vs growth-метрика) — не гадай вслепую.
2. Проверь кандидата-нексуса против `GROUND/NEXUS/_registry.yaml`:
   - slug зарегистрирован → это `target_nexus`.
   - slug не зарегистрирован (или сигнал не подпадает ни под одну строку
     таблицы) → `target_nexus: null`, `action: "queue"`,
     `reason: "нет зарегистрированного нексуса под сигнал"`.
3. Присвой `route_confidence` (0–1) — насколько уверенно сигнал страницы
   соответствует выбранной строке таблицы и единственному нексусу. Ниже уверенность,
   если пришлось разрешать неоднозначность между двумя нексусами из одной
   строки, или сигнал пограничный.
4. Примени `confidence_rules.md`:
   - `route_confidence ≥ 0.7` и `target_nexus` резолвлен → `action: "auto"`.
   - иначе → `action: "queue"` + `reason` (конкретная причина: низкая
     уверенность / конфликт двух нексусов / нет подходящего нексуса).
5. **`node_id`** генерируется только для узлов с резолвленным `target_nexus`
   (включая случай `action: "queue"` из-за низкой уверенности, но с известным
   нексусом-кандидатом — тогда `node_id` всё равно вычисляется, он пригодится
   PO при ревью в `_intake/unrouted.md`). Если `target_nexus: null` —
   `node_id` не генерируется (нет базы для слага).
   ```python
   from sa_documentation.cindex_ids import make_node_id
   node_id = make_node_id(target_nexus, title)  # title — из nodes-draft.jsonl
   ```

### Этап 3: Сохранение

Сохрани `artefacts/confluence/routing.jsonl` — один JSON-объект на строку,
дизайн-спека §6, **все поля кроме `links`** (его добавляет `/cindex-link`):

```json
{"tmp_id":"n-131074-1","node_type":"decision","target_nexus":"precedents","node_id":"precedents-vybor-sinhronnogo-platezhnogo-potoka","route_confidence":0.82,"action":"auto"}
{"tmp_id":"n-131090-2","node_type":"risk","target_nexus":null,"route_confidence":0.34,"action":"queue","reason":"нет уверенного нексуса"}
```

Каждый кандидат из `nodes-draft.jsonl` даёт ровно одну запись (порядок
сохраняется) — как `auto`, так и `queue` попадают в `routing.jsonl`, финальное
разделение по `GROUND/NEXUS/<slug>/` и `_intake/unrouted.md` делает
`/cindex-deliver`.

### Этап 4: Отчёт (без STOP)

```
Роутинг завершён: artefacts/confluence/routing.jsonl (<N> записей)
Разбивка по action: auto: X, queue: Y.
Разбивка queue по reason: <низкая уверенность: A, конфликт нексусов: B, нет нексуса: C>.

Дальше: /cindex-link <space_key>.
```

STOP не требуется — следующая обязательная пауза после `/cindex-link`, перед
`/cindex-deliver`.

## Запреты

1. НЕ роутить в нексус, которого нет в `GROUND/NEXUS/_registry.yaml` — только
   очередь `_intake/unrouted.md` через `action: "queue"`.
2. НЕ присваивать/менять `node_type` — это уже сделал `/cindex-digitize`.
3. НЕ путать `route_confidence` (уверенность роутинга, порог 0.7) с
   `confidence` узла (фиксированные 0.3, поле пишет `/cindex-deliver`).
4. НЕ добавлять поле `links` — это работа `/cindex-link`.
5. НЕ разрешать неоднозначность между двумя нексусами угадыванием — понижай
   `route_confidence` и уводи в очередь.
6. НЕ изобретать свой алгоритм слагификации `node_id` — использовать ровно
   `sa_documentation/cindex_ids.py`.
