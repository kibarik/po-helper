# Перенос GANTT-anchored sync в po-helper — дизайн

> Дата: 2026-07-13 · Автор: PO (Ишманов) + Claude · Статус: спека на ревью
> Контекст: функционал разработан и обкатан на живом JIRA в инстансе `mts-po-workspace`
> (ветка `gantt-sync-readmodel`). Задача — вынести generic-слой в фреймворк po-helper,
> чтобы любой пользователь получал синхронизацию GANTT ↔ OKR ↔ JIRA через `install.sh`.
> Исходная механика: `docs/superpowers/specs/2026-07-10-gantt-anchored-sync-design.md` (в workspace).

## 1. Цель

Дать любому проекту на po-helper read-model сверку трёх источников:
**GANTT** (скелет квартала, GanttPRO xlsx) ↔ **OKR** (KR) ↔ **JIRA** (Инициативы/Эпики).
Автоген джойнит источники поверх GANTT и подсвечивает дрейф покрытия. Read-only:
ничего не пишем ни в GANTT, ни в JIRA — только читаем и сверяем.

Механика (модель высот, ключ-mapping, 6 правил дрейфа, формат зеркала) переносится
как есть — она проектно-нейтральна. Переносу подлежит **функционал + описание**,
без данных MTS и без жёстких привязок к `mts-po-workspace`.

## 2. Что переносим / что нет

| Переносим (generic) | НЕ переносим (данные/инстанс) |
|---|---|
| Движок `gen-sync-status.mjs` + тест + фикстуры | `Roadmap-GDS-Q3-2026.xlsx` |
| Skill `gantt-sync` + команда `/gantt-sync` | Реальный `KR-EPIC-MAP.md` MTS |
| Ключи `domain-profile.template.md` | `issues.json`, `GANTT-SYNC-STATUS.md` |
| Обезличенная спека-дизайн | Привязки: Камнев, GDSLV/TLND, TC↔БАЗИС |

## 3. Упаковка в po-helper (конвенции фреймворка)

Следуем сложившейся структуре (как `okr-planner`: движок в `resources/engine/`;
команда — тонкая обёртка в `.claude/commands/`).

```
.claude/skills/gantt-sync/
  SKILL.md                              роль: резолв конфига → сбор issues (MCP) → прогон → показ дрейфа
  resources/engine/
    gen-sync-status.mjs                 движок (парс xlsx + mapping + join + diff + render)
    gen-sync-status.test.mjs            node --test
    fixtures/                           sheet-sample.xml, map-sample.md, jira-sample.json
  examples/
    GANTT-SYNC-STATUS.example.md        обезличенный образец зеркала
.claude/commands/gantt-sync.md          /gantt-sync → invoke skill
```

## 4. Genericize движка

Убрать привязки, вынести в аргументы/конфиг:

1. **Пути** (xlsx / mapping / output) — CLI-аргументы (`--xlsx`, `--map`, `--out`),
   резолвятся skill'ом из `domain-profile.paths`. Убрать хардкод `../Roadmap-GDS-Q3-2026.xlsx`
   и относительный `dirname(import.meta.url)/..`.
2. **JIRA** — только режим `--issues <file>` (уже есть). Прямой REST + `JIRA_PAT` **выпилить**:
   в po-helper трекер строго через MCP (гигиена доступа `domain-profile.tracker.mcp`).
   Issues собирает SKILL.md через `mcp jira_search` по `tracker.projects`, пишет во временный
   `issues.json`, скармливает движку.
3. **Якоря xlsx + JQL-проекты** — аргументы/конфиг с дефолтами под GanttPRO. Раскладка колонок
   B..P и типы фаз (`PHASE_MAP`) остаются с дефолтами; ожидаемая форма экспорта GanttPRO
   документируется в SKILL.md. Проверка опорных строк (внятная ошибка при уехавшей структуре)
   сохраняется.

Чистота: движок остаётся оффлайновым и детерминированным (вход — файлы, выход — markdown),
всё сетевое — на стороне skill через MCP. Это упрощает тест и убирает секреты из кода.

## 5. Новые ключи `domain-profile.template.md`

```yaml
paths:
  # экспорт GanttPRO (скелет квартала; кладёт владелец GANTT, файл заменяется)
  gantt_source_xlsx:     "{planning_root}/Roadmap.xlsx"
  # автоген-зеркало сверки (перезатирается движком, руками не править)
  gantt_sync_status_doc: "{planning_root}/GANTT-SYNC-STATUS.md"
  # kr_epic_map_doc — УЖЕ ЕСТЬ (ключ связи: карточка GANTT → KR → эпики)

tracker:
  # какие проекты сверять со сверкой покрытия (JQL project in (...))
  projects: ["PROJ1", "PROJ2"]

# опц.: якоря парсера GanttPRO. Пусто → дефолты. Правишь, если экспорт на другом языке/шаблоне.
gantt:
  anchors:
    header: "Инициативы в квартале"
    legend: "Легенда фаз:"
    stack:  "Стек:"
```

`base_url`, `mcp` берутся из существующей секции `tracker`.

## 6. Skill `gantt-sync` — поток

1. Резолв путей из `domain-profile.paths`; проверка наличия xlsx и mapping.
2. Сбор live-issues через `mcp jira_search`: `project in (tracker.projects) AND issuetype in (Инициатива, Эпик) AND status != Closed`. Запись в временный `issues.json`.
3. Прогон `gen-sync-status.mjs --xlsx … --map … --issues … --out …` (или `--dry` для превью).
4. Показ PO блока «## Дрейф» как чеклиста + сводки; пункты дрейфа — к разбору вручную (правки в JIRA/OKR/GANTT по согласованию).
5. Кадэнс: раз в спринт, по границам спринтов GANTT (документируется, крон — вне скоупа).

## 7. Границы (как в исходной спеке)

- Read-only: не пишем в GANTT и JIRA автоматически.
- Только дрейф покрытия связей (верх свимлейн↔Инициатива, середина карточка↔KR↔Эпик). Статус↔фаза и rollup — вне скоупа.
- Уровень Историй/Багов не сверяем.

## 8. PR-механика

- Ветка `feat/gantt-sync` от `origin/main` в po-helper (создана).
- Изменения: skill + команда + движок/тест/фикстуры + ключи профиля + обезличенная спека (`docs/.../gantt-anchored-sync-design.md`) + запись в `README.md`/каталог навыков, если требуется.
- Верификация: `node --test` в `resources/engine/` зелёный; движок гоняется на фикстурах end-to-end (`--dry`).
- Данные MTS не коммитятся (проверить `git status` перед коммитом).
- `gh pr create` в po-helper против `main`.

## 9. Решённые развилки

- **Цель PR:** po-helper upstream (раздача через `install.sh --update`), не workspace.
- **Объём:** движок + skill + доки (полный рабочий функционал).
- **JIRA-доступ:** только MCP на стороне skill; прямой REST+PAT из движка удаляется.
- **Язык движка:** Node `.mjs` (как оригинал и `mts-link-chat-sync`), не переписываем на Python.
- **Тесты:** встроенный `node --test`.
