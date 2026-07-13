---
description: 'Промоут устойчивых сигналов радар-ноты в узлы NEXUS через ревью-гейт (additive-only, CP=0.3 для новых) (роль: Куратор контекста)'
---

## Использование

```
/pulse-promote [YYYY-MM-DD]
```

- дата → взять `PULSE/radar/YYYY-MM-DD-pulse-radar.md`; без аргумента → последняя нота.
  Нет нот → СТОП, сначала `/pulse-radar`. Выход: новые/additive-узлы NEXUS после одобрения PO.

## Важно

**Ревью-гейт обязателен.** Ничего не писать в NEXUS до явного выбора PO. Апдейты additive
(curated-текст не трогать). Новые узлы `confidence: 0.3`. Нет якоря — нет промоута. Идемпотентно.

## Инструкция для LLM

Запусти навык **`pulse-promote`** (`.claude/skills/pulse-promote/SKILL.md`):
1. Прочитай `.claude/domain-profile.md` → `po_name` + team-node-id PO (для `owner`/`owns_node`),
   `paths.pulse_radar_dir`.
2. Извлеки сигналы, примени фильтр устойчивости (`resources/promote_rules.md`), дедуп по NEXUS.
3. Напечатай список кандидатов (+ SKIP). Жди выбор PO. Запиши только одобренное. Отчёт.
