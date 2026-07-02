---
description: 'Информационные каналы — создать/обновить разметку канала (для чего, темы, стейкхолдеры, участки, цели) как channel-узел NEXUS (роль: Channel Curator)'
---

## Использование

```
/channel-map <slug> [платформа/суть]
```

- `<slug>` — короткий ascii-слаг канала (напр. `billing-tg`, `pm-weekly-sync`). Узел создаётся как `chan-<slug>`.
- `[платформа/суть]` — опц. подсказка (напр. «Telegram», «созвон с лидами»).

Выход: `<channels_nexus>/chan-<slug>.md` + обновлённые `_index.md` (секция «Узлы»).

## Важно

**Роль: Channel Curator.** Задача — разметить один канал так, чтобы ИИ знал, **откуда** приходит информация, **для чего** канал, **по каким темам** пишут, **кто** здесь и куда роутить входящее. Существующий `chan-<slug>` → режим обновления (diff + подтверждение PO).

Каждое поле ← источник (слова PO = R1/R2). Не выдумывать стейкхолдеров/участки/цели — только реальные узлы, иначе `[УТОЧНИТЬ]`.

---

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `.claude/domain-profile.md` — резолвь `paths.channels_nexus` (дефолт `GROUND/NEXUS/channels`), `stakeholders`, `cortex`, `teams`. Профиль пуст → дефолт + `[УТОЧНИТЬ]`.
2. Прочитай `skills/info-channels/SKILL.md`, `resources/channel_schema.md`, шаблон `<channels_nexus>/_template.md`.
3. Проверь `<channels_nexus>/chan-<slug>.md`: есть → режим обновления; нет → создание.
4. Нет `<channels_nexus>/` вовсе → bootstrap: создай папку, `_index.md` (по каталогу §4.2 seed_questions) и зарегистрируй `channels` в `GROUND/NEXUS/_registry.yaml` (`source: custom`), если ещё не зарегистрирован.

### Этап 2: Интервью (по одному вопросу)
Спрашивай по очереди, грунтуясь доменом (не форма — информированная разметка):
1. **Тип и платформа** — `channel_type` + `platform` + `handle` + `direction` + `cadence`.
2. **Назначение** — для чего канал (`purpose`, 1-2 фразы).
3. **Темы** — по каким вопросам здесь пишут (`topics`).
4. **Типы сигналов** — что приходит: requirement/bug/decision/feedback/status/risk (`signal_types`).
5. **Стейкхолдеры** — кто в канале. Сопоставь с `GROUND/NEXUS/team` (node_ids). Нет person-узла → `[УТОЧНИТЬ: нет в team]` или предложи `/paf-nexus-create team`.
6. **Участки системы** — что затрагивает (`system_areas` → CORTEX/product). Нет — `[УТОЧНИТЬ]`.
7. **Цели** — какие OKR питает (`goals` → OBJ/KR). Нет — `[УТОЧНИТЬ]`.
8. **Правило обработки** — что делать с входящим (`ingest_action`, по `routing_rules.md`).

### Этап 3: Запись узла
1. Заполни шаблон `_template.md` ответами. `node_id: chan-<slug>`, `node_type: channel`, `kind: empirical`, `ttl_days: 180`, `updated: today`, `ripeness: fresh`.
2. `confidence`: 0.5 со слов PO; 0.2–0.4 если допущение. `sources`: `["po:observation"]` / `["onboarding:interview"]` (добавляй, не затирай при обновлении).
3. Обязательные `purpose`/`topics`/`stakeholders` пусты → пометь `[УТОЧНИТЬ]` в теле, не выдумывай.
4. Обнови `<channels_nexus>/_index.md` секцию «Узлы» — строка со ссылкой на узел.

### Этап 4: Отчёт + STOP
```
Канал размечен: <channels_nexus>/chan-<slug>.md
Назначение: <кратко>. Темы: <N>. Стейкхолдеры: <список/[УТОЧНИТЬ]>. Роутинг: <ingest_action кратко>.
Покрытие: 🟢/🟡/🔴 (по routing_rules.md §D).
── СТОП ── PO: проверьте разметку. Дальше — /channel-list (обзор) или /channel-route (разметить входящее).
```

## Запреты
1. НЕ выдумывать стейкхолдеров/участки/цели — только реальные узлы, иначе `[УТОЧНИТЬ]`.
2. НЕ затирать `sources` при обновлении — добавлять.
3. Каждый факт о канале ← слова PO или узел домена. Стиль — `skills/bft-writer/resources/writing_style.md` (без декоративных эмодзи).
