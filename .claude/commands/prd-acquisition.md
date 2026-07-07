---
description: 'Discovery Step 8 (Acquisition) — плейлист: AARRR(acq) → каналы; конфиг привлечения + гейт PCF (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-acquisition
/prd-acquisition <lens_id>   # aarrr | distribution-channels
```
Вход: узлы Step 5–7. Выход: growth-узлы + state.yaml(acquisition).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-8-ACQUISITION-PCF/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы growth/product (unit-эк, каналы, воронка) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **aarrr** (acquisition-фокус) → воронка привлечения → `funnel-stage` (growth, judgment) + метрики → `input-metric` (growth, estimate).
- **distribution-channels** → конфиг «сегмент-канал-оффер» → `dist-channel` (growth, judgment).
Мини-STOP после каждой.

### Этап 3: Гейт PCF (мягкий)
4. По `fit_gates.md`: конфиг привлечения окупается (LTV/CAC). Нет данных → 🟡, долг в open_questions. Напомни: PCF требует **evidence** (реальная окупаемость).

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(acquisition)` + `journal.md`.
```
Step 8 (Acquisition): линз L/2. Узлов N (growth). CP: X. Гейт PCF: <🟢/🟡>.
── СТОП ── PO. Discovery-цикл пройден по всем 8 шагам → /prd-assemble (витрина), /prd-research (доска).
```

## Запреты
1. Тела линз не редактировать. 2. CAC/LTV/оценки → `estimate`; узел без `sources` не создавать; «не знаю» → parked. 3. PCF ✅ только при `evidence`. 4. RACI growth → Growth Engineer. `docs/` read-only.
