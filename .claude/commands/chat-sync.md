---
description: 'Выгрузить сообщения отслеживаемых чатов за окно в GROUND/_intake/chats по контракту чат-дампа через source-адаптер (роль: Диспетчер выгрузки)'
---

## Использование

```
/chat-sync [за неделю | за месяц | YYYY-MM-DD..YYYY-MM-DD]
```

- окно — из запроса; дефолт 14 дней. Выход: файлы `GROUND/_intake/chats/*.md` по контракту.

## Инструкция для LLM

Запусти навык **`chat-sync`** (`.claude/skills/chat-sync/SKILL.md`):
1. Прочитай `.claude/domain-profile.md` → `info_sources.chat_adapter`, `info_sources.chat_intake_dir`.
2. Адаптер/реестр не готовы → подскажи setup адаптера или ручной drop по
   `.claude/skills/chat-sync/resources/chat_dump_contract.md`.
3. Выгрузи окно через адаптер → дампы в `_intake/chats/`. Отчитайся: файлы, чаты. Read-only.
