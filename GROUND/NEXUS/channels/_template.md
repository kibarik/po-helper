---
nexus: channels
node_id: chan-slug                 # ascii-slug [a-z][a-z0-9-]*; напр. chan-billing-tg. КИРИЛЛИЦУ НЕ ИСПОЛЬЗОВАТЬ
node_type: channel
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.5                     # 0.2–0.4 = допущение онбординга; 0.6–0.8 = подтверждено PO; 0.9–1.0 = верифицировано
sources: ["onboarding:interview"]   # реальный источник: onboarding:interview | po:observation | <ссылка на канал>
updated: YYYY-MM-DD
ttl_days: 180
ripeness: fresh
tags: [channel]

# --- schema_extensions (Information Channels Graph) ---

# Идентификация (обязательные)
channel_type: chat                 # chat | email | telegram | call | tracker | wiki | other
platform: "Платформа"              # Telegram | Slack | Mattermost | Zoom | Email | ...
handle: "@идентификатор"           # @канал / id группы / email / ссылка на созвон
direction: inbound                 # inbound | outbound | bidirectional
cadence: "поток"                   # поток | ежедневно | еженедельно | по событию

# Назначение (ДЛЯ ЧЕГО канал — обязательные)
purpose: >                         # зачем канал существует, 1-2 фразы — ОБЯЗАТЕЛЬНО
  Описание назначения канала.
topics:                            # ПО КАКИМ ВОПРОСАМ здесь пишут — ОБЯЗАТЕЛЬНО
  - "тема 1"
  - "тема 2"
signal_types:                      # типы сигналов канала — ОБЯЗАТЕЛЬНО
  - requirement                    # requirement | bug | decision | feedback | status | risk

# Связи (роутинг)
stakeholders:                      # кто в канале — node_ids из NEXUS/team (ascii) — ОБЯЗАТЕЛЬНО
  - team-lastname-firstname
system_areas:                      # затрагиваемые участки системы — ссылки на CORTEX/product
  - "[[cortex-area-slug]]"
goals:                             # цели/OKR, которые питает канал — OBJ/KR-коды
  - "KR-0.0"

# Обработка входящей информации
ingest_action: >                   # что делать с инфой отсюда: → /req-context | → CORTEX/decisions | → OKR-сигнал | → трекер | FYI
  Правило обработки входящих сообщений из этого канала.
---

# {{platform}} · {{handle}} — {{purpose}}

> ⚠️ **допущение клиента (онбординг)**, требует валидации. CP отражает уровень доверия, не подтверждённый факт.

## Назначение

{{purpose}}

## Темы (по каким вопросам пишут)

{{topics}}

## Типы сигналов

{{signal_types}}

## Кто в канале (стейкхолдеры)

{{stakeholders}}   ← [[team-lastname-firstname]]

## Участки системы

{{system_areas}}

## Цели / OKR

{{goals}}

## Как обрабатывать входящую информацию

{{ingest_action}}
