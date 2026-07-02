---
nexus: compliance
node_id: compliance-index
node_type: step-overview
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.3
sources: []
updated: 2026-07-01
ttl_days: 180
ripeness: fresh
tags: [nexus-index, onboarding, intake, bft, nfr]
---

# Нексус стандартов / комплаенса

Placeholder-Узел каталога `compliance`. Корпоративные стандарты, security/legal-ограничения и NFR-бейзлайн ещё не оцифрованы.
Наполнение — через `/paf-onboard` (ингестия корпоративного шаблона БФТ, security/legal-политик, NFR-гайдов).

## Зачем этот Нексус

Корпоративный шаблон БФТ, security/legal-ограничения, NFR-бейзлайн. В бигтехе часто жёстко формализован — без него документ завернут на ревью.

## seed_questions (из `sa_documentation/nexus_catalog.md`)

- Какой корпоративный шаблон БФТ обязателен?
- Какие security/legal-ограничения применимы?
- Каков NFR-бейзлайн (доступность, latency, приватность, аудит)?
- Какие ревью/подписи нужно пройти перед принятием?

## Узлы

*(пусто — наполняются `/paf-onboard` или при разборе запроса)*

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
