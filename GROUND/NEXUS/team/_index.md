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
tags: [nexus-index, onboarding, people-graph, po-navigation]
---

# Нексус организационной структуры

Placeholder-Узел каталога `team`. People Graph организации ещё не оцифрован.
Наполнение — через интервью по `seed_questions` или добавлением person-узлов по шаблону [`_template.md`](_template.md).

## Структура People Graph

Каждый Узел нексуса `team` = один человек (`node_type: person`). Граф строится в пяти слоях:

| Слой | Поля Узла | Назначение |
|---|---|---|
| **Org Chart** | `reports_to`, `manages` | Иерархия подчинения |
| **Social Graph** | `collaborates_with` | Рабочие связи вне иерархии |
| **Team Grouping** | `team_unit`, `team_role`, `team_mission` | Группировка по командам и зоны ответственности команд |
| **Expertise Graph** | `expertise_topics`, `contact_for`, `influence_zones` | ИИ-роутинг к нужному человеку |
| **PO Navigation** | `proximity`, `interaction_cadence`, `inbound_topics`, `clarify_with`, `approves`, `escalate_via` | Карта «я-как-PO ↔ человек»: кто ближе/дальше, кто с чем приходит, у кого уточнять, кто согласовывает. Основа `/people-map` |

> **PO Navigation — главный слой.** Описывает рёбра между PO и человеком, а не свойства человека вообще. Наполняется командой `/people-links` (описание отношений PO → контур), навигирует по нему `/people-map`.

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- Полное ФИО и должность каждого ключевого человека?
- Какие зоны ответственности и принятия решений у каждого?
- Кто кому подчиняется (прямая иерархия)?
- В какие команды (`team_unit`) сгруппированы люди и за что отвечает каждая команда?
- Кто с кем взаимодействует по рабочим вопросам (не иерархически)?
- По каким вопросам к кому обращаться? Каким уникальным контекстом обладает каждый?
- **PO navigation:** насколько человек близок к PO (core/close/extended/peripheral)? С чем сам приходит к PO? Какие детали PO у него уточняет? Что он согласовывает? Через кого эскалировать?

## Узлы

*(пусто — добавляются по шаблону `_template.md`)*

## Калибровка качества (People Radar)

Наполненный граф проверяется навыком [`nexus-calibration`](../../../.claude/skills/nexus-calibration/SKILL.md): ситуационные вопросы «к кому/почему» и «к тебе обратились — что делаешь» → сверка LLM-выборки с реальностью PO → `correction-Prompt` при расхождении. Цикл до `10/10` (короткая) / `50/50` (длинная).

- `/radar-graph` — диаграмма связей (3 слоя).
- `/radar-calibrate short|long` — прогон.
- `/radar-review <run_id>` — разбор расхождений + Prompt для правки узлов.

Прогоны живут в `_calibration/<run_id>/`.

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
