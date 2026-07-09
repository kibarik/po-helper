# BFT Backlog Control — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сделать состояние каждого БФТ видимым на доске Backlog.md — прикрепить синхронизацию доски к существующему пайплайну `bft-writer`, без нового навыка/команд.

**Architecture:** Два измерения: **статус задачи Backlog = контроль процесса** (5 состояний `To Do → In Progress → Wait for Review → Accepted → Done`), **чек-лист AC = стадии пайплайна** (value…deliver). Протокол вызовов `backlog`/`mcp__backlog__*` живёт в одном месте — секция «§ Синхронизация с доской» в `bft-writer/SKILL.md`. Каждый командный файл `bft-*.md` получает одну строку-ссылку на протокол. Доска — операционное зеркало, не источник истины.

**Tech Stack:** Markdown (навык + команды), Backlog.md CLI/MCP (v1.44+), bash (`install.sh`), YAML (`backlog/config.yml`). Кода нет — документарно-конфигурационная задача, «тесты» = верификационные команды.

## Global Constraints

- **Инварианты дизайна (не переоткрывать)** — из `docs/superpowers/specs/2026-07-09-bft-backlog-control-design.md`:
  - статус = контроль процесса (5 состояний), AC = стадии пайплайна;
  - прикрепление к существующему `bft-writer`, **без нового навыка/команд/хуков/MCP-серверов**;
  - `Wait for Review` = приёмка внешним PO (заказчик); `Accepted` — **только после внесения всех правок**; отказ → `In Progress` + `--priority high`; обе ветки приёмки — **обязательный** `--append-notes`;
  - «комментарии» = notes задачи (`--append-notes`), треда комментариев в Backlog.md нет;
  - 5 статусов контроля — **только для label `bft`**; OKR/sprint/request/release остаются `To Do/In Progress/Done`.
- **Единый источник истины по механике** — секция «§ Синхронизация с доской» в `bft-writer/SKILL.md`. Командные файлы на неё только ссылаются, механику не дублируют.
- **Канонический список стадий BFT** (порядок AC), из `backlog-ops.template.md`:
  `value · context-gen · ext-teams · problem · concept · debate · constraints · draft · validate · deliver` (10 стадий; `context-gen-deep` — вариант `context-gen`, отдельного AC не создаёт).
- **Точное имя статуса приёмки:** `Wait for Review` (не `Review` — семантика важнее краткости, открытый вопрос спеки закрыт в пользу полного имени).
- **Идемпотентность:** повторный прогон `install.sh` и повторные вызовы синхронизации не ломают состояние (find-or-create задачи, guard на наличие статуса перед правкой конфига).

## Маппинг стадия → команда → статус контроля → AC

Единая таблица, используется в Task 1 и Task 2. `find-or-create` — только на первой стадии (`/bft-value`); дальше задача уже существует.

| # | Стадия (AC) | Команда(ы) | Статус контроля после стадии |
|---|---|---|---|
| 1 | `value` | `/bft-value` | `In Progress` (**find-or-create** задачи, label `bft`) |
| 2 | `context-gen` | `/bft-context-gen`, `/bft-context-gen-deep` | `In Progress` |
| 3 | `ext-teams` | `/bft-ext-teams` | `In Progress` |
| 4 | `problem` | `/bft-problem` | `In Progress` |
| 5 | `concept` | `/bft-concept` | `In Progress` |
| 6 | `debate` | `/bft-debate` | `In Progress` (забраковано → `--uncheck-ac concept`, остаёмся `In Progress`) |
| 7 | `constraints` | `/bft-constraints` | `In Progress` |
| 8 | `draft` | `/bft-draft` | `In Progress` |
| 9 | `validate` | `/bft-validate` | 🟢/🟡 → **`Wait for Review`**; 🔴 → `--uncheck-ac draft`, остаёмся `In Progress` |
| — | (приёмка внешним PO) | развилка §2.4, не команда | одобрено+правки внесены → **`Accepted`**; отказ → `--uncheck-ac validate` + `--priority high` + `In Progress` |
| 10 | `deliver` | `/bft-deliver` | `Done` (предусловие: задача в `Accepted`) |

---

## File Structure

- `.claude/skills/bft-writer/SKILL.md` — **добавить** секцию «§ Синхронизация с доской» (протокол + таблица маппинга + правило аудита приёмки). Единственный источник механики. **Modify.**
- `.claude/commands/bft-*.md` (×11) — **добавить** по одной строке-ссылке на протокол в конец файла. **Modify ×11.**
- `backlog-ops.template.md` — **добавить** блок «BFT — жизненный цикл контроля» (5 состояний + маппинг статус/стадия + правило обязательного аудита на приёмке). **Modify.**
- `install.sh` — **добавить** идемпотентную простановку 5 статусов в `backlog/config.yml` после `backlog init`. **Modify.**
- `docs/bft-pipeline/` — визуальный референс. **Уже готов** (перенесён на ветку), в этом плане не трогаем.

---

### Task 1: Секция «§ Синхронизация с доской» в SKILL.md

Единый источник механики. Всё остальное на неё ссылается — делаем первой.

**Files:**
- Modify: `.claude/skills/bft-writer/SKILL.md` (добавить секцию перед финальным блоком «## Главное правило процесса»)

**Interfaces:**
- Produces: секция с якорным заголовком `## § Синхронизация с доской (Backlog.md control)`, на которую ссылаются все 11 командных файлов (Task 2) строкой вида «по протоколу SKILL.md § Синхронизация с доской».
- Consumes: таблицу маппинга стадия→статус (см. выше в плане).

- [ ] **Step 1: Добавить секцию в SKILL.md**

Вставить перед строкой `## Главное правило процесса` следующий блок:

```markdown
## § Синхронизация с доской (Backlog.md control)

Доска Backlog.md — операционное зеркало этого пайплайна: состояние каждого БФТ видно на доске, PO не теряет ни один БФТ из контекста. **Это единственный источник механики синхронизации** — командные файлы `bft-*.md` только ссылаются сюда.

**Два измерения задачи `bft`:**
- **status задачи = контроль процесса** (жизненный цикл, 5 состояний).
- **чек-лист AC = стадии пайплайна** (`value`…`deliver`).

**Пять состояний контроля** (только для label `bft`): `To Do → In Progress → Wait for Review → Accepted → Done`.

| Стадия (команда) | AC отметить | status после стадии |
|---|---|---|
| `/bft-value` | `value` | `In Progress` (**find-or-create** задачи) |
| `/bft-context-gen` · `/bft-context-gen-deep` | `context-gen` | `In Progress` |
| `/bft-ext-teams` | `ext-teams` | `In Progress` |
| `/bft-problem` | `problem` | `In Progress` |
| `/bft-concept` | `concept` | `In Progress` |
| `/bft-debate` | `debate` (забраковано → `--uncheck-ac concept`) | `In Progress` |
| `/bft-constraints` | `constraints` | `In Progress` |
| `/bft-draft` | `draft` | `In Progress` |
| `/bft-validate` | `validate` (🔴 → `--uncheck-ac draft`) | 🟢/🟡 → `Wait for Review`; 🔴 → `In Progress` |
| приёмка внешним PO (§ ниже) | — | `Accepted` / отказ → `In Progress` |
| `/bft-deliver` | `deliver` | `Done` |

**Find-or-create (на стадии `/bft-value`):**
```bash
# ищем задачу этого эпика среди bft
backlog task list -l bft --plain | grep -i "<epic_code>"
# нет → создаём с полным чек-листом стадий
backlog task create "БФТ <epic_code> — <название>" -l bft -s "In Progress" \
  -d "Артефакт: bft_documentation/<epic_code>/ · трекер: <jira_key>" \
  --ac value --ac context-gen --ac ext-teams --ac problem --ac concept \
  --ac debate --ac constraints --ac draft --ac validate --ac deliver
```
Задача уже есть → переиспользуем её id, второй раз не создаём. То же доступно через `mcp__backlog__task_create` / `mcp__backlog__task_list`.

**Отметка стадии** (после каждой стадии, на STOP-паузе):
```bash
backlog task edit <task-id> --check-ac <N>          # N — позиция стадии в чек-листе (value=1…deliver=10)
backlog task edit <task-id> -s "In Progress"        # если меняется status
backlog task edit <task-id> --append-notes "стадия <name>: <краткий итог/где остановились>"
```
Возврат на шаг назад (дебаты забраковали / валидация 🔴) → `--uncheck-ac <N>`, status остаётся `In Progress`.

**Развилка приёмки (Wait for Review) — обязательный аудит.**
После `/bft-validate` 🟢/🟡: status → `Wait for Review`, черновик уходит внешнему PO (заказчику).
- **ОДОБРЕНО** → **обязательно** `--append-notes "одобрил {кто} · {когда} · замечания {…}"`. Status → `Accepted` **только когда все правки внесены и учтены в БФТ**. Одобрение с замечаниями само по себе ≠ `Accepted`, пока замечания не внесены.
  ```bash
  backlog task edit <task-id> --append-notes "одобрил {кто} · {дата} · замечания {…}"
  backlog task edit <task-id> -s "Accepted"     # только после внесения всех правок
  ```
- **ОТКАЗАНО** → **обязательно** `--append-notes "отказал {кто} · правки на следующую итерацию {…}"`, затем новая итерация с повышенным приоритетом:
  ```bash
  backlog task edit <task-id> --append-notes "отказал {кто} · правки {…}"
  backlog task edit <task-id> --uncheck-ac 9 --priority high -s "In Progress"
  ```
Замечания ревью также питают Lessons Learned (`resources/review_feedback.md`, принцип 14).

**Отгрузка** (`/bft-deliver`): предусловие — задача в `Accepted`. После публикации:
```bash
backlog task edit <task-id> --check-ac 10 -s "Done"
```

**Правила:** доска отражает, а не решает (валидность — за hard gates/Светофором); содержание требований на доску не копируем (только ссылки/коды/пути); повторный вызов синхронизации идемпотентен (find-or-create, notes только добавляют).
```

- [ ] **Step 2: Проверить, что секция на месте и уникальна**

Run: `grep -c "§ Синхронизация с доской" .claude/skills/bft-writer/SKILL.md`
Expected: `1`

Run: `grep -n "## Главное правило процесса" .claude/skills/bft-writer/SKILL.md`
Expected: строка секции «Главное правило» идёт **после** новой секции (номер строки больше, чем у «§ Синхронизация»).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/bft-writer/SKILL.md
git commit -m "feat(bft-writer): § Синхронизация с доской — протокол контроля БФТ на Backlog.md"
```

---

### Task 2: Строка-ссылка в 11 командных файлах bft-*.md

Минимальный след: каждый командный файл получает одну строку в конце, указывающую стадию/статус и отсылающую к протоколу в SKILL.md. Механику не дублируем.

**Files:**
- Modify: `.claude/commands/bft-value.md`
- Modify: `.claude/commands/bft-context-gen.md`
- Modify: `.claude/commands/bft-context-gen-deep.md`
- Modify: `.claude/commands/bft-ext-teams.md`
- Modify: `.claude/commands/bft-problem.md`
- Modify: `.claude/commands/bft-concept.md`
- Modify: `.claude/commands/bft-debate.md`
- Modify: `.claude/commands/bft-constraints.md`
- Modify: `.claude/commands/bft-draft.md`
- Modify: `.claude/commands/bft-validate.md`
- Modify: `.claude/commands/bft-deliver.md`

**Interfaces:**
- Consumes: секцию «§ Синхронизация с доской» из Task 1 (ссылка по имени).

- [ ] **Step 1: Дописать строку синхронизации в конец каждого файла**

В **конец** каждого файла (после блока «## Запреты», если он есть) добавить блок из двух строк — с точной стадией и статусом для этого файла:

`bft-value.md`:
```markdown

## Синхронизация с доской
`value` · status `In Progress` (**find-or-create** задачи `bft`) — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-context-gen.md` и `bft-context-gen-deep.md`:
```markdown

## Синхронизация с доской
`context-gen` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-ext-teams.md`:
```markdown

## Синхронизация с доской
`ext-teams` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-problem.md`:
```markdown

## Синхронизация с доской
`problem` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-concept.md`:
```markdown

## Синхронизация с доской
`concept` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-debate.md`:
```markdown

## Синхронизация с доской
`debate` · status `In Progress` (забраковано → `--uncheck-ac concept`) — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-constraints.md`:
```markdown

## Синхронизация с доской
`constraints` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-draft.md`:
```markdown

## Синхронизация с доской
`draft` · status `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-validate.md`:
```markdown

## Синхронизация с доской
`validate` · 🟢/🟡 → status `Wait for Review` (приёмка внешним PO); 🔴 → `--uncheck-ac draft`, `In Progress` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

`bft-deliver.md`:
```markdown

## Синхронизация с доской
`deliver` · предусловие status `Accepted` → после публикации `--check-ac deliver` + status `Done` — по протоколу `bft-writer/SKILL.md` § Синхронизация с доской.
```

- [ ] **Step 2: Проверить, что все 11 файлов получили ровно одну ссылку**

Run:
```bash
grep -rl "§ Синхронизация с доской" .claude/commands/bft-*.md | wc -l
```
Expected: `11`

Run (ни одного дубля внутри файла):
```bash
for f in .claude/commands/bft-*.md; do echo "$(grep -c 'Синхронизация с доской' "$f") $f"; done
```
Expected: каждая строка начинается с `1 ` (по одному упоминанию в каждом из 11 файлов).

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/bft-*.md
git commit -m "feat(bft-commands): ссылка на протокол синхронизации с доской в 11 стадиях"
```

---

### Task 3: BFT-жизненный цикл в backlog-ops.template.md

Конвенция операционного штаба должна описывать 5-состояний контроль для BFT (сейчас там только `To Do/In Progress/Done`).

**Files:**
- Modify: `backlog-ops.template.md` (добавить блок после раздела «## Стадии пайплайнов (готовые чек-листы AC)»)

**Interfaces:**
- Consumes: имена статусов и правило аудита — те же, что в Task 1 (согласованность).

- [ ] **Step 1: Добавить блок BFT-жизненного цикла**

После раздела «## Стадии пайплайнов (готовые чек-листы AC)» (перед «## Когда обновлять доску…») вставить:

```markdown
---

## BFT — жизненный цикл контроля (5 состояний)

Для label `bft` **status задачи = контроль процесса** (не просто крупная фаза). Остальные типы (`okr`/`sprint`/`request`/`release`) — обычные `To Do/In Progress/Done`.

`To Do → In Progress → Wait for Review → Accepted → Done`

| status | Значение | Переход |
|---|---|---|
| **To Do** | взят на контроль, пайплайн не начат | парковка будущего БФТ, чтоб не забыть |
| **In Progress** | идёт пайплайн (`value`…`validate`) | старт `/bft-value` (find-or-create задачи) |
| **Wait for Review** | черновик у внешнего PO на приёмке требований | `/bft-validate` 🟢/🟡 |
| **Accepted** | внешний PO одобрил **и все правки внесены в БФТ** | развилка приёмки (см. ниже) |
| **Done** | опубликовано в JIRA + Confluence | `/bft-deliver` |

**Обязательный аудит на приёмке (`Wait for Review`):**
- **Одобрено** → `--append-notes "одобрил {кто} · {когда} · замечания {…}"`; status → `Accepted` **только после внесения всех правок** (одобрение с замечаниями ≠ `Accepted`, пока не внесены).
- **Отказано** → `--append-notes "отказал {кто} · правки {…}"`, затем `--uncheck-ac validate --priority high` и status → `In Progress` (новая итерация).

Механика вызовов (find-or-create, `--check-ac`, `-s`, `--append-notes`) — в `bft-writer/SKILL.md` § Синхронизация с доской.
```

- [ ] **Step 2: Проверить**

Run: `grep -c "Wait for Review" backlog-ops.template.md`
Expected: `≥ 2` (заголовок таблицы + правило аудита).

Run: `grep -c "BFT — жизненный цикл контроля" backlog-ops.template.md`
Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add backlog-ops.template.md
git commit -m "docs(backlog-ops): BFT-жизненный цикл контроля (5 состояний + аудит приёмки)"
```

---

### Task 4: install.sh — идемпотентная простановка 5 статусов

После `backlog init` (который ставит `To Do/In Progress/Done`) дописать статусы контроля BFT в `backlog/config.yml`. `backlog config set statuses` **не поддерживается** (массивы правятся в файле напрямую) — правим `sed`-ом по строке, с guard на идемпотентность.

**Files:**
- Modify: `install.sh` (внутри функции `adapt_backlog_init`, после успешного init / в конце функции)

**Interfaces:**
- Consumes: `$TARGET/backlog/config.yml`, созданный `backlog init` (строка `statuses: [...]`).

- [ ] **Step 1: Добавить блок простановки статусов**

В функцию `adapt_backlog_init` (в `install.sh`), **после** блока `backlog init …` и **до** копирования `operational-hq.md`, добавить:

```bash
  # BFT-контроль: расширенные статусы доски (идемпотентно; массивы backlog правятся в файле)
  local CFG="$TARGET/backlog/config.yml"
  if [ -f "$CFG" ] && ! grep -q "Wait for Review" "$CFG"; then
    local _tmp; _tmp="$(mktemp)"
    sed 's/^statuses:.*/statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]/' \
      "$CFG" > "$_tmp" && mv "$_tmp" "$CFG"
    echo "  ✓ backlog статусы расширены для BFT-контроля (5 состояний)"
    rep "backlog_statuses: OK (5 для BFT)"
  fi
```

- [ ] **Step 2: Синтаксис-чек**

Run: `bash -n install.sh && echo "syntax OK"`
Expected: `syntax OK`

- [ ] **Step 3: Проверить sed-преобразование на копии конфига (реальный прогон)**

Run:
```bash
tmp=$(mktemp -d); printf 'statuses: ["To Do", "In Progress", "Done"]\ndefaultStatus: To Do\n' > "$tmp/config.yml"
sed 's/^statuses:.*/statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]/' "$tmp/config.yml"
```
Expected: первая строка вывода =
`statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]`

- [ ] **Step 4: Проверить идемпотентность (второй прогон не дублирует)**

Run:
```bash
out=$(sed 's/^statuses:.*/statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]/' <<<'statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]')
echo "$out"; echo "$out" | grep -c "Wait for Review"
```
Expected: строка без изменений, счётчик `1` (guard `grep -q "Wait for Review"` в install.sh при этом вообще пропустит правку).

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install): 5 статусов доски для BFT-контроля (идемпотентно)"
```

---

### Task 5: Сквозная верификация фичи (end-to-end на реальной доске)

Не новый код — проверка, что синхронизация реально работает на живом Backlog.md (v1.44+).

**Files:** нет (только прогон CLI во временной директории).

- [ ] **Step 1: Прогнать жизненный цикл BFT на временной доске**

Run:
```bash
d=$(mktemp -d); cd "$d"; git init -q
backlog init "e2e" --defaults --integration-mode mcp --check-branches false >/dev/null 2>&1
sed -i.bak 's/^statuses:.*/statuses: ["To Do", "In Progress", "Wait for Review", "Accepted", "Done"]/' backlog/config.yml
# find-or-create
backlog task create "БФТ EPIC-99 — тест" -l bft -s "In Progress" \
  --ac value --ac context-gen --ac ext-teams --ac problem --ac concept \
  --ac debate --ac constraints --ac draft --ac validate --ac deliver >/dev/null
# пройти до validate
backlog task edit task-1 --check-ac 1 --check-ac 2 >/dev/null
# приёмка
backlog task edit task-1 -s "Wait for Review" --append-notes "одобрил PO · 2026-07-09" >/dev/null
backlog task edit task-1 -s "Accepted" >/dev/null
backlog task edit task-1 --check-ac 10 -s "Done" >/dev/null
backlog task view task-1 --plain
cd - >/dev/null; rm -rf "$d"
```
Expected: карточка показывает status `Done`, notes содержат «одобрил PO», чек-лист с отмеченными AC. Все команды exit 0 (статус `Wait for Review`/`Accepted` приняты — значит config.yml с 5 статусами валиден).

- [ ] **Step 2: Финальный self-check плана против спеки**

Пройтись по разделу 4 спеки (`2026-07-09-bft-backlog-control-design.md`): пункты 1–4 покрыты Task 1–4, пункт 5 (референс) уже готов. Инварианты Global Constraints не нарушены.

---

## Self-Review

**1. Spec coverage** (раздел 4 спеки):
- п.1 `SKILL.md` § → Task 1 ✓
- п.2 команды ×11 → Task 2 ✓ (11 файлов перечислены поimenно)
- п.3 `backlog-ops.template.md` → Task 3 ✓
- п.4 `install.sh` статусы → Task 4 ✓
- п.5 `docs/bft-pipeline/` → уже готов (перенесён на ветку), Task 5 верифицирует целиком.
- Развилка приёмки §2.4 (обязательный аудит, Accepted после правок, отказ→high) → в Task 1 и Task 3 ✓

**2. Placeholder scan:** плейсхолдеров-заглушек нет — весь вставляемый контент приведён дословно; `<epic_code>`/`<task-id>`/`{кто}` — намеренные слоты, заполняемые в рантайме пайплайна, не пробелы плана.

**3. Type consistency:** имя якоря секции `§ Синхронизация с доской` идентично в Task 1 (определение), Task 2 (11 ссылок), Task 3 (ссылка). Имена статусов `To Do/In Progress/Wait for Review/Accepted/Done` и строка `statuses:` конфига совпадают в Task 1/3/4/5. Список из 10 AC идентичен в find-or-create (Task 1) и e2e (Task 5).
