---
description: Сбор контекста PO уровня Deep Research — sprint/epic/risk/decision/bft. Fast (руками) или Deep (Workflow).
---

## Использование

```
/po-research <domain> <topic-id> [fast|deep]
```

**Параметры:**
- `<domain>` — `sprint` | `epic` | `bft` | `risk` | `decision`.
- `<topic-id>` — id топика: sprint-id (`2026Q3-S3`), jira_key (`PROJ-101`), epic_code+key (`EPIC-10 PROJ-101`), risk-id/topic.
- режим (опц.) — `fast` (по умолчанию) или `deep`.

## Примеры

```
/po-research epic PROJ-101
/po-research sprint 2026Q3-S3
/po-research risk legacy_db-spof
/po-research bft EPIC-10 PROJ-101
/po-research epic PROJ-101 deep
```

## Что делает

Собирает `context-pack.md` (CORTEX-фон + NEXUS-факты с якорями + coverage-matrix + `[УТОЧНИТЬ]`) на выходе:

```
{research_workspace}/context-pack.md
```

- **fast** — single-pass, руками, через навык `po-research`. Routine / quick check / KR Low.
- **deep** — **Phase 0 (опрос PO → seed)** → Perplexity-loop через Workflow `po-context-research` с `args.seed`. KR Critical/High. Дорого (fan-out агентов) — запускать осознанно.

## Важно

**Read-only, нулевой допуск к галлюцинациям.** Каждый факт ← источник (JIRA / Confluence / repowise / vault / web). Нет источника → `[УТОЧНИТЬ]`. VPN недоступен → собрать доступное, остальное пометить честно.

`bft`-домен — совместим с прежним `/bft-context-gen` (та же матрица БФТ).

---

## Инструкция для LLM

Запусти навык **`po-research`** (`.claude/skills/po-research/SKILL.md`):
1. Распознай `<domain>` + `<topic-id>` + режим.
2. Возьми пресет из `resources/domains.md`, finding-контракт из `resources/source-registry.md`, шаблон из `resources/pack-template.md`.
3. **fast** → выполни шаги 0–6 раздела «FAST» навыка, СТОП для PO.
4. **deep** → сначала **Phase 0: опрос PO** (раздел «DEEP — Phase 0» навыка): по 1 вопросу из `resources/domains.md` (блок «Phase 0 seed»), PO может прервать «достаточно». Собери `seed` (`intent`/`hypotheses`/`scope`/`priorities`/`risks`/`known_anchors`). Затем запусти Workflow `po-context-research` с `args = { domain, topic, tier, seed }` (через инструмент Workflow). Планировщик получит `seed` и приоритизирует sub-Q вокруг образа результата PO. Вернёт тот же артефакт с Evidence Quality + `seed=PO ✅` в meta.

Жёсткие правила — раздел «Anti-rules» навыка.
