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

> `minimal: true` — входит в дефолтный набор, инстанцируется `/paf-init`. `minimal: false` — опциональные PAF-типы, клиент подключается по необходимости (PAF определяет 6 типов: 4 минимальных + `ops-model` + `company`).

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

> Эти типы PAF определяет как часть методологии (всего 6 типов: 4 минимальных + 2 опциональных). Они не получают `seed_questions` по умолчанию — клиент формирует вопросы под свой контекст или через `/paf-nexus-create`-интервью.

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
**Version:** 1.0 · **Last updated:** 2026-06-21 · **Связанные:** [[nexus_schema]] · [[naming_conventions]] · [[GROUND/NEXUS/_registry|_registry.yaml]]
