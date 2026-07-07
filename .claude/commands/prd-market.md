---
description: 'Discovery Step 3 (Market) — линза TAM/SAM/SOM; наполняет market-Нексус (роль: Discovery Facilitator + рыночный аналитик)'
---

## Использование

```
/prd-market
```
Вход: узлы Step 1/2 (сегменты, канал). Выход: market-узлы + state.yaml(market).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md` (CP-политики), `resources/lenses.yaml` (линза `tam-sam-som`).
2. Прочитай `docs/AI-PROCESSES/STEP-3-MARKET/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы market/customer (сегменты `cust-seg-*`, `idea-lens-market-*`) — вход и `depends_on`.

### Этап 2: Линза tam-sam-som (Wrap)
4. Исполни линзу `tam-sam-som` по `lens_runtime.md` (PULSE→промт дословно, 9 стадий, top-down+bottom-up→HARVEST).
   HARVEST: TAM/SAM/SOM + sensitivity → `tam-sam-som` (market, **estimate**, `[estimate]` в теле); выявленные конкуренты/альтернативы → `competitor` (market, judgment). `depends_on` = сегменты Step 2.

### Этап 3: Состояние
5. Обнови `{discovery_workspace(market)}/state.yaml` (nodes/cp/status/open_questions/last_touched) + `journal.md`.

### Этап 4: СТОП
```
Step 3 (Market): узлов N (market). Средний CP: X. [estimate]-узлов: k.
── СТОП ── PO: проверь узлы. Дальше → /prd-value, либо /prd-lens rat.
```

## Запреты
1. Тело линзы НЕ редактировать. 2. Числа рынка → `estimate` CP ≤ 0.4, не факт; узел без `sources` не создавать. 3. «Не знаю» → `parked`. 4. RACI market → Portfolio Manager. `docs/` read-only.
