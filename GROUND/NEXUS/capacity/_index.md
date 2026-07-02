---
nexus: capacity
node_id: capacity-index
node_type: step-overview
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.3
sources: []
updated: 2026-07-01
ttl_days: 30
ripeness: fresh
tags: [nexus-index, onboarding, intake, bft, capacity]
---

# Нексус мощности

Placeholder-Узел каталога `capacity`. Velocity, capacity и cost of delay ещё не оцифрованы.
Наполнение — через `/paf-onboard` или из результатов `/sprint-planner` (загрузка команды).

## Зачем этот Нексус

Velocity команды, capacity, cost of delay. Даёт не только «что», но и «какой ценой», без чего БФТ неполноценен для принятия решения.

`ttl_days: 30` — мощность самая волатильная из всех Нексусов (меняется на уровне спринта), поэтому wilting-порог короткий.

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- Какова текущая velocity команды?
- Какова доступная capacity (с учётом отпусков/дежурств)?
- Каков cost of delay запроса?
- Какой ценой (сроки/ресурсы) обойдётся реализация?

## Узлы

*(пусто — наполняются `/paf-onboard` или из `/sprint-planner`)*

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
