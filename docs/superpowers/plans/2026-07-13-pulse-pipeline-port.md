# Pulse-pipeline Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Перенести цепочку `chat-watch → chat-sync → /pulse-radar → /pulse-promote` из инстанса `mts-po-workspace` в фреймворк po-helper как generic, независимый от MTS.Link функционал, раздаваемый через `install.sh`.

**Architecture:** 4 скилла (skill + тонкая команда, конвенция po-helper). Интерфейс между ingest и анализом — контракт чат-дампа (resource-док). Платформенная привязка (MTS.Link) изолирована в opt-in адаптере `tools/adapters/mts-link/`, не течёт в тела скиллов. Нейминг `pulse-*` снимает коллизию с People Radar (`/radar-*` = `nexus-calibration`).

**Tech Stack:** Markdown-скиллы Claude Code; Node-адаптер (Playwright + WS, opt-in); pytest для lint-гейта (`sa_documentation/tests/`); bash `install.sh`.

## Global Constraints

- **Источник (порт из):** `/Users/aleksishmanov/.superset/worktrees/71127651-8584-4849-82d8-40aade7ac975/chat-analytics-llm-export` — далее `$SRC`.
- **Целевой репо:** `~/projects/po-helper` — далее `$PO`. Все git-операции из `$PO`.
- **Ветка:** `feat/pulse-pipeline-port` от `origin/main` (уже создана).
- **Нейминг:** `link-radar` → `pulse-radar`; `radar-promote` → `pulse-promote`. `chat-watch`/`chat-sync` имена сохраняются. People Radar (`/radar-calibrate|graph|review`, `nexus-calibration`) НЕ трогать.
- **Данные MTS не коммитить:** ни реальных `watched-chats.yaml`, ни чат-дампов, ни радар-нот, ни `auth.json`, ни `node_modules`. Примеры пишутся заново, обезличенные.
- **Запрещённые токены в портированных скиллах** (grep-гейт, Task 8): `link-radar`, `radar-promote`, `mts-po-workspace`, `Ишманов`, `team-ishmanov-aleksej`, `Парфило`, `GDS Daily`. Абсолютные `~/tools`-пути — только внутри `tools/adapters/mts-link/`.
- **PO-идентичность** в шаблонах узлов резолвится из `.claude/domain-profile.md` (`po_name` + team-node-id PO), не хардкодится.
- **Контракт чат-дампа** — единственный источник правды формата; на него ссылаются и `chat-sync`, и `pulse-radar`.

---

### Task 1: Контракт чат-дампа + скилл chat-sync (ядро-интерфейс)

**Files:**
- Create: `$PO/.claude/skills/chat-sync/SKILL.md`
- Create: `$PO/.claude/skills/chat-sync/resources/chat_dump_contract.md`

**Interfaces:**
- Produces: контракт чат-дампа — файл `GROUND/_intake/chats/YYYY-MM-DD..YYYY-MM-DD <chat>.md` с frontmatter `type: chat-dump`, `source`, `chat-id`, `window`, `purpose`, `extract`, `msg-count` и телом `Автор HH:MM: текст` по дням. Потребляют: `pulse-radar` (Task 3), адаптер (Task 5).

- [ ] **Step 1: Создать контракт-док**

Записать `$PO/.claude/skills/chat-sync/resources/chat_dump_contract.md`:

````markdown
# Контракт чат-дампа

Единый формат файлов `GROUND/_intake/chats/`. Продюсер — source-адаптер (`/chat-sync`),
потребитель — `/pulse-radar`. Любой адаптер обязан писать ровно этот формат.

## Имя файла

```
GROUND/_intake/chats/YYYY-MM-DD..YYYY-MM-DD <название чата>.md
```

`YYYY-MM-DD..YYYY-MM-DD` — окно выгрузки (from..to). Один файл = один чат за окно.

## Frontmatter (порядок ключей обязателен)

```yaml
---
type: chat-dump
source: "<название источника, напр. MTS Link>"
chat-id: "<идентификатор чата в источнике>"
window: "YYYY-MM-DD..YYYY-MM-DD"
purpose: "<зачем PO следит за чатом — из watched-chats.yaml>"
extract: "<что вытаскивать — из watched-chats.yaml>"
msg-count: <n>
---
```

## Тело

Реплики, сгруппированные по дням; внутри дня — по времени:

```
## YYYY-MM-DD

Автор Фамилия HH:MM: текст реплики
Другой Автор HH:MM: текст следующей реплики
```

- Автор — как в источнике (сверка с `NEXUS/team` — уже на стороне `/pulse-radar`).
- Время — `HH:MM` источника; неизвестно → `--:--`.
- Пустые чаты (0 сообщений за окно) — файл не создаётся.
````

- [ ] **Step 2: Создать generalized skill chat-sync**

Записать `$PO/.claude/skills/chat-sync/SKILL.md`:

````markdown
---
name: chat-sync
description: "Выгрузить сообщения из отслеживаемых чатов за период в GROUND/_intake/chats через source-адаптер. По реестру watched-chats.yaml тянет окно, пишет по markdown-файлу на чат по контракту чат-дампа — готово к /pulse-radar. Триггеры: «выгрузи чаты», «что нового в чатах за неделю», «синхронизируй чаты», /chat-sync."
---

# /chat-sync — выгрузить сообщения отслеживаемых чатов

Обёртка над **source-адаптером**: по реестру `/chat-watch` выкачивает сообщения за окно
в markdown по [контракту чат-дампа](resources/chat_dump_contract.md). Дальше разбор —
`/pulse-radar` поверх скачанных файлов.

> Роль: **диспетчер выгрузки чатов PO**. Ты качаешь сырые сообщения за период; глубокий
> разбор — уже поверх дампов, под цель (`purpose`/`extract`) каждого чата.

## Константы окружения

- **Адаптер:** `tools/adapters/<chat_adapter>/` — `chat_adapter` из `.claude/domain-profile.md`
  (`info_sources.chat_adapter`). Референс-адаптер: `mts-link` (см. его README — setup, SSO, флаги).
- **Реестр:** `GROUND/_intake/chats/watched-chats.yaml` (заполняется через `/chat-watch`).
- **Куда качает:** `GROUND/_intake/chats/` (формат — `resources/chat_dump_contract.md`).

## Шаг 0. Проверить адаптер и реестр

- Адаптер не сконфигурирован (`info_sources.chat_adapter` пуст / папки нет) → сказать PO:
  либо поставить адаптер (README в `tools/adapters/<name>/`), либо **положить дампы руками**
  в `GROUND/_intake/chats/` по контракту.
- Реестр пуст → сначала `/chat-watch`.
- Setup адаптера (сессия/SSO/зависимости) — по README конкретного адаптера, не здесь.

## Шаг 1. Выгрузить окно

Окно — из запроса PO; дефолт 14 дней. «за неделю» → 7 дней; «за месяц» → 30; явные даты → from..to.
Запустить выгрузку через адаптер (интерфейс вызова — в README адаптера). Адаптер пишет по файлу
на чат в `GROUND/_intake/chats/` строго по контракту. Пустые чаты пропускаются.

## Шаг 2. Анализ

Кратко отчитаться: сколько файлов, куда, перечислить чаты. Затем предложить разбор: на каждый
файл прочитать `purpose`/`extract` из frontmatter и вытащить именно запрошенное (блокеры,
эскалации, решения, дедлайны…). По многим файлам — раздать субагентам. Глубокий разбор — по просьбе PO.

## Guardrails

- **Read-only.** Адаптер только читает; не шлёт сообщений, не помечает прочитанным.
- **Секреты вне git.** Токены/сессии адаптера не коммитить и не читать (см. README адаптера).
- **Дампы не редактировать построчно.** Перенос/переименование — файловой операцией.
- **Формат = контракт.** Любой дамп в `_intake/chats/` соответствует `resources/chat_dump_contract.md`.
- Нет адаптера → честно сказать PO про ручной drop, не выдумывать данные.
````

- [ ] **Step 3: Verify — файлы на месте, нет MTS-хардкода, контракт валиден**

Run:
```bash
cd $PO
test -f .claude/skills/chat-sync/SKILL.md && test -f .claude/skills/chat-sync/resources/chat_dump_contract.md && echo "FILES_OK"
grep -q "type: chat-dump" .claude/skills/chat-sync/resources/chat_dump_contract.md && echo "CONTRACT_OK"
grep -Eq "mts-link-chat-sync|MTS\.Link|~/tools|~/\.mts-link-sync" .claude/skills/chat-sync/SKILL.md && echo "MTS_LEAK" || echo "NO_MTS_LEAK"
```
Expected: `FILES_OK`, `CONTRACT_OK`, `NO_MTS_LEAK`.

- [ ] **Step 4: Commit**

```bash
cd $PO
git add .claude/skills/chat-sync/
git commit -m "feat(pulse): generic chat-sync + контракт чат-дампа (ядро-интерфейс)"
```

---

### Task 2: Скилл chat-watch (generalized, поле source)

**Files:**
- Create: `$PO/.claude/skills/chat-watch/SKILL.md`

**Interfaces:**
- Produces: реестр `GROUND/_intake/chats/watched-chats.yaml` (записи с полями `chat-id`, `name`, `source`, `purpose`, `extract`). Потребляют: `chat-sync` (Task 1), `pulse-radar` (Task 3).

- [ ] **Step 1: Создать generalized skill chat-watch**

Записать `$PO/.claude/skills/chat-watch/SKILL.md`:

````markdown
---
name: chat-watch
description: "Настроить, за какими чатами следит PO. Показывает список чатов из источника → PO выбирает → на каждый спрашивает purpose (зачем слежу) и extract (что вытаскивать) → пишет в GROUND/_intake/chats/watched-chats.yaml. Дальше /chat-sync качает эти чаты. Триггеры: «настрой слежку за чатами», «добавь чат в мониторинг», «за какими чатами слежу», /chat-watch."
---

# /chat-watch — настроить отслеживаемые чаты

Управляет реестром чатов, за которыми следит PO: какой чат, из какого источника, зачем
(`purpose`) и что вытаскивать (`extract`). Реестр использует `/chat-sync` при выгрузке.

> Роль: **настройщик мониторинга чатов PO**. Ты не разбираешь содержание (это `/pulse-radar`
> после `/chat-sync`), ты помогаешь PO выбрать чаты и зафиксировать по каждому цель и предмет интереса.

## Константы окружения

- **Реестр:** `GROUND/_intake/chats/watched-chats.yaml` (в vault; можно править руками).
- **Источник/адаптер:** `tools/adapters/<chat_adapter>/` из `.claude/domain-profile.md`
  (`info_sources.chat_adapter`). Листинг чатов — через адаптер (см. его README).

## Шаг 0. Проверить источник

Адаптер сконфигурирован → перечисление чатов через него (см. README адаптера: сессия/листинг).
Адаптера нет → PO ведёт реестр руками (структура записи — ниже).

## Шаг 1. Показать список чатов

Получить у адаптера нумерованный список чатов (фильтр по подстроке, если чатов много).
Показать PO и спросить, за какими он хочет следить.

## Шаг 2. По каждому выбранному — спросить purpose и extract

На КАЖДЫЙ выбранный чат спросить у PO:
- **purpose** — зачем следишь за этим чатом (одна фраза).
- **extract** — что именно вытаскивать (блокеры, эскалации, решения, дедлайны, жалобы…).

Записать в реестр `GROUND/_intake/chats/watched-chats.yaml` запись вида:

```yaml
- chat-id: "<id в источнике>"
  name: "<название чата>"
  source: "<название источника, напр. MTS Link>"
  purpose: "<зачем слежу>"
  extract: "<что вытаскивать>"
```

Запись идемпотентна по `chat-id` (повтор не плодит дублей).

## Прочее

- Реестр — обычный YAML, PO может править руками (добавить/убрать/поправить purpose/extract).
- Несколько источников сосуществуют — различаются полем `source`.

## Guardrails

- **Read-only** относительно источника: листинг чатов, не отправка сообщений.
- **Секреты вне git** (сессии/токены адаптера — см. README адаптера).
- **Не выбирать чаты за PO.** Список → PO называет чаты → уточнить purpose/extract.
````

- [ ] **Step 2: Verify**

Run:
```bash
cd $PO
test -f .claude/skills/chat-watch/SKILL.md && echo "FILE_OK"
grep -q "source:" .claude/skills/chat-watch/SKILL.md && echo "SOURCE_FIELD_OK"
grep -Eq "MTS\.Link следит|mts-link-chat-sync|~/\.mts-link-sync" .claude/skills/chat-watch/SKILL.md && echo "MTS_LEAK" || echo "NO_MTS_LEAK"
```
Expected: `FILE_OK`, `SOURCE_FIELD_OK`, `NO_MTS_LEAK`.

- [ ] **Step 3: Commit**

```bash
cd $PO
git add .claude/skills/chat-watch/
git commit -m "feat(pulse): generic chat-watch с полем source (мультиисточник)"
```

---

### Task 3: Скилл pulse-radar (порт link-radar) + обезличенный пример

**Files:**
- Create: `$PO/.claude/skills/pulse-radar/SKILL.md` (из `$SRC/.claude/skills/link-radar/SKILL.md`)
- Create: `$PO/.claude/skills/pulse-radar/resources/radar_format.md` (из источника)
- Create: `$PO/.claude/skills/pulse-radar/examples/ideal_radar.md` (написать заново, обезличенный)

**Interfaces:**
- Consumes: контракт чат-дампа (Task 1); `GROUND/NEXUS/okr/kr-*.md`, `GROUND/NEXUS/team/team-*.md`.
- Produces: радар-нота `{pulse_radar_dir}/YYYY-MM-DD-pulse-radar.md` (frontmatter `nexus: pulse`, `node_type: radar`, `window`, `signals_count`; секции 🔴🚧✅📈❗🔕). Потребляет: `pulse-promote` (Task 4).

- [ ] **Step 1: Скопировать SKILL и radar_format, применить глобальный ренейм**

Run:
```bash
cd $PO
mkdir -p .claude/skills/pulse-radar/resources .claude/skills/pulse-radar/examples
cp "$SRC/.claude/skills/link-radar/SKILL.md" .claude/skills/pulse-radar/SKILL.md
cp "$SRC/.claude/skills/link-radar/resources/radar_format.md" .claude/skills/pulse-radar/resources/radar_format.md
# глобальный ренейм имени скилла и производных (покрывает /link-radar, -link-radar.md, link-radar/resources)
LC_ALL=C sed -i '' 's/link-radar/pulse-radar/g' .claude/skills/pulse-radar/SKILL.md .claude/skills/pulse-radar/resources/radar_format.md
```

- [ ] **Step 2: Genericize SKILL.md (снять MTS из описания/заголовка/входа)**

Применить Edit-ы к `$PO/.claude/skills/pulse-radar/SKILL.md`:

Edit A — `description`:
- old: `"Радар по чатам MTS.Link: превращает выгруженные чат-дампы в одну датированную PULSE-радар-заметку — срез «что горит сейчас» (инциденты/блокеры/решения/риски/действия-на-PO), с привязкой к KR. Используй когда: радар по чатам, что горит в чатах, инциденты из MTS Link, дайджест чатов, /pulse-radar."`
- new: `"Радар по чатам: превращает выгруженные чат-дампы в одну датированную PULSE-радар-заметку — срез «что горит сейчас» (инциденты/блокеры/решения/риски/действия-на-PO), с привязкой к KR. Используй когда: радар по чатам, что горит в чатах, инциденты из чатов, дайджест чатов, /pulse-radar."`

Edit B — заголовок (глобальный sed не трогает `Link-Radar` с большой буквы):
- old: `# Навык: Link-Radar — радар сигналов из чатов MTS.Link`
- new: `# Навык: Pulse-Radar — радар сигналов из чатов`

Edit C — вход роли:
- old: `Ты — **радар-аналитик PO**. На вход — готовые чат-дампы MTS.Link за окно.`
- new: `Ты — **радар-аналитик PO**. На вход — готовые чат-дампы за окно (формат — `../chat-sync/resources/chat_dump_contract.md`).`

- [ ] **Step 3: Genericize radar_format.md (frontmatter источника/тегов + пример строки)**

Применить Edit-ы к `$PO/.claude/skills/pulse-radar/resources/radar_format.md`:

Edit A — источник во frontmatter:
- old: `source: MTS Link (chats)`
- new: `source: <источник из адаптера, напр. "MTS Link">`

Edit B — теги:
- old: `tags: [progress-pulse, radar, mts-link]`
- new: `tags: [progress-pulse, radar, chats]`

Edit C — пример строки сигнала (обезличить):
- old: `- 🟠 web_db кино: данные только на уровне кэша, миграция в БД не сделана ← GDS Daily · Парфило Сергей · 09:15 · KR 2.4 · [NEW]`
- new: `- 🟠 payments: остатки только в кэше, миграция в БД не сделана ← Чат «Платежи» · Иванов Иван · 09:15 · KR 1.2 · [NEW]`

- [ ] **Step 4: Написать обезличенный пример ideal_radar.md**

Записать `$PO/.claude/skills/pulse-radar/examples/ideal_radar.md`:

````markdown
---
nexus: pulse
node_type: radar
source: "MTS Link"
window: 2026-01-13..2026-01-15
generated: 2026-01-15
chats_scanned: 3
signals_count: 4
tags: [progress-pulse, radar, chats]
---

## 🔴 Инциденты

- 🔴 payments: платёжный шлюз отдаёт 500 на пике, часть заказов теряется ← Чат «Платежи» · Иванов Иван · 08:40 · KR 1.2 · [NEW]

## 🚧 Блокеры

- 🟠 catalog: индексация карточек не запущена, релиз поиска ждёт ← Чат «Каталог» · Петров Пётр · 11:05 · KR 2.1 · [идёт]
- 🟠 payments: нет ответственного за миграцию остатков из кэша в БД ← Чат «Платежи» · Иванов Иван · 09:15 · [KR?] · [NEW]

## ✅ Решения / изменения

- ⚪ решили временно кешировать остатки на 5 минут как обходной путь ← Чат «Платежи» · Сидоров Сидор · 15:20 · KR 1.2 · [NEW]

## 📈 Влияние на цели спринта

- payments-инцидент риск KR 1.2
- catalog-индексация тормозит KR 2.1

## ❗ Требует твоего ответа

- ❗ согласовать окно для миграции остатков в БД ← Чат «Платежи» · Иванов Иван · 09:16 · [KR?] · [NEW]

## 🔕 Прочее / инфошум

- ⚪ Каналы-вещание без значимых сигналов: «Новости компании», «Дежурная смена» ← скипнуто (только анонсы)
````

- [ ] **Step 5: Verify — нет запрещённых токенов, есть новое имя**

Run:
```bash
cd $PO
grep -rEl "link-radar|MTS\.Link|Парфило|GDS Daily|web_db кино" .claude/skills/pulse-radar/ && echo "LEAK" || echo "CLEAN"
grep -q "pulse-radar" .claude/skills/pulse-radar/SKILL.md && grep -q "Pulse-Radar" .claude/skills/pulse-radar/SKILL.md && echo "RENAMED_OK"
```
Expected: `CLEAN`, `RENAMED_OK`.

- [ ] **Step 6: Commit**

```bash
cd $PO
git add .claude/skills/pulse-radar/
git commit -m "feat(pulse): pulse-radar (порт link-radar, генерик + обезличенный пример)"
```

---

### Task 4: Скилл pulse-promote (порт radar-promote) + генерик PO-идентичности + пример

**Files:**
- Create: `$PO/.claude/skills/pulse-promote/SKILL.md` (из `$SRC/.claude/skills/radar-promote/SKILL.md`)
- Create: `$PO/.claude/skills/pulse-promote/resources/promote_rules.md` (из источника)
- Create: `$PO/.claude/skills/pulse-promote/examples/ideal_promotion.md` (написать заново, обезличенный)

**Interfaces:**
- Consumes: радар-нота `*-pulse-radar.md` (Task 3); узлы `GROUND/NEXUS/{problem,okr,system,ownership}/`.
- Produces: новые/additive-обновлённые узлы NEXUS (`confidence: 0.3` для новых; ревью-гейт; идемпотентность).

- [ ] **Step 1: Скопировать SKILL и promote_rules, применить глобальный ренейм**

Run:
```bash
cd $PO
mkdir -p .claude/skills/pulse-promote/resources .claude/skills/pulse-promote/examples
cp "$SRC/.claude/skills/radar-promote/SKILL.md" .claude/skills/pulse-promote/SKILL.md
cp "$SRC/.claude/skills/radar-promote/resources/promote_rules.md" .claude/skills/pulse-promote/resources/promote_rules.md
# ренейм имени скилла + upstream ссылок (radar-promote→pulse-promote, link-radar→pulse-radar)
LC_ALL=C sed -i '' -e 's/radar-promote/pulse-promote/g' -e 's/link-radar/pulse-radar/g' \
  .claude/skills/pulse-promote/SKILL.md .claude/skills/pulse-promote/resources/promote_rules.md
```

- [ ] **Step 2: Genericize PO-идентичность в promote_rules.md**

Применить Edit-ы к `$PO/.claude/skills/pulse-promote/resources/promote_rules.md`:

Edit A — owner в шаблоне узла:
- old: `owner: Ишманов Алексей Юрьевич`
- new: `owner: <po_name из .claude/domain-profile.md>`

Edit B — owns_node в шаблоне узла:
- old: `owns_node: team-ishmanov-aleksej`
- new: `owns_node: <team-node-id PO из domain-profile (node_id PO-узла в NEXUS/team)>`

Edit C — правило заполнения owns_node:
- old: `- `owns_node: team-ishmanov-aleksej` — всегда для новых узлов из этого скилла.`
- new: `- `owns_node` — team-узел PO (node_id из `NEXUS/team`, PO из domain-profile); всегда для новых узлов из этого скилла.`

- [ ] **Step 3: Написать обезличенный пример ideal_promotion.md**

Записать `$PO/.claude/skills/pulse-promote/examples/ideal_promotion.md`:

````markdown
# Эталон промоута — pulse-promote

Источник сигналов: `../../pulse-radar/examples/ideal_radar.md` (обезличенный).
Радар-нота: `GROUND/PULSE/radar/2026-01-15-pulse-radar.md` (window 2026-01-13..2026-01-15, 4 сигнала).

## Список кандидатов (шаг 5)

```
1. new-problem · GROUND/NEXUS/problem/problem-payments-cache-migration.md · нет ответственного за миграцию остатков кэш→БД
2. ownership-fact · GROUND/NEXUS/ownership/ownership-payments-migration.md · зона миграции остатков без владельца
SKIP: инцидент шлюза 500 — разовый, закрыт обходным кешированием (не структурный)
SKIP: ❗ согласовать окно миграции — действие-на-PO (факт уже поднят кандидатом #1)
SKIP: catalog-индексация — уже промоучена ранее (already-promoted)
```

## Новый узел (после выбора PO: «1»)

`GROUND/NEXUS/problem/problem-payments-cache-migration.md`:

```yaml
---
nexus: problem
node_id: problem-payments-cache-migration
node_type: step-overview
kind: empirical
owner: <po_name из domain-profile>
confidence: 0.3
sources: [radar-2026-01-15, "Чат «Платежи» · Иванов Иван · 09:15"]
updated: 2026-01-15
ttl_days: 90
ripeness: fresh
title: Миграция остатков кэш→БД без ответственного
source_note: GROUND/PULSE/radar/2026-01-15-pulse-radar.md
owns_node: <team-node-id PO>
mentions: []
involves: []
---
# Миграция остатков кэш→БД без ответственного

Остатки платежей держатся только в кэше; перенос в БД не сделан и не закреплён за
владельцем. Всплыло на инциденте шлюза (обходной путь — кеш на 5 минут), риск потери
данных при сбое. Якорь: Чат «Платежи» · Иванов Иван · 09:15.
```

## Additive-апдейт (пример на существующем узле)

Если бы `ownership-payments-migration.md` уже существовал — в конец тела, раздел
`## Сигналы из чатов (радар)`, один булет (curated-текст и frontmatter кроме `updated`/`sources` не трогаются):

```
- [2026-01-15] зона миграции остатков кэш→БД без владельца ← Чат «Платежи» · Иванов Иван · 09:15 (radar)
```

## Идемпотентность

Повторный прогон по той же `2026-01-15-pulse-radar.md`: узел `problem-payments-cache-migration`
уже есть → `already-promoted`, пропуск. Дубли не плодятся.
````

- [ ] **Step 4: Verify**

Run:
```bash
cd $PO
grep -rEl "radar-promote|link-radar|Ишманов|team-ishmanov-aleksej" .claude/skills/pulse-promote/ && echo "LEAK" || echo "CLEAN"
grep -q "pulse-promote" .claude/skills/pulse-promote/SKILL.md && echo "RENAMED_OK"
grep -q "ГГГГ-ММ-ДД-pulse-radar.md" .claude/skills/pulse-promote/resources/promote_rules.md && echo "SOURCE_NOTE_OK"
```
Expected: `CLEAN`, `RENAMED_OK`, `SOURCE_NOTE_OK`.

- [ ] **Step 5: Commit**

```bash
cd $PO
git add .claude/skills/pulse-promote/
git commit -m "feat(pulse): pulse-promote (порт radar-promote, генерик PO-идентичности + пример)"
```

---

### Task 5: Opt-in адаптер MTS.Link (`tools/adapters/mts-link/`)

**Files:**
- Create: `$PO/tools/adapters/mts-link/` (копия `$SRC/tools/mts-link-chat-sync/`, без `node_modules`/`.env`/`auth.json`)
- Modify: `$PO/.gitignore` (страховка для адаптер-секретов/артефактов)

**Interfaces:**
- Consumes: `watched-chats.yaml` (Task 2).
- Produces: чат-дампы по контракту (Task 1) в `GROUND/_intake/chats/`.

- [ ] **Step 1: Скопировать инструмент без секретов и зависимостей**

Run:
```bash
cd $PO
mkdir -p tools/adapters
rsync -a --exclude 'node_modules' --exclude '.env' --exclude 'auth.json' \
  --exclude '.last-chats.json' --exclude 'chats-out' --exclude '*.log' \
  "$SRC/tools/mts-link-chat-sync/" tools/adapters/mts-link/
ls tools/adapters/mts-link/
```
Expected: видны `chats.mjs`, `config.mjs`, `harvest.mjs`, `login.mjs`, `registry.mjs`, `wsClient.mjs`, `package.json`, `.env.example`, `.gitignore`, `README.md` — и НЕТ `node_modules`/`.env`/`auth.json`.

- [ ] **Step 2: Добавить преамбулу про контракт в README адаптера**

Prepend в начало `$PO/tools/adapters/mts-link/README.md` блок (Edit: вставить перед первой строкой файла):

```markdown
> **Адаптер `mts-link` для po-helper Pulse-pipeline.** Референс source-адаптера для `/chat-sync`.
> Пишет чат-дампы в `GROUND/_intake/chats/` строго по контракту
> `.claude/skills/chat-sync/resources/chat_dump_contract.md` (frontmatter `type: chat-dump` + тело).
> **Opt-in:** `install.sh` его не ставит. Setup: `npm install` (тянет Playwright chromium),
> затем `npm run login` (корпоративный SSO — только PO). Секреты (`.env`, `auth.json`) — вне git.

---

```

- [ ] **Step 3: Страховка в корневом .gitignore**

Добавить в конец `$PO/.gitignore`:

```
# opt-in чат-адаптеры (node-зависимости и секреты не коммитим)
tools/adapters/*/node_modules/
tools/adapters/*/.env
tools/adapters/*/auth.json
tools/adapters/*/.last-chats.json
```

- [ ] **Step 4: Verify — нет секретов и node_modules в индексе**

Run:
```bash
cd $PO
git add tools/adapters/mts-link/ .gitignore
git status --porcelain | grep -E "adapters/mts-link/(node_modules|\.env$|auth\.json)" && echo "SECRET_LEAK" || echo "NO_SECRET"
test -f tools/adapters/mts-link/.env.example && echo "ENV_EXAMPLE_OK"
git ls-files tools/adapters/mts-link/ | grep -q "chats.mjs" && echo "TOOL_TRACKED"
```
Expected: `NO_SECRET`, `ENV_EXAMPLE_OK`, `TOOL_TRACKED`.

- [ ] **Step 5: Commit**

```bash
cd $PO
git commit -m "feat(pulse): opt-in MTS.Link адаптер в tools/adapters/mts-link"
```

---

### Task 6: Command-врапперы (4 команды)

**Files:**
- Create: `$PO/.claude/commands/chat-watch.md`
- Create: `$PO/.claude/commands/chat-sync.md`
- Create: `$PO/.claude/commands/pulse-radar.md`
- Create: `$PO/.claude/commands/pulse-promote.md`

**Interfaces:**
- Consumes: соответствующие скиллы (Tasks 1–4). Каждая команда резолвит `domain-profile` и делегирует в свой SKILL.

- [ ] **Step 1: chat-watch.md**

Записать `$PO/.claude/commands/chat-watch.md`:

````markdown
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
````

- [ ] **Step 2: chat-sync.md**

Записать `$PO/.claude/commands/chat-sync.md`:

````markdown
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
````

- [ ] **Step 3: pulse-radar.md**

Записать `$PO/.claude/commands/pulse-radar.md`:

````markdown
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
````

- [ ] **Step 4: pulse-promote.md**

Записать `$PO/.claude/commands/pulse-promote.md`:

````markdown
---
description: 'Промоут устойчивых сигналов радар-ноты в узлы NEXUS через ревью-гейт (additive-only, CP=0.3 для новых) (роль: Куратор контекста)'
---

## Использование

```
/pulse-promote [YYYY-MM-DD]
```

- дата → взять `PULSE/radar/YYYY-MM-DD-pulse-radar.md`; без аргумента → последняя нота.
  Нет нот → СТОП, сначала `/pulse-radar`. Выход: новые/additive-узлы NEXUS после одобрения PO.

## Важно

**Ревью-гейт обязателен.** Ничего не писать в NEXUS до явного выбора PO. Апдейты additive
(curated-текст не трогать). Новые узлы `confidence: 0.3`. Нет якоря — нет промоута. Идемпотентно.

## Инструкция для LLM

Запусти навык **`pulse-promote`** (`.claude/skills/pulse-promote/SKILL.md`):
1. Прочитай `.claude/domain-profile.md` → `po_name` + team-node-id PO (для `owner`/`owns_node`),
   `paths.pulse_radar_dir`.
2. Извлеки сигналы, примени фильтр устойчивости (`resources/promote_rules.md`), дедуп по NEXUS.
3. Напечатай список кандидатов (+ SKIP). Жди выбор PO. Запиши только одобренное. Отчёт.
````

- [ ] **Step 5: Verify — 4 команды, ссылаются на правильные скиллы, нет старых имён**

Run:
```bash
cd $PO
for c in chat-watch chat-sync pulse-radar pulse-promote; do test -f .claude/commands/$c.md || echo "MISSING $c"; done; echo "CMD_CHECK_DONE"
grep -rEl "link-radar|radar-promote" .claude/commands/pulse-radar.md .claude/commands/pulse-promote.md && echo "LEAK" || echo "CLEAN"
```
Expected: `CMD_CHECK_DONE` (без MISSING), `CLEAN`.

- [ ] **Step 6: Commit**

```bash
cd $PO
git add .claude/commands/chat-watch.md .claude/commands/chat-sync.md .claude/commands/pulse-radar.md .claude/commands/pulse-promote.md
git commit -m "feat(pulse): command-врапперы chat-watch/chat-sync/pulse-radar/pulse-promote"
```

---

### Task 7: domain-profile ключи + GROUND-скаффолд + install.sh + README

**Files:**
- Modify: `$PO/domain-profile.template.md` (секция `paths` + новая `info_sources`)
- Create: `$PO/GROUND/PULSE/radar/.gitkeep`, `$PO/GROUND/_intake/chats/.gitkeep`
- Create: `$PO/GROUND/_intake/chats/watched-chats.yaml` (шаблон-заготовка)
- Modify: `$PO/install.sh` (скаффолд PULSE/radar + _intake/chats; заметка про адаптер)
- Modify: `$PO/README.md` (строка таблицы фич)

- [ ] **Step 1: Ключи в domain-profile.template.md**

В `$PO/domain-profile.template.md`, в блоке `paths:` (после строки `meeting_notes: "GROUND/PULSE/meetings"`), добавить перед закрывающими ```` ``` ````:

```yaml
  # Pulse-радар (навык pulse-radar): датированные радар-ноты из чат-дампов
  pulse_radar_dir: "GROUND/PULSE/radar"
```

И добавить новую секцию сразу после блока `paths` (перед `## 1a. Планнер PO`):

````markdown
## 1b. Источники чатов (info_sources)

Откуда `/chat-sync` берёт сообщения. Пусто → ручной drop дампов по контракту
(`.claude/skills/chat-sync/resources/chat_dump_contract.md`).

```yaml
info_sources:
  # адаптер выгрузки чатов; "" → ручной режим. Референс-адаптер: tools/adapters/mts-link (opt-in)
  chat_adapter: ""
  # куда адаптер пишет дампы (вход /pulse-radar)
  chat_intake_dir: "GROUND/_intake/chats"
```

---
````

- [ ] **Step 2: GROUND-скаффолд + шаблон реестра**

Run:
```bash
cd $PO
mkdir -p GROUND/PULSE/radar GROUND/_intake/chats
touch GROUND/PULSE/radar/.gitkeep GROUND/_intake/chats/.gitkeep
```

Записать `$PO/GROUND/_intake/chats/watched-chats.yaml`:

```yaml
# Реестр отслеживаемых чатов (заполняется через /chat-watch, можно править руками).
# Одна запись = один чат. Поле source различает источники при мультиисточнике.
# Пример (удали при заполнении):
# - chat-id: "example-123"
#   name: "Чат «Платежи»"
#   source: "MTS Link"
#   purpose: "следить за инцидентами платежей"
#   extract: "блокеры, эскалации, решения"
watched: []
```

- [ ] **Step 3: install.sh — скаффолд каталогов Pulse**

В `$PO/install.sh`, внутри функции `adapt_backlog_init` (или рядом, после блока `mkdir -p "$TARGET/backlog/docs"`), добавить перед `}` функции:

```bash
  # Pulse-pipeline: каталоги радара и intake чатов
  mkdir -p "$TARGET/GROUND/PULSE/radar" "$TARGET/GROUND/_intake/chats"
```

И в финальный отчёт (после строки `echo "   2) Reload Window в IDE ..."`) добавить:

```bash
  echo "   3) (опц.) чат-адаптер: tools/adapters/mts-link — npm install && npm run login (не ставится авто)"
```

- [ ] **Step 4: README — строка таблицы фич**

В `$PO/README.md` вставить после строки `**Инфо-каналы**` (строка с `/channel-route`) новую строку таблицы:

```markdown
| **Pulse-радар чатов** | `/chat-watch` · `/chat-sync` · `/pulse-radar` · `/pulse-promote` | Оперативные сигналы из чатов: реестр слежки → выгрузка через source-адаптер (MTS.Link opt-in) → датированная радар-нота «что горит» с привязкой к KR → промоут устойчивых сигналов в NEXUS через ревью-гейт | [SKILL](.claude/skills/pulse-radar/SKILL.md) |
```

- [ ] **Step 5: Verify**

Run:
```bash
cd $PO
grep -q "pulse_radar_dir" domain-profile.template.md && grep -q "info_sources:" domain-profile.template.md && echo "PROFILE_OK"
test -f GROUND/_intake/chats/watched-chats.yaml && test -f GROUND/PULSE/radar/.gitkeep && echo "SCAFFOLD_OK"
grep -q "GROUND/PULSE/radar" install.sh && echo "INSTALL_OK"
grep -q "Pulse-радар чатов" README.md && echo "README_OK"
bash -n install.sh && echo "INSTALL_SYNTAX_OK"
```
Expected: `PROFILE_OK`, `SCAFFOLD_OK`, `INSTALL_OK`, `README_OK`, `INSTALL_SYNTAX_OK`.

- [ ] **Step 6: Commit**

```bash
cd $PO
git add domain-profile.template.md install.sh README.md GROUND/PULSE/radar/.gitkeep GROUND/_intake/chats/.gitkeep GROUND/_intake/chats/watched-chats.yaml
git commit -m "feat(pulse): domain-profile ключи + GROUND-скаффолд + install.sh + README"
```

---

### Task 8: pytest lint-гейт + install dry-run (финальная верификация)

**Files:**
- Create: `$PO/sa_documentation/tests/test_pulse_pipeline_lint.py`

**Interfaces:**
- Consumes: все портированные файлы (Tasks 1–7). Кодирует grep-гейт §9 спеки.

- [ ] **Step 1: Написать падающий тест (TDD RED)**

Записать `$PO/sa_documentation/tests/test_pulse_pipeline_lint.py`:

```python
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILLS = REPO / ".claude/skills"
CMDS = REPO / ".claude/commands"

PULSE_SKILLS = ["chat-watch", "chat-sync", "pulse-radar", "pulse-promote"]
FORBIDDEN = ["link-radar", "radar-promote", "mts-po-workspace",
             "Ишманов", "team-ishmanov-aleksej", "Парфило", "GDS Daily"]


def _skill_files():
    for s in PULSE_SKILLS:
        for p in (SKILLS / s).rglob("*.md"):
            yield p


def test_all_pulse_skills_present():
    for s in PULSE_SKILLS:
        assert (SKILLS / s / "SKILL.md").is_file(), f"нет скилла {s}"


def test_all_pulse_commands_present():
    for c in PULSE_SKILLS:
        assert (CMDS / f"{c}.md").is_file(), f"нет команды {c}"


def test_no_forbidden_tokens_in_pulse_skills():
    hits = []
    for p in _skill_files():
        text = p.read_text(encoding="utf-8")
        for tok in FORBIDDEN:
            if tok in text:
                hits.append(f"{p.relative_to(REPO)}: {tok}")
    assert not hits, f"запрещённые токены: {hits}"


def test_contract_defines_chat_dump():
    contract = SKILLS / "chat-sync/resources/chat_dump_contract.md"
    assert contract.is_file()
    assert "type: chat-dump" in contract.read_text(encoding="utf-8")


def test_no_absolute_tools_path_outside_adapter():
    # ~/tools и ~/.mts-link-sync допустимы только внутри tools/adapters/mts-link/
    hits = []
    for p in _skill_files():
        text = p.read_text(encoding="utf-8")
        if "~/tools" in text or "~/.mts-link-sync" in text:
            hits.append(str(p.relative_to(REPO)))
    assert not hits, f"абсолютные ~/tools-пути в скиллах: {hits}"
```

- [ ] **Step 2: Запустить тест — до Task 1–7 упал бы; сейчас должен пройти**

Run:
```bash
cd $PO && python -m pytest sa_documentation/tests/test_pulse_pipeline_lint.py -v
```
Expected: 5 passed. Если что-то FAIL — вернуться и починить остаточный токен/файл в соответствующем скилле (не подавлять тест).

- [ ] **Step 3: install.sh dry-run в temp-таргет (скиллы+команды копируются)**

Run:
```bash
cd $PO
TMP="$(mktemp -d)"
bash install.sh "$TMP" 2>&1 | tail -20 || true
ls "$TMP/.claude/skills" | grep -E "chat-watch|chat-sync|pulse-radar|pulse-promote" && echo "SKILLS_INSTALLED"
ls "$TMP/.claude/commands" | grep -E "pulse-radar|pulse-promote" && echo "CMDS_INSTALLED"
test -d "$TMP/GROUND/PULSE/radar" && echo "RADAR_SCAFFOLD_OK"
rm -rf "$TMP"
```
Expected: `SKILLS_INSTALLED`, `CMDS_INSTALLED`, `RADAR_SCAFFOLD_OK`.
(Если у `install.sh` иная сигнатура запуска — свериться с его `usage`/первыми строками и вызвать в dry/target-режиме, не меняя логику.)

- [ ] **Step 4: Полный прогон тестов (без регрессий)**

Run:
```bash
cd $PO && python -m pytest sa_documentation/tests/ -q
```
Expected: всё зелёное (новый файл + существующие не сломаны).

- [ ] **Step 5: Commit**

```bash
cd $PO
git add sa_documentation/tests/test_pulse_pipeline_lint.py
git commit -m "test(pulse): lint-гейт цепочки (файлы + запрещённые токены + контракт)"
```

---

## Итоговая верификация (после Task 8)

```bash
cd $PO
git log --oneline origin/main..HEAD          # 8 коммитов
git status --porcelain                        # чисто, нет секретов/node_modules
python -m pytest sa_documentation/tests/ -q   # зелёно
```

Дальше: PR в po-helper против `main` (`gh pr create`) — по готовности PO.
