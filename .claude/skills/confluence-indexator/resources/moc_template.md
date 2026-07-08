# Шаблон навигационного MOC — `GROUND/NEXUS/_map.md`

Генерирует стадия `/cindex-deliver` (дизайн-спека §7). Назначение — дать
агенту «знать, куда обратиться»: карта экосистемы нексусов, маршруты
«вопрос → нексус/узел», кросс-нексусные мосты. Три обязательные секции,
строго в этом порядке.

## Скелет

```markdown
# Карта экосистемы — GROUND/NEXUS

> Сгенерировано `/cindex-deliver` <YYYY-MM-DD>. Источник — реестр
> `GROUND/NEXUS/_registry.yaml` + граф узлов после Confluence-индексации.

## 1. Карта экосистемы

| Нексус | Узлов | Ключевые узлы | Ripeness-сводка |
|---|---|---|---|
| `precedents` | 12 | `[[precedents-sync-payment-flow]]` | fresh: 9, ripening: 2, wilting: 1 |
| `system-landscape` | 8 | `[[system-landscape-payment-gateway]]` | fresh: 6, ripening: 1, wilting: 1 |
| `compliance` | 5 | `[[compliance-pci-dss]]` | fresh: 5 |
| `team` | 20 | `[[team-ivanov-ivan]]` | fresh: 18, ripening: 2 |
| … | … | … | … |

## 2. Маршруты «вопрос → нексус/узел»

| Тип вопроса | Куда идти |
|---|---|
| Почему приняли решение X? | `precedents` — узлы `node_type: decision` |
| Какой SLA/НФТ у компонента Y? | `compliance` — узлы `node_type: nfr` |
| Кто владелец домена Y? | `ownership` / `team` — узлы `node_type: person` |
| Какой сервис/API отвечает за Z? | `system-landscape` — узлы `node_type: component` |
| Что значит термин T? | `requester-domain` / `product` — узлы `node_type: term` |
| Какая метрика/KPI цели квартала? | `strategy` / `growth` — узлы `node_type: metric` |
| Какой закон/стандарт затрагивает X? | `compliance` — узлы `node_type: regulation` |
| Какие риски у инициативы X? | `problem` / `capacity` — узлы `node_type: risk` |
| Кто внешняя команда по домену Y? | `landscape` / `ownership` |
| Не нашли ответ / узел не создан? | `_intake/unrouted.md` — очередь на ревью PO |

## 3. Кросс-нексусные мосты

Список межнексусных рёбер, где темы одного нексуса связаны с темами другого
(семантические связи, `linking_rules.md`, правило 2):

| Из | В | Через что связаны |
|---|---|---|
| `[[precedents-sync-payment-flow]]` (precedents) | `[[system-landscape-payment-gateway]]` (system-landscape) | общая сущность «платёжный поток/шлюз» |
| `[[compliance-pci-dss]]` (compliance) | `[[system-landscape-payment-gateway]]` (system-landscape) | регуляторное требование к компоненту |
| `[[strategy-kr-3-2]]` (strategy) | `[[growth-activation-metric]]` (growth) | общая метрика цели квартала |
```

## Правила заполнения

1. **Секция 1** — по одному ряду на нексус из `_registry.yaml`; «Ключевых
   узлов» — 1–3 самых связанных/цитируемых узла нексуса, не полный список.
   Ripeness-сводка — счётчик по `nexus_schema.md` §4 (`fresh`/`ripening`/
   `wilting`).
2. **Секция 2** — таблица собирается из реально встретившихся типов
   вопросов (не исчерпывающий список заранее); каждая строка ссылается на
   существующий нексус/`node_type` из `routing_table.md`.
3. **Секция 3** — только реально построенные кросс-нексусные рёбра
   (`linking_rules.md`, правило 2); внутринексусные структурные рёбра сюда
   не выносятся — они видны в самих узлах.
4. MOC не заменяет `GROUND/NEXUS/_index.md` (индекс структуры), а
   дополняет его навигационным слоем «куда идти по вопросу».
5. Перегенерируется целиком при каждом `/cindex-deliver`; не редактируется
   PO вручную (источник — граф узлов, не MOC).
