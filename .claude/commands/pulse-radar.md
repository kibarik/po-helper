---
description: 'Радар по чатам: чат-дампы за окно → одна датированная PULSE-радар-нота (инциденты/блокеры/решения/действия-на-PO) с привязкой к KR (роль: Радар-аналитик)'
---

## Использование

```
/pulse-radar [--days N | --from YYYY-MM-DD --to YYYY-MM-DD]
```

Выход: `{pulse_radar_dir}/YYYY-MM-DD-pulse-radar.md` (дефолт `GROUND/PULSE/radar`). STOP — отчёт PO.

## Важно

**Нулевой допуск к галлюцинациям.** Каждый сигнал ← реальная реплика в дампе (чат · автор · время).
Нет якоря — нет сигнала. KR-привязка только по существующим `NEXUS/okr/kr-*.md`; нет матча → `[KR?]`.

## Инструкция для LLM

Запусти навык **`pulse-radar`** (`.claude/skills/pulse-radar/SKILL.md`):
1. Прочитай `.claude/domain-profile.md` → `paths.pulse_radar_dir` (дефолт `GROUND/PULSE/radar`).
2. Нет дампов за окно в `_intake/chats/` → СТОП, подскажи `/chat-sync`.
3. Классифицируй сигналы (формат — `resources/radar_format.md`), дедуп по последней ноте, запиши файл.
Read-only: пишет только в `PULSE/radar/`, NEXUS не трогает.
