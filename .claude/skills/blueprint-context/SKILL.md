---
name: blueprint-context
description: "Старт Blueprint-pipeline: подготовка контекста (БФТ? Nexus? config) и выбор режима ENRICH|SCRATCH. Создаёт GROUND/BLUEPRINT/<task>/."
---

# /blueprint-context — старт Blueprint-pipeline

Первый шаг pipeline `/blueprint-*`. Готовит контекст и выбирает режим. Не рисует диаграмму.

> Пошаговый план для LLM. Читай файлы перед записью. Ноль выдуманной PAF-терминологии
> (`sa_documentation/naming_conventions.md`).

## 0. Контекст (прочитать)
- `sa_documentation/blueprint_schema.md` — схема Scope Model.
- `GROUND/config.yaml` — slug продукта, roster (если есть).
- `sa_documentation/naming_conventions.md` — термины PAF.

## 1. Вход
- Спроси/определи: путь к БФТ-файлу задачи (если есть) и slug задачи (`[a-z0-9][a-z0-9-]*`).

## 2. Детект режима
- БФТ-файл найден/указан → `mode: enrich`.
- БФТ нет → `mode: scratch`.

## 3. Скан источников
- ENRICH: зафиксируй разделы БФТ как кандидаты в `sources` (kind: bft).
- Проверь доступность Nexus: `mcp__ruflo__memory_search` или `GROUND/NEXUS/_registry.yaml` (kind: nexus).

## 4. Создать каталог + skeleton
- `GROUND/BLUEPRINT/<task>/scope-model.yaml` с шапкой (task, title, mode, created=сегодня,
  confidence: 0.3, пустые sources/journey/cells/gaps), по `blueprint_schema.md`.

## 5. Выход (readiness-строка)
```
Blueprint-pipeline инициализирован: task=<slug>, mode=<enrich|scratch>.
Источники: БФТ=<да/нет>, Nexus=<да/нет>.
→ mode=enrich:  /blueprint-extract
→ mode=scratch: /blueprint-discover
```

## Guardrails
- Idempotent: существующий `scope-model.yaml` не затирать без подтверждения.
- slug валиден `[a-z0-9][a-z0-9-]*`.
