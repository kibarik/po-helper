# Эталон: узлы Step 1 (Idea) — few-shot для /prd-idea

> Иллюстрация формата. Реальные значения — из диалога с PO. Не копировать содержание, копировать структуру.

<!-- Предметная область примера — иллюстративная (условный B2B-сервис бронирования переговорных). Доменные термины ниже — образец заполнения, не часть фреймворка. Универсальна структура: набор frontmatter-ключей §2.3, три Линзы (Strategy → market, Business → growth, Product → product), три статуса hyp_status, шкала CP по источнику. -->

---

## Узел 1 — `market` · Линза Strategy · `hyp_status: hypothesis`

<!-- PO-суждение о сдвиге/адресате, не проверено desk-research или интервью → CP в нижней трети шкалы (0.2–0.4). -->

`GROUND/NEXUS/market/idea-lens-market-1.md`

```yaml
---
nexus: market
node_id: idea-lens-market-1
node_type: bet
paf_step: 1
sprint_phase: scout
kind: empirical
owner: Product Engineer
confidence: 0.3
sources: ["onboarding:interview"]
updated: 2026-07-06
ttl_days: 90
ripeness: fresh
hyp_status: hypothesis
depends_on: []
tags: [discovery, lens-strategy]
---
```

# Bet: смещение спроса к самообслуживанию переговорных в гибридных офисах

PO-гипотеза (Линза Strategy): в компаниях 50–300 чел. с гибридным графиком офис-менеджер больше не успевает вручную разруливать бронирования переговорных — команды хотят бронировать сами, без звонка на ресепшн. Окно «сейчас» — рост доли гибридного графика в целевых компаниях в 2025–2026.

Для кого: HR/Office-менеджер среднего B2B (не отдел ИТ — решение покупают операционные роли).
Почему сейчас: PO наблюдает рост жалоб на «нет свободной переговорной» в собственной компании и у 2 знакомых операционных директоров — сигнал не проверен на выборке.

> ⚠️ гипотеза discovery, CP отражает доверие к допущению, не факт.

---

## Узел 2 — `growth` · Линза Business · `hyp_status: parked`

<!-- PO ответил «не знаю, кто и как будет платить» — легальный терминальный статус. Узел всё равно создаётся (source = сам факт вопроса/ответа PO), но без гипотезы монетизации: не выдумываем модель. -->

`GROUND/NEXUS/growth/idea-lens-growth-1.md`

```yaml
---
nexus: growth
node_id: idea-lens-growth-1
node_type: lever
paf_step: 1
sprint_phase: scout
kind: empirical
owner: Product Engineer
confidence: 0.2
sources: ["onboarding:interview"]
updated: 2026-07-06
ttl_days: 60
ripeness: fresh
hyp_status: parked
depends_on: []
tags: [discovery, lens-business]
---
```

# Lever: модель монетизации бронирования переговорных — открыт

PO-гипотеза (Линза Business): на вопрос «кто платит и за что именно — за место, за интеграцию с календарём, за аналитику загрузки?» PO ответил «не знаю, ещё не считал юнит-экономику и не разговаривал с потенциальными плательщиками». Desk-research по аналогам на этом шаге не запрашивался (PO решил отложить).

Решение: не придумывать модель (freemium/per-seat/enterprise) без основания. Узел паркуется до Step 5 (Business Model) или до отдельного интервью с 2–3 кандидатами в первые платящие клиенты.

> ⚠️ гипотеза discovery, CP отражает доверие к допущению, не факт.

---

## Узел 3 — `product` · Линза Product · `hyp_status: validating` (web-якорь)

<!-- Elevator pitch PO дополнен коротким web desk-research (аналог/тренд), найденным через WebSearch/WebFetch по инструкции Этапа 2 — источник получает URL + дату получения, CP поднимается в диапазон 0.5–0.7 web desk-research. -->

`GROUND/NEXUS/product/idea-lens-product-1.md`

```yaml
---
nexus: product
node_id: idea-lens-product-1
node_type: feature
paf_step: 1
sprint_phase: scout
kind: empirical
owner: Product Engineer
confidence: 0.5
sources: ["onboarding:interview", "https://example.com/reports/hybrid-workplace-booking-trend-2026 (2026-07-06)"]
updated: 2026-07-06
ttl_days: 90
ripeness: fresh
hyp_status: validating
depends_on: []
tags: [discovery, lens-product]
---
```

# Feature/Vision: самостоятельное бронирование переговорной за один клик из календаря

Elevator pitch PO (Линза Product): «Сервис показывает свободные переговорные прямо в календаре сотрудника и бронирует их за один клик, без звонка на ресепшн и без Excel-таблицы у офис-менеджера».

Desk-research (лёгкий, WebSearch): найден отраслевой отчёт о росте спроса на self-service бронирование переговорных в гибридных офисах (аналог/тренд подтверждает направление, но не подтверждает конкретно наш сегмент/гео) — источник `https://example.com/reports/hybrid-workplace-booking-trend-2026`, дата получения 2026-07-06. Статус `validating`: гипотеза подкреплена внешним источником, но ещё не проверена интервью/экспериментом на целевом сегменте — до `validated` не дотягивает.

> ⚠️ гипотеза discovery, CP отражает доверие к допущению, не факт.

---

## Что взять со собой в /prd-idea

- Три Нексуса (market/product/growth) заполняются в рамках одного прохода Step 1 — по одному узлу на Линзу минимум.
- `hyp_status` — честный: `hypothesis` для непроверенного суждения PO, `parked` для «не знаю» (без узла-выдумки), `validating` — только когда реально есть внешний якорь (URL + дата получения) или начатая проверка.
- `confidence` — по шкале источника (§2.3 `sa_documentation/nexus_schema.md`): суждение PO 0.2–0.4, web desk-research 0.5–0.7, интервью/эксперимент 0.7–1.0. Не завышать CP авансом.
- `sources` — никогда не пусто. `onboarding:interview` валиден для PO-суждения, но не заменяет desk-research там, где он был проведён.
- `ttl_days`: market/product = 90, growth = 60.
- Тело узла — не только заголовок и frontmatter: короткая суть гипотезы + явная пометка `⚠️ гипотеза discovery`.
