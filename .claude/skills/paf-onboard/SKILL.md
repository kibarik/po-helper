---
name: paf-onboard
description: "Цифровизация контекста клиента по ВСЕМУ реестру Нексусов: ингестия доков из GROUND/_intake/ + интервью по seed_questions → low-CP узлы + readiness-отчёт. Repeatable, idempotent. Запусти после /paf-init (и /paf-nexus-create, если есть кастомные)."
---

# /paf-onboard — цифровизация контекста (главное; repeatable)

Skill коробки «PAF Team OS». Наполняет GROUND Vault контекстом клиента по **всем** Нексусам реестра (`GROUND/NEXUS/_registry.yaml` — дефолт + кастом): ингестия документов + интервью по пробелам → узлы как **low-CP допущения** (`confidence: 0.2–0.4`). Без этого Нексусы пустые, Context Ripeness ≈ 0 и Steps 1–8 не открываются.

> Пошаговый план для LLM. Выполняй по порядку. Читай перечисленные файлы перед записью. Онбординг **цифровизует, не валидирует** — допущения не выдавать за факты. Ноль выдуманной PAF-терминологии вне `sa_documentation/naming_conventions.md`. Узел без `sources[]` = workslop, не создавать.

## 0. Контекст (прочитать перед стартом)

- `sa_documentation/nexus_schema.md` — Node schema (§2 ключи; §2.2 empirical-узлы клиента: `sources`, low-CP, `ttl_days`; §4 формула Context Ripeness).
- `sa_documentation/nexus_catalog.md` — `seed_questions` дефолтных типов (§3) и опц. типов (§4) для интервью Phase B.
- `sa_documentation/ground_schema.md` — поля `onboarding.*` в `config.yaml` и `nexus_types[].onboarded` в `_registry.yaml`.
- `GROUND/config.yaml` — `team.roster` (owner'ы), `cortex.ruflo_mcp` (дедуп через memory_search или Grep), `onboarding.*` (текущий статус).
- `GROUND/NEXUS/_registry.yaml` — **полный** реестр Нексусов клиента (источник списка для всех фаз).
- Для кастомных Нексусов `seed_questions` берутся из их `_index.md` (записаны `/paf-nexus-create`), а не из каталога.

---

## 1. Предусловия

- `GROUND/config.yaml` существует. Если нет — останови и подскажи запустить `/paf-init`.
- Прочитай `GROUND/NEXUS/_registry.yaml` → список `nexus_types[]`. Работаешь по **каждому** (дефолт + кастом), не только по дефолтным 4.
- Прочитай `onboarding.status` из `config.yaml`. Если `done` — это **пере-онбординг**: предупреди, что пройдёшь idempotent (дедуп + upsert, не дублируя узлы), и продолжай только с согласия.
- Установи `onboarding.status: in_progress` в `config.yaml` в начале прогона.

---

## 2. Phase A — ингестия доков (`GROUND/_intake/`)

Цель: превратить материалы клиента в узлы Нексусов.

1. **Собери источники.** Перечисли файлы в `GROUND/_intake/` (md/txt/pdf-выжимки/выгрузки). Если папка пуста — сообщи и переходи к Phase B (интервью), пометив `sources_ingested: []`.
2. **Для каждого документа:**
   - Прочитай и извлеки факты/допущения, релевантные seed_questions Нексусов реестра.
   - Отнеси каждый факт к Нексусу по смыслу (сегменты/JTBD → `customer`; конкуренты/объём → `market`; идея/фичи/Vision → `product`; каналы/монетизация/COGS → `growth`; кастом — по его `purpose`).
   - Создай/обнови узел с `sources: ["onboarding:<имя-файла-без-расширения>"]`.
3. **Дедуп (idempotent).** Перед записью проверь, нет ли уже узла на этот же факт:
   - если `cortex.ruflo_mcp: true` → `mcp__ruflo__memory_search` по ключевым словам;
   - иначе → `Grep` по `GROUND/NEXUS/<slug>/`.
   - Совпадение → **upsert** (дополни существующий узел, добавь источник в `sources[]`, обнови `updated`), не плоди дубль.
4. Записывай в `onboarding.sources_ingested` имя каждого обработанного источника.

> Где живёт узел: см. §4 (формат узла). Каждый узел Phase A — `kind: empirical`, low-CP, с пометкой-допущением.

---

## 3. Phase B — интервью по пробелам

Цель: закрыть seed_questions, на которые доки не ответили. По **каждому** Нексусу реестра.

1. Для каждого `nexus_types[]`:
   - возьми `seed_questions`: для дефолтных — из `nexus_catalog.md` §3; для опц. каталожных (`team`/`ops-model`/`company`) — §4; для кастомных — из секции «seed_questions» в `GROUND/NEXUS/<slug>/_index.md`.
   - отметь, какие вопросы уже закрыты узлами Phase A (не переспрашивай — покажи, что нашёл, и спроси только уточнение при необходимости).
2. **Задавай по одному вопросу за раз**, фиксируя ответ. Не угадывай — переспрашивай при неоднозначности. Клиент может ответить «не знаю / нет данных» — это валидно: фиксируй пробел (узел не создаём), он попадёт в карту пробелов Phase D.
3. Ответ → узел с `sources: ["onboarding:interview"]`. Дедуп так же, как в §2.3 (upsert поверх Phase A, если тема пересекается).
4. **`team`-Нексус:** не интервьюируй заново ФИО/роли (они засеяны из roster `/paf-nexus-create`) — уточняй полное ФИО, `reports_to`/`collaborates_with`, зоны влияния и экспертизу для уже существующих person-узлов.

---

## 4. Формат узла (Phase A и B)

Узлы контекста живут в папке своего Нексуса: `GROUND/NEXUS/<slug>/<node_id>.md`. Frontmatter — по `nexus_schema.md` §2 + §2.2 (empirical):

```yaml
---
nexus: <slug>                 # из реестра
node_id: <slug>-<тема>        # ascii [a-z0-9-], напр. customer-segments
node_type: step-overview      # person — только для team (см. nexus_catalog §4.1); иначе step-overview
paf_step: <paf_step_ref типа или null>
sprint_phase: null
kind: empirical               # контекст клиента, не методология
owner: <из roster по owner_role; роль не назначена → "Cortex">
confidence: 0.3               # low-CP допущение онбординга (0.2–0.4); НЕ выше
sources: ["onboarding:<doc>"] # или ["onboarding:interview"]; узел без sources не создавать
updated: <YYYY-MM-DD>         # сегодня
ttl_days: <по типу>           # market/customer/product = 90, growth = 60
ripeness: fresh               # updated = сегодня → fresh
tags: [onboarding, <slug>]
---

# <Короткий заголовок факта/темы>

<1–3 абзаца: что оцифровали, с привязкой к seed_question.>

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
```

- `ttl_days` по `nexus_schema.md` §2.2: `growth` = 60; остальные empirical = 90.
- `confidence` — строго 0.2–0.4. Поднимать CP — задача Steps 1–8 (валидация/эксперименты), не онбординга.
- Параллельно **обнови `_index.md`** каждого Нексуса: в секции seed_questions проставь ссылки на закрывшие их узлы (MOC растёт → completeness растёт).
- Не создавай узел-«воду»: если факт тривиален или без источника — не плоди узел, зафиксируй пробел.

---

## 5. Phase C — verify + CP + статусы реестра

1. **CP-дисциплина.** Пройди созданные/обновлённые узлы: `confidence` в диапазоне 0.2–0.4, `sources[]` не пуст, пометка-допущение на месте. Узел без источника — удали или верни в пробелы. Это anti-workslop гейт.
2. **`_registry.yaml` — статус `onboarded` по каждому Нексусу:**
   - `done` — все его seed_questions закрыты узлами (из доков и/или интервью);
   - `partial` — закрыта часть;
   - `todo` — не тронут (нет ни доков, ни ответов).
3. **`config.yaml` — блок `onboarding`:** `sources_ingested` (из Phase A), `baseline_cr` (карта Context Ripeness из Phase D, см. ниже), `status: done` если хотя бы один Нексус вышел из `todo`, иначе оставь `in_progress`; `onboarded_at: <сегодня>` при `done`.

---

## 6. Phase D — readiness-отчёт

1. **Посчитай Context Ripeness** по каждому Нексусу (формула `nexus_schema.md` §4):
   - `completeness = (узлы с заполненными обязательными полями) / (всего узлов Нексуса)`;
   - `freshness = weighted_mean(clamp(1 − age/ttl_days, 0, 1), weight=confidence)`; для свежего онбординга ≈ 1.0;
   - `CR = completeness × freshness`.
   - Пустой Нексус (0 узлов) → CR = 0.
2. Запиши карту CR в `config.yaml onboarding.baseline_cr` (`{<slug>: <CR>, ...}`).
3. **Карта пробелов:** перечисли незакрытые seed_questions по Нексусам (что спросить/найти дальше).
4. **Top low-CP:** узлы с самым низким `confidence` — кандидаты №1 на валидацию в Steps 1–8.

---

## 7. Verify

```bash
python3 sa_documentation/validate_ground.py GROUND
```

- Ожидается `OK`. Если ошибки (чаще: невалидный `slug` в реестре, `source` ≠ default|custom) — исправь и перезапусти.
- Визуально проверь созданные узлы: у каждого `sources[]` не пуст, `confidence` 0.2–0.4, `kind: empirical`, пометка-допущение.
- Не заканчивай скилл, пока валидатор не вернёт `OK`.

---

## 8. Гвардраилы

- **Цифровизует, не валидирует.** Не выдавать допущения за факты. CP строго 0.2–0.4 — поднимают Steps 1–8.
- **Ноль галлюцинаций.** Узел без `sources[]` = workslop, не создавать. Источник — только реальный (`onboarding:<doc>` из `_intake/` или `onboarding:interview`).
- **Idempotent / repeatable.** Дедуп перед записью (ruflo memory_search или Grep) → upsert, не дубль. Пере-онбординг не затирает контекст — дополняет.
- **Весь реестр.** Обрабатывай каждый `nexus_types[]` (дефолт + кастом), а не фиксированные 4.
- **owner из roster.** В узлах `owner` — из `team.roster` по `owner_role`; роль не назначена → `"Cortex"`.
- **team — не выдумывать связи.** ФИО/иерархия/экспертиза только из явного ввода клиента; неизвестное — `[]`/`null` + пометка.
- **Каталог read-only.** `nexus_catalog.md`/`nexus_schema.md` не править — только читать.
- **Ноль выдуманного PAF.** Термины только из `naming_conventions.md`.

---

## 9. Финал (readiness-строка)

После `OK` валидатора выведи:

```
GROUND Vault наполнен (онбординг).
- Источники: <N> доков из _intake/ + интервью по <M> Нексусам.
- Узлы: <K> создано/обновлено (CP 0.2–0.4, kind: empirical).
- Статусы реестра: <slug: done|partial|todo, ...>.
- Валидатор: OK.

Context Ripeness (baseline):
  <slug>: <CR>   ...
Карта пробелов: <незакрытые seed_questions по Нексусам>.
Top low-CP на валидацию: <узлы>.

Readiness: <LOW|MEDIUM|HIGH> — порог перехода Context Ripeness ≥ 0.6 (fit-points).
→ Steps 1–8 ВАЛИДИРУЮТ допущения и поднимают CP над насыщенным GROUND Nexus.
→ Повторный /paf-onboard — когда добавите доки в _intake/ или создадите кастомный Нексус (/paf-nexus-create).
```

---

## 10. Связи

- [[sa_documentation/nexus_schema]] — Node schema (§2.2 empirical, §4 Context Ripeness).
- [[sa_documentation/nexus_catalog]] — seed_questions дефолтных/опц. типов.
- [[sa_documentation/ground_schema]] — поля `onboarding.*` и `onboarded`.
- [[sa_documentation/naming_conventions]] — термины PAF.
- `/paf-init` — создаёт реестр (предшествует). `/paf-nexus-create` — кастомные Нексусы (онбордятся здесь же).
