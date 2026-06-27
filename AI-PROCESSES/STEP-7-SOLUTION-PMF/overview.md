---
nexus: product
node_id: aip-7-overview
node_type: step-overview
paf_step: 7
sprint_phase: null
kind: normative
owner: Product Engineer
confidence: 1.0
sources: ["[S1]", "[S2]", "[S3]", "[S4]", "RB-STEP-7"]
updated: 2026-06-20
ttl_days: 365
ripeness: fresh
tags: ["fit-point"]
---

# overview — Step 7: Solution & PMF

> Веха Discovery · Линза: **Product** · Fit-точка: 🟫 PMF
> Источник: [[operating-model]] (5 столпов, 3PL, цикл Sprint, CP, роли) · Термины — по [[sa_documentation/naming_conventions|naming_conventions]].
> Версия Нексуса продукта: **v0.3 (из Step 4–6) → v1.0 (Stage 7, CR ≥ 80%, PMF-точка)**.

---

## 🎯 Цель шага в PAF-оптике

Запустить **цикл Product Sprint до PMF**: перевести подтверждённую ценность (из Step 4–6) в конкретное работающее решение, для которого группа потребителей выбирает продукт **основным способом** удовлетворения потребности. На выходе:

1. **Нексус продукта v1.0** (CR ≥ 80%): узлы `solution-hypothesis` → `prototype` → `final-solution` → `user-story/use-case/nfr` → `entity/sequence/state` → `increment` → `pmf-signal/mnsm/npv`.
2. **MVP как стратегия разработки** (Бланк/Робинсон/Шарп) — не «минимум фич», а параллельная/синхронная разработка и верификация для диверсификации рисков.
3. **PMF-точка (🟫)** — конвергенция **≥3 сигналов**: retention-плато (или referral/post-deal) + опрос Шона Эллиса ≥40% + **NPV > 0** воспроизводимо.
4. **Harvesting**: фиксация NPV/mNSM как инкремента контекста → триггер нового цикла Sprint → переход к Step 8 (Acquisition / PCF).

> **Сначала Нексус, потом Кортекс** [S1] IX — без спелого контекста продукта Кортекс вайбкодит мусор. Каждый узел без источника/гипотезы-источника → CP=0. **MVP ≠ «продукт с минимумом фич»** — это концепция разработки.

---

## 🗺️ Карта фаз Sprint (активны в Step 7)

Шесть фаз цикла Product Sprint [S1] VI.4–VI.5 крутятся здесь в **build-режиме** (EXECUTE = разработка+дистрибуция). Три фазы — **тяжёлые**:

| Фаза | Активность в Step 7 | Вес |
|---|---|---|
| **PULSE** | Фиксация состояния Нексуса продукта v0.3 (узлы ценности из Step 4–6), Гэп (gap) к Видению → intent цикла | лёгкая |
| **SCOUT** | Скаутинг возможностей/угроз через Линзу продукта: генерация гипотез решения (Identify-фаза Und-Id-Ex), CJM/User Flow, ИИ-метафоры | средняя |
| **BUNCH** | **ТЯЖЁЛАЯ.** Гипотезы решения как фичи Банча (Bunch Size/Window, кандидат mNSM, NPV-оценка). MoSCoW не объект управления — Банч. | 🔴 |
| **PITCH** | **Pitching of Trust**: юзабилити ≥5 + Red-Team Банча; скоринг через mNSM×CP→вклад в NPV; финальное решение для разработки | средняя |
| **EXECUTE** | **ТЯЖЁЛАЯ.** Вайбкодинг прототип → MVP (Build+Bale+Germination); цифровой профиль продукта; Entity/Sequence/State; цикл Build→Change Log; параллельная верификация | 🔴 |
| **HARVEST** | **ТЯЖЁЛАЯ.** PMF-точка: фиксация NPV/mNSM, PMF-детектор (≥3 сигнала), инкремент контекста → новый Pulse | 🔴 |

---

## 📥 Вход / 📤 Выход (узлы Нексуса продукта)

**Вход (из Step 4–6):**
- **Нексус продукта v0.3**: VP-node, VPC-node (need/value fit 🟧 из Step 4), узлы бизнес-модели (NPV>0, 🟥 biz-model fit из Step 5), Bale/Germination/позиционирование из Step 6.
- Нексус потребителя: JTBD, персоны, поведение AS-IS, подтверждённая ценность.
- **Карта Целей (Goal Map)** [S1] VI.1 — связь 3 Линз; кандидат mNSM из Step 2–3.

**Выход (в Step 8):**
- **Нексус продукта v1.0** (CR ≥ 80%): живой граф узлов `solution-hypothesis` … `pmf-result`/`harvesting`.
- **🟫 PMF подтверждён** (конвергенция ≥3 сигналов): группа потребителей выбрала продукт основным способом.
- **mNSM подтверждена** (NSM прошла проверку монетизируемости) → ребро NPV.
- **Проигравшие решения** (losing-solutions) с условием возврата — Ставки следующих итераций.

> **Не пройден PMF → главная точка осознанного отказа** в Product Discovery [S1] reformation 7.9. PMF не объявлять преждевременно (premature PMF = масштабирование непродукта).

---

## 👥 Роли

Step 7 = объект **Product Lens** [S1] VI.1 → ведущие роли: **Product Engineer** + **Discovery/Launcher PM** (вайбкодинг).

| Роль | Функция на Step 7 | Зона |
|---|---|---|
| **Product Engineer** | Проектирует «цифровой профиль продукта» (инженерия контекста по Тоби Лютке); определяет AI workflow; формулирует Гэп к Видению; отвечает за конвергенцию сигналов PMF; стратегическое решение об уровне MVP. **НЕ вайбкодер.** | продукт |
| **Discovery / Launcher PM** | **Вайбкодинг** прототип→MVP; минимизация time-to-market/time-to-PMF; full-stack человек-команда (весь цикл). | запуск продукта |
| **AI UX Designer** | ИИ-метафоры взаимодействия (намерение→черновик→уточнение); Screen Map; онбординг вокруг Aha Moment; tone-of-voice. | UX & UI |
| **Technical / AI Product Manager** | AI-свойства: сшивает агентов, KPI точность/прецизионность/полнота, контроль **COGS токенов**. | продукт с ИИ |
| **Product Ops** | Поддерживает Нексус продукта, цикл Build→Change Log, асинхронный Kanban; рост ИИ-зрелости команды. | product operations |

> ⚠️ **Зона человека (не делегируется ИИ) [S2] III.4:** стратегическое решение об уровне MVP, фокусный JTBD, финальное решение для разработки, **объявление PMF и масштабирования**. Агенты — инструменты, не акторы; ответственность не передать.

---

## 🤖 Кортекс: 6 инструкций Step 7 (узлы Нексуса продукта)

Из `AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/`:

1. **Генератор гипотез решения + AI UX Designer-агент + CJM/User Flow-билдер + CP-скорер** — `7.1` — Identify-фаза Und-Id-Ex; кандидаты фич Банча в формате Solution Hypothesis Card.
2. **Вайбкодинг-агент / MVP-builder + Smoke-test-агент + Сценарий-билдер + CR-трекер** — `7.2` — 7 типов прототипов генерирует Кортекс.
3. **Модератор юзабилити + Affinity-агент + Pitching of Trust-агент (Red-Team) + NPV/mNSM-скорер** — `7.3` — Pitching of Trust gate.
4. **Генератор User Stories/Use Cases + NFR-агент + Screen Map + Банч-архитектор + Traceability** — `7.4` — цифровой профиль продукта (Нексус).
5. **Вайбкодинг-агент MVP + Entity/Sequence/State-агенты + Верификация-агент + Product Ops-агент** — `7.5` — Build-фаза, цикл Build→Change Log.
6. **Аналитика-агент + Aha Moment-агент + PMF-детектор + mNSM-агент + Harvesting-агент** — `7.6` — Harvesting и PMF-точка.

---

## 🛡️ Главные риски шага

1. **Premature PMF** (workslop-зона №1 Step 7): объявление PMF на одном сигнале / на маленькой выборке / без NPV. Защита — конвергенция ≥3 сигналов, минимальная выборка (50–100 в когорте, ≥40 ответов опроса) [S1] reformation 7.9.
2. **Workslop в вайбкодинге (~15,4%)** [S2] III.7: сгенерированный код/прототип выглядят убедительно, но не проверяют гипотезы. Защита — метапознание Launcher PM: проходит сам, объясняет команде, veto на «красивый, но пустой».
3. **MoSCoW-рефлексия**: «80% Must Have» = не сократили MVP, а переложили весь продукт. Объект управления — **Банч** в моменте под Карту Целей, Must Have ≤ 60%.
4. **NSM ↔ mNSM-путаница**: NSM ценностна, но может быть не монетизируема; без mNSM NPV не считается.

---

## 🔗 Референсы

- **Методы:** [[RB-STEP-7-SOLUTION-VALIDATION/index]] + 7.1 (гипотезы решения/UX) · 7.2 (прототипы) · 7.3 (валидация/скоринг) · 7.4 (требования) · 7.5 (MVP) · 7.6 (аналитика/PMF).
- **«Почему»:** [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.1 instruction|7.1]] · [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.2 instruction|7.2]] · [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.3 instruction|7.3]] · [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.4 instruction|7.4]] · [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.5 instruction|7.5]] · [[AI-TRANSFORMATION/RB-STEP-7-SOLUTION-VALIDATION/7.6 instruction|7.6]] · [[AI-TRANSFORMATION/reformation|reformation §7]].
- Фазы шага: [[1.pulse]] · [[2.scout]] · [[3.bunch]] · [[4.pitch]] · [[5.execute]] · [[6.harvest]].
- Назад: [[STEP-6-GO-TO-MARKET/overview]] · Дальше: [[STEP-8-ACQUISITION-PCF/overview]] (PCF; Discovery завершён).

---

## 🧩 Skill Map / профстандарт

- **Skill Map [S3]:** сектор **2 Value & Solution Design** (ценностные предложения и решения) + сектор **3 Development & Delivery** (вайбкодинг, требования, MVP) + зарождающийся сектор **4 Growth & Experiments** (PMF-точка). Средний круг, middle/senior.
- **Профстандарт 06.012 [S4]:** обобщённая функция **B** «Управление ИТ-продуктом», уровень 5 — B/02.5 «определение продукта/дизайн/требования» + B/03.5 «дизайн/выпуск обновлений» + B/04.5 «заказ разработки/контроль/приёмка» + B/06.5 «вывод на рынок» + B/08.5 «показатели успешности» (Product Engineer; Launcher PM как full-stack продукт+код).

> ⚠️ Связка стандарт ↔ PAF — **интерпретативная** [S3]. PAF переопределяет **способ** работы — через Нексус и Кортекс, не вручную [S1].

---
**Version:** 1.0 · **Last updated:** 2026-06-20 · **Maintained by:** AI-KORTEX
