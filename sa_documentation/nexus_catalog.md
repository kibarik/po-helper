# Master Nexus Catalog — кураторский набор PAF Nexus-типов (read-only)

> **Принцип коробки:** дистрибутив `PAF Team OS` даёт **минимально-необходимый набор** Nexus-типов, покрывающий базовый продуктовый контекст PAF. Клиент **расширяет** каталог кастомными типами под своё решение через `/paf-nexus-create` → запись в `GROUND/NEXUS/_registry.yaml` (`source: custom`).
>
> Поле `nexus` в Node schema — **открытый slug**: значение берётся из реестра клиента (`GROUND/NEXUS/_registry.yaml`), а не из фиксированного enum. Этот файл задаёт дефолтный минимум и опциональные PAF-типы; реестр клиента — источник истины для инстанцированных Нексусов.
>
> **Read-only:** это кураторский мастер-каталог платформы (shipped). Правки — только в upstream коробки. См. [[nexus_schema]] (базовая Node schema + формат кастомного типа), [[GROUND/NEXUS/_registry|_registry.yaml]] (реестр клиента).

---

## 1. Контекст PAF

PAF (https://productframework.ru/ops/main, Тихомиров С., CC BY-SA 4.0) управляет продуктом через **Нексусы** — живые модели объектов управления. PAF-минимум покрывает четыре объекта: рынок (Portfolio Manager), потребитель (Product Engineer), продукт (Product Engineer), система роста (Growth Engineer). Роли — по RACI PAF [S1], [S2] (см. [[naming_conventions]]).

Поверх PAF-минимума дистрибутив **po-helper** добавляет второй ярус дефолтного набора — **восемь Нексусов контекста внешнего запроса** (§3A: `problem`, `system-landscape`, `ownership`, `requester-domain`, `precedents`, `compliance`, `strategy`, `capacity`). Они снабжают пайплайн `request-intake → bft-writer` контекстом, без которого БФТ по запросу внешней команды технически корректен, но негоден к принятию решения.

Поверх четырёх стратегических объектов PAF Team OS добавляет **обязательный операционный Нексус `project-management`** — delivery map PO: этапы, сроки и набор проектов, артефактов и планов в зоне ответственности конкретного PO. Он входит в базовый шаблон (`/paf-init`) наравне с четырьмя стратегическими, но описывает не объект управления, а **проработку** — кто что делает, к какому сроку и в каком статусе.

---

## 2. Таблица типов

| slug | name | purpose | owner_role | paf_step_ref | minimal | seed_questions |
|---|---|---|---|---|---|---|
| `market` | Нексус рынка | объём рынка, тренды, конкуренты, Ставки (Bets) | Portfolio Manager | 3 | ✅ | Объём рынка и динамика? Тренды рынка? Конкуренты и их позиции? Ставки (Bets) стратегического сценария? |
| `customer` | Нексус потребителя | сегменты, JTBD, боли, mNSM-гипотеза | Product Engineer | 2 | ✅ | Кто основные сегменты? Какие работы (JTBD) они «нанимают»? Главные боли и их причины? Гипотеза монетизируемой ценности (mNSM)? |
| `product` | Нексус продукта | идея, фичи, Vision, гэп | Product Engineer | 1, 4, 7 | ✅ | В чём идея продукта? Какие фичи закрывают гэп? Видение (Vision) — образ нужного рынку продукта? Гэп между текущим продуктом и Видением? |
| `growth` | Нексус системы роста | каналы, модель монетизации, AI-COGS | Growth Engineer | 5, 6, 8 | ✅ | Каналы дистрибуции/роста? Модель монетизации? AI-COGS (составляющая затрат ИИ)? Рычаги (Lever) роста NPV? |
| `project-management` | Нексус проектного управления PO | delivery map — этапы, сроки, набор проектов/артефактов/планов в зоне ответственности PO | Product Engineer / Product Ops | — | ✅ | Какие проекты/артефакты/планы в зоне ответственности PO? Какие этапы проходит каждый? Сроки и вехи по этапам? В каком статусе? |
| `problem` | Нексус проблемы | проблема под запросом (не симптом): метрика под угрозой, выгодоприобретатель, цена бездействия | Product Engineer | — | ✅ | Какая бизнес-метрика под угрозой? Кто выгодоприобретатель? Что произойдёт при бездействии? Чем проблема отличается от предложенного решения? |
| `system-landscape` | Нексус системного ландшафта | bounded contexts, API-контракты, что уже есть vs строить заново, скрытые зависимости | Product Ops / Product Architect | — | ✅ | Какие bounded contexts затрагивает запрос? Какие API-контракты задействованы? Что уже есть vs строить заново? Какие скрытые зависимости? |
| `ownership` | Нексус владения (RACI) | владельцы затронутых доменов, согласующие, эскалационные пути, скрытые стейкхолдеры | Product Ops / Portfolio Manager | — | ✅ | Кто владелец каждого домена? Кого согласовывать? Каковы эскалационные пути? Есть ли скрытые стейкхолдеры? |
| `requester-domain` | Нексус домена заказчика | бизнес-логика и KPI внешней команды; специфическая боль vs платформенная потребность | Product Engineer | — | ✅ | Какова бизнес-логика заказчика? Какие KPI у команды? Специфическая боль или платформенная потребность? Как решение повлияет на их метрики? |
| `precedents` | Нексус прецедентов | прошлые обсуждения, причины отказов, связанный техдолг | Product Ops | — | ✅ | Обсуждался ли похожий запрос? Почему отклоняли похожие? Какой связанный техдолг? Есть ли решения/ADR, закрывающие часть запроса? |
| `compliance` | Нексус стандартов/комплаенса | корпоративный шаблон БФТ, security/legal, NFR-бейзлайн | Product Ops / Portfolio Manager | — | ✅ | Какой шаблон БФТ обязателен? Какие security/legal-ограничения? Каков NFR-бейзлайн? Какие ревью пройти? |
| `strategy` | Нексус стратегии/roadmap | связь запроса с OKR и приоритетами квартала | Portfolio Manager | — | ✅ | С какими OKR соотносится запрос? Приоритеты квартала? Как защитим на приоритизации? Не конфликтует ли с roadmap? |
| `capacity` | Нексус мощности | velocity, capacity, cost of delay — какой ценой | Product Ops | — | ✅ | Какова velocity команды? Какова доступная capacity? Каков cost of delay? Какой ценой обойдётся реализация? |
| `ops-model` | Нексус операционной модели | операционная модель, кадренсы, эффект асинхронности | Product Ops / Product Architect | — | ❌ | — |
| `company` | Нексус портфеля/компании | портфель продуктов, бизнес-юниты (Business Pod) | Portfolio Manager / Bizdev Architect | — | ❌ | — |
| `team` | Нексус организационной структуры | персоны, роли, зоны влияния, связи, экспертиза, группировка по командам + **PO navigation** (proximity/inbound/clarify/approve) — People Graph для ИИ-навигации (`/people-map`) | Product Ops / Portfolio Manager | — | ❌ | ФИО и должности? Зоны ответственности? Группировка по командам и их миссии? Кто с кем взаимодействует? Как PO взаимодействует с каждым: кто ближе/дальше, кто с чем приходит, у кого уточнять, кто согласовывает? |
| `channels` | Нексус информационных каналов | каналы поступления информации: назначение, темы, стейкхолдеры, участки системы, цели — Information Channels Graph для разметки входящей информации | Product Ops | — | ❌ | Какие каналы поступления информации использует команда? Для чего каждый канал, по каким вопросам пишут? Кто в каждом канале? Какие участки системы и цели затрагивает информация? Что делать с входящей информацией из канала? |
| `system` | Нексус системного ландшафта (поставочный) | сервисы, БД, потоки данных, интеграции, границы ответственности | Solution Architect / Product Architect | — | ❌ BFT-ярус | Какие сервисы и БД в домене? Кто источник истины по каждой сущности? Какие интеграции связывают домены? Где границы ответственности команд? |
| `decisions` | Нексус решений | ADR + PO-решения + rationale, что вынесено в СА | PO / Architect | — | ❌ BFT-ярус | Какие ключевые решения приняты в домене? Кто и когда решил? Каково обоснование? Что вынесено за границу БФТ (в СА)? |
| `rules` | Нексус бизнес-правил | BR-*, инварианты, расчётные политики, исключения | BA / PO | — | ❌ BFT-ярус | Какие бизнес-правила действуют в домене? Какие инварианты всегда истинны? Где закреплён источник правила? Какие исключения (negative flow)? |
| `quality` | Нексус качества и НФТ-стандартов | реестр НФТ, SLA-классы, security baseline, RED/алертинг | SA / QA / SRE | — | ❌ BFT-ярус | Какие SLA-классы приняты? Каков security baseline? Какие RED-метрики обязательны? Где корпоративный реестр НФТ? |
| `risk` | Нексус рисков | реестр рисков: вероятность/влияние/митигация, bus-factor | PO | — | ❌ BFT-ярус | Какие риски в домене? Вероятность и влияние? Митигация? Где bus-factor по ключевым зонам? |
| `lexicon` | Нексус единого языка | Ubiquitous Language: понятие → технический термин, синонимы | BA | — | ❌ BFT-ярус | Какие ключевые сущности домена? Как называются в коде/API? Какие синонимы/двусмысленности? |
| `metrics` | Нексус измеримости | mNSM-декомпозиция, driver/guardrail-метрики, RED, источник данных | Growth / PO | — | ❌ BFT-ярус | Какова mNSM домена? Какие driver-метрики? Guardrail-метрики? Где источник данных (BI/аналитика)? |

> `minimal: ✅` — входит в **дефолтный набор**, инстанцируется `/paf-init`. `minimal: ❌` — опциональные PAF-типы (`ops-model`, `company`), каталожные расширения коробки для ИИ-навигации `team` (People Graph, §4.1) и `channels` (Information Channels Graph, §4.2), а также поставочный BFT-ярус (§4.3); клиент подключается по необходимости.
>
> **Три яруса дефолтного набора (13 Нексусов).** (1) **PAF-минимум** — 4 стратегических объекта управления (`market`/`customer`/`product`/`growth`, базовый продуктовый контекст PAF). (2) **Обязательный операционный** Нексус PAF Team OS `project-management` — **delivery map PO**: не объект управления, а **проработка** (этапы, сроки, набор проектов/артефактов/планов) в зоне ответственности конкретного PO. (3) **Набор po-helper для intake→БФТ** — 8 Нексусов контекста внешнего запроса (`problem`/`system-landscape`/`ownership`/`requester-domain`/`precedents`/`compliance`/`strategy`/`capacity`), без которого БФТ по внешнему запросу технически корректен, но негоден к принятию решения. Все три яруса `/paf-init` инстанцирует одинаково (`source: default`).
>
> **Поставочный BFT-ярус (опциональный, §4.3)** — **коробочное расширение po-helper, НЕ канон PAF.** Курируется дистрибутивом для питания БФТ-пайплайна поставочными знаниями; инстанцируется по необходимости, не `/paf-init`. Термины яруса не выдаются за PAF-терминологию (гвардраил `naming_conventions.md`).
> - **P0** (каждому БФТ): `system` (←CORTEX C1), `decisions` (←C5), `rules` (←C2).
> - **P1** (полный БФТ — НФТ/регуляторика/риски): `quality`, `risk`, а регуляторику покрывает уже дефолтный `compliance` (§3A, node_type `regulation` — §4.3).
> - **P2** (точность/единообразие): `lexicon`, `metrics`.

---

## 3. YAML-определения minimal-типов — PAF-минимум

Определение каждого `minimal: true` типа — канонический источник для `/paf-init` (генерирует дефолтный реестр) и `/paf-onboard` (берёт `seed_questions` для интервью, Phase B). Формат перекрёстно-совместим с Node schema [[nexus_schema]] §2 и реестром [[GROUND/NEXUS/_registry|_registry.yaml]].

Дефолтный набор состоит из двух ярусов: **PAF-минимум** (§3, 4 типа — базовый продуктовый контекст) и **набор po-helper для intake→БФТ** (§3A, 8 типов — контекст внешнего запроса). Оба яруса `/paf-init` инстанцирует одинаково (`source: default`).

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

### 3.5 project-management

> **Обязательный операционный Нексус PO** (PAF Team OS extension). В отличие от четырёх стратегических Нексусов выше (объекты управления PAF), этот Нексус описывает **проработку зоны ответственности PO**: что должно быть сделано, какими этапами, к каким срокам. Каждый Узел = один deliverable (`node_type: deliverable`) — проект, артефакт или план. Источник истины по дедлайнам и статусам proработки.

```yaml
slug: project-management
name: Нексус проектного управления PO
purpose: >
  Delivery map PO. Описывает этапы, сроки и набор проектов, артефактов и планов,
  входящих в зону ответственности PO. Каждый Узел = один deliverable
  (node_type: deliverable) типа project | artifact | plan, с этапами проработки
  (stages), сроками (start_date/due_date/milestones) и образом приёмки.
  Сшивается с OKR/БФТ/спринтами/релизами через linked_*-поля.
owner_role: "Product Engineer / Product Ops"
paf_step_ref: null
minimal: true
seed_questions:
  - Какие проекты, артефакты и планы входят в зону ответственности PO?
  - Какие этапы проходит каждый проект/артефакт — от идеи до приёмки?
  - Каковы сроки: старт, дедлайны и ключевые вехи по каждому этапу?
  - Какие артефакты (БФТ, OKR, роадмап, ПЛАН-спринта, релиз) PO обязан подготовить и к какому сроку?
  - Кто отвечает за каждый проект/артефакт и от чего зависит срок?
  - В каком статусе сейчас каждый проект/артефакт/план?
schema_extensions:
  # --- Идентичность (обязательные для node_type: deliverable) ---
  title:
    type: string
    required: true
    description: "Название проекта / артефакта / плана"
  deliverable_type:
    type: enum
    required: true
    description: "project | artifact | plan"
  po_owner:
    type: string
    required: true
    description: "node_id PO из нексуса team — кто отвечает за проработку"
  status:
    type: enum
    required: true
    description: "idea | in-progress | review | done | blocked"

  # --- Сроки (обязательные) ---
  start_date:
    type: date
    required: true
    description: "Старт проработки (ISO YYYY-MM-DD)"
  due_date:
    type: date
    required: true
    description: "Дедлайн готовности / приёмки (ISO YYYY-MM-DD)"
  milestones:
    type: list[object]
    required: false
    description: "Ключевые вехи: [{name, date}]"

  # --- Этапы (обязательно) ---
  stages:
    type: list[object]
    required: true
    description: "Этапы проработки: [{name, status, due}] — от идеи до приёмки"

  # --- Связи с артефактами PO ---
  linked_okr:
    type: list[string]
    required: false
    description: "OBJ/KR, которые двигает этот deliverable"
  linked_bft:
    type: list[string]
    required: false
    description: "БФТ (JIRA-эпики), входящие в проработку"
  linked_sprint:
    type: list[string]
    required: false
    description: "Спринты, в которых ведётся работа"
  depends_on:
    type: list[string]
    required: false
    description: "node_ids deliverable'ов, от которых зависит срок"

  # --- Критерий готовности ---
  definition_of_done:
    type: string
    required: false
    description: "Образ приёмки deliverable (свободный текст)"
```

> **Примечание по wilting:** `ttl_days` для deliverable-узлов рекомендуется **60 дней** — планы и сроки протухают быстрее контекста рынка/потребителя; короткий TTL раньше триггерит ресинк статусов и дедлайнов. При смене этапа/срока обновляйте `stages`/`status`/`due_date`.

> **Источники для deliverable-узлов:** `sources` должен указывать откуда взят план — `["roadmap"]`, `["jira"]`, `["confluence"]`, `["onboarding:interview"]`. Узел без `sources` = workslop.

---

## 3A. Дефолтный набор po-helper — контекст intake → БФТ (`minimal: true`)

Второй ярус дефолтного набора поверх PAF-минимума. Это восемь Нексусов **контекста внешнего запроса**: без каждого из них БФТ по запросу внешней команды технически корректен, но негоден к принятию решения (решает симптом, противоречит архитектуре, пропускает стейкхолдера, не защитим на приоритизации и т.д.). Инстанцируются `/paf-init` наравне с PAF-минимумом; `seed_questions` использует `/paf-onboard` (Phase B) и `/req-context` при разборе конкретного запроса.

> Высота этих Нексусов — **контекст для принятия решения по запросу**, не декомпозиция реализации. Наполняются из онбординга (ингестия доков + интервью) и обновляются при разборе запросов (`request-intake`) и планировании (`/okr-planner`, `/sprint-planner`).

### 3A.1 problem

```yaml
slug: problem
name: Нексус проблемы
purpose: >
  Проблема под запросом (не симптом). Внешняя команда почти всегда приходит
  с готовым решением, а не с проблемой — без этого Нексуса PO формализует симптом.
  Содержит бизнес-метрику под угрозой, выгодоприобретателя, цену бездействия.
owner_role: Product Engineer
paf_step_ref: null
minimal: true
seed_questions:
  - Какая бизнес-метрика под угрозой?
  - Кто выгодоприобретатель от решения проблемы?
  - Что произойдёт при бездействии (цена бездействия)?
  - Чем проблема отличается от предложенного запросчиком решения?
schema_extensions: {}
```

### 3A.2 system-landscape

```yaml
slug: system-landscape
name: Нексус системного ландшафта
purpose: >
  Системный ландшафт вокруг запроса. В бигтехе критично — десятки сервисов,
  скрытые зависимости. Содержит bounded contexts, существующие API-контракты,
  что уже есть vs что строить заново. Без него — обещание, противоречащее
  архитектуре, или дублирование существующего.
owner_role: "Product Ops / Product Architect"
paf_step_ref: null
minimal: true
seed_questions:
  - Какие bounded contexts и сервисы затрагивает запрос?
  - Какие существующие API-контракты и интеграции задействованы?
  - Что уже реализовано vs что нужно строить заново?
  - Какие скрытые зависимости между сервисами?
schema_extensions: {}
```

### 3A.3 ownership

```yaml
slug: ownership
name: Нексус владения (RACI)
purpose: >
  Кто владелец каждого затронутого домена, кого согласовывать, эскалационные пути.
  В экосистеме бигтеха легко пропустить скрытого стейкхолдера — команду, которая
  физически не участвует в запросе, но зависит от домена. Дополняет team-нексус:
  team — про людей и экспертизу, ownership — про владение доменами по запросу.
owner_role: "Product Ops / Portfolio Manager"
paf_step_ref: null
minimal: true
seed_questions:
  - Кто владелец каждого затронутого домена?
  - Кого нужно согласовывать (Approver) по запросу?
  - Каковы эскалационные пути при разногласиях?
  - Есть ли скрытые стейкхолдеры, зависящие от домена, но не участвующие в запросе?
schema_extensions: {}
```

### 3A.4 requester-domain

```yaml
slug: requester-domain
name: Нексус домена заказчика
purpose: >
  Бизнес-логика и KPI самой внешней команды-заказчика — отдельно от проблемы.
  Позволяет отличить их специфическую боль от универсальной платформенной
  потребности, а это меняет масштаб решения.
owner_role: Product Engineer
paf_step_ref: null
minimal: true
seed_questions:
  - Какова бизнес-логика внешней команды-заказчика?
  - Какие KPI у команды-заказчика?
  - Это их специфическая боль или универсальная платформенная потребность?
  - Как решение повлияет на их метрики?
schema_extensions: {}
```

### 3A.5 precedents

```yaml
slug: precedents
name: Нексус прецедентов
purpose: >
  Что уже обсуждалось, почему отклоняли похожие запросы, связанный техдолг.
  Защищает от повторного изобретения и от повторения прошлых отказов
  без объяснения причин.
owner_role: Product Ops
paf_step_ref: null
minimal: true
seed_questions:
  - Обсуждался ли похожий запрос раньше?
  - Почему отклоняли похожие запросы (причины отказов)?
  - Какой связанный техдолг существует?
  - Есть ли решения/ADR, которые уже закрывают часть запроса?
schema_extensions: {}
```

### 3A.6 compliance

```yaml
slug: compliance
name: Нексус стандартов/комплаенса
purpose: >
  Корпоративный шаблон БФТ, security/legal-ограничения, NFR-бейзлайн.
  В бигтехе часто жёстко формализован — без него документ завернут на ревью.
owner_role: "Product Ops / Portfolio Manager"
paf_step_ref: null
minimal: true
seed_questions:
  - Какой корпоративный шаблон БФТ обязателен?
  - Какие security/legal-ограничения применимы?
  - Каков NFR-бейзлайн (доступность, latency, приватность, аудит)?
  - Какие ревью/подписи нужно пройти перед принятием?
schema_extensions: {}
```

### 3A.7 strategy

```yaml
slug: strategy
name: Нексус стратегии/roadmap
purpose: >
  Как запрос соотносится с текущими OKR и приоритетами квартала.
  Без него БФТ формально верен, но не защитим на приоритизации.
  Связан с /okr-planner (OKR квартала) и /sprint-planner (roadmap по спринтам).
owner_role: Portfolio Manager
paf_step_ref: null
minimal: true
seed_questions:
  - С какими OKR соотносится запрос?
  - Каковы приоритеты текущего квартала?
  - Как запрос защитим на приоритизации?
  - Не конфликтует ли запрос с текущим roadmap?
schema_extensions: {}
```

### 3A.8 capacity

```yaml
slug: capacity
name: Нексус мощности
purpose: >
  Velocity команды, capacity, cost of delay. Даёт не только «что», но и «какой ценой»,
  без чего БФТ неполноценен для принятия решения. Самый волатильный Нексус
  (ttl_days: 30, обновляется на уровне спринта).
owner_role: Product Ops
paf_step_ref: null
minimal: true
seed_questions:
  - Какова текущая velocity команды?
  - Какова доступная capacity (с учётом отпусков/дежурств)?
  - Каков cost of delay запроса?
  - Какой ценой (сроки/ресурсы) обойдётся реализация?
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
  по каким вопросам полезен, с кем взаимодействует, каким контекстом обладает,
  и — главное — как PO взаимодействует с этим человеком (карта навигации).
  Граф формирует пять слоёв: org chart (reports_to/manages),
  social graph (collaborates_with), expertise graph (expertise_topics/contact_for),
  team grouping (team_unit/team_role), PO navigation (proximity/inbound_topics/
  clarify_with/approves) — PO-центричные рёбра «я-как-PO ↔ человек».
owner_role: "Product Ops / Portfolio Manager"
paf_step_ref: null
minimal: false
seed_questions:
  # Идентичность и org chart
  - Полное ФИО и должность каждого ключевого человека?
  - Какие зоны ответственности и принятия решений у каждого?
  - Кто кому подчиняется (прямая иерархия)?
  # Группировка по командам
  - В какие команды/группы (team_unit) сгруппированы люди и за что отвечает каждая команда?
  - Кто лид команды, кто участник, кто представитель команды для PO?
  # Social + expertise
  - Кто с кем взаимодействует по рабочим вопросам (не иерархически)?
  - По каким вопросам к кому обращаться? Каким уникальным контекстом обладает каждый?
  # PO navigation (главное — карта взаимодействия PO)
  - Насколько близок человек к PO в ежедневной работе (core/close/extended/peripheral) и с какой частотой PO с ним взаимодействует?
  - С какими вопросами ЭТОТ человек сам приходит к PO (inbound)?
  - Какие ДЕТАЛИ PO может уточнить у этого человека (источник контекста)?
  - Какие вопросы/решения этот человек СОГЛАСОВЫВАЕТ (право решения, sign-off)?
  - Через кого/к кому эскалировать, если этот человек не решает вопрос?
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

  # --- Team Grouping (как люди сгруппированы по командам) ---
  team_unit:
    type: string
    required: false
    description: "Команда/под/группа внутри department (напр. 'Squad Checkout'); null если вне команд"
  team_role:
    type: enum[lead, member, representative]
    required: false
    description: "Роль человека в team_unit: lead — ведёт команду; member — участник; representative — точка входа команды для PO. null если вне команд"
  team_mission:
    type: string
    required: false
    description: "За что отвечает команда (заполняется на узле lead/representative; свободный текст). Срез ответственности команды для навигации"

  # --- PO Navigation Layer (PO-центричные рёбра: я-как-PO ↔ человек) ---
  proximity:
    type: enum[core, close, extended, peripheral]
    required: false
    description: "Кольцо близости к PO в ежедневной работе. core — ядро (постоянно); close — близкий круг; extended — расширенный; peripheral — периферия. Ось «кто ближе, кто дальше»"
  interaction_cadence:
    type: enum[daily, weekly, biweekly, monthly, ad-hoc, rare]
    required: false
    description: "Частота взаимодействия PO с человеком"
  inbound_topics:
    type: list[string]
    required: false
    description: "С какими вопросами ЧЕЛОВЕК сам приходит к PO (он инициатор обращения). Ось «кто по каким вопросам приходит»"
  clarify_with:
    type: list[string]
    required: false
    description: "Какие ДЕТАЛИ/контекст PO может уточнить у человека (человек — источник информации, не решатель). Ось «у кого какие детали уточняю»"
  approves:
    type: list[string]
    required: false
    description: "Какие вопросы/решения человек СОГЛАСОВЫВАЕТ — право решения, sign-off (не просто мнение). Ось «кто какие вопросы согласовывает»"
  escalate_via:
    type: string
    required: false
    description: "node_id, к кому эскалировать вопрос через/над этим человеком, если он не решает; null если эскалация не определена"

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

> **PO Navigation Layer — главный слой для навигации.** `proximity`/`inbound_topics`/`clarify_with`/`approves` описывают рёбра **«я-как-PO ↔ человек»**, а не свойства человека «вообще». Они отвечают на четыре навигационных вопроса PO: кто ближе/дальше (`proximity`), кто сам приходит с чем (`inbound_topics`), у кого уточнять детали (`clarify_with`), кто согласовывает (`approves`). Эти поля — основа инструментов `/people-links` (наполнение, write) и `/people-map` (навигация, read). Отличие от expertise-слоя: `contact_for`/`expertise_topics` = «человек полезен по теме X вообще»; `clarify_with`/`approves` = «я-как-PO иду к нему за деталями / за согласованием по X». Поля PO-слоя заполняются командой `/people-links` со слов PO (`sources: ["onboarding:interview"]`, `confidence: 0.6`), не угадываются. Собранные рёбра образуют **контур PO** — кольца близости (`proximity`).

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
# team grouping
team_unit: "Squad Checkout"
team_role: lead
team_mission: "Сквозной сценарий оплаты: корзина → платёж → подтверждение. Отвечает за конверсию чекаута и платёжные интеграции"
# PO navigation (я-как-PO ↔ человек)
proximity: core
interaction_cadence: daily
inbound_topics: ["просьбы переприоритизировать фичу", "конфликты ёмкости спринта"]
clarify_with: ["детали customer feedback", "история решений по онбордингу", "статус релиза"]
approves: ["приоритет фич в роадмапе сквада", "дата релиза чекаута"]
escalate_via: team-sidorov-aleksei
# expertise
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

## 4.3 Поставочный ярус (BFT-tier) — коробочное расширение po-helper

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

### 4.3.1 `system` — Нексус системного ландшафта

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

### 4.3.2 `decisions` — Нексус решений (ADR + PO-решения)

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

### 4.3.3 `rules` — Нексус бизнес-правил

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

### 4.3.4 `compliance` — Нексус регуляторики/комплаенса

> ℹ️ **`compliance` — тот же slug, что дефолтный Нексус intake→БФТ (§3A).** Ярус не создаёт второй Нексус: он **обогащает** уже дефолтный `compliance` node_type'ом `regulation` и schema_extensions ниже (структурный реестр требований поверх placeholder-набора онбординга). Один slug — один Нексус в реестре.

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

### 4.3.5 `quality` — Нексус качества и НФТ-стандартов

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

### 4.3.6 `risk` — Нексус рисков

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

### 4.3.7 `lexicon` — Нексус единого языка (Ubiquitous Language)

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

### 4.3.8 `metrics` — Нексус измеримости (мост к OKR)

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
- [[nexus_process_map]] — матрица «Нексус × Процесс»: какой Нексус грунтует какой движок (`request-intake`, `bft-writer`, `okr-planner`, `sprint-planner`, `release-guard`, `po-research`).
- [[GROUND/NEXUS/_registry|_registry.yaml]] — реестр Нексусов, инстанцированных для данного клиента (дефолтные `source: default` + кастомные `source: custom`). Источник истины для поля `nexus` в frontmatter.
- `/paf-nexus-create` — skill создания кастомного Нексуса (§5).

---
**Version:** 1.7 (project-management §3.5 + ярус po-helper intake→БФТ §3A + каталожный `channels` §4.2 + team Team Grouping/PO Navigation §4.1 + поставочный BFT-ярус §4.3: system/decisions/rules/quality/risk/lexicon/metrics + node_type regulation для compliance) · **Last updated:** 2026-07-02 · **Связанные:** [[nexus_schema]] · [[naming_conventions]] · [[GROUND/NEXUS/_registry|_registry.yaml]] · `/paf-nexus-create` · `/people-map`

> **Changelog 1.7:** поставочный ярус BFT-tier (§4.3) — `system` / `decisions` / `rules` / `quality` / `risk` / `lexicon` / `metrics` (коробочное расширение po-helper, не канон PAF); `compliance` из intake→БФТ-набора получил node_type `regulation`; карта «раздел БФТ → Нексус»; порядок чтения граф→CORTEX-fallback.
