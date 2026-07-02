---
name: paf-init
description: "Первоначальная настройка GROUND Vault: интервью → config.yaml + дефолтный каталог Нексусов. One-shot. Запусти после git clone."
---

# /paf-init — первоначальная настройка GROUND Vault

One-shot-скилл коробки «PAF Team OS». Интервьюирует клиента → генерирует `GROUND/config.yaml` и дефолтный минимум Нексусов из `sa_documentation/nexus_catalog.md`. Запускается один раз после `git clone`.

> Это пошаговый план для LLM. Выполняй шаги по порядку. Читай перечисленные файлы перед записью. Не выдумывай PAF-терминологию вне `sa_documentation/naming_conventions.md`.

## 0. Контекст (прочитать перед стартом)

- `sa_documentation/ground_schema.md` — полная schema `config.yaml` + `_registry.yaml` (поля, правила, валидный пример).
- `sa_documentation/nexus_catalog.md` — дефолтный минимум базового шаблона из 5 Нексусов (§3): `customer`, `market`, `product`, `growth` (4 стратегических PAF) + `project-management` (обязательный операционный Нексус PO — delivery map) (их `seed_questions`, `owner_role`, `paf_step_ref`).
- `sa_documentation/nexus_schema.md` — Node schema для placeholder-нот `_index.md` (§2.2 empirical узлы онбординга).
- `sa_documentation/naming_conventions.md` — термины PAF (Банч, Product Engineer, скаутинг, риски, Comb-shaped).

---

## 1. Когда запускать

- Сразу после `git clone` коробки, **один раз**.
- Признак «ещё не инициализировано»: отсутствует `GROUND/config.yaml`.
- Если `GROUND/config.yaml` уже существует — **не затирать без явного подтверждения пользователя** (см. гвардраилы §6).

---

## 2. Интервью (по очереди, один вопрос за раз)

Задавай вопросы последовательно, фиксируя ответы. Не угадывай — переспрашивай, если ответ неоднозначен.

1. **Компания** — название компании клиента.
2. **Продукт** — три подпункта:
   - имя продукта;
   - **ascii-slug** (`[a-z0-9][a-z0-9-]*`, без пробелов/кириллицы/заглавных; напр. `acme-billing`) — если клиент дал кириллицу/пробелы, помоги транслитерировать и предложи валидный вариант;
   - elevator pitch (идея в 1–2 предложениях → пойдёт в `product.idea`).
3. **Размер команды** — целое число (`team.size`).
4. **Кто Product Engineer?** — **ОБЯЗАТЕЛЕН**. Значение — имя человека. Это `team.roster.product_engineer`; не может быть null/пустым (валидатор это требует). Если у клиента нет такой роли — объясни, что PAF её требует, и попроси назначить.
5. **(Опц.) Другие роли roster'а** — для каждой невыбранной роли предложи: имя человека **или** строка `"Cortex"` (делегировано Кортексу), **или** `null` (роль не назначена):
   - `product_ops`, `growth_engineer`, `portfolio_manager`, `discovery_launcher_pm`, `ai_ux_designer`.
6. **Целевая Cortex-фаза** — 1 / 2 / 3 (по умолчанию 2). Пойдёт в `cortex.phase_target`.
7. **(Опц.) Документы для онбординга** — есть ли уже материалы, которые клиент готов положить в `GROUND/_intake/`? Если да — `/paf-onboard` их ингестирует позже. Здесь только фиксируем факт.

---

## 3. Detect ruflo MCP

Проверь доступность ruflo MCP — это влияет на `cortex.ruflo_mcp` и на то, как `/paf-onboard` будет делать дедуп/индексацию.

- Попробуй вызвать `mcp__ruflo__memory_stats`.
- Если вызов успешен → `cortex.ruflo_mcp: true`.
- Если инструмент недоступен / ошибка → `cortex.ruflo_mcp: false`.

> Не падай при отсутствии ruflo — коробка работает и без него (Grep вместо memory_search).

---

## 4. Генерация файлов

Все пути — относительно корня репо. Дата `created` = сегодня (ISO `YYYY-MM-DD`).

### 4.1 `GROUND/config.yaml`

По schema `sa_documentation/ground_schema.md` (§«Валидный пример»). Поля:

```yaml
company: <из интервью>
product:
  name: <из интервью>
  slug: <ascii-slug из интервью>      # ОБЯЗАТЕЛЕН, паттерн [a-z0-9][a-z0-9-]*
  idea: <elevator pitch>
team:
  size: <int>
  roster:
    product_engineer: <ИМЯ>            # ОБЯЗАТЕЛЕН, не null/пусто
    # остальные роли — из интервью или null
cortex:
  phase_target: <1|2|3>
  ruflo_mcp: <true|false>             # из §3
  obsidian: true                       # markdown frontmatter-режим
onboarding:
  status: init                         # init | in_progress | done
  sources_ingested: []
  baseline_cr: {}
  onboarded_at: null
nexus:
  catalog: master
  custom_count: 0
created: <YYYY-MM-DD>
paf_step: 0                            # 0 = до Step-1-IDEA
```

### 4.2 `GROUND/NEXUS/_registry.yaml`

Дефолтный минимум из `nexus_catalog.md` §3 (5 типов). Порядок — как в каталоге. Каждой записи добавь `owner` из roster (по `owner_role` каталога) и `purpose`/`name` — для читаемости; `onboarded: todo`.

```yaml
# Реестр Нексусов клиента. /paf-init → default; /paf-nexus-create → custom; /paf-onboard → по всему реестру.
nexus_types:
  - {slug: customer, source: default, name: Нексус потребителя, owner: <Product Engineer из roster>, purpose: сегменты, JTBD, боли, mNSM-гипотеза, onboarded: todo}
  - {slug: market,   source: default, name: Нексус рынка,       owner: <Portfolio Manager из roster или Cortex>, purpose: объём рынка, тренды, конкуренты, Ставки (Bets), onboarded: todo}
  - {slug: product,  source: default, name: Нексус продукта,    owner: <Product Engineer из roster>, purpose: идея, фичи, Видение (Vision), гэп, onboarded: todo}
  - {slug: growth,   source: default, name: Нексус системы роста, owner: <Growth Engineer из roster или Cortex>, purpose: каналы, монетизация, AI-COGS, рычаги NPV, onboarded: todo}
  - {slug: project-management, source: default, name: Нексус проектного управления PO, owner: <Product Engineer из roster>, purpose: "delivery map PO — этапы, сроки, набор проектов/артефактов/планов в зоне ответственности", onboarded: todo}
```

> Если skeleton-файл `GROUND/NEXUS/_registry.yaml` уже существует (дефолтные без owner/purpose) — **обнови** его, дополнив поля и сохранив порядок; не дублируй записи. `project-management` — обязательный операционный Нексус PO, всегда `source: default`.

### 4.3 `GROUND/NEXUS/{customer,market,product,growth,project-management}/_index.md`

Placeholder-нота для каждого дефолтного Нексуса. Frontmatter — по `nexus_schema.md` §2 (базовый) + §2.2 (empirical онбординг-узел, low-CP). Значения:

```yaml
---
nexus: <slug>                 # customer | market | product | growth
node_id: <slug>-index         # напр. customer-index
node_type: step-overview      # мета-узел каталога Нексуса
paf_step: null                # мета-узел, не привязан к шагу
sprint_phase: null
kind: empirical               # контекст продукта клиента (GROUND Vault)
owner: <из roster по owner_role каталога>
confidence: 0.3               # low-CP: пустой Нексус, допущений ещё нет
sources: []                   # пусто → не финальный факт, placeholder
updated: <YYYY-MM-DD>         # сегодня
ttl_days: <по типу>           # market/customer=90, growth=60, product=90
ripeness: fresh               # updated=сегодня → fresh
tags: [nexus-index, onboarding]
---

# <Человекочитаемое имя Нексуса>

Placeholder-Узел каталога `<slug>`. Контекст этого Нексуса ещё не оцифрован.
Наполнение — через `/paf-onboard` (интервью по seed_questions + ингестия доков из `GROUND/_intake/`).

## seed_questions (из `sa_documentation/nexus_catalog.md`)

<скопируй 4 seed_questions этого типа из каталога §3>

> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.
```

`ttl_days` по типу (`nexus_schema.md` §2.2): `market`/`customer` = 90, `growth` = 60, `product` = 90, `project-management` = 60 (планы/сроки протухают быстро).

> Для `project-management` — обязательный операционный Нексус PO. `_index.md` описывает структуру delivery map (этапы / сроки / набор проектов, артефактов, планов в зоне ответственности PO) и его 6 seed_questions. Реальные deliverable-узлы (`node_type: deliverable`) создаёт `/paf-onboard` по шаблону `GROUND/NEXUS/project-management/_template.md`; `/paf-init` создаёт только placeholder `_index.md`.

### 4.4 (Опц.) `GROUND/PULSE/00-init-pulse.md`

Если skeleton ещё не содержит стартового Pulse — создай snapshot пустых Нексусов:

```yaml
---
nexus: product               # Pulse относится к продукту в целом (мета)
node_id: init-pulse
node_type: step-overview
paf_step: 0
sprint_phase: pulse
kind: empirical
owner: Product Engineer
confidence: 0.3
sources: ["onboarding:init"]
updated: <YYYY-MM-DD>
ttl_days: 90
ripeness: fresh
tags: [progress-pulse, onboarding]
---

# Init Pulse — онбординг GROUND

Snapshot на момент `/paf-init`. Все 5 Нексусов созданы как placeholder'ы (CP 0.3, `onboarded: todo`).

**Intent:** онбординг — оцифровать контекст клиента в GROUND Vault.
**Следующий шаг:** `/paf-onboard` (Phase A ингестия доков + Phase B интервью).

## Context Ripeness (baseline, пустые Нексуса)

| Нексус | completeness | freshness | CR |
|---|---|---|---|
| customer | 0.0 | 1.0 (fresh) | 0.0 |
| market | 0.0 | 1.0 | 0.0 |
| product | 0.0 | 1.0 | 0.0 |
| growth | 0.0 | 1.0 | 0.0 |
| project-management | 0.0 | 1.0 | 0.0 |
```

---

## 5. Verify

После генерации всех файлов — запусти валидатор:

```bash
python3 sa_documentation/validate_ground.py GROUND
```

- Ожидается `OK`. Если выведен список ошибок — **исправь** (чаще всего: невалидный `product.slug`, пустой `product_engineer`, неверный формат `slug` в реестре) и перезапусти.
- Не заканчивай скилл, пока валидатор не вернёт `OK`.

---

## 6. Гвардраилы

- **Idempotent.** Если `GROUND/config.yaml` уже существует — **НЕ затирать без явного подтверждения** пользователя. Предложи: перезаписать / частично обновить / отменить. Дефолт — отменить.
- **Slug валиден.** `product.slug` матчит `[a-z0-9][a-z0-9-]*`; `nexus.slug` — `[a-z][a-z0-9-]*`. Помогай клиенту транслитерировать кириллицу.
- **Product Engineer обязателен.** Не `null`, не пусто, не `"Cortex"` (это роль человека). Валидатор отклонит без него.
- **owner в roster.** В `_registry.yaml` и в `_index.md` `owner` берётся из `team.roster` (по `owner_role` каталога). Если роль не назначена (`null`) — ставь `"Cortex"`.
- **Ноль выдуманного PAF.** Только термины из `sa_documentation/naming_conventions.md`. Запрещённые синонимы (Беклог, PM как финальная роль, приоритизация, потери, T-shaped) — только в negation. Пиши: Банч, Product Engineer, скаутинг, риски, Comb-shaped.
- **Не генерируй empirical-узлы с содержимым.** `_index.md` — placeholder; реальные узлы контекста создаёт `/paf-onboard`.

---

## 7. Финал (readiness-строка)

После `OK` валидатора выведи:

```
GROUND Vault инициализирован.
- config.yaml создан (company, product.slug, roster, phase_target=<N>, ruflo_mcp=<true|false>).
- 5 дефолтных Нексусов созданы: customer, market, product, growth (4 стратегических PAF) + project-management (обязательный delivery map PO) (CP 0.3, onboarded: todo).
- Валидатор: OK.

Readiness: LOW — Нексусы пустые (placeholder), Context Ripeness ≈ 0.
→ /paf-nexus-create (если нужны кастомные Нексусы под ваше решение: sellers, buyers, integrations, compliance, per-product и т.д.)
→ /paf-onboard (оцифровать контекст клиента: ингестия доков + интервью)
```

---

## 8. Связи

- [[sa_documentation/nexus_catalog]] — дефолтный минимум Нексусов (§3 YAML-определения).
- [[sa_documentation/ground_schema]] — schema `config.yaml` + `_registry.yaml`.
- [[sa_documentation/nexus_schema]] — Node schema (§2.2 empirical онбординг-узлы).
- [[sa_documentation/naming_conventions]] — термины PAF.
- `/paf-nexus-create`, `/paf-onboard` — следующие скиллы онбординг-флоу.
