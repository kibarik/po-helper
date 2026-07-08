---
description: 'Discovery Step 6 (Go-To-Market) — плейлист: 4P → каналы → Rory; позиционирование и каналы (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-gtm
/prd-gtm <lens_id>   # positioning-4p | distribution-channels | rory-interrogation
```

Вход: узлы Step 2–5. Выход: growth/product-узлы + state.yaml(gtm).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`.
2. Прочитай `docs/AI-PROCESSES/STEP-6-GO-TO-MARKET/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product/growth (сегменты, value-prop, unit-эк) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **positioning-4p** → `four-p` (growth, judgment) + рекоменд. позиционирование → `positioning` (product, judgment).
- **distribution-channels** → каналы (+RICE-скор) → `dist-channel` (growth, estimate).
- **rory-interrogation** → усиление позиционирования → `positioning` (product, judgment).
Мини-STOP после каждой.

### Этап 3: Состояние + СТОП
4. Обнови `state.yaml(gtm)` + `journal.md`.
```
Step 6 (GTM): линз L/3. Узлов N (growth a / product b). CP: X.
── СТОП ── PO. Дальше → /prd-solution.
```

## Запреты
1. Тела линз не редактировать. 2. RICE/оценки → `estimate`; узел без `sources` не создавать; «не знаю» → `parked`. 3. RACI growth → Growth Engineer, product → Product Engineer. `docs/` read-only.
