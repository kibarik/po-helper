# Onboarding Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Из коробки дать новому PO пошаговый план погружения в Backlog.md, ведущий к настроенной системе (заполнен `domain-profile` + насыщены все Нексусы GROUND Vault), и реализовать недостающий движок наполнения `/paf-onboard`.

**Architecture:** Три компонента. (1) Новый skill `.claude/skills/paf-onboard/SKILL.md` — LLM-инструкция из 4 фаз (ингест `_intake/` → интервью по seed_questions → low-CP + registry → readiness), пишет узлы по `nexus_schema.md`. (2) Committed `backlog/` в репо po-helper (8 задач label `onboarding` + `docs/onboarding.md`) — работает после `git clone`. (3) `install.sh` доставляет paf-*/people-*/nexus-calibration навыки + `sa_documentation/` в проект пользователя и засеивает тот же онбординг-бэклог на свежем `backlog init`.

**Tech Stack:** Markdown-скиллы (Claude Code), Backlog.md CLI (v1.44), Bash (install.sh), YAML-фронтматтер узлов Нексусов. Тестов-фреймворка нет — верификация через реальные прогоны CLI и shell-ассерты.

## Global Constraints

- **Спека-источник:** `docs/superpowers/specs/2026-07-07-onboarding-flow-design.md`; родительская — `docs/superpowers/specs/2026-06-21-paf-team-os-design.md` (§5 `/paf-onboard`, §2.2/§6 CP).
- **Ноль галлюцинаций:** узел без `sources` не пишется (`nexus_schema.md` §2). Онбординг **цифровизует, не валидирует** — `confidence: 0.2–0.4`, пометка «допущение, требует валидации в Steps 1–8».
- **Read-only справочник:** `sa_documentation/`, `AI-PROCESSES/`, `docs/` — правке не подлежат; работа с контекстом клиента — только в `GROUND/`.
- **Node schema строго по** `sa_documentation/nexus_schema.md §2` (обязательные ключи: `nexus, node_id, node_type, paf_step, kind, owner, confidence, sources, updated, ttl_days, ripeness`).
- **Backlog-модель:** 1 задача = 1 артефакт; онбординг-задачи — label `onboarding`, `status: To Do`.
- **Идемпотентность:** `/paf-onboard` — upsert (не затирать более высокий CP из Steps 1–8); install.sh засев — только на свежем `backlog init`, фильтр по label `onboarding`.
- **Ветка:** `feat/onboarding-flow`. Каждая задача завершается коммитом.
- **Язык артефактов:** русский (как весь фреймворк).

---

### Task 1: Skill `/paf-onboard` — движок наполнения Нексусов

**Files:**
- Create: `.claude/skills/paf-onboard/SKILL.md`
- Test: inline shell-ассерты (структурный lint) + ручная acceptance (интерактивный прогон)

**Interfaces:**
- Consumes: `GROUND/config.yaml`, `GROUND/NEXUS/_registry.yaml`, `GROUND/NEXUS/<slug>/_index.md` (seed_questions), `GROUND/_intake/*`, `sa_documentation/{nexus_schema,nexus_catalog,ground_schema}.md`.
- Produces: узлы `GROUND/NEXUS/<slug>/*.md` (`kind: empirical`, `sources: ["onboarding:<doc>"|"onboarding:interview"]`, `confidence 0.2–0.4`); обновлённый `_registry.yaml: onboarded`; обновлённый `config.yaml: onboarding.{status,sources_ingested,onboarded_at}`; readiness-отчёт в чат.

- [ ] **Step 1: Написать падающий структурный тест**

Пишем ассерт, что skill существует и содержит все обязательные разделы. Запусти в корне репо:

```bash
cat > /tmp/paf_onboard_lint.sh <<'SH'
set -eu
F=.claude/skills/paf-onboard/SKILL.md
test -f "$F" || { echo "FAIL: нет $F"; exit 1; }
head -5 "$F" | grep -q '^name: paf-onboard' || { echo "FAIL: нет frontmatter name"; exit 1; }
for s in "Phase A" "Phase B" "Phase C" "Phase D" "seed_questions" "confidence" "0.2" "idempotent" "_registry.yaml"; do
  grep -q "$s" "$F" || { echo "FAIL: нет '$s'"; exit 1; }
done
echo "PASS: paf-onboard skill структурно валиден"
SH
bash /tmp/paf_onboard_lint.sh
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `bash /tmp/paf_onboard_lint.sh`
Expected: `FAIL: нет .claude/skills/paf-onboard/SKILL.md`

- [ ] **Step 3: Создать `.claude/skills/paf-onboard/SKILL.md`**

Создай файл со следующим содержимым (зеркалит стиль `paf-init/SKILL.md`):

````markdown
---
name: paf-onboard
description: "Цифровизация контекста продукта в узлы Нексусов GROUND Vault по всему _registry.yaml: ингестия документов из _intake/ + интервью по seed_questions → low-CP допущения. Главный, repeatable, idempotent. Запусти после /paf-init (и опц. /paf-nexus-create)."
---

# /paf-onboard — цифровизация контекста в GROUND Vault

Skill коробки «PAF Team OS». Наполняет **все** Нексусы `GROUND/NEXUS/_registry.yaml` (дефолт + кастом) узлами-допущениями из документов клиента и интервью. Главная команда онбординга; repeatable и idempotent (upsert + дедуп). Реализует §5 спеки `docs/superpowers/specs/2026-06-21-paf-team-os-design.md`.

> Пошаговый план для LLM. Выполняй фазы по порядку. Читай перечисленные файлы перед записью. Ноль выдуманной PAF-терминологии вне `sa_documentation/naming_conventions.md`. **Узел без `sources` не пишется** — это workslop.

## 0. Контекст (прочитать перед стартом)

- `sa_documentation/nexus_schema.md` — Node schema (§2 обязательные ключи; §2.2 empirical-узлы онбординга: `kind`, `sources`, `confidence 0.2–0.4`, пометка; §3 `node_type`; §4 wilting).
- `sa_documentation/nexus_catalog.md` — seed_questions дефолтных типов (для кастомных — из их `_index.md`).
- `sa_documentation/ground_schema.md` — schema `config.yaml` и `_registry.yaml`.
- `GROUND/config.yaml` — `team.roster` (резолв owner), `onboarding.*`.
- `GROUND/NEXUS/_registry.yaml` — реестр Нексусов (по нему идёт обход).

## 1. Предусловие

- `GROUND/config.yaml` существует. Нет → **останови** и направь на `/paf-init`.
- Detect ruflo MCP: попробуй `mcp__ruflo__memory_stats`. Успех → используешь `mcp__ruflo__memory_search` для дедупа (Phase A). Ошибка/недоступен → fallback Grep по существующим узлам. Не падай без ruflo.

## 2. Определи область обхода

Прочитай `_registry.yaml` → список всех `{slug, source, onboarded}`. Работаешь по каждой записи. Для каждого Нексуса источник seed_questions:
- `source: default` → секция `## seed_questions` в `GROUND/NEXUS/<slug>/_index.md` (там уже скопированы из мастер-каталога).
- `source: custom` → секция `## seed_questions` в его `_index.md` (заполнена `/paf-nexus-create`).

## 3. Phase A — ингестия документов (`GROUND/_intake/`)

1. Перечисли файлы `GROUND/_intake/*` (кроме `.gitkeep`). Пусто → сообщи «`_intake/` пуст — пропускаю ингест, перехожу к интервью» и иди в Phase B.
2. Для каждого документа: прочитай, извлеки факты, разложи по релевантным Нексусам реестра.
3. **Дедуп** перед записью: ruflo `mcp__ruflo__memory_search` (или Grep по `GROUND/NEXUS/<slug>/*.md`). Совпало → **upsert** существующего узла (дополни `sources`, не плоди дубль). Нет → новый узел.
4. Запиши узел по Node schema (§2), `sources: ["onboarding:<имя-файла>"]`. Правила CP — Phase C.

## 4. Phase B — интервью по seed_questions

Для каждого Нексуса реестра, по одному вопросу за раз (конвенция paf-скиллов):
1. Задай его `seed_questions` (из §2). Не угадывай — переспрашивай при неоднозначности.
2. Пропуск вопроса допустим → узел не создаётся, пробел фиксируется для Phase D.
3. Ответ → узел по Node schema (§2), `sources: ["onboarding:interview"]`. Дедуп/upsert как в Phase A (ответ может дополнять узел из документа).

## 5. Phase C — verify + CP + обновление реестра

Для каждого созданного/обновлённого узла:
- `kind: empirical`; `owner` — резолв `owner_role` Нексуса → имя из `config.yaml team.roster` (роль не назначена → `"Cortex"`).
- `confidence: 0.2–0.4` (допущение онбординга, **не валидировано**). Выше не ставить — CP поднимают Steps 1–8.
- `ttl_days` по типу (`nexus_schema.md §2.2`: market/customer=90, growth=60, прочие — по каталогу/`_index.md`).
- `updated` = сегодня (ISO); `ripeness: fresh`.
- В тело узла — пометка: `> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.`
- **Идемпотентность:** при upsert НЕ понижай существующий `confidence`, если он > 0.4 (значит узел уже валидирован в Steps 1–8) — только дополни `sources`/тело.

Затем обнови реестр и конфиг:
- `_registry.yaml`: для Нексуса `onboarded: todo → partial`; `→ done`, если покрыты **все** его seed_questions (интервью+документы).
- `config.yaml`: `onboarding.status: init → in_progress` (или `done`, если все Нексусы `done`); добавь обработанные документы в `onboarding.sources_ingested`; при полном покрытии — `onboarding.onboarded_at: <сегодня>`.

## 6. Phase D — readiness-отчёт GROUND Vault

Выведи в чат (не файл, если не просят сохранить):
- Таблица по всем Нексусам: `slug · узлов создано · onboarded (todo/partial/done) · Context Ripeness`.
- **Карта пробелов:** незакрытые seed_questions и Нексусы без узлов.
- **Top low-CP допущений** (для приоритетной валидации в Steps 1–8).
- Финал: «GROUND насыщен (low-CP) → Steps 1–8 валидируют и поднимают CP. Следующее: первый пайплайн (`/okr-context-gen` · `/bft-context-gen` · `/sprint-roadmap` · `/req-context`).»

## 7. Гвардраилы

- Узел без `sources` **не пишется**.
- Онбординг не валидирует; допущения не выдавать за факты.
- `sa_documentation/`, `AI-PROCESSES/`, `docs/` — read-only.
- Повторный прогон безопасен: дедуп + upsert, не затирает CP Steps 1–8.
- Без ruflo — Grep-дедуп (слабее, но работает). Без `_intake/` — только интервью.
````

- [ ] **Step 4: Запустить lint — убедиться, что проходит**

Run: `bash /tmp/paf_onboard_lint.sh`
Expected: `PASS: paf-onboard skill структурно валиден`

- [ ] **Step 5: Коммит**

```bash
git add .claude/skills/paf-onboard/SKILL.md
git commit -m "feat(paf-onboard): движок наполнения Нексусов (Phase A+B+C+D)"
```

**Ручная acceptance (после плана, интерактивно):** во временном GROUND после `/paf-init` прогнать `/paf-onboard`; проверить, что интервью создаёт узлы с `confidence 0.2–0.4` + пометкой, `_registry.onboarded` меняется на `partial/done`, `config.yaml onboarding.*` обновлён; повторный прогон не дублирует.

---

### Task 2: Онбординг-бэклог в репо po-helper (8 задач + onboarding.md)

**Files:**
- Create: `backlog/config.yml`, `backlog/tasks/task-1 … task-8 *.md` (через `backlog init` + `backlog task create`)
- Create: `backlog/docs/onboarding.md`
- Create: `backlog/docs/operational-hq.md` (копия `backlog-ops.template.md` — чтобы doc-набор доски был полным после clone)
- Test: inline shell-ассерты (`backlog task list`, наличие файлов)

**Interfaces:**
- Consumes: —
- Produces: committed `backlog/` с 8 задачами label `onboarding` и `docs/onboarding.md` — источник для install.sh-засева (Task 4).

- [ ] **Step 1: Написать падающий тест доски**

```bash
cat > /tmp/onboarding_board.sh <<'SH'
set -eu
test -f backlog/config.yml || { echo "FAIL: доска не инициализирована"; exit 1; }
N=$(ls backlog/tasks/ 2>/dev/null | grep -c . || true)
test "$N" -ge 8 || { echo "FAIL: задач < 8 (есть $N)"; exit 1; }
for f in backlog/tasks/*.md; do grep -q 'onboarding' "$f" || { echo "FAIL: $f без label onboarding"; exit 1; }; done
test -f backlog/docs/onboarding.md || { echo "FAIL: нет docs/onboarding.md"; exit 1; }
grep -q 'paf-onboard' backlog/docs/onboarding.md || { echo "FAIL: onboarding.md не упоминает paf-onboard"; exit 1; }
echo "PASS: онбординг-бэклог готов ($N задач)"
SH
bash /tmp/onboarding_board.sh
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `bash /tmp/onboarding_board.sh`
Expected: `FAIL: доска не инициализирована`

- [ ] **Step 3: Инициализировать доску и создать 8 задач**

Из корня репо (доски ещё нет):

```bash
backlog init "po-helper" --defaults --integration-mode mcp --check-branches false
backlog config set remoteOperations false

backlog task create "Старт: как устроен po-helper и GROUND Vault" -l onboarding -s "To Do" --no-dod-defaults \
  -d "Ориентир перед началом. Гайд: backlog/docs/onboarding.md" \
  --ac "Прочитал backlog/docs/onboarding.md" \
  --ac "Понял модель доски «1 задача = 1 артефакт» и где источники истины (GROUND / bft_documentation / трекер / wiki)" \
  --ac "Понял цель онбординга: насыщенный GROUND Vault (все Нексусы) + заполненный domain-profile"

backlog task create "Персонализируй domain-profile.md" -l onboarding -s "To Do" --no-dod-defaults --dep task-1 \
  -d "Доменный слой фреймворка. Файл: .claude/domain-profile.md" \
  --ac "cp .claude/domain-profile.template.md .claude/domain-profile.md" \
  --ac "Заполнил пути планирования, трекер, wiki" \
  --ac "Заполнил глоссарий и стейкхолдеров" \
  --ac "Заполнил landscape.ext_teams (внешние команды)" \
  --ac "Reload Window — команды появились в чате"

backlog task create "Инициализируй GROUND Vault — /paf-init" -l onboarding -s "To Do" --no-dod-defaults --dep task-2 \
  -d "One-shot настройка. Навык: /paf-init" \
  --ac "Прошёл интервью /paf-init" \
  --ac "Создан GROUND/config.yaml (product + Product Engineer заданы)" \
  --ac "Создан GROUND/NEXUS/_registry.yaml с 13 дефолтными Нексусами"

backlog task create "(опц.) Добавь кастомные Нексусы — /paf-nexus-create" -l onboarding -s "To Do" --no-dod-defaults --dep task-3 \
  -d "Нексусы сверх дефолта под специфику продукта. Навык: /paf-nexus-create" \
  --ac "Создал нужные кастомные Нексусы (team / channels / landscape или доменные sellers/buyers)" \
  --ac "Записаны в _registry.yaml с source: custom"

backlog task create "Сложи материалы в GROUND/_intake/" -l onboarding -s "To Do" --no-dod-defaults --dep task-3 \
  -d "Документы для ингестии Phase A. Папка: GROUND/_intake/" \
  --ac "Положил доки продукта (стратегия / аналитика / PRD / интервью) в GROUND/_intake/" \
  --ac "ИЛИ осознанно пропустил — наполнение будет только из интервью"

backlog task create "Наполни Нексусы — /paf-onboard (главное)" -l onboarding -s "To Do" --no-dod-defaults --dep task-5 \
  -d "Цифровизация контекста по всему реестру. Навык: /paf-onboard" \
  --ac "Прогнал /paf-onboard по всему _registry.yaml" \
  --ac "Каждый целевой Нексус получил узлы (onboarding:doc / onboarding:interview)" \
  --ac "В _registry.yaml все onboarded != todo (partial/done)" \
  --ac "Получил readiness-отчёт + карту пробелов"

backlog task create "(опц.) Команда и карта людей" -l onboarding -s "To Do" --no-dod-defaults --dep task-6 \
  -d "People Graph и навигация. Навыки: /people-links, /people-map, /radar-calibrate" \
  --ac "team-нексус насыщен персонами" \
  --ac "/people-links — описан контур отношений PO" \
  --ac "/people-map / /radar-calibrate — навигация и качество People Graph проверены"

backlog task create "Готовность + первый реальный проход" -l onboarding -s "To Do" --no-dod-defaults --dep task-6 \
  -d "Первое применение настроенной системы." \
  --ac "readiness GROUND Vault приемлемый (нет критичных пробелов)" \
  --ac "Выбрал сценарий и запустил один из: /okr-context-gen · /bft-context-gen · /sprint-roadmap · /req-context" \
  --ac "Первый артефакт создан и заведён задачей на доске (label bft/okr/sprint/request)"
```

- [ ] **Step 4: Создать `backlog/docs/onboarding.md`**

Создай гайд со следующим содержимым:

````markdown
# 🚀 Онбординг po-helper — с чего начать

> Ты только что установил po-helper и не знаешь, за что взяться. Этот файл — пошаговый план. Открой доску `backlog board` — там те же шаги как задачи (label `onboarding`), отмечай их по мере прохождения.

**Главный результат онбординга — настроенная система:** заполнен `.claude/domain-profile.md` и насыщены **все Нексусы** GROUND Vault (`GROUND/NEXUS/_registry.yaml` → у всех `onboarded ≠ todo`). После этого po-helper персонализирован под твой продукт и готов к пайплайнам (OKR / БФТ / спринты / запросы).

Модель доски — «1 задача = 1 артефакт» (см. `backlog/docs/operational-hq.md`). Источники истины живут в артефактах (`GROUND/`, `bft_documentation/`, трекер, wiki), не на доске.

---

## Шаг 1 — Старт (понять устройство)
Прочитай этот файл и `operational-hq.md`. Пойми: доска — операционный штаб; цель онбординга — насыщенный GROUND Vault.
**Готово когда:** понимаешь, куда идёшь (config + domain-profile + заполненные Нексусы).

## Шаг 2 — Персонализируй domain-profile
```bash
cp .claude/domain-profile.template.md .claude/domain-profile.md
```
Заполни: пути планирования, трекер, wiki, глоссарий, стейкхолдеров, `landscape.ext_teams`. Затем **Reload Window** в IDE — команды появятся в чате.
**Готово когда:** `.claude/domain-profile.md` заполнен под твой продукт.

## Шаг 3 — Инициализируй GROUND Vault: `/paf-init`
Запусти навык `/paf-init` — one-shot интервью (компания, продукт, Product Engineer, роли). Создаёт `GROUND/config.yaml` + скелет + `_registry.yaml` с 13 дефолтными Нексусами.
**Готово когда:** есть `GROUND/config.yaml`, в `_registry.yaml` — дефолтный каталог.

## Шаг 4 — (опц.) Кастомные Нексусы: `/paf-nexus-create`
Нужны Нексусы сверх дефолта (`team`, `channels`, `landscape` или доменные `sellers`/`buyers`)? Запусти `/paf-nexus-create` — по одному на Нексус.
**Готово когда:** нужные кастомные Нексусы в `_registry.yaml` (`source: custom`).

## Шаг 5 — Сложи материалы в `GROUND/_intake/`
Положи документы продукта (стратегия, аналитика, PRD, транскрипты интервью) в `GROUND/_intake/` — `/paf-onboard` их проингестит. Нет документов — пропусти, наполнение пойдёт из интервью.
**Готово когда:** доки в `_intake/` (или осознанный пропуск).

## Шаг 6 — 🎯 Наполни Нексусы: `/paf-onboard` (ГЛАВНОЕ)
Запусти `/paf-onboard`. Он пройдёт по всему реестру: Phase A — ингест `_intake/`; Phase B — интервью по `seed_questions` каждого Нексуса; Phase C — запишет допущения (low-CP) и обновит `onboarded`; Phase D — выдаст readiness-отчёт и карту пробелов.
**Готово когда:** в `_registry.yaml` у всех Нексусов `onboarded ≠ todo` — **система настроена**.

## Шаг 7 — (опц.) Команда и карта людей
`/people-links` (опиши отношения PO), `/people-map` (навигация: кто по каким вопросам), `/radar-calibrate` (качество People Graph).
**Готово когда:** `team`-нексус насыщен, контур PO описан.

## Шаг 8 — Первый реальный проход
Система настроена — примени её. Выбери сценарий:
- **OKR:** `/okr-context-gen <quarter>` … `/okr-deliver`
- **БФТ:** `/bft-context-gen <epic>` … `/bft-deliver`
- **Спринт:** `/sprint-roadmap <quarter>` → `/sprint-sync <sprint>`
- **Внешний запрос:** `/req-context` … `/req-handoff`

Заведи первый артефакт задачей на доске (label `bft`/`okr`/`sprint`/`request`) — см. `operational-hq.md`.
**Готово когда:** первый артефакт в работе, зафиксирован на доске.

---

> Застрял? Полный список сценариев — в корневом `README.md`. Recall «на чём остановился» — `entire search "<тема>"`.
````

- [ ] **Step 5: Скопировать конвенцию операционного штаба**

```bash
cp backlog-ops.template.md backlog/docs/operational-hq.md
```

- [ ] **Step 6: Запустить тест — убедиться, что проходит**

Run: `bash /tmp/onboarding_board.sh`
Expected: `PASS: онбординг-бэклог готов (8 задач)`

Дополнительно проверь порядок и зависимости:
```bash
backlog task list --plain -l onboarding
```
Expected: 8 задач task-1…task-8; у task-2 dep task-1, task-6 dep task-5, task-8 dep task-6.

- [ ] **Step 7: Коммит**

```bash
git add backlog/
git commit -m "feat(onboarding): онбординг-бэклог из коробки (8 задач + onboarding.md)"
```

---

### Task 3: install.sh — деплой полного набора навыков + sa_documentation

**Files:**
- Modify: `install.sh` (массив `SKILLS`; массив `COMMANDS`; новый блок копирования `sa_documentation/`)
- Test: прогон install.sh во временном git-репо + shell-ассерты

**Interfaces:**
- Consumes: `SCRIPT_DIR/.claude/skills/*`, `SCRIPT_DIR/sa_documentation/`.
- Produces: в целевом `.claude/skills/` — `paf-init`, `paf-nexus-create`, `paf-onboard`, `people-links`, `people-map`, `nexus-calibration`; в `.claude/commands/` — `radar-*`; в корне проекта — `sa_documentation/`.

- [ ] **Step 1: Написать падающий тест деплоя**

```bash
cat > /tmp/install_deploy.sh <<'SH'
set -eu
SRC="$(pwd)"
T="$(mktemp -d)"; cd "$T"; git init -q
bash "$SRC/install.sh" "$T/.claude" >/dev/null 2>&1 || true
for s in paf-init paf-nexus-create paf-onboard people-links people-map nexus-calibration; do
  test -f ".claude/skills/$s/SKILL.md" || { echo "FAIL: не задеплоен skill $s"; exit 1; }
done
test -d "sa_documentation" || { echo "FAIL: sa_documentation не скопирован"; exit 1; }
test -f ".claude/commands/radar-calibrate.md" || { echo "FAIL: команда radar-calibrate не задеплоена"; exit 1; }
echo "PASS: деплой навыков и справочника полный"; cd "$SRC"; rm -rf "$T"
SH
bash /tmp/install_deploy.sh
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `bash /tmp/install_deploy.sh`
Expected: `FAIL: не задеплоен skill paf-init`

- [ ] **Step 3: Расширить массив `SKILLS` в install.sh**

Найди строку:
```bash
SKILLS=(bft-writer okr-planner sprint-planner po-research info-channels summary)
```
Замени на:
```bash
SKILLS=(bft-writer okr-planner sprint-planner po-research info-channels summary paf-init paf-nexus-create paf-onboard people-links people-map nexus-calibration)
```

- [ ] **Step 4: Расширить массив `COMMANDS` в install.sh**

Найди в массиве `COMMANDS=( … )` строку с `channel-map channel-list channel-route` (или конец списка перед `)`), добавь строку с People Radar командами. Итог — блок `COMMANDS` содержит дополнительно:
```bash
  radar-calibrate radar-graph radar-review
```
(добавь эти имена отдельной строкой внутри скобок `COMMANDS=( … )`, перед закрывающей `)`.)

- [ ] **Step 5: Добавить копирование `sa_documentation/`**

После блока копирования доменного профиля (после `fi` секции «доменный профиль: НИКОГДА не перезаписываем…», перед секцией entire) вставь:
```bash
# --- справочник sa_documentation (read-only, нужен paf-навыкам) ---
SRC_SADOC="$SCRIPT_DIR/sa_documentation"
if [ -d "$SRC_SADOC" ]; then
  if [ -d "$DEST_ROOT/../sa_documentation" ] && [ "$MODE" = "install" ]; then
    echo "  · sa_documentation/ уже есть — пропускаю (для обновления: --update)"
  else
    mkdir -p "$DEST_ROOT/../sa_documentation"
    cp -R "$SRC_SADOC/." "$DEST_ROOT/../sa_documentation/"
    echo "  ✓ sa_documentation/ (справочник PAF, read-only)"
  fi
fi
```

- [ ] **Step 6: Запустить тест — убедиться, что проходит**

Run: `bash /tmp/install_deploy.sh`
Expected: `PASS: деплой навыков и справочника полный`

- [ ] **Step 7: Коммит**

```bash
git add install.sh
git commit -m "feat(install): деплой paf-*/people-*/nexus-calibration + sa_documentation"
```

---

### Task 4: install.sh — засев онбординг-бэклога + текст «Дальше»

**Files:**
- Modify: `install.sh` (блок инициализации backlog — засев онбординг-задач на свежем init; финальный echo-блок «Дальше:»)
- Test: прогон install.sh во временном git-репо + shell-ассерты

**Interfaces:**
- Consumes: `SCRIPT_DIR/backlog/tasks/*.md` (label `onboarding`), `SCRIPT_DIR/backlog/docs/onboarding.md` (из Task 2).
- Produces: в целевом `backlog/tasks/` — 8 онбординг-задач; `backlog/docs/onboarding.md`.

- [ ] **Step 1: Написать падающий тест засева**

```bash
cat > /tmp/install_seed.sh <<'SH'
set -eu
SRC="$(pwd)"
command -v backlog >/dev/null || { echo "SKIP: нет backlog CLI"; exit 0; }
T="$(mktemp -d)"; cd "$T"; git init -q
bash "$SRC/install.sh" "$T/.claude" >/dev/null 2>&1 || true
N=$(ls backlog/tasks/ 2>/dev/null | grep -c 'onboarding\|Старт\|paf' || true)
test -f backlog/docs/onboarding.md || { echo "FAIL: onboarding.md не засеян"; exit 1; }
CNT=$(grep -rl 'onboarding' backlog/tasks/ 2>/dev/null | grep -c . || true)
test "$CNT" -ge 8 || { echo "FAIL: онбординг-задач < 8 (есть $CNT)"; exit 1; }
echo "PASS: онбординг засеян ($CNT задач + onboarding.md)"; cd "$SRC"; rm -rf "$T"
SH
bash /tmp/install_seed.sh
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `bash /tmp/install_seed.sh`
Expected: `FAIL: onboarding.md не засеян` (или `SKIP` если нет backlog CLI — тогда установи `bun add -g backlog.md` и повтори)

- [ ] **Step 3: Добавить засев в блок инициализации backlog**

Найди в install.sh блок успешной инициализации (внутри `if ( cd "$PROJECT_ROOT" && backlog init … ); then`), после строки `echo "  ✓ backlog/ инициализирован"`. Сразу после неё вставь засев онбординга:
```bash
      # --- засев онбординг-бэклога (только на свежем init; идемпотентно, фильтр по label) ---
      SRC_BL="$SCRIPT_DIR/backlog"
      if [ -d "$SRC_BL/tasks" ]; then
        mkdir -p "$PROJECT_ROOT/backlog/tasks" "$PROJECT_ROOT/backlog/docs"
        seeded=0
        for tf in "$SRC_BL"/tasks/*.md; do
          [ -e "$tf" ] || continue
          grep -q 'onboarding' "$tf" || continue      # только онбординг-задачи
          cp "$tf" "$PROJECT_ROOT/backlog/tasks/"
          seeded=$((seeded+1))
        done
        [ -f "$SRC_BL/docs/onboarding.md" ] && cp "$SRC_BL/docs/onboarding.md" "$PROJECT_ROOT/backlog/docs/onboarding.md"
        echo "  ✓ онбординг-бэклог засеян ($seeded задач + docs/onboarding.md) — открой: backlog board"
      fi
```

- [ ] **Step 4: Обновить финальный блок «Дальше:»**

Найди в финале install.sh строку:
```bash
echo "  1) cp $DEST_ROOT/domain-profile.template.md $DEST_ROOT/domain-profile.md  и заполните под проект"
```
Замени весь нумерованный список «Дальше» на версию, где шаг 1 — доска:
```bash
echo "  1) backlog board — пошаговый план погружения (задачи 1→8: domain-profile → /paf-init → /paf-onboard → первый пайплайн)"
echo "  2) cp $DEST_ROOT/domain-profile.template.md $DEST_ROOT/domain-profile.md  и заполните под проект"
echo "  3) Reload Window в IDE — команды появятся в чате"
echo "  4) /paf-init → (опц.) /paf-nexus-create → /paf-onboard  (насытить GROUND Vault)"
echo "  5) Первый артефакт: /okr-context-gen · /bft-context-gen · /sprint-roadmap · /req-context"
```
(Удали прежние строки пунктов 1–4, заменив их этими пятью.)

- [ ] **Step 5: Запустить тест — убедиться, что проходит**

Run: `bash /tmp/install_seed.sh`
Expected: `PASS: онбординг засеян (8 задач + onboarding.md)`

- [ ] **Step 6: Проверить идемпотентность (засев не бьёт существующую доску)**

```bash
SRC="$(pwd)"; T="$(mktemp -d)"; cd "$T"; git init -q
mkdir -p backlog/tasks && printf -- '---\nid: TASK-1\ntitle: Мой артефакт\nstatus: In Progress\nlabels: [bft]\n---\n' > "backlog/tasks/task-1 - Мой артефакт.md"
backlog init "x" --defaults --integration-mode mcp --check-branches false >/dev/null 2>&1 || true
bash "$SRC/install.sh" "$T/.claude" >/dev/null 2>&1 || true
grep -q 'Мой артефакт' "backlog/tasks/task-1 - Мой артефакт.md" && echo "PASS: чужая задача не тронута" || echo "FAIL: затёрли существующую задачу"
cd "$SRC"; rm -rf "$T"
```
Expected: `PASS: чужая задача не тронута` (доска уже была → ветка свежего init не сработала → засев пропущен).

- [ ] **Step 7: Коммит**

```bash
git add install.sh
git commit -m "feat(install): засев онбординг-бэклога + план погружения в блоке «Дальше»"
```

---

### Task 5: Сквозная верификация + регрессионный харнесс

**Files:**
- Create: `test/onboarding_flow_check.sh` (консолидированный регрессионный прогон)
- Test: сам скрипт

**Interfaces:**
- Consumes: всё выше.
- Produces: committed `test/onboarding_flow_check.sh` — повторяемая проверка всей фичи.

- [ ] **Step 1: Создать `test/onboarding_flow_check.sh`**

```bash
mkdir -p test
cat > test/onboarding_flow_check.sh <<'SH'
#!/usr/bin/env bash
# Регрессионная проверка фичи onboarding-flow. Запуск из корня репо: bash test/onboarding_flow_check.sh
set -eu
SRC="$(cd "$(dirname "$0")/.." && pwd)"; cd "$SRC"
fail(){ echo "FAIL: $1"; exit 1; }

# 1. paf-onboard skill
F=.claude/skills/paf-onboard/SKILL.md
test -f "$F" || fail "нет $F"
for s in "Phase A" "Phase B" "Phase C" "Phase D" "seed_questions" "_registry.yaml"; do grep -q "$s" "$F" || fail "paf-onboard без '$s'"; done

# 2. committed онбординг-бэклог
test -f backlog/docs/onboarding.md || fail "нет backlog/docs/onboarding.md"
CNT=$(grep -rl 'onboarding' backlog/tasks/ | grep -c .)
test "$CNT" -ge 8 || fail "онбординг-задач < 8 ($CNT)"

# 3. install.sh деплой + засев во временном репо
if command -v backlog >/dev/null 2>&1; then
  T="$(mktemp -d)"; ( cd "$T" && git init -q )
  bash "$SRC/install.sh" "$T/.claude" >/dev/null 2>&1 || true
  for sk in paf-init paf-nexus-create paf-onboard people-links people-map nexus-calibration; do
    test -f "$T/.claude/skills/$sk/SKILL.md" || fail "не задеплоен $sk"
  done
  test -d "$T/sa_documentation" || fail "sa_documentation не скопирован"
  test -f "$T/backlog/docs/onboarding.md" || fail "onboarding.md не засеян"
  SC=$(grep -rl 'onboarding' "$T/backlog/tasks/" | grep -c .)
  test "$SC" -ge 8 || fail "засеяно задач < 8 ($SC)"
  rm -rf "$T"
else
  echo "  (backlog CLI нет — пропускаю install-часть)"
fi
echo "PASS: onboarding-flow регрессия зелёная"
SH
chmod +x test/onboarding_flow_check.sh
```

- [ ] **Step 2: Запустить харнесс**

Run: `bash test/onboarding_flow_check.sh`
Expected: `PASS: onboarding-flow регрессия зелёная`

- [ ] **Step 3: Проверить `git clone`-путь (доска в самом репо)**

```bash
backlog task list --plain -l onboarding | grep -c onboarding || true
```
Expected: ≥ 8 задач видны в самом репо po-helper (⇒ после `git clone` `backlog board` покажет план).

- [ ] **Step 4: Коммит**

```bash
git add test/onboarding_flow_check.sh
git commit -m "test(onboarding): регрессионный харнесс фичи onboarding-flow"
```

---

## Self-Review (выполнено при написании плана)

**Spec coverage:**
- §3 `/paf-onboard` (Phase A/B/C/D, CP, idempotent, registry-update) → Task 1. ✓
- §4 онбординг-бэклог (8 задач + onboarding.md, committed) → Task 2. ✓
- §4.3 идемпотентность/фильтр label → Task 4 Step 3 + Step 6. ✓
- §5 install.sh деплой полного набора + sa_documentation → Task 3. ✓
- §5 засев + текст «Дальше» → Task 4. ✓
- §7 проверки (paf-onboard, clone, install, DoD) → Task 1 (ручная acceptance), Task 5. ✓
- §6 порядок (paf-onboard → бэклог → install) → Task 1→2→3→4. ✓

**Placeholder scan:** содержимое обоих авторских файлов (SKILL.md, onboarding.md) приведено полностью; команды `backlog task create` — с реальными `--ac`; правки install.sh — с точными anchor-строками. Плейсхолдеров нет.

**Type/имена consistency:** label `onboarding` единообразен во всех задачах и фильтрах; `_registry.onboarded` значения `todo/partial/done` согласованы (Task 1 Phase C ↔ Task 2 AC ↔ Task 5); имена навыков (`paf-onboard`, `people-links`, `people-map`, `nexus-calibration`) совпадают в install.sh-массиве (Task 3) и тестах (Task 3/5).

**Открытый момент для исполнителя:** точное расположение строки `channel-map channel-list channel-route` внутри `COMMANDS=( … )` проверить глазами перед правкой (Task 3 Step 4) — массив многострочный.
