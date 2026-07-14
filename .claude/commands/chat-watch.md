---
description: 'Настроить реестр отслеживаемых чатов PO (source/purpose/extract) → watched-chats.yaml. Дальше /chat-sync качает (роль: Настройщик мониторинга)'
---

## Использование

```
/chat-watch
```

Выход: записи в `GROUND/_intake/chats/watched-chats.yaml`. STOP — ждать выбора чатов от PO.

## Инструкция для LLM

Запусти навык **`chat-watch`** (`.claude/skills/chat-watch/SKILL.md`):
1. Прочитай `.claude/domain-profile.md` → `info_sources.chat_adapter` (референс `mts-link`).
2. Адаптер есть → перечисли чаты через него; нет → веди реестр руками.
3. На каждый выбранный PO чат спроси `purpose`/`extract`, запиши в реестр (поле `source`).
Не выбирать чаты за PO.
