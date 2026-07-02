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
| `system` | Нексус системного ландшафта | сервисы, БД, потоки данных, интеграции, границы ответственности | Solution Architect / Product Architect | — | ❌ BFT-ярус | Какие сервисы и БД в домене? Кто источник истины по каждой сущности? Какие интеграции связывают домены? Где границы ответственности команд? |
| `decisions` | Нексус решений | ADR + PO-решения + rationale, что вынесено в СА | PO / Architect | — | ❌ BFT-ярус | Какие ключевые решения приняты в домене? Кто и когда решил? Каково обоснование? Что вынесено за границу БФТ (в СА)? |
| `rules` | Нексус бизнес-правил | BR-*, инварианты, расчётные политики, исключения | BA / PO | — | ❌ BFT-ярус | Какие бизнес-правила действуют в домене? Какие инварианты всегда истинны? Где закреплён источник правила? Какие исключения (negative flow)? |
| `compliance` | Нексус регуляторики/комплаенса | законы, стандарты, ПДн/PCI, обязательства, кто согласует | PO / Legal | — | ❌ BFT-ярус | Какие законы/стандарты применимы к домену? Какие данные регулируются? Кто согласует соответствие? Какие обязательства и сроки? |
| `quality` | Нексус качества и НФТ-стандартов | реестр НФТ, SLA-классы, security baseline, RED/алертинг | SA / QA / SRE | — | ❌ BFT-ярус | Какие SLA-классы приняты? Каков security baseline? Какие RED-метрики обязательны? Где корпоративный реестр НФТ? |
| `risk` | Нексус рисков | реестр рисков: вероятность/влияние/митигация, bus-factor | PO | — | ❌ BFT-ярус | Какие риски в домене? Вероятность и влияние? Митигация? Где bus-factor по ключевым зонам? |
| `lexicon` | Нексус единого языка | Ubiquitous Language: понятие → технический термин, синонимы | BA | — | ❌ BFT-ярус | Какие ключевые сущности домена? Как называются в коде/API? Какие синонимы/двусмысленности? |
| `metrics` | Нексус измеримости | mNSM-декомпозиция, driver/guardrail-метрики, RED, источник данных | Growth / PO | — | ❌ BFT-ярус | Какова mNSM домена? Какие driver-метрики? Guardrail-метрики? Где источник данных (BI/аналитика)? |

> `minimal: true` — входит в дефолтный набор, инстанцируется `/paf-init`. `minimal: false` — опциональные типы, клиент подключается по необходимости.
>
> **Два происхождения опциональных типов:**
> - **PAF-канон** (`ops-model`, `company`, `team`) — часть методологии PAF (всего 7 типов: 4 минимальных + эти 3). Определения — §4.
> - **BFT-ярус** (`system`, `decisions`, `rules`, `compliance`, `quality`, `risk`, `lexicon`, `metrics`) — **коробочное расширение po-helper, НЕ канон PAF.** Курируется дистрибутивом для питания БФТ-пайплайна. Определения — §4.2. Термины этих типов не выдаются за PAF-терминологию.
>   - **P0** (каждому БФТ): `system` (←CORTEX C1), `decisions` (←C5), `rules` (←C2).
>   - **P1** (полный БФТ — НФТ/регуляторика/риски): `compliance` (←C3), `quality`, `risk`.
>   - **P2** (точность/единообразие): `lexicon`, `metrics`.

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

> Эти типы PAF определяет как часть методологии (всего 7 типов: 4 минимальных + 3 опциональных). `ops-model` и `company` не получают `seed_questions` по умолчанию — клиент формирует вопросы через `/paf-nexus-create`-интервью. `team` имеет полную YAML-спецификацию (§4.1) ниже.

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

---

## 4.2 Поставочный ярус (BFT-tier) — коробочное расширение po-helper

> ⚠️ **Не канон PAF.** `system` / `decisions` / `rules` / `compliance` / `quality` / `risk` / `lexicon` / `metrics` — курируемые дистрибутивом типы, покрывающие *поставочный* уровень знаний, от которого зависит БФТ. PAF определяет 7 типов (§4); эти восемь — расширение коробки po-helper поверх PAF. Термины ниже не выдаются за PAF-терминологию (гвардраил `naming_conventions.md`).
>
> **Зачем ярус.** Стратегические Нексусы (`market/customer/product/growth`) питают разделы БФТ «ценность/сегменты/JTBD». Но разделы *Границы системы*, *As-Is→To-Be*, *ФТ*, *НФТ*, *Открытые решения*, *Регуляторика*, *Риски*, *Зависимости*, *Словарь* требуют поставочных знаний, которые сегодня либо лежат плоскими реестрами CORTEX (`cortex.architecture` C1, `cortex.decisions` C5, `cortex.business_rules` C2, `cortex.regulatory` C3), либо отсутствуют структурно (риски, реестр НФТ, единый язык, измеримость). Промоут/структурирование в Нексусы даёт им wilting (детект устаревания), Confidence Point, RACI-владельца и место в общем графе OKR→БФТ→Спринт→Релиз.
>
> **Карта раздел БФТ → Нексус яруса:**
>
> | Раздел БФТ (`bft_standards.md` §18-40) | Нексус | Приоритет |
> |---|---|---|
> | Границы системы, As-Is→To-Be, ФТ, высота, Зависимости | `system` | P0 |
> | Открытые вопросы / Ключевые решения, обоснование границ | `decisions` | P0 |
> | ФТ, negative flows, параметры/ограничения | `rules` | P0 |
> | Регуляторика, часть НФТ (security/хранение), Риски | `compliance` | P1 |
> | Нефункциональные требования НФТ (весь раздел) | `quality` | P1 |
> | Риски | `risk` | P1 |
> | Словарь (Ubiquitous Language), сквозная трассировка | `lexicon` | P2 |
> | Критерии успеха, измеримость → мост к KR | `metrics` | P2 |
>
> Инстанцируются через `/paf-nexus-create` (каталожный режим). Owner резолвится из `config.yaml team.roster` по `owner_role`; роль не назначена → `"Cortex"`. Засева узлов у типов яруса нет (в отличие от `team`) — узлы наполняет `/paf-onboard`.

### 4.2.1 `system` — Нексус системного ландшафта

Абсорбирует CORTEX C1 (`cortex.architecture`) + SA-store (`cortex.sa_store`) в живой граф. Каждый Узел = компонент ландшафта. **Питает БФТ:** Границы системы, As-Is→Gap→To-Be, ФТ, высота документа (гейт 14), Зависимости. **Питает цепочку:** `sprint-decompose` (какие сервисы затронуты), `release-guard` (дрейф scope по компонентам).

```yaml
slug: system
name: Нексус системного ландшафта
purpose: >
  Живой граф системного ландшафта домена. Каждый Узел = компонент
  (node_type: component): сервис, БД, интеграция, поток данных или граница.
  Рёбра upstream/downstream образуют карту зависимостей; team_owner связывает
  компонент с владеющей командой (ребро в team). Источник границ и As-Is для БФТ.
owner_role: "Solution Architect / Product Architect"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие сервисы и БД в домене?
  - Кто источник истины по каждой бизнес-сущности?
  - Какие интеграции связывают домены (upstream/downstream)?
  - Где границы ответственности команд по компонентам?
  - Какие SLA-классы у ключевых компонентов?
schema_extensions:
  component_type:
    type: string
    required: true
    description: "service | database | integration | data-flow | boundary"
  owns_data:
    type: list[string]
    required: false
    description: "Сущности/данные, для которых компонент — источник истины"
  upstream:
    type: list[string]
    required: false
    description: "node_ids компонентов, которые вызывают/питают этот (входящие)"
  downstream:
    type: list[string]
    required: false
    description: "node_ids компонентов, которые этот вызывает/питает (исходящие)"
  team_owner:
    type: string
    required: false
    description: "node_id владеющей команды/человека (ребро в nexus team)"
  sla_class:
    type: string
    required: false
    description: "Класс SLA или порог (напр. 'P95 200ms чтение' / 'gold')"
```

> **Wilting:** `ttl_days` ≈ **180** — архитектура меняется быстрее нормативки, но медленнее рынка. При рефакторинге/миграции обновляйте `upstream`/`downstream`/`team_owner` — граф связей устаревает раньше `component_type`.

### 4.2.2 `decisions` — Нексус решений (ADR + PO-решения)

Абсорбирует CORTEX C5 (`cortex.decisions`). Каждый Узел = одно решение. **Питает БФТ:** Открытые вопросы / Ключевые решения, обоснование границ, «что вынесено в СА». **Питает цепочку:** атрибуцию дрейфа релиза (`release-change` — кто и когда решил менять scope), обоснование приоритетов, коммуникацию.

```yaml
slug: decisions
name: Нексус решений
purpose: >
  Живой реестр архитектурных (ADR) и продуктовых (PO) решений домена.
  Каждый Узел = одно решение (node_type: decision) с контекстом, самим решением,
  обоснованием и последствиями. supersedes выстраивает цепочку эволюции;
  affects связывает решение с затронутыми компонентами/фичами.
owner_role: "PO / Architect"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие ключевые решения приняты в домене (архитектурные и продуктовые)?
  - Кто и когда принял решение?
  - Каков контекст и обоснование каждого?
  - Какие последствия и что вынесено за границу БФТ (в СА)?
  - Какие решения замещены новыми (supersedes)?
schema_extensions:
  decision_type:
    type: string
    required: true
    description: "adr | po-decision"
  status:
    type: string
    required: true
    description: "proposed | accepted | superseded | deprecated"
  context:
    type: string
    required: false
    description: "Ситуация выбора — почему решение потребовалось"
  decision:
    type: string
    required: true
    description: "Что именно решено"
  rationale:
    type: string
    required: false
    description: "Обоснование выбора (почему именно так)"
  consequences:
    type: string
    required: false
    description: "Последствия; что вынесено в СА / за границу БФТ"
  supersedes:
    type: string
    required: false
    description: "node_id замещаемого решения (цепочка эволюции)"
  affects:
    type: list[string]
    required: false
    description: "node_ids затронутых компонентов (system) / фич (product)"
```

> **Wilting:** `ttl_days` ≈ **365** — решения долговечны, но помечайте `status: superseded` при замещении, а не удаляйте (история обоснований нужна для атрибуции дрейфа и приоритетов).

### 4.2.3 `rules` — Нексус бизнес-правил

Абсорбирует CORTEX C2 (`cortex.business_rules`, BR-*). Каждый Узел = одно правило. **Питает БФТ:** ФТ, negative flows, параметры/ограничения, инварианты.

```yaml
slug: rules
name: Нексус бизнес-правил
purpose: >
  Живой реестр бизнес-правил домена (BR-*). Каждый Узел = одно правило
  (node_type: rule): инвариант, который всегда истинен, с областью применения,
  исключениями и источником истины. Питает функциональные требования и
  негативные сценарии БФТ.
owner_role: "BA / PO"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие бизнес-правила действуют в домене?
  - Какой инвариант каждое правило гарантирует?
  - К каким сущностям/процессам применяется?
  - Какие исключения (negative flow) у правила?
  - Где закреплён источник правила (регламент / закон / ADR)?
schema_extensions:
  rule_id:
    type: string
    required: true
    description: "Бизнес-код правила (напр. BR-014)"
  category:
    type: string
    required: false
    description: "расчёт | валидация | доступ | жизненный цикл"
  applies_to:
    type: list[string]
    required: false
    description: "Сущности/процессы, к которым применяется правило"
  invariant:
    type: string
    required: true
    description: "Само правило — что всегда истинно"
  exceptions:
    type: string
    required: false
    description: "Исключения / негативный сценарий"
  source_of_truth:
    type: string
    required: false
    description: "Где закреплено: регламент / закон / node_id решения (decisions)"
```

> **Wilting:** `ttl_days` ≈ **365**. При изменении расчётной политики обновляйте `invariant`/`exceptions` и связывайте `source_of_truth` с узлом `decisions`, зафиксировавшим изменение.

### 4.2.4 `compliance` — Нексус регуляторики/комплаенса

Абсорбирует CORTEX C3 (`cortex.regulatory`). Каждый Узел = одно применимое требование (закон/стандарт/политика). **Питает БФТ:** Регуляторика, security/хранение-НФТ, Риски. **Питает цепочку:** релизный гейт (регуляторный sign-off), юридические блокеры приоритетов.

```yaml
slug: compliance
name: Нексус регуляторики/комплаенса
purpose: >
  Живой реестр применимых регуляторных требований домена. Каждый Узел =
  одно требование (node_type: regulation): закон, стандарт или политика,
  с юрисдикцией, обязательством, областью применения и согласующим.
  Источник раздела «Регуляторика» и части НФТ (security/хранение) для БФТ.
owner_role: "PO / Legal"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие законы/стандарты применимы к домену?
  - Какие данные регулируются (ПДн / карты / фискализация)?
  - Кто согласует соответствие (sign-off)?
  - Какие обязательства и сроки накладывает каждое требование?
  - Каков риск/санкция при нарушении?
schema_extensions:
  regulation_type:
    type: string
    required: true
    description: "law | standard | policy (напр. 152-ФЗ, PCI DSS, GDPR)"
  jurisdiction:
    type: string
    required: false
    description: "Юрисдикция/область действия"
  applies_to:
    type: list[string]
    required: false
    description: "Домены/данные/процессы, к которым применяется"
  obligation:
    type: string
    required: true
    description: "Что именно обязывает требование"
  sign_off_by:
    type: string
    required: false
    description: "Кто согласует соответствие (node_id team / роль)"
  penalty:
    type: string
    required: false
    description: "Санкция/риск при нарушении"
```

> **Wilting:** `ttl_days` ≈ **365** — законы меняются медленно, но при изменении регуляторики обновляйте `obligation` и связывайте с узлом `risk` (риск нарушения) и `decisions` (как решили соответствовать).

### 4.2.5 `quality` — Нексус качества и НФТ-стандартов

Структурирует корпоративный реестр НФТ (`bft_standards.md` §«Стандартный НФТ-набор» / §«Корпоративный реестр НФТ»). Каждый Узел = один НФТ-стандарт. **Питает БФТ:** раздел НФТ целиком (приоритет — брать из реестра, а не формулировать с нуля). **Питает цепочку:** Definition of Done, релизный гейт.

```yaml
slug: quality
name: Нексус качества и НФТ-стандартов
purpose: >
  Живой реестр нефункциональных стандартов домена/компании. Каждый Узел =
  один НФТ-стандарт (node_type: nfr): SLA-класс, порог нагрузки, security
  baseline, шаблон RED-метрик или алертинга, с измеримым порогом и способом
  проверки. Приоритетный источник раздела НФТ БФТ.
owner_role: "SA / QA / SRE"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие SLA-классы приняты (P95/P99 по операциям)?
  - Каков security baseline (TLS, аудит, сервисные учётки)?
  - Какие RED-метрики и алерты обязательны?
  - Есть ли корпоративный реестр НФТ — где и какие ID?
  - Какие требования по логированию/хранению/идемпотентности?
schema_extensions:
  nfr_group:
    type: string
    required: true
    description: "идемпотентность | SLA | нагрузка | RED | алертинг | логирование | доступ-аудит | надёжность"
  metric:
    type: string
    required: false
    description: "Измеряемая величина (напр. 'P95 латентность записи')"
  threshold:
    type: string
    required: true
    description: "Порог приёмки (напр. '2000 ms', '150 RPS чтение')"
  applies_to:
    type: list[string]
    required: false
    description: "Типы компонентов (backend-API, batch, UI, …)"
  verification:
    type: string
    required: false
    description: "Как проверяется (нагрузочный тест / мониторинг / аудит)"
  registry_id:
    type: string
    required: false
    description: "ID в корпоративном реестре НФТ, если есть"
```

> **Wilting:** `ttl_days` ≈ **365**. Ссылайтесь на `registry_id` вместо переформулирования (гвардраил БФТ: не выдумывать НФТ при наличии стандарта).

### 4.2.6 `risk` — Нексус рисков

Структурирует реестр рисков (сегодня — нет структурного дома). Каждый Узел = один риск. **Питает БФТ:** раздел Риски (`Риск | Вероятность | Влияние | Митигация`). **Питает цепочку:** `okr-debate` (adversarial), `sprint`-риски, `release-guard`.

```yaml
slug: risk
name: Нексус рисков
purpose: >
  Живой реестр рисков домена. Каждый Узел = один риск (node_type: risk)
  с вероятностью, влиянием, типом, митигацией и связями с затронутыми
  компонентами/решениями. Источник раздела «Риски» БФТ и вход в OKR-debate.
owner_role: "PO"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие риски есть в домене (тех / продукт / ресурс / регуляторный / зависимость)?
  - Какова вероятность и влияние каждого?
  - Какая митигация и кто ответственный?
  - Где bus-factor по ключевым зонам/людям?
schema_extensions:
  risk_type:
    type: string
    required: true
    description: "технический | продуктовый | ресурсный | регуляторный | зависимость"
  probability:
    type: string
    required: true
    description: "low | medium | high"
  impact:
    type: string
    required: true
    description: "low | medium | high"
  mitigation:
    type: string
    required: false
    description: "План снижения риска"
  mitigation_owner:
    type: string
    required: false
    description: "node_id ответственного за митигацию (team)"
  affects:
    type: list[string]
    required: false
    description: "node_ids затронутых (system / decisions / compliance)"
```

> **Wilting:** `ttl_days` ≈ **90** — риски динамичны. Протухший риск-узел = сигнал пересмотреть актуальность/митигацию, а не автоматически закрыть.

### 4.2.7 `lexicon` — Нексус единого языка (Ubiquitous Language)

Структурирует словарь проекта (`bft_standards.md` §«Словарь»; сегодня — плоский `glossary` в профиле). Каждый Узел = один термин. **Питает БФТ:** раздел Словарь + сквозную трассировку БТ←ПТ←ИТ / БТ←ФТ←НФТ. Кросс-секущий для всех Нексусов.

```yaml
slug: lexicon
name: Нексус единого языка
purpose: >
  Живой словарь Ubiquitous Language домена. Каждый Узел = один термин
  (node_type: term): бизнес-понятие ↔ технический термин, с определением,
  синонимами и доменной привязкой. Исключает двусмысленность во всём графе
  и в разделе «Словарь» БФТ.
owner_role: "BA"
paf_step_ref: null
minimal: false
seed_questions:
  - Какие ключевые сущности и роли домена?
  - Как каждая называется в коде/API (технический термин)?
  - Какие синонимы/двусмысленности встречаются?
  - К какому домену/Нексусу относится термин?
schema_extensions:
  concept:
    type: string
    required: true
    description: "Бизнес-понятие (напр. 'Расчётный период')"
  technical_term:
    type: string
    required: true
    description: "Имя в коде/API (напр. 'billing_cycle')"
  definition:
    type: string
    required: false
    description: "Каноничное определение"
  aliases:
    type: list[string]
    required: false
    description: "Синонимы/устаревшие названия (для дедупликации)"
  domain:
    type: string
    required: false
    description: "Домен/slug Нексуса, к которому относится термин"
```

> **Wilting:** `ttl_days` ≈ **365**. Термин со сменившимся `technical_term` (рефакторинг) обновляйте, старое имя — в `aliases`.

### 4.2.8 `metrics` — Нексус измеримости (мост к OKR)

Структурирует измеримость (частично пересекается с `growth`: mNSM). Каждый Узел = одна метрика. **Питает БФТ:** Критерии успеха (измеримый образ приёмки). **Питает цепочку:** KR-measurability (`okr-key-results`/`okr-smart`), `metrics` как источник target-значений.

```yaml
slug: metrics
name: Нексус измеримости
purpose: >
  Живой реестр метрик домена. Каждый Узел = одна метрика (node_type: metric):
  north-star / driver / guardrail / RED / продуктовая, с единицей, формулой,
  текущим/целевым значением и источником данных. Мост между «Критериями успеха»
  БФТ и измеримостью KR.
owner_role: "Growth / PO"
paf_step_ref: null
minimal: false
seed_questions:
  - Какова mNSM (монетизируемая north-star) домена?
  - Какие driver-метрики двигают north-star?
  - Какие guardrail-метрики нельзя ухудшать?
  - Где источник данных (BI / аналитика) и как считается?
schema_extensions:
  metric_type:
    type: string
    required: true
    description: "north-star | driver | guardrail | RED | product"
  unit:
    type: string
    required: false
    description: "Единица измерения (%, руб, ms, шт)"
  formula:
    type: string
    required: false
    description: "Как вычисляется метрика"
  current_value:
    type: string
    required: false
    description: "Текущее значение (baseline)"
  target_value:
    type: string
    required: false
    description: "Целевое значение (при наличии KR)"
  source_system:
    type: string
    required: false
    description: "Откуда данные (BI / аналитика / трекер)"
  relates_to:
    type: list[string]
    required: false
    description: "node_ids связанных KR/OBJ/фич (product/growth)"
```

> **Wilting:** `ttl_days` ≈ **90** — значения метрик протухают быстро. `current_value` без свежего `updated` = сигнал перечитать источник, а не доверять baseline.

> **Пересечение с `growth`.** `growth` держит стратегические рычаги роста и модель монетизации; `metrics` — операционный реестр измеримости (значения, формулы, источники). Если продукт маленький и метрик мало — держите их узлами прямо в `growth` и `metrics` не инстанцируйте.

> **Связь яруса с CORTEX.** До промоута БФТ-пайплайн (`/bft-context-gen`) читает плоские `cortex.*`-реестры (C1/C2/C3/C5). После инстанцирования Нексусов яруса пайплайн читает граф с приоритетом (`GROUND/NEXUS/<slug>/*`), а плоский реестр — fallback и источник первичного онбординга (`/paf-onboard` наполняет из него узлы). Маппинг слой↔Нексус и порядок чтения — в `/bft-context-gen` (Этап 1) и `/bft-context-gen-deep`. Типы без CORTEX-предка (`quality`, `risk`, `lexicon`, `metrics`) наполняются онбордингом с нуля.

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
**Version:** 1.4 · **Last updated:** 2026-07-02 · **Связанные:** [[nexus_schema]] · [[naming_conventions]] · [[GROUND/NEXUS/_registry|_registry.yaml]] · `/paf-nexus-create`

> **Changelog 1.4:** ярус BFT-tier (§4.2) расширен до 8 типов — P1 `compliance`/`quality`/`risk` + P2 `lexicon`/`metrics`; добавлена карта «раздел БФТ → Нексус»; уточнён порядок чтения граф→CORTEX-fallback.
> **Changelog 1.3:** добавлен поставочный ярус (BFT-tier, §4.2): `system` / `decisions` / `rules` — коробочное расширение po-helper (не канон PAF) для питания БФТ-пайплайна.
