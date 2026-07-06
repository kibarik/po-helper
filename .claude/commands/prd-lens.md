---
description: 'Cross-cutting Research-линза — запуск rat/ab-design/ost/nsm на текущем шаге через единый Wrap (роль: по линзе)'
---

## Использование

```
/prd-lens <id> [step]
```
`<id>` — из lenses.yaml (rat | ab-design | ost | nsm). `[step]` — текущий шаг для HARVEST-нексуса (по умолчанию — активный шаг доски).

Пример: `/prd-lens rat solution`

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/prd-research/SKILL.md` и `skills/prd-research/resources/lens_runtime.md`.
2. Прочитай `skills/prd-research/resources/lenses.yaml`; найди линзу по `<id>`. Нет / не `cross_cutting` → сообщи PO и остановись.
3. Определи `step` (аргумент или активный шаг из state.yaml доски).

### Этап 2: Исполнение по Wrap
4. Исполни линзу строго по `lens_runtime.md`: PULSE (вход из узлов `step` + первопричин) → запуск `prompt_file` дословно (гейты `продолжить/ревизия`, язык ru) → HARVEST.
5. HARVEST: если у линзы есть `harvest` — по нему; иначе (rat/ab-design/ost/nsm без harvest в реестре) создай узлы по природе выхода: rat → `risk-card` (product), ab-design → `ab-test` (product), ost → `opportunity`/`solution`/`experiment` (product), nsm → `nsm-metric`/`input-metric` (growth). CP-политика: risk/ab/ost → `judgment` (или `estimate` для числовых); nsm → `judgment`. Нексус — по `step`.

### Этап 3: СТОП
```
Линза <id> на шаге <step>: создано узлов N (<типы>). Средний CP: X. [estimate]: k.
── СТОП ── PO: проверь узлы. Вернуться к доске → /prd-research.
```

## Запреты
1. Тело промта линзы НЕ редактировать — только вход/персист (Wrap).
2. Оценки/допущения → `estimate`/`judgment`, не `validated`. Узел без `sources` не создавать.
3. Линза не `cross_cutting` → не запускать здесь (это шаг-команда `/prd-<step>`).
