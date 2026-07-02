---
nexus: strategy
node_id: strategy-index
node_type: step-overview
paf_step: null
sprint_phase: null
kind: empirical
owner: Portfolio Manager
confidence: 0.3
sources: []
updated: 2026-07-01
ttl_days: 90
ripeness: fresh
tags: [nexus-index, onboarding, intake, bft, okr]
---

# Нексус стратегии / roadmap

Placeholder-Узел каталога `strategy`. Связь запросов с OKR и приоритетами квартала ещё не оцифрована.
Наполнение — через `/paf-onboard` (ингестия OKR/ROADMAP) или из результатов `/okr-planner`.

## Зачем этот Нексус

Как запрос соотносится с текущими OKR и приоритетами квартала. Без него БФТ формально верен, но **не защитим на приоритизации**.

Связан с `/okr-planner` (OKR квартала) и `/sprint-planner` (roadmap по спринтам) — этот Нексус хранит текущий стратегический контекст для intake.

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- С какими OKR соотносится запрос?
- Каковы приоритеты текущего квартала?
- Как запрос защитим на приоритизации?
- Не конфликтует ли запрос с текущим roadmap?

## Узлы

*(пусто — наполняются `/paf-onboard` или из `/okr-planner`)*

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
