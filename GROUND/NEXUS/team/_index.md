---
nexus: team
node_id: team-index
node_type: step-overview
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.3
sources: []
updated: 2026-06-25
ttl_days: 180
ripeness: fresh
tags: [nexus-index, onboarding, people-graph]
---

# Нексус организационной структуры

Placeholder-Узел каталога `team`. People Graph организации ещё не оцифрован.
Наполнение — через интервью по `seed_questions` или добавлением person-узлов по шаблону [`_template.md`](_template.md).

## Структура People Graph

Каждый Узел нексуса `team` = один человек (`node_type: person`). Граф строится в трёх слоях:

| Слой | Поля Узла | Назначение |
|---|---|---|
| **Org Chart** | `reports_to`, `manages` | Иерархия подчинения |
| **Social Graph** | `collaborates_with` | Рабочие связи вне иерархии |
| **Expertise Graph** | `expertise_topics`, `contact_for`, `influence_zones` | ИИ-роутинг к нужному человеку |

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- Полное ФИО и должность каждого ключевого человека?
- Какие зоны ответственности и принятия решений у каждого?
- Кто кому подчиняется (прямая иерархия)?
- Кто с кем взаимодействует по рабочим вопросам (не иерархически)?
- По каким вопросам к кому обращаться?
- Каким уникальным контекстом или экспертизой обладает каждый человек?

## Узлы

*(пусто — добавляются по шаблону `_template.md`)*

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
