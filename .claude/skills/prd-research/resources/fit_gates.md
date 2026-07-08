# prd-research — fit-гейты (мягкие)

Fit-точки методологии (docs/AI-PROCESSES/fit-points.md) как Stage-Gate по Confidence Point.

| Гейт | После шага | Порог (рекоменд.) |
|---|---|---|
| Need/Value Fit | Step 4 Value | Context Ripeness(product) ≥ 0.6 |
| Biz-model | Step 5 | Context Ripeness(growth) ≥ 0.6 |
| PMF | Step 7 Solution | Context Ripeness(product) ≥ 0.6 + PMF-критерии |
| PCF | Step 8 Acquisition | LTV/CAC-конфиг валидирована |

Context Ripeness = completeness × freshness (формула §4 nexus_schema.md).

## Логика мягкого гейта
- Порог не достигнут → **не блокировать**. Вывести: «🟡 Гейт <name> не пройден (Ripeness X < 0.6). Можно продолжить, но раздел PRD будет помечен «на гипотезах». Долг записан в open_questions.»
- PO решает: углубить текущий шаг или идти дальше с пометкой долга.
- Принцип: «ненулевое знание > чистое знание» (docs/AI-PROCESSES/README.md).
