# Перенос Pulse-pipeline (чаты → радар → промоут) в po-helper — дизайн

> Дата: 2026-07-13 · Автор: PO (Ишманов) + Claude · Статус: спека на ревью
> Контекст: цепочка разработана и обкатана в инстансе `mts-po-workspace` — скиллы
> `chat-watch → chat-sync → link-radar → radar-promote` + node-тул `tools/mts-link-chat-sync`.
> Задача — вынести generic-слой в фреймворк po-helper, чтобы любой пользователь получал
> pipeline «оперативные сигналы из чатов → радар-нота → промоут в NEXUS» через `install.sh`,
> без привязки к MTS.Link и к `mts-po-workspace`.

## 1. Цель

Дать любому проекту на po-helper цепочку курирования оперативного контекста PO:

```
chat-watch → chat-sync → /pulse-radar → /pulse-promote
 (реестр)    (ingest)    (радар-нота)   (промоут в NEXUS)
             ↑ adapter                  ↓
      tools/adapters/mts-link/     GROUND/NEXUS/*
```

- **chat-watch** — реестр отслеживаемых источников/чатов (`purpose`/`extract` на запись).
- **chat-sync** — обобщённый ingest: по реестру гонит **source-адаптер**, пишет чат-дампы в
  `GROUND/_intake/chats/` по **контракту**. MTS.Link — референс-адаптер, не единственный.
- **/pulse-radar** (был `link-radar`) — чат-дампы → датированная радар-нота в `GROUND/PULSE/radar/`.
- **/pulse-promote** (был `radar-promote`) — устойчивые сигналы радар-ноты → узлы `GROUND/NEXUS/*`
  через обязательный ревью-гейт (additive-only, CP=0.3 для новых, якорь чат·автор·время).

Механика скиллов проектно-нейтральна и переносится как есть. Платформенная привязка
(MTS.Link WS-протокол, SSO) изолирована в опциональном адаптере и не течёт в тела скиллов.

## 2. Что переносим / что нет

| Переносим (generic) | НЕ переносим (данные/инстанс) |
|---|---|
| 4 скилла: `chat-watch`, `chat-sync`, `pulse-radar`, `pulse-promote` | Реальные `watched-chats.yaml` MTS |
| 4 command-враппера `.claude/commands/` | Скачанные чат-дампы `GROUND/_intake/chats/*` |
| Контракт чат-дампа (resource-док) | Реальные радар-ноты `PULSE/radar/*` |
| node-тул как opt-in `tools/adapters/mts-link/` | `~/.mts-link-sync/auth.json` (SSO) |
| Обезличенные `examples/ideal_*` | `node_modules` адаптера (gitignore) |
| Ключи `domain-profile.template.md` | Привязки: конкретные чаты/люди/KR MTS |
| `transcript-sync` — **вне scope** (кормит `/summary`, не радар) | |

## 3. Упаковка в po-helper (конвенции фреймворка)

Следуем сложившейся структуре (skill + тонкая команда, как `summary`, `info-channels`).

```
.claude/skills/chat-watch/SKILL.md              реестр источников/чатов → watched-chats.yaml
.claude/skills/chat-sync/
  SKILL.md                                       ingest: резолв адаптера → дампы по контракту
  resources/chat_dump_contract.md                КОНТРАКТ (единый источник правды формата)
.claude/skills/pulse-radar/
  SKILL.md                                       чат-дампы → радар-нота
  resources/radar_format.md                      формат радар-ноты (секции 🔴🚧✅📈❗🔕)
  examples/ideal_radar.md                        обезличенный образец
.claude/skills/pulse-promote/
  SKILL.md                                       радар-нота → NEXUS через ревью-гейт
  resources/promote_rules.md                     фильтр устойчивости + шаблоны узлов
  examples/ideal_promotion.md                    обезличенный образец (кандидаты+узел+дифф)
.claude/commands/{chat-watch,chat-sync,pulse-radar,pulse-promote}.md   тонкие обёртки → invoke skill
tools/adapters/mts-link/                          opt-in node-тул (npm+SSO+Playwright)
```

`tools/` в po-helper раньше не было — создаётся. `install.sh` копирует только
`.claude/skills`+`.claude/commands`; `tools/adapters/*` **не** ставится авто (см. §7).

## 4. Контракт чат-дампа = интерфейс (стабильное ядро)

Один resource-док `chat-sync/resources/chat_dump_contract.md`. На него ссылаются
**и** `chat-sync` (спека выхода адаптера), **и** `pulse-radar` (спека входа). Единственный
источник правды формата — всё вниз по потоку знает контракт, не платформу.

- Файл: `GROUND/_intake/chats/YYYY-MM-DD..YYYY-MM-DD <chat>.md`
- Frontmatter: `type: chat-dump` (обобщено с `mts-chat`), `source:` (напр. `"MTS Link"`),
  `chat-id`, `window`, `purpose`, `extract`, `msg-count`
- Тело: реплики `Автор HH:MM: текст`, сгруппированы по дням; пустые чаты пропускаются

Изменение относительно оригинала: `type: mts-chat` → `type: chat-dump` + явное поле `source`.

## 5. Адаптер: контракт + бандл

- `tools/adapters/mts-link/` — node-тул (перенос из `tools/mts-link-chat-sync`). **Opt-in**:
  свои npm-deps, SSO (`~/.mts-link-sync/auth.json`), Playwright + WS. Read-only (не шлёт
  сообщений, не сбивает счётчики непрочитанного).
- `chat-sync` (скилл) обобщается: «запусти сконфигурированный source-адаптер и получи дампы
  по контракту §4; MTS.Link — референс в `tools/adapters/mts-link` (см. его README)». Флаги
  окна (`--days N` / `--from/--to`, дефолт 14 дней) — часть контракта вызова адаптера.
- Платформенная специфика (WS `v=`-версия протокола, `auth.json`, `npm run login`) уезжает
  в `tools/adapters/mts-link/README.md`, вон из тела скилла.
- `chat-watch` реестр получает поле `source:` на запись — несколько источников сосуществуют.
- Нет адаптера / пустой реестр → `chat-sync` инструктирует: либо `/chat-watch`, либо «положи
  дампы руками в `GROUND/_intake/chats/` по контракту».

## 6. Genericize тел скиллов (снять привязку к MTS/workspace)

1. Вычистить хардкод MTS.Link и абсолютные `~/tools`-пути из тел скиллов — оставить только
   в README адаптера. Домен-специфику брать из `.claude/domain-profile.md` и `GROUND/NEXUS/`,
   как остальные po-helper-скиллы (примеры в `examples/` помечены иллюстративными).
2. **Нейминг-миграция** (снимает коллизию с People Radar `/radar-calibrate|graph|review`):
   - `link-radar` → `pulse-radar`, `radar-promote` → `pulse-promote` (dir + `name:` + description + триггеры)
   - радар-нота `*-link-radar.md` → `*-pulse-radar.md`
   - кросс-ссылки: `link-radar/resources/radar_format.md` → `pulse-radar/…`; поле `source_note`;
     упоминания `/link-radar`→`/pulse-radar`, `/radar-promote`→`/pulse-promote` в телах и guardrails
   - People Radar (`/radar-*` = `nexus-calibration`) **не трогаем**
3. Сохранить guardrails `pulse-promote` без изменений по сути: ревью-гейт обязателен,
   additive-only, CP=0.3 для новых, идемпотентность (`already-promoted`), нет якоря — нет промоута.

## 7. Новые ключи / скаффолд / витрина

**`domain-profile.template.md`** — секция источников чатов (опц., пусто → manual-режим):

```yaml
info_sources:
  # активный адаптер выгрузки чатов; "" или отсутствие → ручной drop дампов
  chat_adapter: "mts-link"        # референс-адаптер в tools/adapters/mts-link
  chat_intake_dir: "{ground}/_intake/chats"
paths:
  pulse_radar_dir: "{ground}/PULSE/radar"   # датированные радар-ноты (автоген pulse-radar)
```

**GROUND-скаффолд:** `GROUND/PULSE/radar/.gitkeep`, `GROUND/_intake/chats/.gitkeep`
+ `GROUND/_intake/chats/watched-chats.yaml` (шаблон-заготовка с полем `source`).

**`README.md`:** строка про Pulse-pipeline в таблице фич
(`/chat-watch` · `/chat-sync` · `/pulse-radar` · `/pulse-promote`).

**`install.sh`:** ядро не меняется (skills/commands копируются авто). Добавить:
скаффолд `GROUND/PULSE/radar` + `GROUND/_intake/chats`; заметку в отчёт про opt-in адаптер
(`tools/adapters/mts-link` — поставить вручную: `npm install` + `npm run login`).

## 8. Границы

- `chat-sync`/адаптер строго **read-only** — не шлёт сообщений, не помечает прочитанным.
- `pulse-promote` не пишет в NEXUS до одобрения PO; апдейты additive; curated-текст не трогает.
- Промоутятся только устойчивые сигналы (new-problem / kr-risk-update / system-fact /
  ownership-fact); эфемерное (action-on-PO, разовые инциденты, 🔕, 📈) остаётся в радаре.
- `transcript-sync` и весь транскрипт-путь — вне scope.

## 9. Верификация

- `install.sh` dry-run в temp-таргет: 4 новых скилла + 4 команды на месте, счётчики сходятся.
- Grep-гейт (pytest в `tests/`): в портированных скиллах нет `link-radar`/`radar-promote`,
  нет `mts-po-workspace`, нет абсолютных `~/tools` (кроме `tools/adapters/mts-link/README.md`).
- Round-trip примеров: `pulse-radar/examples/ideal_radar.md` соответствует контракту §4;
  `pulse-promote/examples/ideal_promotion.md` ссылается на радар-ноту `*-pulse-radar.md`.
- Данные MTS не коммитятся (проверить `git status` перед коммитом; `node_modules` в `.gitignore`).

## 10. Решённые развилки

- **Scope:** вся цепочка (chat-watch+chat-sync+pulse-radar+pulse-promote), `chat-sync` абстрактный.
- **Адаптер:** контракт + бандленный opt-in MTS.Link-адаптер в `tools/adapters/mts-link`
  (не ставится `install.sh` авто; другие юзеры пишут свой адаптер под контракт или кладут дампы руками).
- **Нейминг:** `pulse-*` (ложится на `GROUND/PULSE`, снимает коллизию с People Radar).
- **transcript-sync:** вне scope.
- **Цель PR:** po-helper upstream (раздача через `install.sh`), не workspace.
- **Ветка:** `feat/pulse-pipeline-port` от `origin/main` (создана).
