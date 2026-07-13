---
description: 'Read-model сверка GANTT ↔ OKR ↔ JIRA: автоген джойнит KR и live-JIRA поверх скелета GANTT (GanttPRO xlsx) и подсвечивает дрейф покрытия. Read-only (роль: Аудитор соответствия плана квартала)'
---

## Использование

```
/gantt-sync [--dry]
```

- `--dry` — превью зеркала в чат без записи файла.

Входы (из `.claude/domain-profile.md`): `paths.gantt_source_xlsx` (экспорт GanttPRO), `paths.kr_epic_map_doc` (ключ связи карточка→KR→эпики), `tracker.projects` (что сверять, через MCP). Выход: `paths.gantt_sync_status_doc` (зеркало `GANTT-SYNC-STATUS.md`) + блок «## Дрейф» как чеклист в чат. STOP — разбор дрейфа вручную.

## Важно

**Роль: Аудитор соответствия плана квартала.** GANTT — скелет (правит владелец в GanttPRO); KR и JIRA-эпики сверяются с ним. Read-only: ничего не пишем ни в GANTT, ни в JIRA.

**Гигиена:** live-issues — только через MCP (`tracker.mcp`), не прямым REST/PAT. Движок оффлайновый, получает issues готовым `issues.json`.

Полная инструкция — `.claude/skills/gantt-sync/SKILL.md`. Механика — `resources/gantt-anchored-sync-design.md`.
