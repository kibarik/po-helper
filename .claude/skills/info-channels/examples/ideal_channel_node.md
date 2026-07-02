---
nexus: channels
node_id: chan-billing-tg
node_type: channel
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.6
sources: ["onboarding:interview", "po:observation"]
updated: 2026-06-25
ttl_days: 180
ripeness: fresh
tags: [channel]

# --- schema_extensions (Information Channels Graph) ---
channel_type: telegram
platform: "Telegram"
handle: "@billing_team"
direction: inbound
cadence: "поток"

purpose: >
  Оперативный канал по биллингу: смежные команды пишут про ошибки списаний,
  статусы платежей и просят новые тарифы. Первый источник багов до того, как
  они попадают в трекер.
topics:
  - "ошибки списаний и возвраты"
  - "статусы платежей и вебхуки"
  - "запросы на новые тарифы"
signal_types:
  - bug
  - requirement
  - feedback

stakeholders:
  - team-ivanov-ivan
  - team-petrov-dmitry
system_areas:
  - "[[cortex-billing]]"
  - "[[cortex-payments]]"
goals:
  - "KR-3.2"

ingest_action: >
  Баг списания → трекер (участок cortex-billing). Запрос на тариф → /req-context
  (front door intake). Статус/фидбек → FYI. Всё остальное → [УТОЧНИТЬ источник].
---

# Telegram · @billing_team — оперативный канал по биллингу

> Пример-эталон channel-узла. Домен иллюстративный; реальные значения — из вашего `NEXUS/team`, CORTEX и OKR.

## Назначение

Оперативный канал по биллингу: смежные команды пишут про ошибки списаний, статусы платежей и просят новые тарифы. Первый источник багов до трекера.

## Темы (по каким вопросам пишут)

- ошибки списаний и возвраты
- статусы платежей и вебхуки
- запросы на новые тарифы

## Типы сигналов

bug · requirement · feedback

## Кто в канале (стейкхолдеры)

- [[team-ivanov-ivan]] — Product Manager, биллинг
- [[team-petrov-dmitry]] — BE-инженер, платежи

## Участки системы

- [[cortex-billing]]
- [[cortex-payments]]

## Цели / OKR

- KR-3.2 — снижение доли ошибочных списаний

## Как обрабатывать входящую информацию

- **bug** (ошибка списания) → трекер, участок `cortex-billing`.
- **requirement** (запрос на тариф) → `/req-context` — front door intake, meta канала как источник.
- **feedback / status** → FYI.
- источник/тема неясны → `[УТОЧНИТЬ источник]`, спросить PO.
