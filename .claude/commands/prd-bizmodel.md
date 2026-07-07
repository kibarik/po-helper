---
description: 'Discovery Step 5 (Business Model) — плейлист: UNIT-экономика → AARRR(revenue); гейт Biz-model (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-bizmodel
/prd-bizmodel <lens_id>   # unit-economics | aarrr
```

Вход: узлы Step 2–4. Выход: growth-узлы + state.yaml(bizmodel).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-5-BUSINESS-MODEL/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product/market (сегменты, value-prop, размеры) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **unit-economics** → LTV/CAC/ratio + cohorts → `unit-econ` (growth, **estimate**) + `cohort` (growth, estimate). Все числа — `[estimate]`.
- **aarrr** (revenue-фокус) → воронка → `funnel-stage` (growth, judgment); revenue-метрики → `input-metric` (growth, estimate).
Мини-STOP после каждой.

### Этап 3: Гейт Biz-model (мягкий)
4. По `fit_gates.md`: Context Ripeness(growth) ≥ 0.6? Нет → 🟡, долг в open_questions.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(bizmodel)` + `journal.md`.
```
Step 5 (BizModel): линз L/2. Узлов N (growth). CP: X. Гейт Biz-model: <🟢/🟡>. [estimate]: k.
── СТОП ── PO. Дальше → /prd-gtm.
```

## Запреты
1. Тела линз не редактировать. 2. Финансовые числа → `estimate` CP ≤ 0.4 (нет данных = не факт); узел без `sources` не создавать. 3. Не выдавать 🟡 за гейт. 4. RACI growth → Growth Engineer. `docs/` read-only.
