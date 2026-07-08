---
description: 'Discovery Step 2 (Customer) — адаптивный плейлист линз: сегментация → единый контекст → ODI; наполняет customer-Нексус (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-customer            # весь плейлист по порядку
/prd-customer <lens_id>  # запустить одну линзу шага (segmentation|consumer-context|odi)
```

Вход: узлы Step 1 (market/product/growth). Выход: узлы customer-Нексуса + state.yaml(customer).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md` (Wrap), `resources/node_conventions.md` (frontmatter + CP-политики), `resources/lenses.yaml` (линзы customer).
2. Прочитай `docs/AI-PROCESSES/STEP-2-CUSTOMER/overview.md` (какие фазы активны).

### Этап 1: PULSE — вход из Step 1
3. Прочитай узлы market/product/growth (особенно `idea-lens-market-*`) — они станут input-паком и `depends_on` для узлов Customer. Пусто → предложи PO сначала `/prd-idea`.

### Этап 2: Плейлист линз (адаптивно; PO может пропустить/переставить)
Рекомендуемый порядок: `segmentation` → `consumer-context` → `odi`. Для каждой линзы — исполни по `lens_runtime.md` (PULSE→промт дословно→HARVEST):

- **segmentation** → HARVEST по lenses.yaml: HIGH-сегменты → `segment` (customer, `estimate`), JTBD → `jtbd` (customer, `judgment`), 5 гипотез сегмента → `opportunity` (customer, `judgment`). `depends_on` = релевантные Step 1 узлы.
- **consumer-context** → context_structure → `persona-context` (customer, `judgment`); value_propositions → `value-prop` (product, `judgment`, depends_on сегмент).
- **odi** → Core Job → `jtbd` (customer); Desired Outcomes → `outcome` (customer); Opportunity Scores → `opportunity` (customer, `estimate`).

После каждой линзы — мини-STOP (PO проверяет её узлы).

### Этап 3: HARVEST-свод + состояние
4. Обнови `{discovery_workspace(customer)}/state.yaml`: nodes[], cp (среднее), status (`converging`/`gate-ready`), open_questions[], last_touched. Допиши `journal.md` (какие линзы пройдены).

### Этап 4: СТОП
```
Step 2 (Customer): линз пройдено L/3. Узлов N (customer a / product b). Средний CP: X.
[estimate]-узлов: k. Открытых вопросов: q.
── СТОП ── PO: проверь узлы. Дальше → /prd-market, /prd-lens rat (риски), либо /prd-assemble.
```

## Запреты
1. Тело промтов-линз НЕ редактировать (Wrap: только вход/персист).
2. Оценки (размеры сегментов, LTV/CAC, scores) → `estimate` CP ≤ 0.4, не факт. Узел без `sources` не создавать.
3. «Не знаю» PO → `hyp_status: parked`, не выдумывать.
4. RACI: customer → Product Engineer, product → Product Engineer. Методология `docs/` read-only.
