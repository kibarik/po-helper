# Excalidraw Board — дизайн навыка для итеративного планирования

**Дата:** 2026-07-09
**Ветка:** `feat/excalidraw-board`
**Статус:** дизайн утверждён, реализация отложена (этот PR = спека, реализация отдельно)

## 1. Задача

PO использует Excalidraw при планировании спринта и OKR. Нужно из Claude Code:

1. **Мгновенно получать предзаполненную доску.** Claude строит содержимое (таблицы задач по KR, OKR-деревья) из обсуждения / OKR-файла / спринт-плана и отдаёт ссылку. Открыл — уже всё нарисовано, работа ведётся оттуда.
2. **Итеративно дорабатывать через доску.** Claude нарисовал → PO правит на доске (двигает, добавляет, удаляет) → передаёт Claude обратно → Claude видит правки и дорабатывает. И так по кругу.
3. **Продолжать в любой момент.** Доска сохраняется как артефакт, к ней можно вернуться в следующей сессии.

### Референс от PO

Целевой вид доски (спринт-план) — сгруппированные таблицы по KR:

- Блоки-заголовки: «Снятие нагрузки БАЗИС», «Развитие витрины Ticketland», «Процессинг Live».
- Каждый блок — таблица с колонками: **Задачи | Образ результата | Критичность | SP**.
- Легенда сверху: **Must — критично** (красный), **Should — важно** (жёлтый), **Could → N+1** (зелёный).
- Строки подсвечены цветом по критичности (Must = красный фон, Should = жёлтый, Could = зелёный).

Прежний UX, который PO получал в другом инструменте:
`http://localhost:5001/#url=http://localhost:5002/board.excalidraw` — self-host excalidraw app (5001) + файл-сервер (5002), deep-link через `#url=`. Открытие ссылки давало уже заполненную доску, от которой велась работа.

## 2. Принятые решения (brainstorming)

| Вопрос | Решение | Почему |
|--------|---------|--------|
| MCP: готовый или свой? | **Готовый** off-the-shelf | Плумбинг решён, вся ценность po-helper — в skill поверх |
| Какой сервер? | **`yctimlin/mcp-excalidraw-server`** | 26 tools, `describe_scene` + `get_canvas_screenshot` (Claude видит правки PO), zero-install через npx, Claude-native |
| С чем синкать доску? | **Свободная доска** | Доска = живой thinking-space; экспорт в vault/backlog по команде; минимум связок, максимум гибкости |
| Где хранить доски? | **Файлы в vault** `GROUND/PULSE/boards/<slug>.excalidraw` | Git-версионируется, привязано к планированию, даёт «продолжить в любой момент» |
| Топология / handoff | **MCP live-канвас** (единый `127.0.0.1:3000`) | Правки PO Claude читает автоматом через `describe_scene`+скриншот — самый гладкий handoff. Опция: `export_to_excalidraw_url` для шаринга/презентации |

## 3. Исследование MCP-серверов

Сравнивались два основных кандидата.

### yctimlin/mcp_excalidraw ← ВЫБРАН
- Репо: https://github.com/yctimlin/mcp_excalidraw · PyPI/npm: `mcp-excalidraw-server` (v1.1.0)
- Установка: zero-setup через npx. Auto-старт канвас-сервера если не поднят.
- Канвас: `http://127.0.0.1:3000`, web UI + REST + WebSocket real-time sync (`ENABLE_CANVAS_SYNC=true` по умолчанию).
- **26 tools:**
  - Элементы: `create_element`, `get_element`, `update_element`, `delete_element`, `query_elements`, `batch_create_elements`, `duplicate_elements`
  - Раскладка: `align_elements`, `distribute_elements`, `group_elements`, `ungroup_elements`, `lock_elements`, `unlock_elements`
  - **Awareness (ключ для handoff):** `describe_scene`, `get_canvas_screenshot`
  - I/O: `export_scene`, `import_scene`, `export_to_image`, `export_to_excalidraw_url`, `create_from_mermaid`
  - State: `clear_canvas`, `snapshot_scene`, `restore_snapshot`
  - Прочее: `set_viewport`, `read_diagram_guide`, `get_resource`
- Персистентность: канвас **in-memory** (рестарт чистит). Durable — только явный `export_scene` в `.excalidraw` файл.
- Ship собственный Claude Code skill (`skills/excalidraw-skill/`, ставится через `install-skill`). **Берём как reference, не как конкурирующий триггер** — наш skill сидит выше и знает про OKR/спринт-паттерны.

### whallysson/excalidraw-mcp (не выбран)
- Репо: https://github.com/whallysson/excalidraw-mcp
- Требует clone + build backend/frontend. 12 tools. Порты 3333 (backend) / 5173 (frontend).
- **Плюс:** durable `CANVAS_DATA_DIR` + localStorage, авто-sync каждые 3с, защита от echo-loop (`source: mcp|frontend`).
- **Минус:** нет `describe_scene`/`get_canvas_screenshot` — handoff «PO поправил → Claude прочитал» слепой. Больше возни с установкой.

### Прочие найденные (не рассматривались детально)
- `excalidraw/excalidraw-mcp` (официальный, streamable) — https://github.com/excalidraw/excalidraw-mcp
- `excalidraw-mcp` (PyPI, Python)
- `@iflow-mcp/0xartex-excalidraw` (npm)
- excalidraw issue #9736 — обсуждение официальной MCP-интеграции

## 4. Архитектура

Три части:

```
┌─────────────────────────────────────────────────────────────┐
│ Skill  excalidraw-board  (.claude/skills/excalidraw-board/)  │  ← мозг (наш)
│  - оркестрация loop, команды, load/save дисциплина           │
│  - рендер-шаблоны sprint-table / okr-tree                    │
└───────────────┬─────────────────────────────────────────────┘
                │ вызывает MCP tools
┌───────────────▼─────────────────────────────────────────────┐
│ MCP  excalidraw  (yctimlin, npx)                             │  ← плумбинг (готовый)
│  - live-канвас 127.0.0.1:3000, WebSocket 2-way              │
│  - 26 tools (batch_create_elements, describe_scene, ...)     │
└───────────────┬─────────────────────────────────────────────┘
                │ export_scene / import_scene
┌───────────────▼─────────────────────────────────────────────┐
│ Vault store  GROUND/PULSE/boards/<slug>.excalidraw           │  ← durable
│  - git-версионируется, источник для «продолжить»             │
└─────────────────────────────────────────────────────────────┘
```

**Ключевой принцип:** канвас = эфемерный рабочий слой (in-memory, чистится на рестарте). Файл в vault = durable. Skill **всегда синхронизирует их явно** (import на старте, export на save/sync).

## 5. Loop / handoff-протокол

```
fill  →  [PO открывает линк, видит заполненную доску]  →  PO правит
   ↑                                                          │
   └────────── Claude дорабатывает  ←──  sync  ←──────────────┘
                                    (авто-save на каждом sync)
```

1. **`fill`** (главное): Claude строит предзаполненную доску из источника (обсуждение / OKR-файл / спринт-план) по рендер-шаблону → `batch_create_elements` → авто-`export_scene` в vault. PO открывает `127.0.0.1:3000` — всё готово.
2. **PO правит** на доске (двигает/добавляет/удаляет). Видно в браузере через WebSocket.
3. **`sync`** (передача назад): `describe_scene` + `get_canvas_screenshot` — Claude читает состояние доски визуально + структурно, диффит с тем что помнит, видит правки PO, комментирует, дорабатывает → авто-`export_scene`.
4. Цикл повторяется. Всегда авто-save, чтобы не терять правки.

`describe_scene` + `get_canvas_screenshot` = «глаза» Claude на правки PO. Без них handoff слепой — это причина выбора yctimlin.

## 6. Команды skill

Триггер `/excalidraw-board` (алиас `/board`). Глаголы:

| Команда | Действие |
|---------|----------|
| `open <slug>` | Поднять канвас (auto), `import_scene` из vault-файла (если есть) иначе новая доска; печать URL `127.0.0.1:3000` |
| `fill <slug> from <source>` | **Главное.** Построить предзаполненную доску из источника (обсуждение / OKR-файл / спринт-план) по рендер-шаблону, `batch_create_elements`, авто-save. Открыл линк → готово |
| `sync` | `describe_scene` + `get_canvas_screenshot`, прочитать правки PO, диффить, дорабатывать, авто-save |
| `save [<slug>]` | `export_scene` → `GROUND/PULSE/boards/<slug>.excalidraw` |
| `list` | Доски в vault |
| `present` | (опц.) `export_to_excalidraw_url` для шаринга/презентации |

## 7. Файлы к созданию (реализация)

1. **`.mcp.json`** — добавить блок:
   ```json
   "excalidraw": {
     "command": "npx",
     "args": ["-y", "mcp-excalidraw-server"],
     "env": { "ENABLE_CANVAS_SYNC": "true" }
   }
   ```
   (env опционален — `ENABLE_CANVAS_SYNC` по умолчанию `true`; зафиксировать явно.)

2. **`.claude/skills/excalidraw-board/SKILL.md`** — оркестрация loop + команды раздела 6. Frontmatter `name` + `description` с триггерами («доска», «excalidraw», «нарисуй спринт на доске», «/excalidraw-board», «/board») по образцу существующих skill (см. `diagram-view`, `okr-planner`).

3. **`.claude/skills/excalidraw-board/resources/render-templates.md`** — рецепты рендера в excalidraw-элементы:
   - **sprint-table**: KR-блок = заголовок + таблица (колонки Задачи/Образ результата/Критичность/SP), строки-задачи, цвет строки по критичности (Must=красный `#ffc9c9`, Should=жёлтый `#ffec99`, Could=зелёный `#b2f2bb`), легенда сверху. Точь-в-точь референс PO.
   - **okr-tree**: OBJ → KR-карточки.
   - Геометрия: X-координаты колонок, высота строки, вертикальный отступ между блоками, группировка каждого блока через `group_elements`.

4. **`.claude/skills/excalidraw-board/resources/element-schema.md`** — шпаргалка по excalidraw element JSON (rectangle / text / line, привязка text к контейнеру `containerId`, `boundElements`) для корректных `batch_create_elements`. Excalidraw не имеет нативных таблиц — таблица = прямоугольники + текст + grid-линии.

5. **`GROUND/PULSE/boards/.gitkeep`** — папка досок.

6. **Reference:** `npx -y mcp-excalidraw-server install-skill` — забрать родной yctimlin-skill как справочник по tool-семантике, НЕ регистрировать как конкурирующий триггер.

## 8. Открытые вопросы для реализации

- Точная геометрия sprint-table (ширины колонок, перенос длинного «Образа результата») — подобрать итеративно, используя `get_canvas_screenshot` для самопроверки раскладки.
- Нужен ли `fill` со слотом источника (`from okr-q3`, `from sprint-42`, `from discussion`) как явный аргумент или Claude инферит из контекста.
- Стоит ли авто-`open` браузера (у yctimlin CLI есть авто-старт канваса; открытие вкладки — на стороне PO).
- Именование slug'ов: свободное или конвенция (`sprint-<n>`, `okr-<quarter>`).

## 9. Проверенные предпосылки

- `node v25.6.1`, `npx 11.9.0` — есть.
- `.excalidraw` не в `.gitignore` — файлы будут трекаться.
- `GROUND/PULSE/` существует (операционный слой) — валидный дом для досок.

## Источники

- [yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw)
- [whallysson/excalidraw-mcp](https://github.com/whallysson/excalidraw-mcp)
- [excalidraw/excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp)
- [excalidraw issue #9736 — MCP integration](https://github.com/excalidraw/excalidraw/issues/9736)
- [excalidraw-mcp · PyPI](https://pypi.org/project/excalidraw-mcp/)
