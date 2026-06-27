---
nexus: growth
node_id: aip-5-overview
node_type: step-overview
paf_step: 5
sprint_phase: null
kind: normative
owner: Growth Engineer
confidence: 1.0
sources: ["[S1]", "[S2]", "[S3]", "[S4]", "RB-STEP-5"]
updated: 2026-06-20
ttl_days: 365
ripeness: fresh
tags: []
---

# overview — Step 5: Business Model

> **Веха Discovery · Линза: Business (Рычаги/Lever → NPV, Business Sprint) · Fit-точка: 🟥 Biz-model fit**
> Источник: PAF [S1]–[S4]; методы — `TRADITIONAL/RB-STEP-5-BUSINESS-MODEL-VALIDATION` (index + 5.1–5.6); «почему» — `AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION` (6 инструкций). Терминология — [[sa_documentation/naming_conventions|naming_conventions]].

---

## 🎯 Цель шага в PAF-оптике

Спроектировать и насытить **Нексус системы роста** [S1] III.1 — живой цифровой профиль бизнес-модели, в котором **NPV (Net Present Value) является вершиной метрик** [S1, S2], а не LTV/CAC как самоцель. Шаг переводит валидированную на Step 4 ценность в **математически доказанную окупаемую и масштабируемую бизнес-модель** через систему Рычагов (Lever):

- **NPV** = возврат монетизируемой ценности на инвестиции; решающий критерий (LTV/CAC≥3 — лишь необходимое) [[fit-points#🟥 Biz-model fit]];
- **Рычаги (Lever)** = измеримые свойства Б-модели, рост NPV при инвестиции [naming_conventions]; операциональная единица Business Sprint (Рычаги/Lever → NPV [S1] VI.1);
- **AI-COGS** = отдельный рычаг, не спрятанный в «серверах»: `AI-COGS = cost-per-token × tokens-per-user × active-users` [reformation §5.3]; контрольная точка помимо CAC/LTV [S2] III.6;
- **Monte-Carlo** по распределениям входных параметров **заменяет ручной sensitivity ±50%** [5.5] → распределение NPV (P10/P50/P90), а не точечные сценарии.

**Ключевой сдвиг PAF в этом шаге:** финальный артефакт — не «БМ v1.0» как документ, а **цифровой профиль БМ** (`business-model-profile`) в Нексусе системы роста: версонируемый, event-driven обновляемый, с Context Ripeness и CP-планом [reformation §5.3 разрыв 4]. Перебор 6–9 конфигураций в матрице [5.6] **заменён на бизнес-Банч** — связку 2–3 Рычагов в моменте в окне (Bunch Window) с максимальным NPV [S1] VI.6.

**Итог шага:** `business-model-profile` (CR ≥ 65%) + `business-bunch` (NPV > 0 на P50) + проход гейта **🟥 Biz-model fit** (или осознанный отказ — валидный результат, экономия инвестиций).

---

## 🗺️ Карта фаз Sprint (активны)

Внутри Step 5 крутится цикл **Product Sprint** в оптике **Business Lens** [S1] VI.1. Тяжёлые фазы — **BUNCH** (гипотезы БМ, бизнес-Банч рычагов), **EXECUTE** (моделирование NPV/Monte-Carlo, AI-COGS), **HARVEST** (NPV, biz-model fit gate).

| # | Фаза | Суть в Step 5 | Тяжесть |
|---|---|---|---|
| 1 | **PULSE** | Progress Pulse: фиксация состояния Нексуса системы роста + Гэп до biz-model fit (CR после Step 4) | лёгкая |
| 2 | **SCOUT** | Скаутинг паттернов БМ (6 типов), разрывов конкурентов, ценовых возможностей через Business Lens | средняя |
| 3 | **BUNCH** | Гипотеза БМ (BMC/Lean Canvas) + проектирование монетизации из mNSM + воронка AARRR; формирование **бизнес-Банча рычагов** | **тяжёлая** |
| 4 | **PITCH** | Pitching of Trust: защита бизнес-Банча, CP-гейты 5.1–5.4, veto на запуск | средняя |
| 5 | **EXECUTE** | Картирование издержек (7 групп + AI-COGS), моделирование NPV Monte-Carlo, ранжирование Рычагов по эластичности, детект «убийц экономики» | **тяжёлая** |
| 6 | **HARVEST** | Бизнес-Банч с максимальным NPV; breakeven; фиксация цифрового профиля БМ; **гейт 🟥 Biz-model fit** | **тяжёлая** |

> Und-Id-Ex [S1] VI.5: Understand (PULSE/SCOUT) → Identify (BUNCH) → Execute (EXECUTE финмодель). Методы подробно — в `TRADITIONAL/RB-STEP-5-BUSINESS-MODEL-VALIDATION/index.md`.

**Маппинг фаз → подшаги RB-STEP-5:**
- PULSE/SCOUT → подготовка к 5.1;
- BUNCH → **5.1** (гипотеза БМ, BMC, паттерн) + **5.2** (монетизация) + **5.3** (воронка AARRR);
- PITCH → **5.4** (издержки + AI-COGS);
- EXECUTE → **5.5** (юнит-экономика, NPV Monte-Carlo, рычаги);
- HARVEST → **5.6** (breakeven, бизнес-Банч, фиксация цифрового профиля БМ, гейт).

**Три CP-гейта стадии** [reformation §5.7]: 5.2 (монетизация) → 5.4 (издержки/AI-COGS) → 5.5/5.6 (biz-model fit, финальный).

---

## 📥 Вход / 📤 Выход (узлы Нексуса системы роста)

**Вход (из Step 4 — Value):**
- Нексус продукта: валидированное ценностное предложение, **🟧 Need/Value Fit** пройден [[fit-points]];
- Узел **mNSM** (монетизируемая NSM) из 4.6 — корневая метрика, в которую упирается каждая схема монетизации;
- VP-node, VPC-node с CP ≥ порога stage-gate.

**Выход (в Step 6 — Go-to-Market):**
- `business-model-profile` — агрегирующий цифровой профиль БМ (CR ≥ 65%);
- `business-bunch` — выбранный бизнес-Банч (2–3 Рычага в окне, NPV > 0 на P50, Bunch Size/Window);
- `monetization` + `funnel` + `cost-structure` (+ `ai-cogs`) + `unit-economics` (`levers-ranking`, `economy-killers`) + `breakeven-forecast`;
- `cp-trust-plan` — план поднятия CP до подтверждения в Stage 6–8 (Soft Launch, реальные конверсии);
- **🟥 Biz-model fit пройден** (или осознанный отказ).

---

## 👥 Роли

| Роль | Функция в Step 5 |
|---|---|
| **Инженер по развитию бизнеса / Bizdev Architect** | Владелец Нексуса системы роста; **NPV как вершина метрик**; выбор бизнес-Банча; veto на запуск. NPV-моделирование и выбор ставки дисконтирования — **зона человека** [S2] III.4. |
| **Growth Engineer** | Владелец mNSM в финмодели, **AI-COGS** как рычага (cost-per-token × tokens-per-user), time-to-activation; контроль COGS наряду с CAC/LTV [S2] III.6. |
| **Product Ops / Product Architect** | Настройка Кортекс-области «финмодели» (NPV Monte-Carlo, COGS-калькулятор, A/B-симулятор цен); RAG по прайс-листам/бенчмаркам; event-driven пересчёт NPV; рост ИИ-зрелости. |
| **Portfolio Manager** (если есть) | NPV бизнес-Банча как аргумент инвестиционного решения портфеля (Goal Map). |

**Зона человека (критично для Step 5) [S2] III.4, [reformation §5.9]:** **NPV-моделирование и выбор бизнес-Банча — стратегическое распределение ресурсов, не передаётся ИИ как актору.** Кортекс считает и оптимизирует (перебирает комбинации Рычагов), человек верифицирует допущения, выбирает распределения, интерпретирует результат, имеет veto. Утрата стратегического контроля при делегировании NPV-моделирования ИИ — сквозной риск трансформации.

---

## 🔗 Референсы

**Методы (TRADITIONAL/RB-STEP-5-BUSINESS-MODEL-VALIDATION):** [[TRADITIONAL/RB-STEP-5-BUSINESS-MODEL-VALIDATION/index]] · [[5.1 Формирование гипотезы бизнес-модели]] (BMC Остервальдера, 6 паттернов БМ, Lean Canvas) · [[5.2 Схема монетизации]] (5 измерений, 3 метода ценового коридора) · [[5.3 Структура воронки потребителя]] (AARRR, Channel Mix, Aha-moment, churn) · [[5.4 Издержки цепочки создания ценности]] (7 групп, CAC/COGS/SG&A) · [[5.5 Юнит-экономика и моделирование]] (LTV/CAC, sensitivity ±50%, прямая/обратная задача) · [[5.6 Точка безубыточности, прогноз роста и фиксация]]

**«Почему» (AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION):** [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.1 instruction]] (BMC-генератор, Pattern Clusterer) · [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.2 instruction]] (проектировщик монетизации, A/B-симулятор цен, NPV-оценщик схем) · [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.3 instruction]] (симулятор AARRR, churn-предиктор) · [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.4 instruction]] (COGS-калькулятор + AI-COGS) · [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.5 instruction]] (NPV Monte-Carlo, ранжирование Рычагов) · [[AI-TRANSFORMATION/RB-STEP-5-BUSINESS-MODEL-VALIDATION/5.6 instruction]] (оптимизатор бизнес-Банча) · [[AI-TRANSFORMATION/reformation|reformation]] §5

**Каркас:** [[README]] · [[operating-model]] · [[fit-points]] · [[STEP-4-VALUE/overview]]

---

## 🧩 Skill Map / профстандарт

**Skill Map [S3] IV.2 — активные сектора в Step 5:**
- **⑥ Sales & Economics** (монетизация ценности продукта и финансовое планирование) — **ядро шага**; внешний круг (senior/head/CPO): NPV-моделирование, бизнес-Банч, цифровой профиль БМ как стратегические артефакты;
- **④ Growth & Experiments** (воронка AARRR, retention, churn-модели) — фаза EXECUTE.

**Профстандарт 06.012 [S4]:** **C/02.6** (бизнес-планы / цены / стратегия серии, уровень 6 — Portfolio Manager / Bizdev Architect) и **B/02.5** (определение продукта / показатели успешности, уровень 5 — Product Engineer). NPV как инвестиционный критерий → C/02.6.

**Уровень владения:** внешний круг (senior/head/CPO) [S3] IV.3 — целеполагание, стратегические инициативы, NPV бизнес-юнита. Профиль компетенций — **Comb-shaped** [S2], не T-shaped.

---

## 🧭 Ключевые концепции шага (глоссарий)

| Понятие | Суть | Источник |
|---|---|---|
| **NPV (вершина метрик)** | Возврат монетизируемой ценности на инвестиции; решающий критерий biz-model fit | [S1, S2], fit-points |
| **Рычаг (Lever)** | Измеримое свойство Б-модели, рост NPV при инвестиции; операционная единица Business Sprint | naming_conventions, [S1] VI.1 |
| **AI-COGS** | cost-per-token × tokens-per-user × active-users; отдельный рычаг, не спрятанный в «серверах» | reformation §5.3 |
| **Бизнес-Банч** | Связка 2–3 Рычагов в моменте под Bunch Size/Window; НЕ матрица конфигураций, НЕ Беклог | [S1] VI.6, reformation §5.3 |
| **Monte-Carlo** | Моделирование по распределениям параметров; заменяет ручной sensitivity ±50% | 5.5, reformation |
| **Цифровой профиль БМ** | Живой узел Нексуса (`business-model-profile`); НЕ «БМ v1.0» как документ | naming_conventions |
| **COGS-эксплозия** | Стресс-тест AI-COGS при usage ×2/×5; парадокс Джевонса | [S2] III.5, reformation §5.9 |
| **«Убийцы экономики»** | Параметры, малое ухудшение которых обращает NPV в отрицательный | 5.4, 5.5 |

---

## ⚠️ Главные риски шага (что может убить валидность)

1. **«Оптимистичный Excel»** [reformation §5.9] — каскадная ошибка: неточность в одном параметре размножается через формулы в breakeven. Контрмера: Monte-Carlo (вскрывает чувствительность), не точечная модель.
2. **COGS-эксплозия AI-фич** — AI-COGS спрятан в «серверах» → ложный breakeven. Контрмера: AI-COGS как отдельная строка + стресс usage ×2/×5.
3. **Галлюцинации цифр** — ARPU/WTP/конверсии без источника = workslop (~15,4% [S2] III.7). Контрмера: трассировка каждого числа до источника.
4. **Утрата стратегического контроля** — делегирование NPV-моделирования/выбора Банча ИИ как актору. Контрмера: зона человека [S2] III.4; агенты = инструменты.
5. **Дофаминовая петля ИИ** [S2] III.7 — «красивая» модель с положительным NPV приятнее реалистичной с NPV≈0. Контрмера: человек обязан сопротивляться.

---
**Version:** 1.0 · **Last updated:** 2026-06-20 · **Maintained by:** AI-KORTEX
