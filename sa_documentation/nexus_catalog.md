# Master Nexus Catalog — кураторский набор PAF Nexus-типов (read-only)

> **Принцип коробки:** дистрибутив `PAF Team OS` даёт **минимально-необходимый набор** Nexus-типов, покрывающий базовый продуктовый контекст PAF. Клиент **расширяет** каталог кастомными типами под своё решение через `/paf-nexus-create` → запись в `GROUND/NEXUS/_registry.yaml` (`source: custom`).
>
> Поле `nexus` в Node schema — **открытый slug**: значение берётся из реестра клиента (`GROUND/NEXUS/_registry.yaml`), а не из фиксированного enum. Этот файл задаёт дефолтный минимум и опциональные PAF-типы; реестр клиента — источник истины для инстанцированных Нексусов.
>
> **Read-only:** это кураторский мастер-каталог платформы (shipped). Правки — только в upstream коробки. См. [[nexus_schema]] (базовая Node schema + формат кастомного типа), [[GROUND/NEXUS/_registry|_registry.yaml]] (реестр клиента).

---

## 1. Контекст PAF

PAF (https://productframework.ru/ops/main, Тихомиров С., CC BY-SA 4.0) управляет продуктом через **Нексусы** — живые модели объектов управления. Минимально-необходимый набор покрывает четыре объекта: рынок (Portfolio Manager), потребитель (Product Engineer), продукт (Product Engineer), система роста (Growth Engineer). Роли — по RACI PAF [S1], [S2] (см. [[naming_conventions]]).

---

## 2. Таблица типов

| slug | name | purpose | owner_role | paf_step_ref | minimal | seed_questions |
|---|---|---|---|---|---|---|
| `market` | Нексус рынка | объём рынка, тренды, конкуренты, Ставки (Bets) | Portfolio Manager | 3 | ✅ | Объём рынка и динамика? Тренды рынка? Конкуренты и их позиции? Ставки (Bets) стратегического сценария? |
| `customer` | Нексус потребителя | сегменты, JTBD, боли, mNSM-гипотеза | Product Engineer | 2 | ✅ | Кто основные сегменты? Какие работы (JTBD) они «нанимают»? Главные боли и их причины? Гипотеза монетизируемой ценности (mNSM)? |
| `product` | Нексус продукта | идея, фичи, Vision, гэп | Product Engineer | 1, 4, 7 | ✅ | В чём идея продукта? Какие фичи закрывают гэп? Видение (Vision) — образ нужного рынку продукта? Гэп между текущим продуктом и Видением? |
| `growth` | Нексус системы роста | каналы, модель монетизации, AI-COGS | Growth Engineer | 5, 6, 8 | ✅ | Каналы дистрибуции/роста? Модель монетизации? AI-COGS (составляющая затрат ИИ)? Рычаги (Lever) роста NPV? |
| `ops-model` | Нексус операционной модели | операционная модель, кадренсы, эффект асинхронности | Product Ops / Product Architect | — | ❌ | — |
| `company` | Нексус портфеля/компании | портфель продуктов, бизнес-юниты (Business Pod) | Portfolio Manager / Bizdev Architect | — | ❌ | — |
| `team` | Нексус организационной структуры | персоны, роли, зоны влияния/ответственности, связи, экспертиза — People Graph для ИИ-навигации | Product Ops / Portfolio Manager | — | ❌ | ФИО и должности ключевых людей? Зоны ответственности каждого? Кто с кем взаимодействует по рабочим вопросам? По каким вопросам к кому обращаться? |
| `channels` | Нексус информационных каналов | каналы поступления информации: назначение, темы, стейкхолдеры, участки системы, цели — Information Channels Graph для разметки входящей информации | Product Ops | — | ❌ | Какие каналы поступления информации использует команда? Для чего каждый канал, по каким вопросам пишут? Кто в каждом канале? Какие участки системы и цели затрагивает информация? Что делать с входящей информацией из канала? |

> `minimal: true` — входит в дефолтный набор, инстанцируется `/paf-init`. `minimal: false` — опциональные типы, клиент подключается по необходимости. PAF определяет 6 методологических типов (4 минимальных + `ops-model` + `company`); `team` и `channels` — расширения коробки для ИИ-навигации (People Graph и Information Channels Graph) с полной YAML-спецификацией ниже.

---

## 3. YAML-определения minimal-типов

Определение каждого `minimal: true` типа — канонический источник для `/paf-init` (генерирует дефолтный реестр) и `/paf-onboard` (берёт `seed_questions` для интервью, Phase B). Формат перекрёстно-совместим с Node schema [[nexus_schema]] §2 и реестром [[GROUND/NEXUS/_registry|_registry.yaml]].

### 3.1 customer

```yaml
slug: customer
name: Нексус потребителя
purpose: сегменты, JTBD, боли, mNSM-гипотеза
owner_role: Product Engineer
paf_step_ref: 2
minimal: true
seed_questions:
  - Кто основные сегменты?
  - Какие работы (JTBD) они «нанимают»?
  - Главные боли и их причины?
  - Гипотеза монетизируемой ценности (mNSM)?
schema_extensions: {}
```

### 3.2 market

```yaml
slug: market
name: Нексус рынка
purpose: объём рынка, тренды, конкуренты, Ставки (Bets) стратегического сценария
owner_role: Portfolio Manager
paf_step_ref: 3
minimal: true
seed_questions:
  - Каков объём рынка и его динамика?
  - Какие тренды формируют рынок?
  - Кто конкуренты и каковы их позиции?
  - Каковы Ставки (Bets) стратегического сценария?
schema_extensions: {}
```

### 3.3 product

```yaml
slug: product
name: Нексус продукта
purpose: идея продукта, фичи, Видение (Vision), гэп между текущим продуктом и Видением
owner_role: Product Engineer
paf_step_ref:
  - 1
  - 4
  - 7
minimal: true
seed_questions:
  - В чём идея продукта?
  - Какие фичи закрывают гэп до Видения?
  - Каково Видение (Vision) — образ продукта, нужный рынку и компании?
  - Каков гэп между текущим продуктом и Видением?
schema_extensions: {}
```

### 3.4 growth

```yaml
slug: growth
name: Нексус системы роста
purpose: каналы дистрибуции, модель монетизации, AI-COGS, рычаги (Lever) роста NPV
owner_role: Growth Engineer
paf_step_ref:
  - 5
  - 6
  - 8
minimal: true
seed_questions:
  - Каковы каналы дистрибуции и роста?
  - Какова модель монетизации?
  - Каков AI-COGS (затраты ИИ в стоимости)?
  - Какие рычаги (Lever) дают рост NPV?
schema_extensions: {}
```

---

## 4. Опциональные PAF-типы (`minimal: false`)

Не входят в дефолтный минимум `/paf-init`; клиент подключается по необходимости (создание/регистрация вручную или через расширение коробки).

- **`ops-model`** — Нексус операционной модели. Purpose: операционная модель, кадренсы спринтов, эффект асинхронности (нарушение кадренсов при росте локальных скоростей → event-based). Owner role: **Product Ops / Product Architect**.
- **`company`** — Нексус портфеля/компании. Purpose: портфель продуктов, бизнес-юниты (Business Pod), скаутинг возможностей/угроз на уровне компании. Owner role: **Portfolio Manager / Bizdev Architect**.
- **`team`** — Нексус организационной структуры. Purpose: People Graph — каждый узел = один человек (node_type: person), с ролью, зонами влияния, связями и экспертизой для ИИ-навигации. Owner role: **Product Ops / Portfolio Manager**.
- **`channels`** — Нексус информационных каналов. Purpose: Information Channels Graph — каждый узел = один канал поступления информации (node_type: channel), с назначением, темами, стейкхолдерами, участками системы и целями. Даёт ИИ-агенту разметку входящей информации: откуда пришло, для чего канал, кого касается, куда роутить. Owner role: **Product Ops**.

> `ops-model` и `company` — методологические PAF-типы (не получают `seed_questions` по умолчанию — клиент формирует вопросы через `/paf-nexus-create`-интервью). `team` (§4.1) и `channels` (§4.2) — расширения коробки для ИИ-навигации с полной YAML-спецификацией ниже.

### 4.1 `team` — полная спецификация

```yaml
slug: team
name: Нексус организационной структуры
purpose: >
  People Graph организации. Каждый Узел = один человек (node_type: person).
  Даёт ИИ-агенту структурированное представление кто, на какой роли работает,
  по каким вопросам полезен, с кем взаимодействует, каким контекстом обладает.
  Граф формирует три слоя: org chart (reports_to/manages),
  social graph (collaborates_with), expertise graph (expertise_topics/contact_for).
owner_role: "Product Ops / Portfolio Manager"
paf_step_ref: null
minimal: false
seed_questions:
  - Полное ФИО и должность каждого ключевого человека?
  - Какие зоны ответственности и принятия решений у каждого?
  - Кто кому подчиняется (прямая иерархия)?
  - Кто с кем взаимодействует по рабочим вопросам (не иерархически)?
  - По каким вопросам к кому обращаться?
  - Каким уникальным контекстом или экспертизой обладает каждый человек?
schema_extensions:
  # --- Идентичность (обязательные для node_type: person) ---
  full_name:
    type: string
    required: true
    description: "Полное ФИО (Иванов Иван Иванович)"
  role_title:
    type: string
    required: true
    description: "Должность/титул (напр. 'Product Manager', 'CTO')"
  department:
    type: string
    required: false
    description: "Отдел или подразделение"

  # --- Org Chart (W3C org:reportsTo / org:Membership) ---
  reports_to:
    type: string
    required: false
    description: "node_id руководителя (прямое подчинение)"
  manages:
    type: list[string]
    required: false
    description: "node_ids прямых подчинённых"
  membership_since:
    type: date
    required: false
    description: "Дата начала в роли (ISO YYYY-MM-DD)"

  # --- Social Graph (кто с кем взаимодействует) ---
  collaborates_with:
    type: list[string]
    required: false
    description: "node_ids ключевых коллег по рабочим вопросам (не иерархия)"

  # --- Expertise Graph (что знает, куда роутить) ---
  influence_zones:
    type: list[string]
    required: true
    description: "Зоны ответственности/влияния (напр. ['бюджет продукта', 'найм команды'])"
  expertise_topics:
    type: list[string]
    required: true
    description: "Темы экспертизы — для AI-поиска нужного человека"
  contact_for:
    type: list[string]
    required: true
    description: "По каким вопросам обращаться (routing hint для ИИ-агента)"
  context_holds:
    type: string
    required: false
    description: "Уникальный контекст, которым обладает человек (свободный текст для RAG)"

  # --- Контакты ---
  communication_channels:
    type: list[string]
    required: false
    description: "Как связаться (напр. ['Slack: @ivan', 'email: ivan@co.ru'])"
```

> **Примечание по wilting:** `ttl_days` для person-узлов рекомендуется **180 дней** — роли меняются реже рынка, но быстрее нормативных документов. При реорганизации обновляйте `reports_to`/`manages`/`collaborates_with` — граф связей устаревает быстрее, чем `full_name`/`role_title`.

> **Источники для person-узлов:** `sources` должен указывать откуда взяты данные — `["onboarding:interview"]`, `["hr-system"]`, `["self-reported"]`, `["linkedin"]`, `["config.yaml:roster"]`. Узел без `sources` = workslop (как и для всех Нексусов).

> **Связь с `config.yaml team.roster`:** roster — **источник истины по ролям** (кто Product Engineer, Growth Engineer, …), team-нексус — **богатый профиль человека** (связи, экспертиза, контекст). При создании нексуса через `/paf-nexus-create` (каталожный режим, §3.1 скилла) каждый **именованный** человек из roster (не `"Cortex"`/null) засевает заготовку person-узла: `full_name`/`role_title` из roster, `sources: ["config.yaml:roster"]`, `confidence: 0.3`; иерархия (`reports_to`/`manages`/`collaborates_with`) и экспертиза остаются пустыми до явного наполнения (`/paf-onboard` или вручную). Так устраняется двойной ввод людей без выдумывания связей.

> **Подключение нексуса `team`** — опциональный, инстанцируется не `/paf-init`, а **`/paf-nexus-create`** (каталожный режим): берёт это определение (§4.1), создаёт `GROUND/NEXUS/team/`, регистрирует в `_registry.yaml` (`source: custom`), засевает узлы из roster.

**Пример frontmatter person-узла:**

```yaml
---
nexus: team
node_id: team-ivanov-ivan
node_type: person
paf_step: null
kind: empirical
owner: Product Ops
confidence: 0.8
sources: ["onboarding:interview", "hr-system"]
updated: 2026-06-24
ttl_days: 180
ripeness: fresh
# schema_extensions:
full_name: Иванов Иван Иванович
role_title: Product Manager
department: Продукт
reports_to: team-sidorov-aleksei
manages: [team-petrov-dmitry, team-kozlova-anna]
collaborates_with: [team-kuznecov-sergei, team-morozova-elena]
influence_zones: ["роадмап продукта", "приоритизация фич", "релизы"]
expertise_topics: ["product discovery", "JTBD", "A/B тесты", "mobile UX"]
contact_for: ["приоритет фичи", "статус релиза", "customer feedback"]
context_holds: "Знает историю решений по онбордингу за 2 года, имеет прямой доступ к топ-клиентам"
communication_channels: ["Slack: @ivan.ivanov", "email: i.ivanov@company.ru"]
membership_since: 2024-03-01
---
```

### 4.2 `channels` — полная спецификация

```yaml
slug: channels
name: Нексус информационных каналов
purpose: >
  Information Channels Graph команды. Каждый Узел = один канал поступления
  информации (node_type: channel): рабочий чат, Email, Telegram-канал,
  регулярный созвон. Даёт ИИ-агенту разметку входящей информации — откуда
  пришло сообщение, для чего канал, по каким темам здесь пишут, кто в канале
  (стейкхолдеры), к каким участкам системы и целям привязать, куда роутить.
owner_role: "Product Ops"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие каналы поступления информации использует команда (чаты, Email, Telegram, созвоны)?
  - Для чего каждый канал — по каким вопросам здесь пишут?
  - Кто находится в каждом канале (стейкхолдеры)?
  - Какие участки системы и цели затрагивает информация из канала?
  - Что делать с входящей информацией из канала (в intake, в решения, в трекер, FYI)?
schema_extensions:
  # --- Идентификация (обязательные для node_type: channel) ---
  channel_type:
    type: enum
    required: true
    description: "chat | email | telegram | call | tracker | wiki | other"
  platform:
    type: string
    required: true
    description: "Платформа канала (напр. 'Telegram', 'Slack', 'Zoom', 'Email')"
  handle:
    type: string
    required: false
    description: "Идентификатор канала: @канал / id группы / email / ссылка на созвон"
  direction:
    type: enum
    required: false
    description: "inbound | outbound | bidirectional — направление потока"
  cadence:
    type: string
    required: false
    description: "Ритм канала (напр. 'поток', 'ежедневно', 'еженедельно', 'по событию')"

  # --- Назначение (для чего канал, по каким вопросам) ---
  purpose:
    type: string
    required: true
    description: "Зачем канал существует, 1-2 фразы"
  topics:
    type: list[string]
    required: true
    description: "По каким вопросам здесь пишут — для роутинга входящей информации"
  signal_types:
    type: list[string]
    required: true
    description: "Типы сигналов канала: requirement | bug | decision | feedback | status | risk"

  # --- Связи (роутинг) ---
  stakeholders:
    type: list[string]
    required: true
    description: "Кто в канале — node_ids из NEXUS/team (ascii)"
  system_areas:
    type: list[string]
    required: false
    description: "Затрагиваемые участки системы — ссылки на CORTEX/product"
  goals:
    type: list[string]
    required: false
    description: "Цели/OKR, которые питает канал — OBJ/KR-коды"

  # --- Обработка входящей информации ---
  ingest_action:
    type: string
    required: false
    description: "Что делать с инфой отсюда: → /req-context | → CORTEX/decisions | → OKR-сигнал | → трекер | FYI"
```

> **Примечание по wilting:** `ttl_days` для channel-узлов рекомендуется **180 дней** — каналы и их состав меняются реже рынка, но быстрее нормативных документов. При реорганизации/смене инструментов обновляйте `stakeholders`/`platform`/`handle` — связи устаревают быстрее, чем назначение канала.

> **Источники для channel-узлов:** `sources` указывает откуда взяты данные — `["onboarding:interview"]`, `["po:observation"]` (наблюдение PO), ссылка на сам канал. Узел без `sources` = workslop (как и для всех Нексусов).

> **Связь с `team`:** `stakeholders` в channel-узле ссылается на person-узлы `NEXUS/team` (обратная сторона поля `communication_channels` в person-узле). Так граф людей и граф каналов сшиваются: «кто в канале» ↔ «через какие каналы связаться с человеком».

> **Подключение нексуса `channels`** — опциональный, инстанцируется не `/paf-init`, а навыком **`info-channels`** (`/channel-map`) либо **`/paf-nexus-create channels`** (каталожный режим): берёт это определение (§4.2), создаёт `GROUND/NEXUS/channels/`, регистрирует в `_registry.yaml` (`source: custom`).

**Пример frontmatter channel-узла:**

```yaml
---
nexus: channels
node_id: chan-billing-tg
node_type: channel
paf_step: null
kind: empirical
owner: Product Ops
confidence: 0.6
sources: ["onboarding:interview"]
updated: 2026-06-25
ttl_days: 180
ripeness: fresh
tags: [channel]
# schema_extensions:
channel_type: telegram
platform: "Telegram"
handle: "@billing_team"
direction: inbound
cadence: "поток"
purpose: "Оперативные вопросы и баги по биллингу от смежных команд"
topics: ["ошибки списаний", "статусы платежей", "запросы на новые тарифы"]
signal_types: [bug, requirement, feedback]
stakeholders: [team-ivanov-ivan, team-petrov-dmitry]
system_areas: ["[[cortex-billing]]", "[[cortex-payments]]"]
goals: ["KR-3.2"]
ingest_action: "Баг → трекер; запрос на тариф → /req-context; статус/фидбек → FYI"
---
```

---

## 5. Кастомные Nexus-типы клиента

Поверх дефолтного минимума и опциональных PAF-типов клиент определяет **кастомные** Нексусы под своё решение (например, `sellers`, `buyers`, `supply-chain`):

- Команда: `/paf-nexus-create` → интервью (name, slug, purpose, owner из roster, seed_questions, опц. paf_step, опц. schema_extensions) → `GROUND/NEXUS/<slug>/` (`_index.md` + template) + запись в `GROUND/NEXUS/_registry.yaml` (`source: custom`).
- Гвардраилы: slug уникален; конфликт с дефолтными/мастер-каталогом → предупреждение; owner должен быть из roster.
- Узлы кастомного Нексуса подчиняются тем же правилам Node schema [[nexus_schema]]: `sources`, `confidence` (Confidence Point), `updated`/`ttl_days`, `ripeness` (wilting). `schema_extensions` добавляет тип-специфичные поля поверх базовой schema.

> Каталог живой: клиент добавляет кастомные Нексусы когда угодно (`/paf-nexus-create`); затем `/paf-onboard` наполняет и их.

---

## 6. Связи

- [[nexus_schema]] — базовая Node schema, формат определения кастомного типа (`schema_extensions`), empirical узлы клиента (GROUND Vault).
- [[GROUND/NEXUS/_registry|_registry.yaml]] — реестр Нексусов, инстанцированных для данного клиента (дефолтные `source: default` + кастомные `source: custom`). Источник истины для поля `nexus` в frontmatter.
- `/paf-nexus-create` — skill создания кастомного Нексуса (§5).

---
**Version:** 1.2 · **Last updated:** 2026-06-25 · **Связанные:** [[nexus_schema]] · [[naming_conventions]] · [[GROUND/NEXUS/_registry|_registry.yaml]] · `/paf-nexus-create`
