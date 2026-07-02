---
nexus: team
node_id: team-lastname-firstname   # ascii-slug [a-z][a-z0-9-]*; напр. team-ivanov-ivan. КИРИЛЛИЦУ НЕ ИСПОЛЬЗОВАТЬ
node_type: person
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Ops
confidence: 0.5                     # 0.2–0.4 = допущение онбординга; 0.6–0.8 = подтверждено интервью; 0.9–1.0 = верифицировано несколькими источниками
sources: ["onboarding:interview"]   # указать реальный источник: hr-system | self-reported | linkedin | onboarding:interview
updated: YYYY-MM-DD
ttl_days: 180
ripeness: fresh
tags: [person]

# --- schema_extensions (People Graph) ---

# Идентичность (обязательные)
full_name: "Фамилия Имя Отчество"
role_title: "Должность"
department: "Отдел"

# Org Chart
reports_to: team-manager-slug                  # node_id руководителя (ascii); null если CEO/нет руководителя
manages:                                        # node_ids прямых подчинённых (ascii); [] если никого
  - team-report-slug
membership_since: YYYY-MM-DD                   # дата начала в роли; null если неизвестно

# Social Graph
collaborates_with:                              # ключевые рабочие связи вне иерархии (ascii node_ids)
  - team-colleague-slug

# Team Grouping (как сгруппированы по командам)
team_unit: "Squad <name>"                       # команда/под/группа внутри отдела; null если вне команд
team_role: member                               # lead | member | representative; null если вне команд
team_mission: >                                 # за что отвечает команда (заполнять у lead/representative)
  Зона ответственности команды одним абзацем.

# PO Navigation Layer (я-как-PO ↔ человек — ГЛАВНОЕ для /people-map)
proximity: close                                # core | close | extended | peripheral — кто ближе/дальше
interaction_cadence: weekly                     # daily | weekly | biweekly | monthly | ad-hoc | rare
inbound_topics:                                 # с чем ЧЕЛОВЕК сам приходит к PO (он инициатор)
  - "вопрос 1"
clarify_with:                                   # какие ДЕТАЛИ PO уточняет у человека (источник контекста)
  - "деталь 1"
approves:                                       # какие решения человек СОГЛАСОВЫВАЕТ (право решения/sign-off)
  - "решение 1"
escalate_via: team-manager-slug                 # node_id для эскалации через/над этим человеком; null

# Expertise Graph (критично для ИИ-роутинга)
influence_zones:                               # зоны ответственности/влияния — ОБЯЗАТЕЛЬНО
  - "зона 1"
  - "зона 2"
expertise_topics:                              # темы экспертизы — ОБЯЗАТЕЛЬНО
  - "тема 1"
  - "тема 2"
contact_for:                                   # по каким вопросам обращаться — ОБЯЗАТЕЛЬНО
  - "вопрос 1"
  - "вопрос 2"
context_holds: >                               # уникальный контекст для RAG; свободный текст
  Описание уникального контекста, истории решений, доступа к информации.

# Контакты
communication_channels:
  - "Slack: @handle"
  - "email: name@company.ru"
---

# {{full_name}} — {{role_title}}

> ⚠️ **допущение клиента (онбординг)**, требует валидации. CP отражает уровень доверия, не подтверждённый факт.

## Профиль

**Роль:** {{role_title}}  
**Отдел:** {{department}}  
**Команда:** {{team_unit}} ({{team_role}})  
**В роли с:** {{membership_since}}

## Навигация PO (я-как-PO ↔ человек)

- **Близость:** {{proximity}} · взаимодействие {{interaction_cadence}}
- **Приходит ко мне с:** {{inbound_topics}}
- **Уточняю детали:** {{clarify_with}}
- **Согласовывает:** {{approves}}
- **Эскалация через:** [[{{escalate_via}}]]

## Команда

**{{team_unit}}** — {{team_mission}}

## Зоны влияния

{{influence_zones}}

## Экспертиза

{{expertise_topics}}

## По каким вопросам обращаться

{{contact_for}}

## Контекст

{{context_holds}}

## Связи

- **Руководитель:** [[{{reports_to}}]]
- **Подчинённые:** {{manages}}
- **Ключевые коллеги:** {{collaborates_with}}
