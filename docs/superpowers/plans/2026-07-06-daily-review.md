# Daily-Review Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать навык `/daily-review` — обработку транскрипта стендапа/созвона в папку-снапшот PULSE (тонкая заметка + plain-text блокеры + реестр обязательств + дельта перемещений карточек).

**Architecture:** Навык — набор markdown-файлов в `.claude/skills/daily-review/` (`SKILL.md` + `resources/*` + `examples/`), как существующие `summary`/`sprint-planner`. Исполнение — LLM по инструкции SKILL, без кода. Один прогон = папка `GROUND/PULSE/meetings/{type}-{YYYY-MM-DD-HHMM}/` с четырьмя артефактами; carry-forward (входное состояние «что висит») читается из **открытых задач Backlog** по labels, а не из прошлой папки. JIRA read-only.

**Tech Stack:** Markdown, YAML frontmatter. Валидация — `bash`/`grep`/`python3 -c "import yaml"`. Конвенции — из `.claude/skills/summary/` и `.claude/skills/sprint-planner/`.

## Global Constraints

- **Язык артефактов и навыка** — русский (как все навыки po-helper).
- **Минимализм человеко-facing выводов** — `blockers.md` и `report.md` без emoji/иконок/светофоров; факты, plain-text, готово к отправке в чат/email. Табличные рабочие реестры (`commitments.md`, `sprint-pulse.md`) — таблицы без emoji. Стиль прозы — `.claude/skills/bft-writer/resources/writing_style.md`.
- **Нулевые галлюцинации** — каждый факт ← транскрипт. Плейсхолдеры вместо догадок: `[КОД?]`, `[КТО?]`, `[KR?]`, `[КАК ПРОВЕРИТЬ?]`, `[УТОЧНИТЬ]`.
- **JIRA read-only** — навык не читает и не пишет **командный JIRA** через MCP. **Backlog.md — отдельный личный планнер PO** (MCP `backlog`), в него навык пишет SMART-задачи (это не JIRA).
- **Два слоя** — PULSE (знание, неизменяемая запись встречи) + Backlog.md (действие, живой трекер, **истина статуса**). Carry-forward читает открытые задачи Backlog, а не прошлую папку.
- **Проекция в Backlog** — три типа с labels: `commitment` (кто-что-к-сроку), `blocker` (требует действия PO), `agreement` (PO держит договорённость). SMART-маппинг: критерий проверки → acceptance criteria, владелец → assignee, срок → в описание задачи (у Backlog.md нет поля `due`), тело → ссылка `← C-NNN · {meeting_notes}/{папка}`. Reconcile: done→закрыть, slipped→сдвинуть `Срок:` в описании, new→создать. `planner.type: none` → проекция пропускается.
- **Хранение** — один прогон = папка `GROUND/PULSE/meetings/{type}-{YYYY-MM-DD-HHMM}/`; файлы внутри с фиксированными именами `report.md`, `blockers.md`, `commitments.md`, `sprint-pulse.md`.
- **Группировка блокеров** — по KR «отгрузка в Production»; заголовок-строка `Статус <KR/релиз>`; секция `Актуальная дата релизов` = Prod-дата KR.
- **Источник спеки** — `docs/superpowers/specs/2026-07-06-daily-review-design.md` (при расхождении — приоритет у спеки).
- Все команды выполняются из корня worktree: `/Users/aleksishmanov/projects/po-helper/.claude/worktrees/optimistic-wing-b6f1a1`.
- **Портативность emoji-проверок.** Шаги валидации используют `grep -P` для детекта emoji; штатный BSD grep на macOS его не поддерживает. Если `grep -P` даёт ошибку — заменить проверку «нет emoji в файле $f» на портативную:
  `python3 -c "import sys,re; t=open('$f').read(); sys.exit(1 if re.search(r'[\U0001F300-\U0001FAFF☀-➿]', t) else 0)" && echo "no-emoji OK"`
  (exit 0 = emoji нет). Либо использовать GNU grep (`ggrep -P` из coreutils).

---

### Task 1: Каркас навыка + path в domain-profile

**Files:**
- Create (dir): `.claude/skills/daily-review/resources/`
- Create (dir): `.claude/skills/daily-review/examples/planning-2026-07-06-0958/`
- Modify: `domain-profile.template.md` (секция `paths`, после строки `summary_notes`)

**Interfaces:**
- Produces: путь `paths.meeting_notes: "GROUND/PULSE/meetings"` — резолвится всеми последующими артефактами и SKILL.

- [ ] **Step 1: Проверка, что path ещё не добавлен (ожидаем провал позже — сначала фиксируем отсутствие)**

Run: `grep -c "meeting_notes" domain-profile.template.md || echo 0`
Expected: `0` (пути ещё нет)

- [ ] **Step 2: Создать директории навыка**

```bash
mkdir -p .claude/skills/daily-review/resources
mkdir -p .claude/skills/daily-review/examples/planning-2026-07-06-0958
```

- [ ] **Step 3: Добавить path `meeting_notes` в секцию `paths`**

Найти строку:
```yaml
  # Папка оперативных сведений — #summary-заметки встреч (/summary). Файл = встреча: {дата}-{slug}.md
  summary_notes: "GROUND/PULSE/summaries"
```
Добавить сразу после неё (внутри того же `paths:`-блока):
```yaml
  # Корень заметок созвонов (/daily-review). Один прогон = папка {type}-{ГГГГ-ММ-ДД-ЧЧММ}/ с report.md + blockers.md + commitments.md + sprint-pulse.md
  meeting_notes: "GROUND/PULSE/meetings"
```

- [ ] **Step 4: Добавить секцию `planner` (слой действия PO)**

Открыть `domain-profile.template.md`, найти конец блока с закрывающими ` ``` ` секции `paths` (строка ` ``` ` после `summary_notes`/`meeting_notes`). Сразу после этого закрывающего ` ``` ` и до заголовка `## 2.`-секции вставить новый подраздел:

```markdown
## 1a. Планнер PO (planner)

Личный трекер действий PO (`/daily-review` проецирует сюда обязательства/блокеры/договорённости как SMART-задачи). `type: none` отключает проекцию.

​```yaml
planner:
  type: "backlog"          # backlog | none
  root: "backlog"          # корень Backlog.md (backlog init)
  labels:
    commitment: "commitment"
    blocker:    "blocker"
    agreement:  "agreement"
  reminder_horizon_days: 3 # «due-скоро» для блока «Висит на PO»
​```
```

(Символ `​` — zero-width, показан только чтобы не закрыть внешний блок; при вставке используй обычные ` ``` `.)

- [ ] **Step 5: Проверить пути/planner и что YAML не сломан**

Run:
```bash
grep -n "meeting_notes" domain-profile.template.md && grep -n "planner:" domain-profile.template.md && \
python3 -c "import re,yaml; s=open('domain-profile.template.md').read(); [yaml.safe_load(b) for b in re.findall(r'\`\`\`yaml\n(.*?)\n\`\`\`', s, re.S)]; print('YAML OK')"
```
Expected: строки `meeting_notes` + `planner:` + `YAML OK`

- [ ] **Step 6: Commit**

```bash
git add domain-profile.template.md .claude/skills/daily-review
git commit -m "feat(daily-review): скелет навыка + paths.meeting_notes + planner"
```

---

### Task 2: resources/blockers_format.md (plain-text, группировка по KR)

**Files:**
- Create: `.claude/skills/daily-review/resources/blockers_format.md`

**Interfaces:**
- Produces: спецификация формата `blockers.md` — потребляется SKILL (Task 7) и эталоном (Task 6).

- [ ] **Step 1: Написать проверку формата (сначала провалится — файла нет)**

Run:
```bash
f=.claude/skills/daily-review/resources/blockers_format.md
grep -q "Актуальная дата релизов" $f && grep -q "отгрузк" $f && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $f && echo PASS || echo FAIL
```
Expected: `FAIL` (файла нет)

- [ ] **Step 2: Создать файл с полным содержимым**

```markdown
# Формат blockers.md — статус блокеров для отправки

`blockers.md` — **полный снапшот** открытых блокеров после созвона. Копируется «как есть» в рабочий чат или корпоративный email. Это главный человеко-facing артефакт дейлика.

## Жёсткие правила

- **Plain text.** Никаких emoji, иконок, светофоров, markdown-таблиц. Только заголовки-строки, нумерованные блокаторы и проза.
- **Группировка по KR отгрузки в Production.** Заголовок-строка = KR / релиз, выходящий в Prod (`Статус релиза «Кино»` ↔ соответствующий KR). Каждый блокатор отвечает на «когда задача появится в Production» и двигает Prod-дату KR через зависимость от внешней команды или доп. объём. Несколько KR → несколько самодостаточных plain-блоков, каждый копируется отдельно.
- **KR не сматчился** с `okr_output_doc`/`KR-EPIC-MAP` → заголовок `Статус [KR?]: <тема>`.
- **Владелец — в прозе** блокатора, не отдельным полем. Трекинг ответственности живёт в `commitments.md`.
- **Метаданные** — единственная строка HTML-комментария сверху файла: `<!-- updated: ГГГГ-ММ-ДД · source: <папка> -->`. При вставке в чат отбрасывается. Больше никакого frontmatter.

## Структура одного блока

```
Статус <KR / релиз>

Блокатор N: <короткий заголовок>
<проза: текущее состояние, кто вовлечён, что мешает, открытый вопрос>
Срок: <когда снимем / выкатим>.

...

Актуальная дата релизов:
Trunkweb: <дата> — <что происходит>.
Production: <дата> — <причина сдвига прозой, ссылка на блокатор N при наличии>.
```

## Правила ведения

- **Нумерация стабильна в рамках KR.** Снятый блокатор не сдвигает номера: помечается снятым и уезжает вниз либо удаляется на следующем прогоне (историю даёт git). Новый блокатор — следующий свободный номер.
- **Отложенное («не блокирует релиз»)** — только если реально прозвучало. Отдельный plain-блок:
  ```
  Не блокирует релиз:
  <тема> — @исполнитель. <договорённость: с кем согласовано, когда сделаем>.
  ```
  Пустой блок не выводить.
- **Пересчёт «Актуальной даты релизов».** После upsert блокеров агрегировать их сроки в вехи (Trunkweb / Production — набор из плана/OKR). Если Prod-дата сдвинулась — указать причину прозой в скобках (`нужно успеть подправить фид-менеджер (блокатор 5)`). Без символов Δ и стрелок.
- **Снятие блокатора** порождает сверку в `commitments.md` (кто снял, как проверено) — связь по прозе/дате, без служебных полей в тексте блокеров.

## Эталон (из практики PO)

```
<!-- updated: 2026-07-06 · source: planning-2026-07-06-0958 -->

Статус релиза «Кино»

Блокатор 1: BE-ручка + ревью по БД
С нашей стороны задержка — планировали выкатить в четверг, фактически накатим в понедельник вечером. Выкладка блокирует работы на FE. Из блокеров остался только маппинг городов — надо придумать решение под выкатку.
Срок: выкатим 6–7 июля.

Блокатор 2: не работает выдача афиши
Остался баг: страница афиши отдаёт 404.
Срок: выкатим 6–7 июля.

Блокатор 3: FE-доработки в UJM
После выкатки BE нужно закатить фиксы: убрать хардкоды и починить все кнопки.
Срок: хотелось бы успеть до 10 июля.

Блокатор 4: дизайн-ревью
После FE-доработок проходим дизайн-ревью.
Срок: до 10 июля.

Блокатор 5: фид-менеджер
Пока непонятно, где и что править. Много доработок в PHP-коде, с которым мы не работаем. Скорее всего исправим на неделе 13–17 июля.

Блокатор 6: SEO-теги
На стороне фронта. С Катей Осташевой общались — блокаторов, вроде, не будет.

Блокатор 7: жанры в админке
Не блокатор в целом, просто нужно чтобы кто-то руками прошёл после нашей миграции и команда SEO завела правильную таксономию. Дальше по этой таксономии сможем прогонять данные.

Актуальная дата релизов:
Trunkweb: 13–15 июля — закатываем, проходим все ревью и стабилизацию на транке.
Production: ближе к 20-м числам — нужно успеть подправить фид-менеджер (блокатор 5).
```
```

- [ ] **Step 3: Прогнать проверку — теперь PASS**

Run:
```bash
f=.claude/skills/daily-review/resources/blockers_format.md
grep -q "Актуальная дата релизов" $f && grep -q "отгрузк" $f && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $f && echo PASS || echo FAIL
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/daily-review/resources/blockers_format.md
git commit -m "feat(daily-review): формат blockers.md (plain-text, KR-Production)"
```

---

### Task 3: resources/commitment_ledger.md (реестр обязательств)

**Files:**
- Create: `.claude/skills/daily-review/resources/commitment_ledger.md`

**Interfaces:**
- Consumes: понятие «снятие блокатора → сверка» из `blockers_format.md`.
- Produces: схема таблицы `commitments.md` со столбцами `id · открыто · владелец · обязательство · критерий проверки · срок · статус · последняя сверка · новый план`; статусы `open · done · slipped · dropped`.

- [ ] **Step 1: Проверка (провалится — файла нет)**

Run:
```bash
f=.claude/skills/daily-review/resources/commitment_ledger.md
grep -q "критерий проверки" $f && grep -q "reconcile" $f && grep -q "carry-forward" $f && echo PASS || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: Создать файл**

```markdown
# Формат commitments.md — снимок обязательств встречи

Неизменяемый снимок обязательств **этой встречи**: новые обязательства + отметки сверки прошлых (что подтвердилось/сдвинулось сегодня). **Истина статуса живёт в Backlog.md** (см. `backlog_projection.md`), здесь — нарративный след с критериями проверки для аудита. Таблица без emoji.

## Схема

```markdown
# Обязательства

| id | открыто | владелец | обязательство | критерий проверки | срок | статус | последняя сверка | новый план |
|----|---------|----------|---------------|-------------------|------|--------|------------------|-----------|
| C-012 | 2026-07-06 (kino) | [КТО?] | накатить ручку BE + ревью БД | ручка отвечает на dev, FE разблокирован | 6–7 июля | open | — | — |
| C-011 | 2026-07-02 (daily) | Дмитрий | правила экономикализатора | PR на ревью, аппрув 1 | 2026-07-06 | done | 2026-07-06 | — |
```

## Поля

- **id** — сквозной `C-NNN`, не переиспользуется. Новый — следующий свободный номер по всему реестру.
- **открыто** — дата + слаг созвона, где обязательство возникло.
- **владелец** — исполнитель. Не назван в транскрипте → `[КТО?]`.
- **обязательство** — что человек взялся сделать (кто-что-к-сроку).
- **критерий проверки** — ключевое поле: как PO убедится, что сделано (наблюдаемый признак). Нет в транскрипте → `[КАК ПРОВЕРИТЬ?]`, PO дозаполняет.
- **срок** — дедлайн словами как прозвучал.
- **статус** — `open` · `done` · `slipped` · `dropped`.
- **последняя сверка** — дата последнего reconcile (без emoji).
- **новый план** — при `slipped`: новая договорённость/срок. Иначе `—`.

## Reconcile (на каждом прогоне)

1. **Carry-forward** — прочитать **открытые задачи Backlog** (label `commitment`), НЕ прошлую папку. Это истина статуса.
2. Для каждого открытого обязательства сопоставить с сегодняшним прогрессом из транскрипта:
   - подтверждено выполнение по критерию → `done`, проставить `последняя сверка`, закрыть задачу Backlog;
   - озвучена задержка/невыполнение → `slipped`, записать причину и **новый план**, сдвинуть `due` задачи Backlog;
   - не упоминалось → остаётся `open` (перенос как есть).
3. **Open новых** — обязательства, впервые прозвучавшие на этом созвоне, добавить строками со следующими `id` и спроецировать в Backlog.
4. **dropped** — только если явно отменено на встрече.

Этот файл (`commitments.md` в папке) фиксирует снимок сегодняшних обязательств + отметки сверки; собственно статус ведёт Backlog.

## Связь с блокерами

Снятие блокатора из `blockers.md` = закрытие соответствующего обязательства (владелец разбора). Сверять по прозе/дате; служебных id-полей в тексте блокеров не заводить.
```

- [ ] **Step 3: Проверка — PASS**

Run:
```bash
f=.claude/skills/daily-review/resources/commitment_ledger.md
grep -q "критерий проверки" $f && grep -q "reconcile" $f && grep -q "carry-forward" $f && echo PASS || echo FAIL
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/daily-review/resources/commitment_ledger.md
git commit -m "feat(daily-review): формат commitments.md (reconcile + критерий проверки)"
```

---

### Task 4: resources/sprint_pulse_format.md (дельта перемещений)

**Files:**
- Create: `.claude/skills/daily-review/resources/sprint_pulse_format.md`

**Interfaces:**
- Produces: схема `sprint-pulse.md` — таблица `Задача · Было → Стало · Кто · Комментарий`, дельта одного созвона.

- [ ] **Step 1: Проверка (провалится)**

Run:
```bash
f=.claude/skills/daily-review/resources/sprint_pulse_format.md
grep -q "Было → Стало" $f && grep -q "дельт" $f && echo PASS || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: Создать файл**

```markdown
# Формат sprint-pulse.md — перемещения карточек

Дельта **одного созвона**: какие задачи двигали по статусу. Без записи в JIRA (read-only) — это то, что PO услышал и должен потом отразить на доске. Таблица без emoji.

## Схема

```markdown
## Перемещения карточек — <type> «<повод>», ГГГГ-ММ-ДД
| Задача | Было → Стало | Кто | Комментарий |
|---|---|---|---|
| <КОД или [КОД?]> <название> | <Статус> → <Статус> | <Кто> | <1 фраза> |
```

## Правила

- Одна строка = одно перемещение карточки, озвученное на созвоне.
- **Код задачи** ← `KR-EPIC-MAP`/план; неизвестен → `[КОД?] <название>`. Название не оставлять пустым.
- **Было → Стало** — статусы как прозвучали; неизвестен исходный → `? → In Progress`.
- Статус только назвали без движения (просто «в работе») → отразить как `— → In Progress` с комментарием, либо не включать, если это не изменение.
- «Пульс во времени» = последовательность `sprint-pulse.md` из папок; сводный взгляд — чтение нескольких последних папок.
```

- [ ] **Step 3: Проверка — PASS**

Run:
```bash
f=.claude/skills/daily-review/resources/sprint_pulse_format.md
grep -q "Было → Стало" $f && grep -q "дельт" $f && echo PASS || echo FAIL
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/daily-review/resources/sprint_pulse_format.md
git commit -m "feat(daily-review): формат sprint-pulse.md (дельта перемещений)"
```

---

### Task 5: resources/daily_format.md (эпизод-заметка report.md)

**Files:**
- Create: `.claude/skills/daily-review/resources/daily_format.md`

**Interfaces:**
- Produces: структура `report.md` (frontmatter + Прогресс к цели спринта + План PO + Цитаты), теги прогресса словами, словарь `PO_Action`.

- [ ] **Step 1: Проверка (провалится)**

Run:
```bash
f=.claude/skills/daily-review/resources/daily_format.md
grep -q "Прогресс к цели спринта" $f && grep -q "на цель" $f && grep -q "PO_Action" $f && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $f && echo PASS || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: Создать файл**

```markdown
# Формат report.md — тонкая эпизод-заметка созвона

Нарратив встречи для аудита «кто что сказал». Тяжёлое состояние (перемещения, блокеры, обязательства) НЕ дублируется — только ссылки на соседние файлы папки. Минимализм, без emoji.

## Структура

```markdown
---
дата: ГГГГ-ММ-ДД
type: planning        # daily | planning | sync | 1on1
источник: <id транскрипта / файл>
участники: [Имя Фамилия, ...]
sprint: <id или [УТОЧНИТЬ]>
kr: [<KR-коды>]
теги: [daily-review]
---

## Прогресс к цели спринта
Sprint Goal: <повтор из плана>

| User | Activity | Task | Progress | Служит цели |
|------|----------|------|----------|-------------|
| <кто> | <направление + KR> | <КОД или [КОД?]> | <что сделал, результат> | <тег> |

## План PO на сегодня
- <личное действие PO: эскалировать / согласовать / подготовить / решить> — <к кому: People Graph, если релевантно>

## Цитаты (опц.)
> Имя Фамилия: <дословно>
```

## Теги «Служит цели»

Словами, без emoji: `на цель` · `по касательной` · `мимо` · `вне плана`. Тег отвечает на вопрос PO «действительно ли действие служит Sprint Goal».

## Словарь PO_Action (для плана PO и синхрона доски)

Одно или несколько через `, `:
- `актуализировать статус` — статус в JIRA устарел относительно услышанного;
- `добавить задачу на доску` — задача прозвучала, но её нет в трекере;
- `декомпозировать задачу` — слишком крупная, нужна разбивка;
- `назначить исполнителя` — задача без ответственного;
- `обновить дедлайн` — изменились сроки;
- `уточнить детали` — нет описания/критериев приёмки;
- `снять блокатор` — явный блокатор, требует PO-вмешательства.

## Правила

- **Task** всегда с кодом или `[КОД?] <описание>` — не пусто.
- **Participants/имена** сверять с `GROUND/NEXUS/team`; не сматченное имя не додумывать.
- **План PO** — только личные действия PO (не команды). «К кому идти» тянуть из People Graph (`/people-map`), если вопрос требует навигации.
- Каждый факт ← транскрипт. Пусто/неясно → плейсхолдер, не выдумка.
```

- [ ] **Step 3: Проверка — PASS**

Run:
```bash
f=.claude/skills/daily-review/resources/daily_format.md
grep -q "Прогресс к цели спринта" $f && grep -q "на цель" $f && grep -q "PO_Action" $f && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $f && echo PASS || echo FAIL
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/daily-review/resources/daily_format.md
git commit -m "feat(daily-review): формат report.md (прогресс-к-цели + PO_Action)"
```

---

### Task 5B: resources/backlog_projection.md (слой действия)

**Files:**
- Create: `.claude/skills/daily-review/resources/backlog_projection.md`

**Interfaces:**
- Consumes: `commitment_ledger.md` (критерий проверки, статусы), `blockers_format.md`.
- Produces: правила проекции `commitment`/`blocker`/`agreement` → SMART-задачи Backlog.md; SMART-маппинг; reconcile create/close/update; деградация `planner.type: none`.

- [ ] **Step 1: Проверить доступность backlog CLI (для точных флагов в реализации)**

Run: `backlog task create --help 2>&1 | head -30 || echo "backlog CLI недоступен — использовать MCP backlog"`
Expected: справка по флагам (`--ac`/`-l`/`-a`/`-s` или аналоги) ЛИБО указание использовать MCP. Зафиксируй фактические флаги для Step 2.

- [ ] **Step 2: Проверка формата (провалится — файла нет)**

Run:
```bash
f=.claude/skills/daily-review/resources/backlog_projection.md
grep -q "acceptance criteria" $f && grep -q "commitment" $f && grep -q "planner.type: none" $f && grep -q "reconcile" $f && echo PASS || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 3: Создать файл**

```markdown
# Проекция в Backlog.md — слой действия PO

PULSE хранит знание, Backlog.md — действие. Каждый требующий догляда пункт встречи = SMART-задача личного планнера PO. Backlog.md ≠ командный JIRA. Backlog — **истина статуса**: открытые задачи = «что висит».

## Что проецируется (три типа)

| Тип | Когда | label | Источник |
|---|---|---|---|
| commitment | человек взял обязательство (кто-что-к-сроку) | `commitment` | commitments.md |
| blocker | блокатор требует действия PO для снятия | `blocker` | blockers.md |
| agreement | договорённость, которую PO должен держать/контролировать | `agreement` | report.md |

НЕ проецируется: перемещения карточек (sprint-pulse), рутинная активность, чисто информационные договорённости без действия PO.

## SMART-маппинг

| SMART | Поле задачи Backlog |
|---|---|
| Specific | заголовок = формулировка обязательства/блокера/договорённости |
| Measurable | acceptance criteria = критерий проверки |
| Assignable | assignee/упоминание = владелец |
| Relevant | привязка к KR отгрузки в Prod (в описании) |
| Time-bound | срок → в описание задачи (`Срок: <дата>`); отдельного поля `due` в Backlog.md нет |

Описание задачи несёт срок + обратную ссылку: `Срок: <дата> · ← C-NNN · {meeting_notes}/{папка}` — срок для «Висит на PO» (парсинг из описания) + backlink для аудита.

## Reconcile (dry-run → approve)

1. **Carry-forward** — прочитать открытые задачи Backlog по трём labels как входное состояние.
2. **Match** — сопоставить с сегодняшними пунктами по ссылке (C-NNN/B-N) или смыслу.
3. **done** — выполнено по критерию → закрыть задачу (статус Closed/Done).
4. **slipped** — задержка → обновить `due` + заметка с новым планом (НЕ создавать дубль).
5. **open (new)** — впервые прозвучало → создать SMART-задачу с нужной label.
6. **carry** — не упоминалось сегодня → оставить.
7. **dropped** — явно отменено → закрыть с пометкой.

**Идемпотентность:** повторный прогон того же транскрипта не плодит дубли (match по ссылке/смыслу перед созданием).

## Команды (уточнить точные флаги через `backlog task create --help` или MCP backlog)

- Создать: `backlog task create "<заголовок>" -d "Срок: <дата> · <описание ← C-NNN · {meeting_notes}/...>" --ac "<критерий проверки>" -l <label> -a "<владелец>" -s "To Do"` (срок — в описании, отдельного поля дедлайна нет; флаги сверить с CLI).
- Закрыть: `backlog task edit <id> -s "Done"`.
- Сдвинуть срок/заметка: `backlog task edit <id> --notes "<новый план, срок>"`.
- Список открытых: `backlog task list -s "To Do" --plain`, затем фильтр по label в выводе/файлах задач (`backlog task list` не фильтрует по label — только status/assignee/milestone/parent/priority). Для carry-forward и блока «Висит на PO».

## Напоминания (стадия 0)

Блок «Висит на PO» на старте: задачи, у которых распарсенный из описания `Срок: <дата>` уже прошёл (просрочка) или наступит в пределах `planner.reminder_horizon_days`. Срок читается best-effort из текста описания — отдельного поля `due` в Backlog.md нет. Единственная механика напоминаний в этой итерации.

## Деградация

`planner.type: none` или MCP `backlog` недоступен → проекция и carry-forward из Backlog пропускаются; навык работает только со слоем PULSE (`commitments.md` — самостоятельный снимок). Явно сообщить PO, что проекция отключена.
```

- [ ] **Step 4: Проверка — PASS**

Run:
```bash
f=.claude/skills/daily-review/resources/backlog_projection.md
grep -q "acceptance criteria" $f && grep -q "commitment" $f && grep -q "planner.type: none" $f && grep -q "reconcile" $f && echo PASS || echo FAIL
```
Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/daily-review/resources/backlog_projection.md
git commit -m "feat(daily-review): проекция в Backlog.md (SMART, reconcile, labels)"
```

---

### Task 6: examples/ — эталонная папка-снапшот из транскрипта «кино»

**Files:**
- Create: `.claude/skills/daily-review/examples/planning-2026-07-06-0958/report.md`
- Create: `.claude/skills/daily-review/examples/planning-2026-07-06-0958/blockers.md`
- Create: `.claude/skills/daily-review/examples/planning-2026-07-06-0958/commitments.md`
- Create: `.claude/skills/daily-review/examples/planning-2026-07-06-0958/sprint-pulse.md`

**Interfaces:**
- Consumes: форматы из Task 2–5.
- Produces: эталон, на который ссылается SKILL (Task 7) и финальный dry-run (Task 8). Все факты — из транскрипта `~/Downloads/transcript-14922789.txt`.

- [ ] **Step 1: Проверка (провалится — файлов нет)**

Run:
```bash
d=.claude/skills/daily-review/examples/planning-2026-07-06-0958
for x in report blockers commitments sprint-pulse; do test -f $d/$x.md || { echo FAIL; break; }; done; \
grep -q "Актуальная дата релизов" $d/blockers.md 2>/dev/null && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $d/blockers.md 2>/dev/null && echo PASS || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: Создать blockers.md** (см. эталон Task 2 — тот же контент)

```markdown
<!-- updated: 2026-07-06 · source: planning-2026-07-06-0958 -->

Статус релиза «Кино»

Блокатор 1: BE-ручка + ревью по БД
С нашей стороны задержка — планировали выкатить в четверг, фактически накатим в понедельник вечером. Выкладка блокирует работы на FE. Из блокеров остался только маппинг городов — надо придумать решение под выкатку.
Срок: выкатим 6–7 июля.

Блокатор 2: не работает выдача афиши
Остался баг: страница афиши отдаёт 404.
Срок: выкатим 6–7 июля.

Блокатор 3: FE-доработки в UJM
После выкатки BE нужно закатить фиксы: убрать хардкоды и починить все кнопки.
Срок: хотелось бы успеть до 10 июля.

Блокатор 4: дизайн-ревью
После FE-доработок проходим дизайн-ревью.
Срок: до 10 июля.

Блокатор 5: фид-менеджер
Пока непонятно, где и что править. Много доработок в PHP-коде, с которым мы не работаем. Скорее всего исправим на неделе 13–17 июля.

Блокатор 6: SEO-теги
На стороне фронта. С Катей Осташевой общались — блокаторов, вроде, не будет.

Блокатор 7: жанры в админке
Не блокатор в целом, просто нужно чтобы кто-то руками прошёл после нашей миграции и команда SEO завела правильную таксономию. Дальше по этой таксономии сможем прогонять данные.

Актуальная дата релизов:
Trunkweb: 13–15 июля — закатываем, проходим все ревью и стабилизацию на транке.
Production: ближе к 20-м числам — нужно успеть подправить фид-менеджер (блокатор 5).
```

- [ ] **Step 3: Создать report.md**

```markdown
---
дата: 2026-07-06
type: planning
источник: transcript-14922789
участники: [Рустам Алиев, Сергей Парфило, Вячеслав Ковальчук, Дмитрий Ананьев, Сергей Жигунов, Алексей Ишманов]
sprint: [УТОЧНИТЬ]
kr: [[KR?] отгрузка кино в Production]
теги: [daily-review]
---

## Прогресс к цели спринта
Sprint Goal: релиз «кино» в Production (15 июля → сдвиг, см. blockers.md)

| User | Activity | Task | Progress | Служит цели |
|------|----------|------|----------|-------------|
| Рустам Алиев | ограничение передачи кино в рекл. фиды | [КОД?] задача 15:90 | взял, взаимодействие с 3 сервисами, до конца недели | на цель |
| Рустам Алиев | аналитика по киношке | [КОД?] | завершить до отпуска | на цель |
| Дмитрий Ананьев | правила экономикализатора билдингов | [КОД?] | написал, отправляет на ревью | по касательной |
| Сергей Парфило | хранимка жанров | [КОД?] | проверяет работу, до след. встречи | на цель |
| Сергей Жигунов | создание жанра кино скриптом | [КОД?] | делает, деталь уточнить у Жени | на цель |
| Вячеслав Ковальчук | статус задач для передачи Тимуру | [КОД?] | соберёт и передаст | по касательной |

## План PO на сегодня
- Разобраться с блокировками релиза (BE-ручка + FE) — эскалация, [к кому: People Graph]
- Согласовать решение по маппингу городов для выкатки BE
- Держать дату релиза: Trunk 13–15 июля, Prod ~20-е — свести с командой фид-менеджер (блокатор 5)

## Цитаты (опц.)
> Алексей Ишманов: релиз кино — на четверг, ответственный я; надо снять блокирующие факторы.
```

- [ ] **Step 4: Создать commitments.md**

```markdown
# Обязательства

| id | открыто | владелец | обязательство | критерий проверки | срок | статус | последняя сверка | новый план |
|----|---------|----------|---------------|-------------------|------|--------|------------------|-----------|
| C-001 | 2026-07-06 (kino) | Рустам Алиев | общаться с Бэком по проблемам кино (жанры) | Бэк подтвердил, жанры отдаются корректно | до конца недели | open | — | — |
| C-002 | 2026-07-06 (kino) | Вячеслав Ковальчук | собрать статус задач и передать Тимуру | Тимур получил сводку | [КАК ПРОВЕРИТЬ?] уточнить срок | open | — | — |
| C-003 | 2026-07-06 (kino) | Дмитрий Ананьев | отправить правила экономикализатора на ревью | PR/док на ревью, есть ревьюер | ближайшее | open | — | — |
| C-004 | 2026-07-06 (kino) | Сергей Парфило | проверить работу хранимки жанров | хранимка отдаёт корректные жанры | до след. встречи | open | — | — |
| C-005 | 2026-07-06 (kino) | Алексей Ишманов | накатить BE-ручку + ревью БД (снять блок FE) | ручка на transaction/dev, FE разблокирован | 6–7 июля | open | — | — |
```

- [ ] **Step 5: Создать sprint-pulse.md**

```markdown
## Перемещения карточек — planning «кино», 2026-07-06
| Задача | Было → Стало | Кто | Комментарий |
|---|---|---|---|
| [КОД?] Ограничение передачи кино в рекл. фиды (15:90) | Backlog → In Progress | Рустам Алиев | 3 сервиса, до конца недели |
| [КОД?] Правила экономикализатора билдингов | In Progress → Review | Дмитрий Ананьев | отправляет на ревью |
| [КОД?] Проверка хранимки жанров | — → In Progress | Сергей Парфило | до след. встречи |
| [КОД?] Создание жанра кино скриптом | — → In Progress | Сергей Жигунов | деталь уточнить у Жени |
```

- [ ] **Step 6: Создать examples/backlog-projection.md** (эталон 3 SMART-задач)

```markdown
# Эталон проекции в Backlog.md — из planning «кино» (2026-07-06)

Три типа задач, спроецированных из папки `planning-2026-07-06-0958/`.

## commitment
Заголовок: Рустам: снять проблему с жанрами кино с Бэком
- label: commitment
- assignee: Рустам Алиев
- acceptance criteria: Бэк подтвердил, жанры отдаются корректно
- описание: Срок: конец недели (11 июля) · ← C-001 · meetings/planning-2026-07-06-0958 · KR отгрузка кино в Prod

## blocker
Заголовок: Снять блок FE: накатить BE-ручку + ревью БД
- label: blocker
- assignee: Алексей Ишманов
- acceptance criteria: ручка на dev, FE разблокирован; маппинг городов решён
- описание: Срок: 7 июля · ← blockers.md блокатор 1 · meetings/planning-2026-07-06-0958 · KR отгрузка кино в Prod

## agreement
Заголовок: Держать релиз кино: Trunk 13–15 июля, Prod ~20-е
- label: agreement
- assignee: Алексей Ишманов
- acceptance criteria: пройдены ревью+стабилизация на транке к 15 июля; фид-менеджер поправлен к Prod
- описание: Срок: 15 июля (Trunk-веха) · ← report.md · meetings/planning-2026-07-06-0958 · KR отгрузка кино в Prod
```

- [ ] **Step 7: Проверка — PASS**

Run:
```bash
d=.claude/skills/daily-review/examples/planning-2026-07-06-0958
b=.claude/skills/daily-review/examples/backlog-projection.md
ok=1; for x in report blockers commitments sprint-pulse; do test -f $d/$x.md || ok=0; done; \
grep -q "Актуальная дата релизов" $d/blockers.md && ! grep -qP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" $d/blockers.md && grep -q "критерий проверки" $d/commitments.md && \
test -f $b && grep -q "commitment" $b && grep -q "blocker" $b && grep -q "agreement" $b && [ $ok = 1 ] && echo PASS || echo FAIL
```
Expected: `PASS` (если `grep -P` не поддержан — заменить emoji-проверку по Global Constraints)

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/daily-review/examples
git commit -m "feat(daily-review): эталонная папка-снапшот + проекция Backlog из транскрипта кино"
```

---

### Task 7: SKILL.md — точка входа навыка

**Files:**
- Create: `.claude/skills/daily-review/SKILL.md`

**Interfaces:**
- Consumes: все `resources/*` (Task 2–5) и `examples/` (Task 6).
- Produces: команда `/daily-review`, регистрируемая по frontmatter `name`/`description`.

- [ ] **Step 1: Проверка frontmatter + разделов (провалится)**

Run:
```bash
f=.claude/skills/daily-review/SKILL.md
python3 -c "import yaml,sys; s=open('$f').read(); fm=s.split('---')[1]; d=yaml.safe_load(fm); assert d['name']=='daily-review'; assert 'daily-review' in d['description']; print('FM OK')" && \
grep -q "meeting_notes" $f && grep -q "carry-forward" $f && grep -q "read-only" $f && grep -q "Backlog" $f && echo PASS || echo FAIL
```
Expected: `FAIL` (файла нет)

- [ ] **Step 2: Создать SKILL.md**

````markdown
---
name: daily-review
description: "Обработка транскрипта дейлика/командного синка в папку-снапшот PULSE + проекция действий в личный планнер Backlog.md. На вход — расшифровка стендапа, на выход — папка {type}-{дата-время}/ с тонкой заметкой (report.md), plain-text блокерами (blockers.md, группировка по KR отгрузки в Production + актуальные даты релиза), снимком обязательств (commitments.md, цикл сделал/не сделал→новый план) и дельтой перемещений карточек (sprint-pulse.md); обязательства/блокеры/договорённости проецируются в Backlog.md как SMART-задачи PO. Используй когда: обработать дейлик, разобрать стендап, актуальные сроки релиза, блокеры спринта, прогресс к цели спринта, сверка договорённостей, задачи PO из дейлика, /daily-review."
---

# Навык: Daily Review — разбор дейликов и созвонов

## Роль

Ты — **аналитик дейликов PO**. На вход — сырой транскрипт стендапа/командного синка (часто с авто-саммари вверху и искажениями распознавания), на выход — **папка-снапшот** оперативного состояния команды: прогресс к цели спринта, статус блокеров с актуальными датами релиза, сверка обязательств, перемещения карточек, личный план PO.

> Ценность — в **актуальных сроках** («когда задача выйдет в Production»), **честном прогрессе к цели** («служит ли действие Sprint Goal») и **цикле обязательств** («сделал то, о чём договорились? как проверить? нет → почему → новый план»). Не пересказ встречи, а операционная память PO.

## Охват

Стендапы и командные синки (формат «кто-что-к-цели»). Не-стендап созвоны (стейкхолдер-синк, custdev) → `/summary`. Оба навыка складывают в общий стор `paths.meeting_notes`, поэтому любые созвоны лежат в одном запрашиваемом месте.

## JIRA — read-only. Backlog.md — пишем

Навык **не читает и не пишет командный JIRA** через MCP. «Синхрон доски» — это список PO_Action и `sprint-pulse.md` (что услышали и надо отразить), а не запись в трекер. Отдельно навык **пишет в личный планнер PO — Backlog.md** (MCP `backlog`); это не JIRA, а персональный трекер действий (см. «Слой действия»).

## Два слоя: знание (PULSE) + действие (Backlog)

- **PULSE-папка** — неизменяемая запись встречи (нарратив, критерии, история).
- **Backlog.md** — живой планнер PO, **истина статуса** открытых обязательств/блокеров/договорённостей.

## Модель хранилища — папка-снапшот на созвон

- Корень: `paths.meeting_notes` из `.claude/domain-profile.md` (дефолт `GROUND/PULSE/meetings`). Профиль пуст → дефолт + `[УТОЧНИТЬ]`.
- Один прогон = папка `{meeting_notes}/{type}-{ГГГГ-ММ-ДД-ЧЧММ}/`, где `type` ∈ `daily|planning|sync|1on1`.
- Внутри — фиксированные имена: `report.md`, `blockers.md`, `commitments.md`, `sprint-pulse.md`. Папка **неизменяема** — следующие прогоны её не мутируют.
- **Carry-forward — из Backlog, не из папки.** Входное состояние («что висит») следующий прогон читает из **открытых задач Backlog** (labels commitment/blocker/agreement). Нулевой дрейф статуса.
- PULSE = Progress Pulse (оперативная динамика). Git-tracked, индексируется RAG.

## Слой действия — Backlog.md

Каждый требующий догляда пункт → SMART-задача. Три типа с labels: `commitment` (кто-что-к-сроку), `blocker` (требует действия PO), `agreement` (PO держит договорённость). SMART-маппинг: критерий проверки → acceptance criteria, владелец → assignee, срок → в описание задачи (у Backlog.md нет поля `due`), тело → `← C-NNN · {meeting_notes}/{папка}`. Reconcile: done→закрыть, slipped→сдвинуть `Срок:` в описании, new→создать (идемпотентно, без дублей). `planner.type: none` или нет MCP `backlog` → проекция и carry-forward из Backlog пропускаются, работает только слой PULSE. Правила — `resources/backlog_projection.md`.

## Артефакты

| Файл/цель | Слой | Природа | Формат |
|---|---|---|---|
| `blockers.md` | PULSE | снимок на момент встречи, готов к отправке в чат/email | `resources/blockers_format.md` |
| `commitments.md` | PULSE | снимок обязательств встречи «как прозвучало» | `resources/commitment_ledger.md` |
| `sprint-pulse.md` | PULSE | дельта перемещений этого созвона | `resources/sprint_pulse_format.md` |
| `report.md` | PULSE | тонкая эпизод-заметка | `resources/daily_format.md` |
| `Backlog.md` | действие | живой трекер SMART-задач PO (истина статуса) | `resources/backlog_projection.md` |
| `GROUND/NEXUS/risk` (дельта) | знание | durable-состояние рисков, вне папки | BFT-ярус (при наличии графа) |

Блокатор ≠ риск: блокатор мешает **сейчас** достичь Prod-даты (оперативно, с датой), риск — **может** помешать (вероятностно).

## Принцип нулевых галлюцинаций

Каждый факт ← транскрипт. Авто-саммари вверху файла — только подсказка, факты перепроверяются по сырому логу. Плейсхолдеры вместо догадок: `[КОД?]`, `[КТО?]`, `[KR?]`, `[КАК ПРОВЕРИТЬ?]`, `[УТОЧНИТЬ]`. Искажения имён/терминов свести к единому написанию (сверка с `GROUND/NEXUS/team`), в конце пометить «термины сведены — проверь глазами».

## Ядро: как `/daily-review` обрабатывает транскрипт

0. **Загрузка + carry-forward + напоминания** — `.claude/domain-profile.md` (`paths`, `jira`, `planner`, `meta.current_quarter`), этот SKILL, `resources/*`. Резолв Sprint Goal + плановых историй (`planning_root`), OKR-квартала (`okr_output_doc`), People Graph (`GROUND/NEXUS/team`), `KR-EPIC-MAP`. Прочитать **открытые задачи Backlog** (labels commitment/blocker/agreement) как входное состояние. Показать блок **«Висит на PO»** — просроченные и скоро-по-сроку задачи.
1. **Приём транскрипта** — аргумент/путь/вставка. Пусто → попросить. Авто-саммари — подсказка, факты ← сырой лог.
2. **Извлечение** — активность по участникам, статус-изменения карточек, блокаторы, риски-дельта, новые договорённости, задачи, вехи/даты.
3. **Якорение** — коды JIRA ← `KR-EPIC-MAP`/план (`[КОД?]`); имена ← `GROUND/NEXUS/team` (не додумывать); блокаторы → KR отгрузки в Prod (`[KR?]`).
4. **Прогресс-к-цели** — тег каждой активности словами (`на цель / по касательной / мимо / вне плана`) против Sprint Goal.
5. **Сверка обязательств** — открытые задачи Backlog × сегодняшний прогресс → `done / slipped (+ причина + новый план) / open`; новые → open. Правила — `resources/commitment_ledger.md`.
6. **Блокаторы** — собрать полный снимок (открытые blocker-задачи Backlog + сегодняшние), группировка по KR (`Статус <KR/релиз>`), пересчёт «Актуальной даты релизов» с обоснованием сдвига прозой. Правила — `resources/blockers_format.md`.
7. **Сборка папки PULSE** — создать `{meeting_notes}/{type}-{ГГГГ-ММ-ДД-ЧЧММ}/`; записать `report.md` + `blockers.md` + `commitments.md` (снимок встречи) + `sprint-pulse.md`; риски-дельта → `GROUND/NEXUS/risk` (при наличии графа).
8. **Проекция в Backlog (dry-run → approve)** — по `resources/backlog_projection.md`: новые → создать SMART-задачи (labels), `done` → закрыть, `slipped` → сдвинуть `Срок:` в описании + заметка. `planner.type: none`/нет MCP → пропустить, сообщить PO.
9. **Отчёт + STOP** — превью PULSE-файлов (особенно `blockers.md` — готов к отправке) и dry-run проекции Backlog (что создать/закрыть/сдвинуть), места `[УТОЧНИТЬ]`, блок «Висит на PO», сводка «что куда записано». Ждать подтверждения PO.

## Команда

| Команда | Роль | Что делает |
|---|---|---|
| `/daily-review [транскрипт \| путь к файлу]` | Аналитик дейликов | Разобрать транскрипт → папка-снапшот PULSE (report + blockers + commitments + sprint-pulse) |

Команда на «Этапе 0: Загрузка» читает `.claude/domain-profile.md` (резолв `paths.meeting_notes`, `paths.planning_root`, `paths.okr_output_doc`, `paths.kr_epic_map_doc`, `planner.*`, `meta.current_quarter`), этот SKILL и `resources/*`.

## Связи с каркасом

- **Питает `/sprint-fact`** — дневные факты (снятые/висящие блокеры, carryover) накапливаются как вход в ФАКТ спринта.
- **Дополняет `/summary`** — общий стор `meeting_notes`; стендапы через `/daily-review`, прочие созвоны через `/summary`.
- **Читает** артефакты `sprint-planner` (Sprint Goal), `okr-planner` (KR отгрузки в Prod), `people-map`/`team`-Нексус (атрибуция + «к кому идти»).
- **Проецирует в `Backlog.md`** через MCP `backlog` — личный планнер PO (≠ командный JIRA), истина статуса действий.

## Стандарты и ресурсы

- `resources/blockers_format.md` — plain-text блокеры, группировка по KR-Production, актуальные даты.
- `resources/commitment_ledger.md` — снимок обязательств встречи, reconcile, критерий проверки.
- `resources/sprint_pulse_format.md` — дельта перемещений карточек.
- `resources/daily_format.md` — эпизод-заметка, прогресс-к-цели, словарь PO_Action.
- `resources/backlog_projection.md` — проекция в Backlog.md (SMART, labels, reconcile, деградация).
- `examples/planning-2026-07-06-0958/` — эталонная папка-снапшот (транскрипт «кино»).
- `examples/backlog-projection.md` — эталон 3 SMART-задач (commitment/blocker/agreement).
- Стиль прозы — `.claude/skills/bft-writer/resources/writing_style.md` (деловая телеграфная проза, без AI-стоп-слов и декоративных эмодзи).

## Главное правило

Не раздувай и не выдумывай. Главный выход — актуальные сроки и честный прогресс к цели. Каждый факт заякорен транскриптом; чего в транскрипте нет — того нет в отчёте. `blockers.md` должен копироваться в рабочий чат без правок. Неизвестное помечай плейсхолдером, а не додумывай.
````

- [ ] **Step 3: Проверка — PASS**

Run:
```bash
f=.claude/skills/daily-review/SKILL.md
python3 -c "import yaml; s=open('$f').read(); d=yaml.safe_load(s.split('---')[1]); assert d['name']=='daily-review'; assert 'daily-review' in d['description']; print('FM OK')" && \
grep -q "meeting_notes" $f && grep -q "carry-forward" $f && grep -q "read-only" $f && grep -q "Backlog" $f && echo PASS || echo FAIL
```
Expected: `FM OK` + `PASS`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/daily-review/SKILL.md
git commit -m "feat(daily-review): SKILL.md — точка входа навыка"
```

---

### Task 8: Регистрация в README + финальный dry-run

**Files:**
- Modify: `README.md` (таблица навыков, после строки `**Summary встреч**`)

**Interfaces:**
- Consumes: весь навык (Task 1–7).

- [ ] **Step 1: Добавить строку в таблицу навыков README**

Найти строку (≈ строка 21):
```
| **Summary встреч** | `/summary [транскрипт]` | Выжимка транскрипта созвона в `#summary`-заметку (Тема / Проблема / Ключевое / Договорённости) → .md в папку оперативных сведений | [SKILL](.claude/skills/summary/SKILL.md) |
```
Добавить сразу после неё:
```
| **Дейлики** | `/daily-review [транскрипт]` | Разбор стендапа в папку-снапшот PULSE: прогресс к цели спринта + plain-text блокеры (по KR отгрузки в Production + актуальные даты) + реестр обязательств (сделал/не сделал→новый план) + перемещения карточек | [SKILL](.claude/skills/daily-review/SKILL.md) |
```

- [ ] **Step 2: Проверить регистрацию**

Run: `grep -c "daily-review" README.md`
Expected: `≥ 1`

- [ ] **Step 3: Финальный dry-run навыка на транскрипте «кино»**

Запустить в этой сессии (или свежей): `/daily-review ~/Downloads/transcript-14922789.txt`

Ожидаемо (визуальная сверка PO, НЕ автопроверка):
- На старте показан блок «Висит на PO» (при первом прогоне пустой — открытых задач Backlog ещё нет).
- Создаётся папка `GROUND/PULSE/meetings/planning-2026-07-06-<ЧЧММ>/` с 4 файлами.
- `blockers.md` — plain-text, группировка «Статус релиза «Кино»», блокаторы 1–N, секция «Актуальная дата релизов» (Trunk 13–15 июля, Prod ~20-е), без emoji.
- `commitments.md` — обязательства (Рустам→Бэк, Вячеслав→Тимур, Алексей→BE-ручка) с полем «критерий проверки».
- `report.md` — прогресс-к-цели с тегами словами, План PO на сегодня.
- `sprint-pulse.md` — перемещения карточек.
- Показан dry-run проекции в Backlog: SMART-задачи с labels `commitment`/`blocker`/`agreement` (сверить с `examples/backlog-projection.md`). При `planner.type: none` — сообщение «проекция отключена».
- После approve задачи созданы: `backlog task list -s "To Do" --plain` показывает ≥1 задачу с label `commitment` (фильтр по label — в выводе, не флагом).
- Навык останавливается на approve-гейте, показывает превью `blockers.md` + dry-run Backlog.

Расхождения с `examples/planning-2026-07-06-0958/` или `examples/backlog-projection.md` → поправить соответствующий `resources/*.md` или SKILL, перезапустить.

- [ ] **Step 4: Commit README + запись памяти проекта**

```bash
git add README.md
git commit -m "docs(daily-review): регистрация /daily-review в README"
```

Опционально: записать в `~/.claude/projects/-Users-aleksishmanov-projects-po-helper/memory/` факт о навыке `daily-review` (артефакты, папка-снапшот, KR-Production группировка) + строку в `MEMORY.md`.

---

## Self-Review (выполнено автором плана)

**1. Spec coverage:**
- §2 форма/охват/JIRA read-only → Task 7 (SKILL: Роль/Охват/JIRA).
- §3 два слоя + папка-снапшот + carry-forward из Backlog → Task 1 (path+planner), Task 7 (модель хранилища/слой действия), пайплайн шаг 0.
- §4.1 blockers формат → Task 2 + эталон Task 6.
- §4.2 sprint-pulse → Task 4 + Task 6.
- §4.3 commitments (снимок встречи) → Task 3 + Task 6.
- §4.4 report.md → Task 5 + Task 6.
- §5 пайплайн 0–9 → Task 7 (Ядро).
- §6 domain-profile path + planner → Task 1.
- §7 связи (/sprint-fact, /summary, Backlog) → Task 7.
- §8 файлы навыка → Task 2–5B, 7; регистрация → Task 8.
- §9 YAGNI → соблюдено структурой.
- §10 Backlog-слой (проекция, SMART, reconcile, напоминания, деградация) → Task 5B (resource) + Task 1 (planner) + Task 6 (пример) + Task 7 (пайплайн 0/8) + Task 8 (dry-run).

**2. Placeholder scan:** намеренные доменные плейсхолдеры (`[КОД?]` и пр.) — часть формата, не пробелы плана. Флаги `backlog task` помечены «сверить с CLI» (Task 5B Step 1) — это осознанная верификация, не пробел. Прочих TODO/TBD нет.

**3. Type consistency:** имена файлов (`report.md`/`blockers.md`/`commitments.md`/`sprint-pulse.md`), path `paths.meeting_notes`, секция `planner` (`type/root/labels/reminder_horizon_days`), labels (`commitment/blocker/agreement`), слаг папки `{type}-{ГГГГ-ММ-ДД-ЧЧММ}`, статусы обязательств (`open/done/slipped/dropped`), теги прогресса (`на цель/по касательной/мимо/вне плана`) — согласованы между Task 1–8 и спекой §1–§10.
