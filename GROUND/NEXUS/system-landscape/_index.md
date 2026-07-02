---
nexus: system-landscape
node_id: system-landscape-index
node_type: step-overview
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.3
sources: []
updated: 2026-07-01
ttl_days: 90
ripeness: fresh
tags: [nexus-index, onboarding, intake, bft]
---

# Нексус системного ландшафта

Placeholder-Узел каталога `system-landscape`. Системный ландшафт ещё не оцифрован.
Наполнение — через `/paf-onboard` (интервью по seed_questions + ингестия доков/ADR/схем из `GROUND/_intake/`).

## Зачем этот Нексус

В бигтехе особенно критично — десятки сервисов, скрытые зависимости. Без этого Нексуса легко пообещать то, что противоречит архитектуре, или продублировать существующее.

Содержит: bounded contexts, существующие API-контракты, что уже есть vs что строить заново, скрытые зависимости между сервисами.

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- Какие bounded contexts и сервисы затрагивает запрос?
- Какие существующие API-контракты и интеграции задействованы?
- Что уже реализовано vs что нужно строить заново?
- Какие скрытые зависимости между сервисами?

## Узлы

*(пусто — наполняются `/paf-onboard` или при разборе запроса)*

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
