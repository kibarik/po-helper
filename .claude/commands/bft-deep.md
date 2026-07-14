---
description: 'V2 БФТ-Обогатитель — берёт seed (Fast-черновик или Summary) и автономно наращивает глубину (ценность/what-if/границы) + синк в канон (роль: Обогатитель)'
---

## Использование
```
/bft-deep <seed> [epic_slug]
```
- `<seed>` — путь к Fast-черновику (письмо bft-fast) или к Summary/контексту.
- `[epic_slug]` — опц.; нет → date-slug из темы.

## Важно
Роль — Обогатитель (V2). Берёт основу, наращивает глубину, укладывает в канон-структуру MTS. Стоп на валидированном черновике; `/bft-deliver` — отдельный ручной шаг PO. Факт без источника → `[УТОЧНИТЬ]`.

## Инструкция для LLM
1. Загрузить `skills/bft-deep-swarm/SKILL.md` + resources (orchestration/enrichment/grounding_verifier/eval_rubric).
2. Резолв конфига (SKILL.md §Резолв).
3. Прогнать оркестрацию `resources/orchestration.md` стадии 0-11.
4. Emit: `workspace/<epic_slug>/<epic_slug>.md` + artefacts + нотификация.
