---
nexus: landscape
node_id: landscape-team-slug        # ascii-slug [a-z][a-z0-9-]*; напр. landscape-team-payments. КИРИЛЛИЦУ НЕ ИСПОЛЬЗОВАТЬ
node_type: ext-team
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.5                      # 0.2–0.4 = допущение; 0.6–0.8 = подтверждено PO/интервью; 0.9–1.0 = верифицировано несколькими источниками
sources: ["okr-landscape:interview"]  # реальный источник: okr-landscape:interview | their-okr | confluence | jira | architecture-inference
updated: YYYY-MM-DD
ttl_days: 180
ripeness: fresh
tags: [ext-team, landscape]

# --- schema_extensions (Landscape Graph — команды вокруг PO) ---

# Идентичность (обязательные)
team_name: "Название команды"
po_name: "Имя PO"                   # ссылка [[team-...]] если PO есть в People Graph (нексус team); иначе имя строкой
po_channels:                        # как связаться с PO
  - "Slack: @handle"

# Что делает команда
mission: >                          # 1–2 фразы: зона ответственности команды
  Описание миссии/зоны ответственности команды.

owned_systems:                      # сервисы/системы во владении (имена из C1-архитектуры)
  - "Система X"

# Связь с нашей командой (критично для роутинга зависимостей)
relationship: peer                  # upstream (мы зависим от них) | downstream (они зависят от нас) | peer | platform | regulator
touchpoints:                        # точки касания — ОБЯЗАТЕЛЬНО (общие системы / API / потоки данных / общие стейкхолдеры)
  - "точка касания 1"
influence: direct                   # direct (прямой стык) | indirect (через посредника)

collaboration_history: >            # опц.: прошлый совместный опыт, договорённости, конфликты
  Описание истории совместной работы (если есть).
---

# {{team_name}} — внешняя команда ({{relationship}})

> ⚠️ **контекст ландшафта**, требует валидации у PO. CP отражает уровень доверия, не подтверждённый факт.

## Миссия

{{mission}}

## Системы во владении

{{owned_systems}}

## Связь с нашей командой

**Тип:** {{relationship}}
**Влияние:** {{influence}}
**Точки касания:** {{touchpoints}}

## PO и контакты

- **PO:** [[{{po_name}}]]
- **Каналы:** {{po_channels}}

## История взаимодействия

{{collaboration_history}}
