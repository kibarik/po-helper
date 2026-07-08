---
description: 'Discovery Step 7 (Solution) — плейлист: OST → A/B → RAT; решение, эксперименты, риски + гейт PMF (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-solution
/prd-solution <lens_id>   # ost | ab-design | rat
```
Вход: узлы Step 2–6. Выход: product-узлы + state.yaml(solution).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-7-SOLUTION-PMF/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product (jtbd/outcome/value-prop) — вход и `depends_on`.

### Этап 2: Плейлист (эти линзы cross-cutting; здесь — рекомендуемая последовательность шага; каждая через lens_runtime):
- **ost** → outcome→opportunity→solution→experiment → узлы `opportunity`/`solution`/`experiment` (product, judgment), связанные `depends_on`.
- **ab-design** → дизайн эксперимента → `ab-test` (product, judgment).
- **rat** → топ-5 рисковых допущений (P×I) → `risk-card` (product, estimate; скоры `[estimate]`).
Мини-STOP после каждой.

### Этап 3: Гейт PMF (мягкий)
4. По `fit_gates.md`: Context Ripeness(product) ≥ 0.6 + PMF-критерии. Нет → 🟡, долг в open_questions. Напомни PO: PMF требует **evidence** (реальные эксперименты), не гипотез.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(solution)` + `journal.md`.
```
Step 7 (Solution): линз L/3. Узлов N (product). CP: X. Гейт PMF: <🟢/🟡>. Риск-карт: r.
── СТОП ── PO. Дальше → /prd-acquisition.
```

## Запреты
1. Тела линз не редактировать. 2. Гипотезы решений → `judgment`, риск-скоры → `estimate`; узел без `sources` не создавать; «не знаю» → parked. 3. PMF ✅ только при `evidence`-узлах — не выдавать гипотезу за PMF. 4. RACI product → Product Engineer. `docs/` read-only.
