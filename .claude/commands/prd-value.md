---
description: 'Discovery Step 4 (Value) — плейлист: NSM → ODI(outcomes) → Rory; ценностное предложение + гейт Need/Value Fit (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-value
/prd-value <lens_id>   # nsm | odi | rory-interrogation
```
Вход: узлы Step 2/3. Выход: product/growth-узлы + state.yaml(value).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-4-VALUE/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer (сегменты/jtbd/persona/value-prop) + market — вход и `depends_on`.

### Этап 2: Плейлист (адаптивно; PO может пропустить/переставить), каждый — через lens_runtime:
- **nsm** (cross-cutting) → `nsm-metric` (product, judgment) + `input-metric` (growth, judgment).
- **odi** → desired outcomes → `outcome` (**product**, judgment) [override customer→product на этом шаге]; opp-scores → `opportunity` (product, estimate).
- **rory-interrogation** → рефрейм ценности → `value-prop` (product, judgment); позиционирование-намёк → `positioning` (product, judgment).
После каждой линзы — мини-STOP.

### Этап 3: Гейт Need/Value Fit (мягкий)
4. По `fit_gates.md`: Context Ripeness(product) ≥ 0.6? Нет → 🟡 не блокировать, пометить долг в open_questions.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(value)` (+ гейт-пометка) + `journal.md`.
```
Step 4 (Value): линз L/3. Узлов N (product a / growth b). CP: X. Гейт Need/Value Fit: <🟢/🟡>.
── СТОП ── PO. Дальше → /prd-bizmodel, либо /prd-lens rat.
```

## Запреты
1. Тела линз не редактировать. 2. Оценки/скоринги → `estimate`; узел без `sources` не создавать; «не знаю» → `parked`. 3. Не выдавать 🟡 за пройденный гейт. 4. RACI product → Product Engineer. `docs/` read-only.
