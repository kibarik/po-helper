---
name: paf-nexus-create
description: "Создаёт кастомный Нексус под решение клиента (sellers, buyers, team, …): интервью → GROUND/NEXUS/<slug>/ + запись в _registry.yaml. Знает каталожные опц. типы (team/ops-model/company) и засевает team из roster, landscape — из domain-profile.landscape.ext_teams."
---

# /paf-nexus-create — создание кастомного Нексуса

Skill коробки «PAF Team OS». Добавляет Нексус сверх дефолтного минимума (`/paf-init` создал market/customer/product/growth). Два режима:

1. **Каталожный опц. тип** (`team`, `ops-model`, `company`) — берёт готовое определение из `sa_documentation/nexus_catalog.md` §4/§4.1, не выдумывает.
2. **Свежий кастом** (`sellers`, `buyers`, `supply-chain`, …) — интервью под решение клиента.

> Пошаговый план для LLM. Выполняй по порядку. Читай файлы перед записью. Ноль выдуманной PAF-терминологии вне `sa_documentation/naming_conventions.md`.

## 0. Контекст (прочитать перед стартом)

- `sa_documentation/nexus_catalog.md` — мастер-каталог. §2 таблица типов; §4 опц. PAF-типы; **§4.1 — полная спецификация `team`** (schema_extensions, seed_questions, пример person-узла).
- `sa_documentation/nexus_schema.md` — Node schema (§2 ключи, §3 `node_type` включая `person`, §4 wilting).
- `sa_documentation/ground_schema.md` — schema `_registry.yaml` (§«_registry.yaml»: slug `[a-z][a-z0-9-]*`, source, owner, purpose, onboarded).
- `GROUND/config.yaml` — `team.roster` (источник людей для засева `team`), `nexus.custom_count`.
- `GROUND/NEXUS/_registry.yaml` — текущий реестр (проверка уникальности slug).

---

## 1. Предусловия

- `GROUND/config.yaml` существует (иначе → сначала `/paf-init`).
- Если нет — останови и подскажи запустить `/paf-init`.

---

## 2. Интервью (по одному вопросу)

1. **Какой Нексус создаём?** — slug (ascii, паттерн `[a-z][a-z0-9-]*`). Помоги транслитерировать кириллицу.
2. **Определи режим:**
   - slug ∈ {`team`, `ops-model`, `company`} → **каталожный режим** (§3). Подтверди клиенту: «Беру определение из мастер-каталога».
   - slug = `landscape` → **кастомный режим (§4) с засевом из domain-profile** (§4.1). Тип определён в po-helper, не в мастер-каталоге.
   - иначе → **кастомный режим** (§4).

---

## 3. Каталожный режим (team / ops-model / company)

Прочитай определение типа из `nexus_catalog.md`:
- `name`, `purpose`, `owner_role`, `seed_questions`, `schema_extensions` — **из каталога, не выдумывай**.
- `owner` — резолвь `owner_role` → конкретное имя из `config.yaml team.roster`; если роль не назначена (null) → `"Cortex"`.

### 3.1 Спец-обработка `team` — засев person-узлов из roster

`team` — People Graph (`node_type: person`, см. каталог §4.1). Roster уже содержит людей по ролям → засей по узлу на каждого **именованного** человека (не `"Cortex"`, не `null`):

Для каждой записи `team.roster.<role>: <Имя>` (где `<Имя>` ≠ `"Cortex"`/null):
1. `node_id` = `team-<translit(фамилия-имя)>` (ascii, `[a-z][a-z0-9-]*`). Если в roster только имя — `team-<translit(имя)>`, пометь в теле «уточнить ФИО».
2. Создай заготовку person-узла по шаблону `GROUND/NEXUS/team/_template.md`, заполнив из roster:
   - `full_name` = значение из roster (как есть; уточнить полное ФИО при онбординге).
   - `role_title` = человекочитаемое имя роли (`product_engineer` → "Product Engineer" по `naming_conventions.md`).
   - `reports_to` / `manages` / `collaborates_with` = `[]` или `null` (**не угадывать иерархию** — заполнит человек/онбординг).
   - `influence_zones` / `expertise_topics` / `contact_for` = `[]` с пометкой в теле «заполнить в онбординге».
   - `confidence: 0.3` (допущение из roster, не валидировано); `sources: ["config.yaml:roster"]`; `ttl_days: 180`.
3. Пометь тело: `> ⚠️ заготовка из roster. ФИО/связи/экспертиза требуют наполнения (/paf-onboard или вручную).`

> **Roster = источник истины по ролям; team-нексус = богатый профиль.** Засев устраняет двойной ввод, но НЕ выдумывает данные сверх roster. Если roster пуст (все Cortex/null) — создай только `_index.md`, узлы добавит клиент.

> **Гвардраил:** не выдумывай `reports_to`/`collaborates_with`/экспертизу из размера команды или ролей. Эти поля — `[]` до явного ввода. Узел без `sources[]` не создавать (тут source = `config.yaml:roster`).

---

## 4. Кастомный режим (свежий тип)

Интервью (по очереди):
1. **name** — человекочитаемое имя («Нексус продавцов»).
2. **purpose** — назначение в 1–2 предложениях.
3. **owner** — из `config.yaml team.roster` (имя). Если нужной роли нет → `"Cortex"` или null.
4. **seed_questions** — 3–5 вопросов для будущего онбординга (как в каталоге §3).
5. **(опц.) paf_step** — привязка к шагу 0–8 или null.
6. **(опц.) schema_extensions** — тип-специфичные поля поверх базовой Node schema (напр. `quota_attainment` для sellers). Формат — как в `nexus_schema.md` §2.1.

---

### 4.1 Спец-обработка `landscape` — засев из domain-profile

`landscape` — Нексус команд вокруг PO (`node_type: ext-team`; шаблон и `_index.md` уже есть в дистрибутиве `GROUND/NEXUS/landscape/`). Определение (не из мастер-каталога):
- `name`: «Нексус ландшафта»; `purpose`: «Команды вокруг PO — миссия, PO, системы, тип связи, точки касания»; `owner`: из `config.yaml team.roster` (роль Product Ops) или `"Cortex"`.
- `seed_questions` — из существующего `GROUND/NEXUS/landscape/_index.md` (не выдумывай).

**Засев ext-team узлов** из `.claude/domain-profile.md` секции `landscape.ext_teams` (аналог team-from-roster, источник другой):

Для каждой записи `landscape.ext_teams[]` (`{code, name, po, relationship}`):
1. `node_id` = `landscape-team-<translit(name)>` (ascii, `[a-z][a-z0-9-]*`).
2. Создай заготовку по шаблону `GROUND/NEXUS/landscape/_template.md`, заполнив из профиля:
   - `team_name` = `name`; `po_name` = `po`; `relationship` = `relationship` (или `peer`, если пусто).
   - `owned_systems` / `touchpoints` / `influence` / `mission` — `[]`/пусто с пометкой «заполнить в /okr-landscape» (**не угадывать** системы/стыки).
   - `confidence: 0.3`; `sources: ["domain-profile:landscape.ext_teams"]`; `ttl_days: 180`; `updated` = сегодня.
3. Пометь тело: `> ⚠️ заготовка из domain-profile. Системы/стыки/влияние наполняет /okr-landscape.`

> **domain-profile = источник ролей команд; landscape-нексус = богатый профиль.** Засев устраняет двойной ввод, но НЕ выдумывает данные сверх профиля. Секция `landscape.ext_teams` пуста → создай только `_index.md` (уже есть), узлы добавит `/okr-landscape`. Узел без `sources[]` не создавать.

---

## 5. Генерация файлов

Дата `updated` = сегодня (ISO). Все пути от корня репо.

### 5.1 Папка Нексуса `GROUND/NEXUS/<slug>/`

- `_index.md` — placeholder-MOC (frontmatter по `nexus_schema.md` §2.2 empirical: `node_type: step-overview`, `kind: empirical`, `confidence: 0.3`, `sources: []`, `ttl_days` по типу, `tags: [nexus-index, onboarding]`). В теле — `purpose`, таблица слоёв (для `team` скопируй из каталога §4.1), `seed_questions`, секция «Узлы».
- Для каталожных типов с шаблоном (`team`) — убедись, что `_template.md` присутствует (если нет — создай из каталога §4.1).
- Для `team` — создай засеянные person-узлы (§3.1).

### 5.2 Регистрация в `GROUND/NEXUS/_registry.yaml`

Добавь запись (не дублируй, если slug уже есть — см. §6):
```yaml
  - {slug: <slug>, source: custom, name: <name>, owner: <owner из roster>, purpose: "<purpose>", onboarded: todo}
```

### 5.3 Обнови `GROUND/NEXUS/_index.md`

Добавь ссылку в раздел «Кастомные Нексусы»: `- [<slug>](<slug>/) — <краткое назначение>.`

### 5.4 Обнови `GROUND/config.yaml`

Инкремент `nexus.custom_count` на 1.

---

## 6. Verify

```bash
python3 sa_documentation/validate_ground.py GROUND
```

- Ожидается `OK`. Частые ошибки: невалидный `slug` (заглавные/кириллица), `source` ≠ default|custom.
- person-узлы `team` валидатор сейчас не проверяет на уровне frontmatter — визуально убедись: у каждого есть `sources[]`, `node_type: person`, обязательные `full_name`/`role_title`.
- Не заканчивай, пока валидатор не вернёт `OK`.

---

## 7. Гвардраилы

- **Slug уникален.** Если уже в `_registry.yaml` — предупреди, предложи: обновить существующий / отменить. Дефолт — отменить. Не дублируй записи/папки.
- **Конфликт с мастер-каталогом.** Если slug совпадает с дефолтным минимумом (`market`/`customer`/`product`/`growth`) — предупреди (он уже создан `/paf-init`), не пересоздавай.
- **owner из roster.** В `_registry.yaml` и узлах `owner` — из `team.roster`. Роль не назначена → `"Cortex"`.
- **Каталог read-only.** `nexus_catalog.md` НЕ правь — только читай определения. Кастомные типы живут в `_registry.yaml`, не в каталоге.
- **Ноль выдуманных данных.** `team`: не угадывай иерархию/экспертизу. Все непровалидированные поля — `[]`/`null` + пометка «онбординг». Узел без `sources[]` = workslop, не создавать.
- **Ноль выдуманного PAF.** Термины только из `naming_conventions.md`.

---

## 8. Финал

```
Нексус <slug> создан (source: custom).
- GROUND/NEXUS/<slug>/_index.md + (team: N заготовок person-узлов из roster).
- _registry.yaml: +1 запись (onboarded: todo). config.yaml: custom_count → <N>.
- Валидатор: OK.

→ /paf-onboard — наполнить узлы (интервью + ингестия). Для team: уточнить ФИО, связи (reports_to/collaborates_with), зоны влияния и экспертизу.
```

---

## 9. Связи

- [[sa_documentation/nexus_catalog]] — определения типов (§4.1 team).
- [[sa_documentation/nexus_schema]] — Node schema (§3 node_type: person).
- [[sa_documentation/ground_schema]] — schema _registry.yaml.
- `/paf-init` — дефолтный минимум (предшествует). `/paf-onboard` — наполнение узлов (следует).
