---
nexus: project-management
node_id: pm-deliverable-slug          # ascii-slug [a-z][a-z0-9-]*; напр. pm-billing-v2 | pm-bft-onboarding | pm-roadmap-q3. КИРИЛЛИЦУ НЕ ИСПОЛЬЗОВАТЬ
node_type: deliverable
paf_step: null
sprint_phase: null
kind: empirical
owner: Product Engineer               # RACI Accountable — PO зоны ответственности
confidence: 0.4                        # 0.2–0.4 = допущение онбординга; 0.6–0.8 = подтверждено планом; 0.9–1.0 = верифицировано (JIRA/релиз)
sources: ["onboarding:interview"]      # реальный источник: jira | confluence | roadmap | onboarding:interview
updated: YYYY-MM-DD
ttl_days: 60                           # план/сроки протухают быстро — короткий TTL триггерит ресинк
ripeness: fresh
tags: [deliverable]

# --- schema_extensions (PO Delivery Map) ---

# Идентичность (обязательные)
title: "Название проекта / артефакта / плана"
deliverable_type: project              # project | artifact | plan — ОБЯЗАТЕЛЬНО
po_owner: team-lastname-firstname      # node_id PO из нексуса team (ascii); кто отвечает за проработку
status: in-progress                    # idea | in-progress | review | done | blocked — ОБЯЗАТЕЛЬНО

# Сроки (обязательные)
start_date: YYYY-MM-DD                 # старт проработки
due_date: YYYY-MM-DD                   # дедлайн готовности (приёмка)

# Этапы проработки — ОБЯЗАТЕЛЬНО (каждый этап = name + status + due)
stages:
  - {name: "Этап 1 (напр. контекст/исследование)", status: done,        due: YYYY-MM-DD}
  - {name: "Этап 2 (напр. БФТ/проектирование)",     status: in-progress, due: YYYY-MM-DD}
  - {name: "Этап 3 (напр. реализация)",             status: todo,        due: YYYY-MM-DD}
  - {name: "Этап 4 (напр. приёмка/релиз)",          status: todo,        due: YYYY-MM-DD}

# Вехи (ключевые контрольные точки)
milestones:
  - {name: "Веха 1", date: YYYY-MM-DD}

# Связи с другими артефактами PO (node_ids / ключи)
linked_okr:   []                       # OBJ/KR, которые этот deliverable двигает
linked_bft:   []                       # БФТ (JIRA-эпики), входящие в проработку
linked_sprint: []                      # спринты, в которых ведётся работа
depends_on:   []                       # node_ids deliverable'ов, от которых зависит срок

# Критерий готовности
definition_of_done: >
  Образ приёмки: что должно быть сделано/опубликовано, чтобы deliverable считался завершённым.
---

# {{title}} — {{deliverable_type}}

> ⚠️ **допущение клиента (онбординг)**, требует валидации. CP отражает уровень доверия к плану, не подтверждённый факт.

## Зона ответственности

**PO:** [[{{po_owner}}]]
**Тип:** {{deliverable_type}} (проект | артефакт | план)
**Статус:** {{status}}

## Сроки

**Старт:** {{start_date}} → **Дедлайн:** {{due_date}}

| Веха | Дата |
|---|---|
| {{milestones}} | |

## Этапы проработки

| Этап | Статус | Срок |
|---|---|---|
| {{stages}} | | |

## Связи

- **OKR/KR:** {{linked_okr}}
- **БФТ:** {{linked_bft}}
- **Спринты:** {{linked_sprint}}
- **Зависимости:** {{depends_on}}

## Образ приёмки (Definition of Done)

{{definition_of_done}}
