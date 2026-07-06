# Spec — Onboarding Flow (backlog «из коробки» + `/paf-onboard`)

> **Status:** design approved 2026-07-07 → `writing-plans`.
> **Branch:** `feat/onboarding-flow`.
> **Родительская спека:** `docs/superpowers/specs/2026-06-21-paf-team-os-design.md` (§5 определяет `/paf-onboard`, §2.2 node schema, §6 CP-дисциплина). Эта спека — её замыкание: реализует `/paf-onboard` и добавляет онбординг-бэклог, который ведёт нового PO к «настроенной системе».

---

## 1. Проблема и цель

**Ситуация.** Пользователь, впервые устанавливающий po-helper, не понимает, как с ним работать. После установки его встречает пустая доска и набор команд без порядка применения.

**Цель.** Из коробки дать **пошаговый план погружения** (StepByStep), заведённый прямо в Backlog.md, который ведёт к главному результату онбординга — **настроенной, готовой к применению системе**: заполнен `domain-profile.md` и **насыщены все Нексусы GROUND Vault** (персонализация под конкретный продукт).

**Definition of Done онбординга (для пользователя):**
- `GROUND/config.yaml` существует (продукт, roster, Product Engineer заданы);
- `.claude/domain-profile.md` заполнен (пути планирования, трекер, wiki, глоссарий, стейкхолдеры, `landscape.ext_teams`);
- в `GROUND/NEXUS/_registry.yaml` **все** Нексусы имеют `onboarded ≠ todo` (`partial`/`done`);
- получен readiness-отчёт GROUND Vault (карта пробелов + top low-CP).

---

## 2. Контекст (что уже есть в репо)

- **Модель распространения 1 (основная для онбординга):** `git clone` репозитория po-helper → работа внутри него; `GROUND/` — это Vault клиента (коммитится). Здесь живут `/paf-init`, `/paf-nexus-create`, `sa_documentation/`, скелет 16 Нексусов.
- **Модель распространения 2:** `curl … | bash install.sh` копирует навыки/команды в `.claude` уже существующего проекта пользователя и делает `backlog init` в корне проекта.
- **Backlog.md** хранит задачи как `backlog/tasks/task-N - <Title>.md` (YAML-фронтматтер `id/title/status/labels/dependencies` + секции `## Description` и `## Acceptance Criteria` с чек-листом `- [ ] #n …`). Доки — `backlog/docs/*.md`. install.sh уже кладёт `backlog-ops.template.md` → `backlog/docs/operational-hq.md`.
- **`_registry.yaml`** трекает `onboarded: todo/partial/done` по каждому Нексусу (16 записей: 4 PAF-минимум + `project-management` + 8 набора intake→БФТ + `team`/`channels`/`landscape`).
- **`/paf-onboard`** описан в родительской спеке §5 и упоминается почти во всех `_index.md` Нексусов («*пусто — наполняются `/paf-onboard`*»), в `README`, `_registry.yaml`, `domain-profile.template.md` — **но не реализован** (нет ни skill, ни command). `/paf-init` и `/paf-nexus-create` реализованы.
- **Node schema GROUND Vault** — `sa_documentation/nexus_schema.md §2` (обязательные ключи) и §2.2 (empirical-узлы онбординга: `kind: empirical`, `sources: ["onboarding:<doc>"|"onboarding:interview"]`, `confidence: 0.2–0.4`, пометка «допущение, требует валидации»).
- **install.sh** сейчас деплоит `SKILLS=(bft-writer okr-planner sprint-planner po-research info-channels summary)` — **paf-навыки и `sa_documentation/` НЕ доставляются**, поэтому curl-путь сегодня не может пройти PAF-онбординг. Это чинится в Компоненте 3.

---

## 3. Компонент 1 — реализация `/paf-onboard` (движок наполнения)

Новый skill `.claude/skills/paf-onboard/SKILL.md` (+ команда `.claude/commands/paf-onboard.md`, если требуется для деплоя — см. §5), строго по родительской спеке §5. Работает по **всему** `_registry.yaml` (дефолт + кастом). Repeatable, idempotent (upsert + дедуп).

**Контекст для чтения перед стартом** (аналогично paf-init):
- `sa_documentation/nexus_schema.md` (§2 node schema, §2.2 empirical-узлы, §3 `node_type`, §4 wilting);
- `sa_documentation/nexus_catalog.md` (seed_questions типов; для кастомных — из их `_index.md`);
- `sa_documentation/ground_schema.md` (`config.yaml`, `_registry.yaml`);
- `GROUND/config.yaml`, `GROUND/NEXUS/_registry.yaml`.

**Предусловие:** `GROUND/config.yaml` существует. Нет → остановиться, направить на `/paf-init`.

### Фазы

- **Phase A — ингестия доков (`GROUND/_intake/`).** Прочитать каждый документ; Cortex извлекает факты → узлы соответствующих Нексусов с `sources: ["onboarding:<doc>"]`. Дедуп: `mcp__ruflo__memory_search` при наличии ruflo, иначе Grep по существующим узлам (structured fallback). Если `_intake/` пуст — фаза пропускается с сообщением, переходим к B.
- **Phase B — интервью.** Для каждого Нексуса реестра — задать его `seed_questions` (из `_index.md` Нексуса; для дефолтных источник — `nexus_catalog.md`). Ответы → узлы с `sources: ["onboarding:interview"]`. Один вопрос за раз (конвенция paf-скиллов). Пропуск вопроса допустим → узел не создаётся, пробел фиксируется для Phase D.
- **Phase C — verify + CP.** Каждый созданный/обновлённый узел: `kind: empirical`, `confidence: 0.2–0.4`, `ttl_days` по типу (market/customer=90, growth=60, прочие по каталогу), пометка в теле «⚠️ допущение клиента (онбординг), требует валидации в Steps 1–8». Обновить `_registry.yaml: onboarded` (`todo→partial`, `→done` если покрыты все seed_questions Нексуса) и `config.yaml onboarding.{status, sources_ingested, onboarded_at}`.
- **Phase D — readiness.** Context Ripeness по всем Нексусам, карта пробелов (незаполненные seed_questions / Нексусы без узлов), top low-CP допущений для приоритетной валидации. Финал: «GROUND насыщен → Steps 1–8 валидируют и поднимают CP».

**Гвардраилы:** ноль галлюцинаций (узел без `sources` не пишется); онбординг **цифровизует, не валидирует** — не выдавать допущения за факты; справочник (`sa_documentation/`, `AI-PROCESSES/`) read-only; при повторном прогоне — upsert существующих узлов, не затирать более высокий CP из Steps 1–8.

**Graceful degradation:** без ruflo MCP — Grep-дедуп; без `_intake/` — только Phase B.

---

## 4. Компонент 2 — онбординг-бэклог (StepByStep к «настроенной системе»)

Единый источник — committed `backlog/` **в репо po-helper** (работает сразу после `git clone`); install.sh засеивает то же в проект пользователя (Компонент 3). Задачи — label `onboarding`, `status: To Do`, связаны `dependencies` в очевидную цепочку.

### 4.1 Задачи (8: 6 core + 2 опц.)

| # | Задача (title) | dep | Ключевые Acceptance Criteria |
|:--|:--|:--|:--|
| 1 | Старт: как устроен po-helper и GROUND Vault | — | прочитал `backlog/docs/onboarding.md`; понял модель «1 задача = 1 артефакт» и где источники истины; понял, что цель онбординга = насыщенный GROUND Vault + заполненный `domain-profile` |
| 2 | Персонализируй `domain-profile.md` | 1 | `cp .claude/domain-profile.template.md .claude/domain-profile.md`; заполнил пути планирования/трекер/wiki; глоссарий; стейкхолдеров; `landscape.ext_teams`; Reload Window (команды появились) |
| 3 | Инициализируй GROUND Vault — `/paf-init` | 2 | прошёл интервью; есть `GROUND/config.yaml` (product + Product Engineer обязателен); `_registry.yaml` с дефолтными Нексусами |
| 4 | (опц.) Кастомные Нексусы — `/paf-nexus-create` | 3 | создал нужные (`team`/`channels`/`landscape` или доменные `sellers`/`buyers`…); записаны `source: custom` |
| 5 | Сложи материалы в `GROUND/_intake/` | 3 | положил доки продукта (стратегия/аналитика/PRD…) в `_intake/`, **или** осознанно пропустил (тогда наполнение только из интервью) |
| 6 | **Наполни Нексусы — `/paf-onboard`** (главное) | 5 | прогнал `/paf-onboard` по всему реестру; каждый Нексус получил узлы; в `_registry.yaml` все `onboarded ≠ todo`; получил readiness-отчёт + карту пробелов |
| 7 | (опц.) Команда и карта людей | 6 | `/people-links` (отношения) + `/people-map` (навигация) + `/radar-calibrate` (качество People Graph); `team`-нексус насыщен персонами, контур PO описан |
| 8 | Готовность + первый реальный проход | 6 | readiness ок; выбрал сценарий и запустил один из `/okr-context-gen`·`/bft-context-gen`·`/sprint-roadmap`·`/req-context`; первый артефакт заведён задачей на доске |

Задача 6 — водораздел: после неё выполнен DoD онбординга (§1). Задачи 7–8 — «первое применение».

### 4.2 Документ `backlog/docs/onboarding.md`

StepByStep-гайд, разворачивающий каждую из 8 задач: назначение шага, точные команды, «как понять, что готово» (маппинг на AC и на `_registry.onboarded`), ссылки на навыки/спеку. Тон — для новичка, который «вообще не понимает, как работать». Ссылается на `operational-hq.md` (модель доски) и на родительскую спеку PAF Team OS.

### 4.3 Идемпотентность и коллизии id

- В репо po-helper `backlog/` коммитится с task-1…task-8 (label `onboarding`) + `docs/onboarding.md`.
- install.sh засеивает онбординг **только в ветке свежего `backlog init`** (доска пуста → id task-1…8 свободны, коллизий нет). Если `backlog/` уже существовал — засев пропускается (пользователь уже начинал работу).
- Копируются только task-файлы с label `onboarding` (фильтр `grep -l 'onboarding'`) — чтобы возможные будущие dev-задачи самого репо po-helper не «протекли» пользователю.

---

## 5. Компонент 3 — install.sh

- **Деплой навыков (полный набор):** добавить в `SKILLS` — `paf-init`, `paf-nexus-create`, `paf-onboard`, `people-links`, `people-map`, `nexus-calibration`. Если какие-то из них распространяются как команды (`/people-map` и т.п. лежат в `.claude/commands/`) — добавить соответствующие имена в `COMMANDS`. Проверить фактическое расположение каждого при имплементации.
- **Деплой справочника:** копировать `sa_documentation/` в целевой проект (read-only reference, нужен paf-навыкам). В `--install` не перезаписывать существующий; в `--update` — обновлять.
- **Засев онбординг-бэклога:** в ветке успешного `backlog init` скопировать из `SCRIPT_DIR/backlog/` в `$PROJECT_ROOT/backlog/`: task-файлы с label `onboarding` и `docs/onboarding.md` (идемпотентно, §4.3).
- **Финальный вывод** «Дальше:» — шаг 1 переписать на: «`backlog board` — там пошаговый план погружения (задачи 1→8)».
- **GROUND Vault для curl-пути** генерируется `/paf-init` внутри целевого проекта (install.sh сам `GROUND/` не копирует); поэтому доставки `sa_documentation/` + paf-навыков достаточно.

---

## 6. Порядок реализации (для writing-plans)

1. **`/paf-onboard`** (Компонент 1) — движок; самостоятельно ценен, разблокирует задачу 6 бэклога.
2. **Онбординг-бэклог** (Компонент 2) — committed `backlog/` + `docs/onboarding.md`.
3. **install.sh** (Компонент 3) — деплой навыков/справочника + засев + текст «Дальше».

---

## 7. Проверка (acceptance)

- **`/paf-onboard` на насыщение:** во временном GROUND (после `/paf-init`) прогон `/paf-onboard` создаёт узлы по seed_questions, выставляет `confidence 0.2–0.4` + пометку, обновляет `_registry.onboarded` и `config.yaml onboarding.*`; повторный прогон не затирает и не дублирует (upsert). Без ruflo — Grep-дедуп, без падения. Узел без `sources` не пишется.
- **Онбординг-бэклог после `git clone`:** `backlog board` в репо po-helper показывает 8 онбординг-задач в правильном порядке + `docs/onboarding.md` на месте.
- **install.sh в чистом временном git-репо:** после прогона `backlog board` показывает те же 8 задач + `onboarding.md`; в `.claude/skills/` присутствуют `paf-init`/`paf-nexus-create`/`paf-onboard`/`people-*`/`nexus-calibration`; `sa_documentation/` скопирован. Повторный прогон / прогон поверх существующей доски — без дублей, чужие задачи не тронуты.
- **Сквозной DoD:** пройдя задачи 1→6, пользователь получает `config.yaml` + заполненный `domain-profile` + `_registry.yaml` со всеми `onboarded ≠ todo` + readiness-отчёт.

---

## 8. Out of scope (YAGNI)

- Автогенерация онбординг-плана под конкретный продукт (план статичный и одинаковый — персонализация происходит через `/paf-init` + `/paf-onboard`, а не через генерацию задач).
- Автоматическая простановка галочек AC агентом по факту прохождения стадий (пользователь чекает сам; авто-трекинг — возможное будущее улучшение).
- Валидация допущений онбординга (по дизайну — работа Steps 1–8, не онбординга).
- Копирование готового `GROUND/` Vault в curl-путь (Vault строит `/paf-init`).

---

**Version:** 1.0 · **Approved:** 2026-07-07 · **Next:** `writing-plans` → implementation plan.
