# overview — Step 1: Idea & Context

> **Веха Discovery · Линза: Strategy + Business + Product (все 3 Линзы) · Fit-точка: — (входная веха)**
> Источник: PAF [S1]–[S4]; методы — `RB-STEP-1-IDEA` (TRADITIONAL); «почему» — `AI-TRANSFORMATION/RB-STEP-1-IDEA` (19 инструкций). Терминология — [[sa_documentation/naming_conventions|naming_conventions]].

---

## 🎯 Цель шага в PAF-оптике

Сгенерировать **BIG Idea** — артикулированное **Видение (Vision)** продукта из **фич (Features)** [S1] базовая логика — проведя её через **все 3 Линзы (3PL)** [S1] VI.1:

- **Strategy Lens** → Нексус рынка → **Ставки (Bets)**;
- **Business Lens** → Нексус роста → **Рычаги (Levers) → NPV / mNSM**;
- **Product Lens** → Нексус продукта → **Банч фич (Feature Bunch)**.

Это **первое насыщение трёх Нексусов** (рынка, продукта, роста) до **Context Ripeness ≥ 60%** [S1] III.1, [reformation] §1.6. Базис цикла — **null base** [S1] VI.5: продукта ещё нет → discovery с нуля (гипотезы потребностей → ЦП → реализации). На data base (есть продукт) — извлекаем знания о поведении.

**Итог шага:** Нексусы v1.0 (CR ≥ 60%) + `Bunch-v2` (Confirmed фичи с final CP) + `Vision-v1` (BIG Idea Statement) + Go-Decision с resource commitment. Fit-точки нет — это входная веха, но внутри шага работают **CP-гейты** каждой фазы Sprint.

**Null base vs Data base** [S1] VI.5 (определяется в PULSE, влияет на весь цикл):
- **Null base** — нет данных/продукта → discovery с нуля: гипотезы потребностей → ЦП → реализации. SCOUT генерирует Vision (1.2 Нексус продукта);
- **Data base** — есть продукт → извлекаем знания о поведении, находим бутылочные горлышки. SCOUT заливает Current State из product analytics.

**Шесть принципов PAF** [S1] Часть II (операционализация для BIG Idea): ① прозрачность до очевидности (Нексусы + отсутствие Беклога); ② совместная унификация контекста; ③ Stagility (стабильность цели, гибкость пути); ④ риск = знание (через CP); ⑤ скаутинг вместо приоритизации; ⑥ прибыль через ценность (mNSM → NPV).

---

## 🗺️ Карта фаз Sprint (активны)

Внутри Step 1 крутится один цикл **Product Sprint** [S1] VI.4. Тяжёлые фазы (SCOUT/BUNCH/PITCH) несут основную нагрузку Discovery; PULSE/EXECUTE/HARVEST — легче.

| # | Фаза | Суть в Step 1 | Линза | Вес |
|---|---|---|---|---|
| 1 | **PULSE** | Progress Pulse: фиксация состояния 3 Нексусов + стартовый Гэп + базис (null/data) | над 3PL | лёгкая |
| 2 | **SCOUT** | Скаутинг возможностей/угроз через 3 Линзы: First Principles + Blue Ocean (ERRC), BMC/JTBD | Strategy + Business + Product | **тяжёлая** |
| 3 | **BUNCH** | Формирование BIG Idea Банча: 5–7 фич по 3 критериям → комплексный NPV | над 3PL | **тяжёлая** |
| 4 | **PITCH** | Pitching of Trust: защита Банча, Red-Team «kill it», final CP, Go-Decision | над 3PL | **тяжёлая** |
| 5 | **EXECUTE** | Rapid validation гипотез Банча (smoke/prototype/customer validation) | Product | лёгкая |
| 6 | **HARVEST** | Harvesting: авто-коммит learnings в Нексусы v1.0, CR ≥ 60% | над 3PL | лёгкая |

> Und-Id-Ex [S1] VI.5: Understand (PULSE/SCOUT) → Identify (BUNCH/EXECUTE) → Execute (валидация). Полный проход методов — в `TRADITIONAL/RB-STEP-1-IDEA/index.md`.

---

## 📥 Вход / 📤 Выход (узлы Нексуса)

**Вход (из Step 0 — Foundation):**
- Скелеты 3 Нексусов как графы Узлов (рынка/продукта/роста) с метаданными `источник`, `Confidence Point`, `timestamp`, `статус увядания` [S1] III.1;
- Каркас PAF (6 принципов, роли, модель зрелости Кортекса) — усвоен;
- Выбрана фаза зрелости Кортекса (1/2/3) [S1] Часть VII.

**Выход (в Step 2 — Customer):**
- Нексусы v1.0 (CR ≥ 60% по каждому) с `aging`/`stale`-флагами;
- `Bunch-v2` (Confirmed фичи, final CP ≥ порога, mNSM-рёбра, NPV-вклад);
- `Vision-v1` (BIG Idea Statement + Supporting Details + Assumption-Audit);
- `Pitching-Decision` + `Resource-Commitment` (approved/dropped per feature);
- `Nexus-Summary-v1.0` (CR-таблица по 3 Нексусам).

---

## 👥 Роли на шаге

| Роль | Функция в Step 1 |
|---|---|
| **Product Engineer** | Запускает цикл, ставит задачи Кортексу, формулирует Vision и Ставки (зона человека [S2] III.4), veto на vanity-mNSM |
| **Product Ops / Product Architect** | Поддерживает Nexus RAG, метрику CR как вычисляемую, пороги увядания; двигает команду по модели зрелости Кортекса |
| **Portfolio Manager** | Сверяет Гэп/Vision с Картой Целей портфеля (Goal Map), подтверждает resource commitment |
| **Growth Engineer** | Валидирует mNSM-потенциал и NPV-вклад фич Банча |
| **Discovery / Launcher PM** (если есть) | Вайбкодит smoke test/прототип в EXECUTE [S2] III.6 |

**Зона человека (не передавать ИИ) [S2] III.4:** целеполагание (какой Гэп закрываем, какие Ставки), формулировка Vision, голосование за CP и решение о resource commitment.

---

## 🔭 Три Линзы (3PL) на этом шаге

Step 1 — единственный шаг, где **активны все три Линзы одновременно** [S1] VI.1:

| Линза | Объект | Спринт | Нексус | Что насыщаем |
|---|---|---|---|---|
| **Strategy** | портфель / рынок | Strategic Sprint | рынка | `Strategic-Opportunity`, `Bet` |
| **Business** | модель роста | Business Sprint | роста | `Monetization-Hypothesis`, `mNSM-numeric`, `Lever` |
| **Product** | продукт | Product Sprint | продукта | `JTBD-Opportunity`, `Feature`, `Vision` |

Связь между Линзами — через **Карту Целей (Goal Map)** [S1] III.2, синхронизация между командами — без прямого вмешательства. SCOUT проходит все три Линзы последовательно; BUNCH/PITCH/HARVEST работают **над 3PL** (синтез).

---

## 🔗 Референсы

**Методы (TRADITIONAL/RB-STEP-1-IDEA):** [[TRADITIONAL/RB-STEP-1-IDEA/index]] · [[TRADITIONAL/RB-STEP-1-IDEA/1.0 Базовые концепции]] · [[TRADITIONAL/RB-STEP-1-IDEA/2.1 Linza Strategy]] · [[TRADITIONAL/RB-STEP-1-IDEA/2.2 Linza Business]] · [[TRADITIONAL/RB-STEP-1-IDEA/2.3 Linza Product]] · [[TRADITIONAL/RB-STEP-1-IDEA/3.3 AI Bunch Formation]] · [[TRADITIONAL/RB-STEP-1-IDEA/5.1 BIG Idea Statement]] · [[TRADITIONAL/RB-STEP-1-IDEA/6.1 Pitching of Trust]]

**«Почему» (AI-TRANSFORMATION/RB-STEP-1-IDEA):** [[AI-TRANSFORMATION/RB-STEP-1-IDEA/0.1 instruction]] (Pulse) · [[AI-TRANSFORMATION/RB-STEP-1-IDEA/2.1 instruction]] (Scouting) · [[AI-TRANSFORMATION/RB-STEP-1-IDEA/3.3 instruction]] (Bunch Architect) · [[AI-TRANSFORMATION/RB-STEP-1-IDEA/5.1 instruction]] (Vision-Synth) · [[AI-TRANSFORMATION/RB-STEP-1-IDEA/6.1 instruction]] (Red-Team) · [[AI-TRANSFORMATION/reformation]] · [[AI-TRANSFORMATION/index]]

**Каркас:** [[README]] · [[operating-model]] · [[fit-points]] · [[STEP-0-FOUNDATION/overview]]

---

## 🧩 Skill Map / профстандарт

**Skill Map [S3] IV.2 — 6 секторов, активны в Step 1:**
1. **Discovery & Researches** (Нексусы рынка/продукта, скаутинг) — ядро шага;
2. **Value & Solution Design** (Vision, ценностное предложение) — фаза PITCH;
3. **Growth & Experiments** (гипотезы, CP, smoke tests) — фаза EXECUTE;
4. **Sales & Economics** (NPV, mNSM, комплексный NPV Банча) — BUNCH/PITCH.

**Профстандарт 06.012 [S4]:** функция **B** (Управление ИТ-продуктом, B/01.5 продуктовые исследования, B/02.5 определение продукта), уровень квалификации 5 — **Product Engineer**. Для стратегической линзы — **C/02.6** стратегия серии (уровень 6, Portfolio Manager).

**Уровень владения:** средний–внешний круг (middle/senior → head/CPO) [S3] IV.3 — анализ, целеполагание, стратегические инициативы. Профиль компетенций — **Comb-shaped** [S2], не T-shaped.

---
**Version:** 1.0 · **Last updated:** 2026-06-20 · **Maintained by:** AI-KORTEX
