# Эталон промоута — pulse-promote

Источник сигналов: `../../pulse-radar/examples/ideal_radar.md` (обезличенный).
Радар-нота: `GROUND/PULSE/radar/2026-01-15-pulse-radar.md` (window 2026-01-13..2026-01-15, 4 сигнала).

## Список кандидатов (шаг 5)

```
1. new-problem · GROUND/NEXUS/problem/problem-payments-cache-migration.md · нет ответственного за миграцию остатков кэш→БД
2. ownership-fact · GROUND/NEXUS/ownership/ownership-payments-migration.md · зона миграции остатков без владельца
SKIP: инцидент шлюза 500 — разовый, закрыт обходным кешированием (не структурный)
SKIP: ❗ согласовать окно миграции — действие-на-PO (факт уже поднят кандидатом #1)
SKIP: catalog-индексация — уже промоучена ранее (already-promoted)
```

## Новый узел (после выбора PO: «1»)

`GROUND/NEXUS/problem/problem-payments-cache-migration.md`:

```yaml
---
nexus: problem
node_id: problem-payments-cache-migration
node_type: step-overview
kind: empirical
owner: <po_name из domain-profile>
confidence: 0.3
sources: [radar-2026-01-15, "Чат «Платежи» · Иванов Иван · 09:15"]
updated: 2026-01-15
ttl_days: 90
ripeness: fresh
title: Миграция остатков кэш→БД без ответственного
source_note: GROUND/PULSE/radar/2026-01-15-pulse-radar.md
owns_node: <team-node-id PO>
mentions: []
involves: []
---
# Миграция остатков кэш→БД без ответственного

Остатки платежей держатся только в кэше; перенос в БД не сделан и не закреплён за
владельцем. Всплыло на инциденте шлюза (обходной путь — кеш на 5 минут), риск потери
данных при сбое. Якорь: Чат «Платежи» · Иванов Иван · 09:15.
```

## Additive-апдейт (пример на существующем узле)

Если бы `ownership-payments-migration.md` уже существовал — в конец тела, раздел
`## Сигналы из чатов (радар)`, один булет (curated-текст и frontmatter кроме `updated`/`sources` не трогаются):

```
- [2026-01-15] зона миграции остатков кэш→БД без владельца ← Чат «Платежи» · Иванов Иван · 09:15 (radar)
```

## Идемпотентность

Повторный прогон по той же `2026-01-15-pulse-radar.md`: узел `problem-payments-cache-migration`
уже есть → `already-promoted`, пропуск. Дубли не плодятся.
