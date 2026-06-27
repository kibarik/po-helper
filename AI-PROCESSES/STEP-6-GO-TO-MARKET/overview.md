---
nexus: growth
node_id: aip-6-overview
node_type: step-overview
paf_step: 6
sprint_phase: null
kind: normative
owner: Growth Engineer
confidence: 1.0
sources: ["[S1]", "[S2]", "[S3]", "[S4]", "RB-STEP-6"]
updated: 2026-06-20
ttl_days: 365
ripeness: fresh
tags: []
---

# overview — Step 6: Go-to-Market

> **Веха Discovery · Линза: Business (+ Product) · Fit-точка: — (дистрибуция = bottleneck по Голдратту [S2])**
> Источник: PAF [S1]–[S4]; методы — `TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY` (index + 6.1–6.6); «почему» — `AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY` (6 инструкций). Терминология — [[sa_documentation/naming_conventions|naming_conventions]].

---

## 🎯 Цель шага в PAF-оптике

Спроектировать **Bale + Germination** — связку «инкремент + оффер + план дистрибуции» [S1] VI.4 и проращивание аудитории в ценность фичи [S1] VI.4 — и провести её через **mNSM/NPV-оптику по каналам и офферам**.

Линза шага — **Business (+ Product для позиционирования и First Value)**. ИИ снял bottleneck с Discovery/разработки и сместил его на **дистрибуцию (последняя миля)** [S2, Голдратт, Theory of Constraints]. Поэтому Step 6 — это проектирование узкого горлышка роста:

- **Bale** = инкремент + оффер (6.2) + дистрибуция (6.3/6.4) + скрипт (6.6) → arteфакт цикла Product Sprint [S1] VI.4.
- **Germination** = агентизированный онбординг, минимизация **time-to-activation**, Кортекс-Handoff (клиент не повторяет контекст между ролями).
- Метрики-вершины — **mNSM / NPV / COGS токенов** (не CAC/LTV как самоцель; CAC/LTV — прокси, `CAC_max = LTV/3` — ограничение, не цель [reformation 5.3]).

Fit-точки на шаге нет, но внутри него работают **CP-гейты** фаз Sprint (Gate-A запуск канала/оффера, Gate-B масштабирование, Gate-C релиз скрипта). Шаг замыкается **Harvesting-циклом**: фактический NPV канала/оффера → инкремент контекста в Нексус системы роста → цикл Product Sprint заново.

---

## 🗺️ Карта фаз Sprint (активны)

Внутри Step 6 крутится один цикл **Product Sprint** [S1] VI.4. В build-шаге (6) EXECUTE = **Build + Bale + Germination** (не валидация, как в discovery-шагах 1–5). Тяжёлые фазы — **SCOUT, BUNCH, EXECUTE**.

| # | Фаза | Суть в Step 6 | Линза | Вес |
|---|---|---|---|---|
| 1 | **PULSE** | Progress Pulse: фиксация состояния Нексуса рынка + системы роста, гэп дистрибуции | Business | лёгкая |
| 2 | **SCOUT** | Скаутинг возможностей/угроз: позиционирование (6.1) + скаутинг каналов (6.3) — замена приоритизации [Принцип 5] | Strategy + Business | **тяжёлая** |
| 3 | **BUNCH** | Bale = оффер (6.2) + бизнес-Банч каналов с комплексным NPV (6.4): 3 критерия Банча [S1 VI.6] | Business | **тяжёлая** |
| 4 | **PITCH** | Pitching of Trust на офферах/бюджете; role-play Pitching на скриптах (6.6 → Gate-C) | Business | средняя |
| 5 | **EXECUTE** | Bale + Germination: онбординг/time-to-activation (6.5), скрипты продаж (6.6), Кортекс-Handoff | Business + Product | **тяжёлая** |
| 6 | **HARVEST** | Harvesting: фиксация NPV канала/оффера → инкремент в Нексус роста; цикл заново | Business | лёгкая |

> Und-Id-Ex [S1] VI.5: Understand (PULSE/SCOUT) → Identify (BUNCH) → Execute (Bale+Germination). Полный проход методов — в `TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/index.md`.

---

## 📥 Вход / 📤 Выход (узлы Нексуса рынка + системы роста)

**Вход (из Step 5 — Business Model):**
- 🟥 Biz-model fit пройден: бизнес-Банч (2–3 рычага) с NPV > 0 на P50; AI-COGS-стресс пройден (cost-per-token × tokens-per-user при usage ×2/×5);
- Нексус системы роста v1 (Рычаги/Lever → NPV; CAC_max = LTV/3);
- Проверенные ценностные предложения из Step 4 (need/value fit) — основа офферов;
- Нексус рынка v1 (конкуренты, mNSM-проверка).

**Выход (в Step 7 — Solution & PMF):**
- **Bale-комплект**: Offer-узлы (6.2) + Marketing-Mix-узел/Банч каналов (6.3) + Budget-NPV-узлы (6.4) + Script-узлы (6.6);
- **Germination-комплект**: Activation-Funnel-узлы, First-Value-узел, Handoff-узлы, Service-Blueprint-узлы, Onboarding-sequence (6.5);
- **Positioning-statement-узел** + подграф Strategy Canvas / Perceptual Map / 4 Forces (6.1) в Нексусе рынка;
- **Harvesting-узел** — фактический NPV канала/оффера после Soft Launch → Context Ripeness Нексуса роста вырос;
- CP-гейты: Gate-A (запуск канала/оффера), Gate-B (масштабирование), Gate-C (релиз скрипта) — пройдены/отказ.

---

## 👥 Роли

| Роль | Функция в Step 6 |
|---|---|
| **Growth Engineer / Growth PM** | Владелец Нексуса системы роста; **минимизация time-to-activation**, максимизация mNSM/LTV; ROI токенизируемых функций; **контроль COGS токенов помимо CAC/LTV** [S2 III.6] |
| **Product Engineer** | Product/Channel Fit (конфигурация сегмент-канал-оффер); veto на запуск канала (Gate-A) и масштабирование (Gate-B); Product-линза воронки активации и First Value |
| **AI UX Designer** | **tone-of-voice** офферов/месседжинга/онбординга/скриптов; проектирование метафор ИИ-взаимодействия (намерение→черновик→уточнение [S2] III.8); не «чат-бот без изменений UX» |
| **Product Ops / Product Architect** | Настройка агентов (позиционирование, генератор офферов, скаутинг каналов, симуляция воронки, Handoff, role-play Pitching); мониторинг Context Ripeness; event-based триггеры; рост ИИ-зрелости |

**Зона человека (не передавать ИИ) [S2] III.4:** стратегический выбор Marketing Mix (распределение ресурсов), выбор фокуса позиционирования (1–2 типа конкурентов), выбор главного оффера, прямые продажи/переговоры, NPV-моделирование и инвестиционные решения по портфелю каналов. Агенты — инструменты, не акторы.

---

## 🔗 Референсы

**Методы (TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY):** [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/index]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.1 Стратегия позиционирования и точки дифференциации|6.1]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.2 Уникальное торговое предложение и офферы|6.2]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.3 Стратегия привлечения: каналы и целевая аудитория|6.3]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.4 Планирование маркетингового бюджета|6.4]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.5 Стратегия активации и процессы работы с клиентом|6.5]] · [[TRADITIONAL/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.6 Скрипты продаж и план продаж|6.6]]

**«Почему» (AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY):** [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.1 instruction|6.1 (позиционирование/скрейпинг)]] · [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.2 instruction|6.2 (офферы + AI UX Designer tone-of-voice)]] · [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.3 instruction|6.3 (Persona/CJM скаутинг каналов)]] · [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.4 instruction|6.4 (симуляция воронки/бюджета + COGS)]] · [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.5 instruction|6.5 (Germination/Handoff)]] · [[AI-TRANSFORMATION/RB-STEP-6-GO-TO-MARKET-STRATEGY/6.6 instruction|6.6 (скрипты/role-play Pitching)]] · [[AI-TRANSFORMATION/reformation]] · [[AI-TRANSFORMATION/index]]

**Каркас:** [[README]] · [[operating-model]] · [[fit-points]] · [[STEP-5-BUSINESS-MODEL/overview]] (назад) · [[STEP-7-SOLUTION-PMF/overview]] (вперёд)

---

## 🧩 Skill Map / профстандарт

**Skill Map [S3] IV.2 — 6 секторов, активны в Step 6:**
1. **Product Marketing (5)** — позиционирование, офферы/УТП, каналы/ЦА/CJM, tone-of-voice (ядро шага);
2. **Sales & Economics (6)** — бюджет-NPV, юнит-экономика, скрипты продаж, план продаж как NPV-модель;
3. **Growth & Experiments (4)** — активация, time-to-activation, онбординг, скаутинг как эксперимент;
4. **Development & Delivery (3)** — Service Blueprint, Handoff между ролями.

**Профстандарт 06.012 [S4]:** функция **B** (Управление ИТ-продуктом) — **B/06.5 «Вывод на рынок»** (позиционирование, офферы, каналы, бюджет, активация, план продаж) и **B/07.5 «Экспертное сопровождение продаж»** (скрипты, банк возражений, Elevator Pitch), уровень квалификации 5 — **Product Engineer / Growth Engineer**. На стратегическом уровне — **C/06.6 «Продвижение»**, **C/04.6 «Бюджет серии»** (уровень 6, Portfolio Manager). Классификация ОКЗ 3322 «агенты по коммерческим продажам».

**Уровень владения:** средний–внешний круг (middle/senior → head/CPO) [S3] IV.3 — анализ, целеполагание, масштабирование. Профиль компетенций — **Comb-shaped** [S2], не T-shaped.

---

## 🧭 Ключевой вопрос шага

> **Почему потребитель должен выбрать именно нас, а не альтернативный продукт — и как мы гарантированно до него доберёмся (дистрибуция = bottleneck [S2, Голдратт])?**

Ответ собирается в **Bale**: позиционирование (6.1) → оффер (6.2) → канал (6.3) → бюджет-NPV (6.4) → Germination (6.5) → скрипт (6.6). Шаг не имеет fit-точки, но его выход (Bale + Germination + Harvesting) — основа для Step 7 (Solution & PMF) и Step 8 (Acquisition & PCF). Полная валидация PCF (4 уровня выборки, LTV/CAC ≥ 3 на когортах) — в Step 8, не здесь.

---

## 🛡️ Гвардраилы шага (свод)

- **Гейт метапознания на офферах (6.2) и скриптах (6.6) — главная зона workslop всей стадии** [reformation 6.3]: проверяемость каждой цифры/гарантии; трассировка до узла Нексуса; Human-in-the-loop.
- **COGS токенов на AI-привлечение/онбординг** — отдельный рычаг (cost-per-token × tokens-per-user); стресс usage ×2/×5; в полный CAC; не прятать в «серверы/OpenAI API» [reformation 5.3].
- **Скаутинг вместо приоритизации** [Принцип 5, S1]: «матрица приоритизации» как артефакт запрещена; Банч каналов в моменте.
- **mNSM/NPV/COGS** — метрики-вершины; CAC/LTV — прокси; `CAC_max = LTV/3` — ограничение, не цель.
- **Event-based, не каденции** [S1] VI.2: ритуалы продаж/активации срабатывают по триггерам, не по расписанию.

---
**Version:** 1.0 · **Last updated:** 2026-06-20 · **Maintained by:** AI-KORTEX
