---
nexus: landscape
node_id: landscape-index
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
tags: [nexus-index, onboarding, landscape]
---

# Нексус ландшафта — команды вокруг PO

Placeholder-Узел каталога `landscape`. Ландшафт окружающих команд ещё не оцифрован.
Наполнение — командой `/okr-landscape <quarter>` (стадия OKR-пайплайна) или добавлением
ext-team-узлов по шаблону [`_template.md`](_template.md). Засев — из
`domain-profile.landscape.ext_teams` (через `/paf-nexus-create landscape`).

## Назначение

`landscape` отвечает на вопрос «что делают команды вокруг нашего PO». Разграничение
с нексусом `team`: `team` = наши люди внутри (People Graph, `node_type: person`),
`landscape` = чужие команды в орбите (`node_type: ext-team`). Контекст нужен, чтобы
при OKR-планировании и написании БФТ точно понимать блокаторы и связи: «с PO каких
команд я связан при разработке этой задачи и почему».

## Структура Landscape Graph

Каждый Узел нексуса `landscape` = одна внешняя команда (`node_type: ext-team`).

| Слой | Поля Узла | Назначение |
|---|---|---|
| **Идентичность** | `team_name`, `po_name`, `po_channels` | Кто команда и её PO |
| **Зона** | `mission`, `owned_systems` | Чем занята, какими системами владеет |
| **Связь** | `relationship`, `touchpoints`, `influence` | Как связана с нами, где стыки, прямо/косвенно |

Стабильные факты (кто команда, системы, тип связи) живут в узле и переживают кварталы.
Текущий OKR/фокус команды в квартале — НЕ в узле, а в снимке
`{okr_workspace}/landscape-{quarter}.md` (создаётся `/okr-landscape`).

## seed_questions

- Какие команды работают в орбите нашего PO (upstream / downstream / peer / platform / regulator)?
- Кто PO каждой из них и как с ним связаться?
- Какими системами владеет каждая команда (пересечение с нашей архитектурой)?
- Где точки касания: общие сервисы, API, потоки данных, общие стейкхолдеры?
- Через что мы можем влиять на команду — прямо или косвенно?

## Узлы

*(пусто — добавляются по шаблону `_template.md` или командой `/okr-landscape`)*

> ⚠️ **контекст ландшафта**, требует валидации у PO. CP отражает уровень доверия к допущению, не подтверждённый факт.
